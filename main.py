import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# --- 1. 核心配置 ---
DB_FILE = 'civil_service_pro_max_v4.csv'
GOAL_SCORE = 75.0

# 模块配置
DEFAULT_MODULES = {
    "政治理论": {"total": 15, "plan": 5, "weight": 0.8, "target_sec": 30},
    "常识判断": {"total": 15, "plan": 5, "weight": 0.8, "target_sec": 30},
    "言语-逻辑填空": {"total": 10, "plan": 9, "weight": 0.8, "target_sec": 45},
    "言语-片段阅读": {"total": 15, "plan": 9, "weight": 0.8, "target_sec": 50},
    "数量关系": {"total": 15, "plan": 25, "weight": 0.8, "target_sec": 90},
    "判断-图形推理": {"total": 5, "plan": 5, "weight": 0.8, "target_sec": 45},
    "判断-定义判断": {"total": 10, "plan": 10, "weight": 0.8, "target_sec": 55},
    "判断-类比推理": {"total": 10, "plan": 5, "weight": 0.8, "target_sec": 35},
    "判断-逻辑判断": {"total": 10, "plan": 15, "weight": 0.8, "target_sec": 60},
    "资料分析": {"total": 20, "plan": 25, "weight": 0.8, "target_sec": 65}
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


# --- 2. 深度分析引擎 ---
def get_advanced_analysis(df):
    if df.empty: return None
    latest = df.iloc[-1]

    potentials = []
    for m in DEFAULT_MODULES:
        acc = latest[f"{m}_正确率"]
        potentials.append({"模块": m, "当前率": acc, "空间": 1 - acc})
    potentials = sorted(potentials, key=lambda x: x['空间'], reverse=True)[:3]

    roi = []
    for m in DEFAULT_MODULES:
        time_spent = max(latest[f"{m}_用时"], 1)
        score = latest[f"{m}_正确数"] * DEFAULT_MODULES[m]['weight']
        roi.append({"模块": m, "性价比": score / time_spent})
    roi = sorted(roi, key=lambda x: x['性价比'], reverse=True)

    return {"potentials": potentials, "roi": roi}


def plot_radar(row):
    categories = list(DEFAULT_MODULES.keys())
    values = [row[f"{m}_正确率"] for m in categories]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='当前表现', line_color='#1e3a8a'))
    fig.add_trace(go.Scatterpolar(r=[0.8] * len(categories), theta=categories, mode='lines', name='优秀线(80%)',
                                  line=dict(color='rgba(255, 75, 75, 0.4)', dash='dash')))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, height=350,
                      margin=dict(l=40, r=40, t=20, b=20))
    return fig


# --- 3. UI 与看板 ---
st.set_page_config(page_title="行测数字化看板 Pro Max", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .main { background: #f8f9fa; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .module-card { background: white; padding: 12px; border-radius: 8px; border-left: 5px solid #eee; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
    </style>
""", unsafe_allow_html=True)

df = load_data()

with st.sidebar:
    st.title("🛡️ 行测复盘")
    menu = st.radio("导航", ["🏠 数字化看板", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"])
    if not df.empty:
        st.divider()
        progress = min(df['总分'].max() / GOAL_SCORE, 1.0)
        st.write(f"🏆 最高分进度: {df['总分'].max():.1f} / {GOAL_SCORE}")
        st.progress(progress)

# A. 看板
if menu == "🏠 数字化看板":
    st.title("📊 数字化深度诊断")
    if df.empty:
        st.info("💡 尚未录入数据，请前往'录入成绩'开始第一篇模考吧！")
    else:
        latest = df.iloc[-1]
        analysis = get_advanced_analysis(df)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("本次总分", f"{latest['总分']:.1f}",
                      delta=f"{latest['总分'] - df.iloc[-2]['总分']:.1f}" if len(df) > 1 else None)
        with c2:
            st.metric("全卷正确率", f"{(latest['总正确数'] / latest['总题数']):.1%}")
        with c3:
            st.metric("进面距离", f"{max(GOAL_SCORE - latest['总分'], 0):.1f}")
        with c4:
            st.metric("总用时", f"{int(latest['总用时'])} min")
        st.divider()
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.subheader("🕸️ 能力模型诊断")
            st.plotly_chart(plot_radar(latest), use_container_width=True)
        with col_right:
            st.subheader("🎯 提分优先级 (TOP 3)")
            for p in analysis['potentials']:
                st.write(f"**{p['模块']}** (正确率: {p['当前率']:.1%})")
                st.progress(p['当前率'])
            st.subheader("⏳ 时间性价比 (每分钟得分)")
            roi_df = pd.DataFrame(analysis['roi']).head(5)
            fig_roi = px.bar(roi_df, x='性价比', y='模块', orientation='h', color_continuous_scale='GnBu',
                             color='性价比')
            fig_roi.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
            st.plotly_chart(fig_roi, use_container_width=True)

# B. 录入 
elif menu == "✏️ 录入成绩":
    st.title("🖋️ 录入原始数据")
    with st.form("exam_input"):
        c1, c2 = st.columns(2)
        date = c1.date_input("考试日期", datetime.now())
        paper = c2.text_input("试卷名称", placeholder="例如：2026国考地市卷")
        grid = st.columns(2)
        entry = {"日期": date, "试卷": paper}
        total_correct, total_q, total_t, total_score = 0, 0, 0, 0

        # 统一分值
        FIXED_WEIGHT = 0.8

        for i, (m, specs) in enumerate(DEFAULT_MODULES.items()):
            with grid[i % 2]:
                st.markdown(f"**{m}** (单题{FIXED_WEIGHT}分)")
                r1, r2, r3 = st.columns(3)
                m_tot = r1.number_input("总题数", 1, 50, specs['total'], key=f"tot_{m}")
                m_q = r2.number_input("对题", 0, m_tot, 0, key=f"q_{m}")
                m_t = r3.number_input("时间(m)", 0, 150, specs['plan'], key=f"t_{m}")

                entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = m_tot, m_q, m_t
                entry[f"{m}_正确率"] = m_q / m_tot
                total_correct += m_q
                total_q += m_tot
                total_t += m_t
                # 此处计算单模块分值：对题数 * 0.8
                total_score += m_q * FIXED_WEIGHT

        entry.update({"总分": round(total_score, 2), "总正确数": total_correct, "总题数": total_q, "总用时": total_t})

        if st.form_submit_button("🚀 存档并生成诊断报告"):
            df = pd.concat([load_data(), pd.DataFrame([entry])], ignore_index=True)
            save_data(df)
            st.success(f"录入成功！本次总分：{total_score:.1f} (单题0.8分)")
            st.rerun()
# C. 趋势分析 
elif menu == "📊 趋势分析":
    st.title("📈 历史动态演变")
    if df.empty:
        st.warning("暂无数据。")
    else:
        tab1, tab2 = st.tabs(["核心指标趋势", "历史全景透视表"])
        with tab1:
            fig = px.line(df, x='日期', y='总分', text='总分', markers=True, title="总分走势")
            st.plotly_chart(fig, use_container_width=True)
            # 模块正确率趋势
            m_sel = st.multiselect("查看模块正确率波动", list(DEFAULT_MODULES.keys()),
                                   default=list(DEFAULT_MODULES.keys())[:3])
            if m_sel:
                m_data = df.melt(id_vars=['日期', '试卷'], value_vars=[f"{m}_正确率" for m in m_sel], var_name='模块',
                                 value_name='正确率')
                st.plotly_chart(px.line(m_data, x='日期', y='正确率', color='模块', markers=True),
                                use_container_width=True)

        with tab2:
            st.subheader("📚 历史套卷详细数据对比")
            # 构建一个汇总表
            summary_df = df[['日期', '试卷', '总分', '总用时']].copy()
            for m in DEFAULT_MODULES.keys():
                # 汇总表显示每个模块的正确率
                summary_df[m] = df[f"{m}_正确率"].apply(lambda x: f"{x:.1%}")

            st.dataframe(summary_df.sort_values(by='日期', ascending=False), use_container_width=True)
            st.caption("注：表格列出了每份试卷的总分、总用时及各细分模块的正确率百分比。")

# D. 单卷复盘 
elif menu == "📑 单卷详情":
    if df.empty:
        st.info("暂无数据")
    else:
        paper_sel = st.selectbox("选择要查看的试卷",
                                 df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
        row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(paper_sel)]

        st.header(f"📋 {row['试卷']} 复盘报告")

        # 指标快报
        c1, c2, c3 = st.columns(3)
        c1.metric("得分", f"{row['总分']:.1f}")
        c2.metric("总正确率", f"{(row['总正确数'] / row['总题数']):.1%}")
        c3.metric("总用时", f"{int(row['总用时'])}min")

        st.write("### 模块明细 (正确数/总题数)")
        cols = st.columns(2)
        for i, m in enumerate(DEFAULT_MODULES.keys()):
            with cols[i % 2]:
                acc = row[f"{m}_正确率"]
                correct_num = int(row[f"{m}_正确数"])
                total_num = int(row[f"{m}_总题数"])
                color = "#52c41a" if acc >= 0.8 else ("#f5222d" if acc < 0.6 else "#1e3a8a")

                st.markdown(f"""
                <div class="module-card" style="border-left-color: {color}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="font-size:1.1em;">{m}</b>
                        <span style="color:{color}; font-weight:bold; font-size:1.2em;">{correct_num} / {total_num}</span>
                    </div>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                        正确率: {acc:.1%} | 耗时: {int(row[f'{m}_用时'])} min
                    </div>
                </div>
                """, unsafe_allow_html=True)

# E. 数据管理 
elif menu == "⚙️ 数据管理":
    st.title("⚙️ 数据后台")
    if df.empty:
        st.info("暂无数据可管理。")
    else:
        st.subheader("🗑️ 删除单条记录")
        # 让用户选择哪一条数据
        delete_list = df.apply(lambda x: f"索引 {x.name} | {x['日期']} | {x['试卷']}", axis=1).tolist()
        to_delete = st.selectbox("请选择要永久删除的记录：", delete_list)

        if st.button("❌ 确认删除选中记录", help="删除后无法恢复"):
            idx = int(to_delete.split(" | ")[0].split(" ")[1])
            new_df = df.drop(idx).reset_index(drop=True)
            save_data(new_df)
            st.error(f"已删除记录：{to_delete}")
            st.rerun()

        st.divider()
        st.subheader("📂 原始数据预览")
        st.dataframe(df)

        if st.button("🚨 清空所有数据库", type="secondary"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)

                st.rerun()
