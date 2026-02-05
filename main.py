import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import streamlit_authenticator as stauth

# --- 1. 用户权限配置 ---
# 请在此处修改或添加你的用户名和密码
credentials = {
    'usernames': {
        'admin': {
            'name': '管理员',
            'password': '123'  # 建议部署后在代码中修改
        },
        'user1': {
            'name': '备考学生01',
            'password': '123'
        }
    }
}

# 初始化验证器 (适配最新版本语法)
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
    # 获取用户信息实现数据隔离
    name = st.session_state["name"]
    username = st.session_state["username"]
    
    # 核心配置
    DB_FILE = f'data_storage_{username}.csv'
    GOAL_SCORE = 75.0
    FIXED_WEIGHT = 0.8  # 单题0.8分逻辑

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
                df_loaded = pd.read_csv(DB_FILE)
                df_loaded['日期'] = pd.to_datetime(df_loaded['日期']).dt.date
                return df_loaded
            except:
                return pd.DataFrame()
        return pd.DataFrame()

    def save_data(df_to_save):
        df_to_save.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

    # 深度分析引擎
    def get_advanced_analysis(df_input):
        if df_input.empty: return None
        latest_row = df_input.iloc[-1]
        
        # 提分空间分析
        potentials = []
        for m in DEFAULT_MODULES:
            acc = latest_row[f"{m}_正确率"]
            potentials.append({"模块": m, "当前率": acc, "空间": 1 - acc})
        potentials = sorted(potentials, key=lambda x: x['空间'], reverse=True)[:3]
        
        # 性价比分析 (ROI)
        roi_list = []
        for m in DEFAULT_MODULES:
            time_spent = max(latest_row[f"{m}_用时"], 1)
            score = latest_row[f"{m}_正确数"] * FIXED_WEIGHT
            roi_list.append({"模块": m, "性价比": score / time_spent})
        roi_list = sorted(roi_list, key=lambda x: x['性价比'], reverse=True)
        return {"potentials": potentials, "roi": roi_list}

    def plot_radar(row_data):
        categories = list(DEFAULT_MODULES.keys())
        values = [row_data[f"{m}_正确率"] for m in categories]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='当前表现', line_color='#1e3a8a'))
        fig_r.add_trace(go.Scatterpolar(r=[0.8] * len(categories), theta=categories, mode='lines', name='优秀线(80%)',
                                      line=dict(color='rgba(255, 75, 75, 0.4)', dash='dash')))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, height=350)
        return fig_r

    # UI设置
    st.set_page_config(page_title="行测数字化看板 Pro Max", layout="wide")
    st.markdown("""<style>.stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .module-card { background: white; padding: 12px; border-radius: 8px; border-left: 5px solid #eee; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)

    df = load_data()

    with st.sidebar:
        st.title(f"🛡️ {name}的复盘")
        menu = st.radio("导航", ["🏠 数字化看板", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"])
        if not df.empty:
            st.divider()
            progress = min(df['总分'].max() / GOAL_SCORE, 1.0)
            st.write(f"🏆 最高分进度: {df['总分'].max():.1f} / {GOAL_SCORE}")
            st.progress(progress)
        authenticator.logout('退出登录', 'sidebar')

    # A. 看板
    if menu == "🏠 数字化看板":
        st.title("📊 数字化深度诊断")
        if df.empty:
            st.info("💡 尚未录入数据，请前往'录入成绩'录入第一篇模考。")
        else:
            latest = df.iloc[-1]
            analysis = get_advanced_analysis(df)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("本次总分", f"{latest['总分']:.1f}")
            c2.metric("全卷正确率", f"{(latest['总正确数'] / latest['总题数']):.1%}")
            c3.metric("进面距离", f"{max(GOAL_SCORE - latest['总分'], 0):.1f}")
            c4.metric("总用时", f"{int(latest['总用时'])} min")
            
            st.divider()
            col_l, col_r = st.columns([1, 1])
            with col_l:
                st.subheader("🕸️ 能力模型诊断")
                st.plotly_chart(plot_radar(latest), use_container_width=True)
            with col_r:
                st.subheader("🎯 提分优先级 (TOP 3)")
                for p in analysis['potentials']:
                    st.write(f"**{p['模块']}** (当前:{p['当前率']:.1%})")
                    st.progress(p['当前率'])
                st.subheader("⏳ 性价比 (每分钟得分)")
                roi_df = pd.DataFrame(analysis['roi']).head(5)
                st.plotly_chart(px.bar(roi_df, x='性价比', y='模块', orientation='h', height=200), use_container_width=True)

    # B. 录入
    elif menu == "✏️ 录入成绩":
        st.title("🖋️ 录入原始数据")
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
                    m_t = r3.number_input("时间", 0, 150, specs['plan'], key=f"t_{m}")
                    entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = m_tot, m_q, m_t
                    entry[f"{m}_正确率"] = m_q / m_tot
                    tc += m_q; tq += m_tot; tt += m_t; ts += m_q * FIXED_WEIGHT
            entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
            if st.form_submit_button("🚀 存档数据"):
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df)
                st.success("存档成功！")
                st.rerun()

    # C. 趋势分析
    elif menu == "📊 趋势分析":
        st.title("📈 历史动态演变")
        if df.empty: st.warning("暂无数据")
        else:
            t1, t2 = st.tabs(["走势图", "历史全景表"])
            with t1:
                st.plotly_chart(px.line(df, x='日期', y='总分', markers=True), use_container_width=True)
            with t2:
                summary = df[['日期', '试卷', '总分', '总用时']].copy()
                for m in DEFAULT_MODULES: summary[m] = df[f"{m}_正确率"].apply(lambda x: f"{x:.1%}")
                st.dataframe(summary.sort_values(by='日期', ascending=False), use_container_width=True)

    # D. 单卷详情 (答对数/总数)
    elif menu == "📑 单卷详情":
        if df.empty: st.info("暂无数据")
        else:
            sel = st.selectbox("选择试卷", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
            row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(sel)]
            st.header(f"📋 {row['试卷']} 复盘报告")
            st.write("### 模块明细 (正确数 / 总题数)")
            cols = st.columns(2)
            for i, m in enumerate(DEFAULT_MODULES.keys()):
                with cols[i % 2]:
                    acc = row[f"{m}_正确率"]
                    color = "#52c41a" if acc >= 0.8 else ("#f5222d" if acc < 0.6 else "#1e3a8a")
                    st.markdown(f"""<div class="module-card" style="border-left:5px solid {color}">
                        <b>{m}</b>: <span style="color:{color}; font-weight:bold;">{int(row[f'{m}_正确数'])} / {int(row[f'{m}_总题数'])}</span><br>
                        <small>正确率: {acc:.1%} | 耗时: {int(row[f'{m}_用时'])} min</small></div>""", unsafe_allow_html=True)

    # E. 数据管理
    elif menu == "⚙️ 数据管理":
        st.title("⚙️ 数据中心")
        if not df.empty:
            del_list = df.apply(lambda x: f"索引 {x.name} | {x['日期']} | {x['试卷']}", axis=1).tolist()
            to_del = st.selectbox("删除记录", del_list)
            if st.button("❌ 确认删除"):
                idx = int(to_del.split(" | ")[0].split(" ")[1])
                save_data(df.drop(idx).reset_index(drop=True))
                st.rerun()
            st.dataframe(df)

# 登录反馈
elif st.session_state.get("authentication_status") is False:
    st.error('❌ 用户名或密码错误')
elif st.session_state.get("authentication_status") is None:
    st.warning('⚠️ 请先登录以访问您的数据')
