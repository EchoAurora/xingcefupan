import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import streamlit_authenticator as stauth

# --- 1. 用户权限配置 ---
# 建议在此处添加你的小伙伴。注意：密码目前为明文，部署后请妥善保管网址
names = ['管理员', '练习生01', '练习生02']
usernames = ['admin', 'user1', 'user2']
passwords = ['123456', '123456', '123456'] # 初始密码统一为 123456

# 初始化验证器
authenticator = stauth.Authenticate(
    {'usernames': {un: {'name': n, 'password': p} for n, un, p in zip(names, usernames, passwords)}},
    'civil_service_cookie',
    'signature_key',
    cookie_expiry_days=30
)

# 渲染登录界面
name, authentication_status, username = authenticator.login('行测数字化看板 - 登录', 'main')

if authentication_status:
    # --- 2. 核心配置与数据隔离 ---
    # 每个用户拥有独立的 CSV 文件，互不干扰
    DB_FILE = f'data_storage_{username}.csv'
    GOAL_SCORE = 100.0  # 125题 * 0.8分 = 100分满分制
    FIXED_WEIGHT = 0.8  # 单题分值

    # 模块配置
    DEFAULT_MODULES = {
        "政治理论": {"total": 15, "plan": 5, "weight": FIXED_WEIGHT, "target_sec": 30},
        "常识判断": {"total": 15, "plan": 5, "weight": FIXED_WEIGHT, "target_sec": 30},
        "言语-逻辑填空": {"total": 10, "plan": 9, "weight": FIXED_WEIGHT, "target_sec": 45},
        "言语-片段阅读": {"total": 15, "plan": 9, "weight": FIXED_WEIGHT, "target_sec": 50},
        "数量关系": {"total": 15, "plan": 25, "weight": FIXED_WEIGHT, "target_sec": 90},
        "判断-图形推理": {"total": 5, "plan": 5, "weight": FIXED_WEIGHT, "target_sec": 45},
        "判断-定义判断": {"total": 10, "plan": 10, "weight": FIXED_WEIGHT, "target_sec": 55},
        "判断-类比推理": {"total": 10, "plan": 5, "weight": FIXED_WEIGHT, "target_sec": 35},
        "判断-逻辑判断": {"total": 10, "plan": 15, "weight": FIXED_WEIGHT, "target_sec": 60},
        "资料分析": {"total": 20, "plan": 25, "weight": FIXED_WEIGHT, "target_sec": 65}
    }

    def load_data():
        if os.path.exists(DB_FILE):
            try:
                df = pd.read_csv(DB_FILE)
                df['日期'] = pd.to_datetime(df['日期']).dt.date
                return df
            except:
                return pd.DataFrame()
        return pd.DataFrame()

    def save_data(df):
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

    df = load_data()

    # --- 3. 侧边栏导航 ---
    with st.sidebar:
        st.title(f"👋 你好, {name}")
        menu = st.radio("功能导航", ["🏠 数字化看板", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"])
        st.divider()
        authenticator.logout('退出登录', 'sidebar')

    # --- A. 数字化看板 ---
    if menu == "🏠 数字化看板":
        st.title("📊 个人备考深度诊断")
        if df.empty:
            st.info("💡 暂无数据。请前往'录入成绩'开始第一次模考复盘！")
        else:
            latest = df.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("本次总分", f"{latest['总分']:.1f}")
            c2.metric("全卷正确率", f"{(latest['总正确数'] / latest['总题数']):.1%}")
            c3.metric("总用时", f"{int(latest['总用时'])} min")
            c4.metric("题目单价", f"{FIXED_WEIGHT} 分")

            st.divider()
            
            # 雷达图表现
            categories = list(DEFAULT_MODULES.keys())
            values = [latest[f"{m}_正确率"] for m in categories]
            fig = go.Figure(go.Scatterpolar(r=values, theta=categories, fill='toself', name='当前表现', line_color='#1e3a8a'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=450)
            st.subheader("🕸️ 模块能力模型")
            st.plotly_chart(fig, use_container_width=True)

    # --- B. 趋势分析 (含历史汇总表) ---
    elif menu == "📊 趋势分析":
        st.title("📈 备考状态演变")
        if df.empty:
            st.warning("数据不足，无法生成趋势图。")
        else:
            tab1, tab2 = st.tabs(["走势图表", "历史全景透视表"])
            with tab1:
                fig_line = px.line(df, x='日期', y='总分', text='总分', markers=True, title="总分变化趋势 (0.8分/题)")
                st.plotly_chart(fig_line, use_container_width=True)
                
                m_sel = st.multiselect("查看特定模块正确率趋势", list(DEFAULT_MODULES.keys()), default=list(DEFAULT_MODULES.keys())[:3])
                if m_sel:
                    m_data = df.melt(id_vars=['日期', '试卷'], value_vars=[f"{m}_正确率" for m in m_sel], var_name='模块', value_name='正确率')
                    st.plotly_chart(px.line(m_data, x='日期', y='正确率', color='模块', markers=True), use_container_width=True)

            with tab2:
                st.subheader("📋 历史练习汇总")
                summary_df = df[['日期', '试卷', '总分', '总用时']].copy()
                for m in DEFAULT_MODULES.keys():
                    summary_df[m] = df[f"{m}_正确率"].apply(lambda x: f"{x:.1%}")
                st.dataframe(summary_df.sort_values(by='日期', ascending=False), use_container_width=True)

    # --- C. 单卷复盘 ---
    elif menu == "📑 单卷详情":
        if df.empty:
            st.info("暂无记录")
        else:
            paper_sel = st.selectbox("选择试卷", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
            row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(paper_sel)]
            
            st.header(f"📋 {row['试卷']} 深度分析")
            
            st.write("### 模块得分明细 (对题数/总题数)")
            cols = st.columns(2)
            for i, m in enumerate(DEFAULT_MODULES.keys()):
                with cols[i % 2]:
                    acc = row[f"{m}_正确率"]
                    correct = int(row[f"{m}_正确数"])
                    total = int(row[f"{m}_总题数"])
                    color = "#52c41a" if acc >= 0.8 else ("#f5222d" if acc < 0.6 else "#1e3a8a")
                    st.markdown(f"""
                        <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid {color}; margin-bottom:10px; box-shadow:0 2px 4px rgba(0,0,0,0.05)">
                            <div style="display:flex; justify-content:space-between">
                                <b>{m}</b> <span style="font-weight:bold; font-size:1.2em; color:{color}">{correct} / {total}</span>
                            </div>
                            <div style="font-size:0.8em; color:gray">正确率: {acc:.1%} | 耗时: {int(row[f'{m}_用时'])} min</div>
                        </div>
                    """, unsafe_allow_html=True)

    # --- D. 录入成绩 ---
    elif menu == "✏️ 录入成绩":
        st.title("🖋️ 录入最新数据")
        with st.form("exam_input"):
            c1, c2 = st.columns(2)
            date = c1.date_input("考试日期", datetime.now())
            paper = c2.text_input("试卷名称", placeholder="例如：2026国考地市级")
            
            grid = st.columns(2)
            entry = {"日期": date, "试卷": paper}
            total_correct, total_q, total_t, total_score = 0, 0, 0, 0
            
            for i, (m, specs) in enumerate(DEFAULT_MODULES.items()):
                with grid[i % 2]:
                    st.markdown(f"**{m}**")
                    r1, r2, r3 = st.columns(3)
                    m_tot = r1.number_input("总题", 1, 50, specs['total'], key=f"tot_{m}")
                    m_q = r2.number_input("对题", 0, m_tot, 0, key=f"q_{m}")
                    m_t = r3.number_input("用时", 0, 150, specs['plan'], key=f"t_{m}")
                    
                    entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = m_tot, m_q, m_t
                    entry[f"{m}_正确率"] = m_q / m_tot
                    total_correct += m_q; total_q += m_tot; total_t += m_t
                    total_score += m_q * FIXED_WEIGHT
            
            entry.update({"总分": round(total_score, 2), "总正确数": total_correct, "总题数": total_q, "总用时": total_t})
            
            if st.form_submit_button("🚀 提交并存储"):
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df)
                st.success("数据已存档！正在刷新看板...")
                st.rerun()

    # --- E. 数据管理 ---
    elif menu == "⚙️ 数据管理":
        st.title("⚙️ 个人数据中心")
        if not df.empty:
            st.subheader("🗑️ 删除单条数据")
            delete_options = df.apply(lambda x: f"{x.name}: {x['日期']} | {x['试卷']}", axis=1).tolist()
            to_delete = st.selectbox("选择要撤销的一条记录", delete_options)
            if st.button("❌ 确认删除选中记录"):
                idx = int(to_delete.split(":")[0])
                df = df.drop(idx).reset_index(drop=True)
                save_data(df)
                st.rerun()
            
            st.divider()
            st.subheader("📄 我的原始数据")
            st.dataframe(df)
        else:
            st.info("当前暂无数据。")

# --- 4. 登录状态处理 ---
elif authentication_status is False:
    st.error('❌ 用户名或密码错误，请重新输入')
elif authentication_status is None:
    st.warning('⚠️ 请先输入用户名和密码登录以访问您的私人备考数据')
