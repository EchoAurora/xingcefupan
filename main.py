import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import streamlit_authenticator as stauth

# --- 1. 用户权限配置 ---
credentials = {
    'usernames': {
        'admin': {
            'name': 'admin',
            'password': '123456' 
        },
        'user1': {
            'name': '1',
            'password': '123'
        }
    }
}

# 初始化验证器
authenticator = stauth.Authenticate(
    credentials,
    'civil_service_cookie',
    'auth_key',
    cookie_expiry_days=30
)

# 渲染登录界面
try:
    authenticator.login(location='main')
except Exception as e:
    st.error(f"登录组件加载失败: {e}")

# --- 2. 核心业务逻辑 (仅在登录成功后运行) ---
if st.session_state.get("authentication_status"):
    # 获取当前登录用户信息
    name = st.session_state["name"]
    username = st.session_state["username"]
    
    # 核心配置
    DB_FILE = f'data_storage_{username}.csv'
    FIXED_WEIGHT = 0.8  
    GOAL_SCORE = 100.0

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
                data = pd.read_csv(DB_FILE)
                data['日期'] = pd.to_datetime(data['日期']).dt.date
                return data
            except:
                return pd.DataFrame()
        return pd.DataFrame()

    def save_data(data_df):
        data_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

    # 加载数据
    df = load_data()

    # 侧边栏导航
    with st.sidebar:
        st.title(f"👋 你好, {name}")
        menu = st.radio("功能导航", ["🏠 数字化看板", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"])
        st.divider()
        authenticator.logout('退出登录', 'sidebar')

    # --- 逻辑分发 ---
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
            
            categories = list(DEFAULT_MODULES.keys())
            values = [latest[f"{m}_正确率"] for m in categories]
            fig = go.Figure(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#1e3a8a'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=400)
            st.plotly_chart(fig, use_container_width=True)

    elif menu == "📊 趋势分析":
        st.title("📈 备考状态演变")
        if df.empty:
            st.warning("数据不足。")
        else:
            tab1, tab2 = st.tabs(["走势图表", "历史透视表"])
            with tab1:
                st.plotly_chart(px.line(df, x='日期', y='总分', text='总分', markers=True), use_container_width=True)
            with tab2:
                summary_df = df[['日期', '试卷', '总分', '总用时']].copy()
                for m in DEFAULT_MODULES.keys():
                    summary_df[m] = df[f"{m}_正确率"].apply(lambda x: f"{x:.1%}")
                st.dataframe(summary_df.sort_values(by='日期', ascending=False), use_container_width=True)

    elif menu == "📑 单卷详情":
        if df.empty: st.info("暂无记录")
        else:
            paper_sel = st.selectbox("选择试卷", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
            row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(paper_sel)]
            st.header(f"📋 {row['试卷']} 分析")
            cols = st.columns(2)
            for i, m in enumerate(DEFAULT_MODULES.items()):
                with cols[i % 2]:
                    acc = row[f"{m}_正确率"]
                    correct, total = int(row[f"{m}_正确数"]), int(row[f"{m}_总题数"])
                    st.markdown(f"""
                        <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #1e3a8a; margin-bottom:10px; box-shadow:0 2px 4px rgba(0,0,0,0.05)">
                            <div style="display:flex; justify-content:space-between">
                                <b>{m}</b> <span style="font-weight:bold; font-size:1.1em;">{correct} / {total}</span>
                            </div>
                            <div style="font-size:0.8em; color:gray">正确率: {acc:.1%}</div>
                        </div>
                    """, unsafe_allow_html=True)

    elif menu == "✏️ 录入成绩":
        st.title("🖋️ 录入最新数据")
        with st.form("exam_input"):
            c1, c2 = st.columns(2)
            date = c1.date_input("考试日期", datetime.now())
            paper = c2.text_input("试卷名称")
            grid = st.columns(2)
            entry = {"日期": date, "试卷": paper}
            tc, tq, tt, ts = 0, 0, 0, 0
            for i, (m, specs) in enumerate(DEFAULT_MODULES.items()):
                with grid[i % 2]:
                    st.markdown(f"**{m}**")
                    r1, r2, r3 = st.columns(3)
                    m_tot = r1.number_input("总题", 1, 50, specs['total'], key=f"tot_{m}")
                    m_q = r2.number_input("对题", 0, m_tot, 0, key=f"q_{m}")
                    m_t = r3.number_input("用时", 0, 150, specs['plan'], key=f"t_{m}")
                    entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = m_tot, m_q, m_t
                    entry[f"{m}_正确率"] = m_q / m_tot
                    tc += m_q; tq += m_tot; tt += m_t; ts += m_q * FIXED_WEIGHT
            entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
            if st.form_submit_button("🚀 提交存档"):
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df)
                st.success("数据已存档！")
                st.rerun()

    elif menu == "⚙️ 数据管理":
        st.title("⚙️ 数据中心")
        if not df.empty:
            to_del = st.selectbox("删除单条记录", df.apply(lambda x: f"{x.name}: {x['日期']} | {x['试卷']}", axis=1))
            if st.button("❌ 确认删除"):
                idx = int(to_del.split(":")[0])
                df = df.drop(idx).reset_index(drop=True)
                save_data(df)
                st.rerun()
            st.dataframe(df)

# --- 3. 登录状态反馈 ---
elif st.session_state.get("authentication_status") is False:
    st.error('❌ 用户名或密码错误')
elif st.session_state.get("authentication_status") is None:
    st.warning('⚠️ 请先在主页面登录')
