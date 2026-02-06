import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
import hashlib
import time

# ==========================================
# 1. 全局配置与响应式 UI 样式
# ==========================================
st.set_page_config(page_title="行测 Pro Max", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* 全局去留白，让一屏显示更多内容 */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    .stApp { background: #f4f6f9; font-family: 'Inter', sans-serif; }

    /* 通用卡片容器 */
    .custom-card {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
        border: 1px solid #f0f2f6;
        transition: transform 0.2s;
    }
    .custom-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.06); }

    /* 模块详情小卡片（更加紧凑） */
    .module-detail-card {
        background: #ffffff;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #e5e7eb;
        border: 1px solid #f1f5f9;
        border-left-width: 4px;
    }
    .module-info-left { display: flex; flex-direction: column; }
    .module-name { font-size: 0.95rem; font-weight: 700; color: #1f2937; line-height: 1.2; }
    .module-meta { font-size: 0.75rem; color: #9ca3af; margin-top: 2px; }
    .module-score-right { font-size: 1.1rem; font-weight: 800; white-space: nowrap; margin-left: 10px; font-family: 'Roboto Mono', monospace; }

    /* 颜色状态类 */
    .status-red { border-left-color: #ef4444 !important; color: #ef4444 !important; background: #fef2f2 !important; }
    .status-green { border-left-color: #10b981 !important; color: #10b981 !important; background: #ecfdf5 !important; }
    .status-blue { border-left-color: #3b82f6 !important; color: #3b82f6 !important; }

    /* 分区小标题 */
    .mini-header {
        font-size: 0.85rem;
        font-weight: 700;
        color: #64748b;
        margin: 15px 0 8px 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
    }
    .mini-header::before {
        content: '';
        display: inline-block;
        width: 6px;
        height: 6px;
        background: #cbd5e1;
        border-radius: 50%;
        margin-right: 8px;
    }

    /* 首页分析卡片 */
    .analysis-box {
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        color: white;
    }
    .analysis-title { font-size: 0.8rem; opacity: 0.9; margin-bottom: 5px; }
    .analysis-val { font-size: 1.2rem; font-weight: bold; }
    .bg-gradient-green { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
    .bg-gradient-red { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }

    /* 复盘建议样式 */
    .tip-box {
        background: #0f172a;
        color: #e2e8f0;
        padding: 14px 16px;
        border-radius: 12px;
        border: 1px solid rgba(148,163,184,0.2);
        margin: 8px 0;
        line-height: 1.45;
        font-size: 0.92rem;
    }
    .tip-box b { color: #f8fafc; }
    .pill {
        display:inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        margin-right: 6px;
        border: 1px solid rgba(148,163,184,0.35);
        background: rgba(148,163,184,0.12);
        color: #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心逻辑与数据结构
# ==========================================
USERS_FILE = 'users_db.json'
FIXED_WEIGHT = 0.8  # 你原来的计分权重（如需按省考真实分值可改）
GOAL_SCORE = 75.0

MODULE_STRUCTURE = {
    "政治理论": {"type": "direct", "total": 15},
    "常识判断": {"type": "direct", "total": 15},
    "言语理解": {"type": "parent",
             "subs": {"言语-逻辑填空": 10, "言语-片段阅读": 15}},
    "数量关系": {"type": "direct", "total": 15},
    "判断推理": {"type": "parent",
             "subs": {"判断-图形推理": 5, "判断-定义判断": 10, "判断-类比推理": 10, "判断-逻辑判断": 10}},
    "资料分析": {"type": "direct", "total": 20}
}

# ✅ 新增：模块计划用时（用于“计划 vs 实际”以及超时提示）
PLAN_TIME = {
    "政治理论": 5,
    "常识判断": 5,
    "言语-逻辑填空": 18,
    "言语-片段阅读": 22,   # 可按你习惯调整
    "数量关系": 25,
    "判断-图形推理": 5,
    "判断-定义判断": 8,
    "判断-类比推理": 7,
    "判断-逻辑判断": 10,
    "资料分析": 25,
}

# ✅ 新增：复盘记录存储（每套卷：错因分类 + 下次动作）
def review_file(un: str) -> str:
    return f"review_notes_{un}.csv"

REVIEW_SCHEMA = [
    "日期", "试卷",
    "模块", "错题数",
    "错因1_知识点不会", "错因2_方法不熟", "错因3_审题选项坑",
    "一句话原因", "下次动作"
]

def get_leaf_modules():
    leaves = []
    for k, v in MODULE_STRUCTURE.items():
        if v["type"] == "direct":
            leaves.append(k)
        else:
            leaves.extend(v["subs"].keys())
    return leaves

LEAF_MODULES = get_leaf_modules()

def hash_pw(pw): 
    return hashlib.sha256(str(pw).encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        d = {"admin": {"name": "管理员", "password": hash_pw("admin123"), "role": "admin"}}
        save_users(d)
        return d
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(d):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

def data_file(un: str) -> str:
    return f"data_storage_{un}.csv"

def ensure_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    ✅ 修复点：
    - 你旧数据/导入数据可能缺少某些列，会导致看板/趋势直接 KeyError
    - 这里统一补齐所有需要的列
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=build_all_columns())

    need_cols = build_all_columns()
    for c in need_cols:
        if c not in df.columns:
            df[c] = 0

    # 日期列统一成 date
    if '日期' in df.columns:
        try:
            df['日期'] = pd.to_datetime(df['日期']).dt.date
        except Exception:
            pass

    # 类型纠正：数值列确保为数值
    for c in df.columns:
        if any(c.endswith(s) for s in ["_正确数", "_总题数", "_用时", "_正确率"]) or c in ["总分", "总正确数", "总题数", "总用时"]:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    return df

def build_all_columns():
    cols = ["日期", "试卷", "总分", "总正确数", "总题数", "总用时"]
    for m in LEAF_MODULES:
        cols.extend([f"{m}_总题数", f"{m}_正确数", f"{m}_用时", f"{m}_正确率"])
        cols.append(f"{m}_计划用时")
    return cols

def load_data(un):
    path = data_file(un)
    if os.path.exists(path):
        df = pd.read_csv(path, encoding='utf-8')
        df = ensure_schema(df)
        return df
    return ensure_schema(pd.DataFrame())

def save_data(df, un):
    df = ensure_schema(df)
    df.to_csv(data_file(un), index=False, encoding='utf-8-sig')

def load_reviews(un: str) -> pd.DataFrame:
    path = review_file(un)
    if os.path.exists(path):
        rdf = pd.read_csv(path, encoding='utf-8')
        # 日期可能是字符串
        if "日期" in rdf.columns:
            try:
                rdf["日期"] = pd.to_datetime(rdf["日期"]).dt.date
            except Exception:
                pass
        # 补列
        for c in REVIEW_SCHEMA:
            if c not in rdf.columns:
                rdf[c] = ""
        return rdf[REVIEW_SCHEMA]
    return pd.DataFrame(columns=REVIEW_SCHEMA)

def save_reviews(rdf: pd.DataFrame, un: str):
    for c in REVIEW_SCHEMA:
        if c not in rdf.columns:
            rdf[c] = ""
    rdf = rdf[REVIEW_SCHEMA]
    rdf.to_csv(review_file(un), index=False, encoding='utf-8-sig')

# ==========================================
# 3. 登录与鉴权
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("<br><br><h1 style='color:#2563eb;'>🚀 行测 Pro Max</h1><h3 style='color:#64748b;'>你的数字化上岸助手</h3>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔑 登录", "📝 快速注册"])
        with t1:
            u = st.text_input("账号", key="l_u")
            p = st.text_input("密码", type="password", key="l_p")
            if st.button("进入系统", type="primary", use_container_width=True):
                users = load_users()
                if u in users and users[u]['password'] == hash_pw(p):
                    st.session_state.logged_in = True
                    st.session_state.u_info = {"un": u, **users[u]}
                    st.rerun()
                else:
                    st.error("账号或密码错误")
        with t2:
            nu = st.text_input("设置账号", key="r_u")
            nn = st.text_input("昵称", key="r_n")
            npw = st.text_input("密码", type="password", key="r_p")
            if st.button("完成注册", use_container_width=True):
                users = load_users()
                if nu in users:
                    st.error("账号已存在")
                elif nu and nn and npw:
                    users[nu] = {"name": nn, "password": hash_pw(npw), "role": "user"}
                    save_users(users)
                    st.success("注册成功！")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. 主程序逻辑
# ==========================================
un = st.session_state.u_info['un']
role = st.session_state.u_info['role']
df = load_data(un)
rdf = load_reviews(un)

with st.sidebar:
    st.markdown(f"### 👋 Hi, {st.session_state.u_info['name']}")
    menu = st.radio(
        "功能导航",
        ["🏠 数字化看板", "📊 趋势分析", "📑 单卷详情", "🧠 复盘记录", "✏️ 录入成绩", "⚙️ 数据管理"] + (["🛡️ 管理后台"] if role == 'admin' else [])
    )
    st.markdown("---")
    if st.button("安全退出", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# 5. 复用函数
# ==========================================
def render_styled_card(name, correct, total, duration, accuracy, plan_time=None):
    if accuracy >= 0.8:
        status = "status-green"
    elif accuracy < 0.6:
        status = "status-red"
    else:
        status = "status-blue"

    extra = ""
    if plan_time is not None and plan_time > 0:
        diff = float(duration) - float(plan_time)
        sign = "+" if diff > 0 else ""
        extra = f" | 计划{int(plan_time)}m ({sign}{diff:.0f}m)"

    return f"""
    <div class="module-detail-card {status}">
        <div class="module-info-left">
            <div class="module-name">{name}</div>
            <div class="module-meta">{accuracy:.1%} | {int(duration)}min{extra}</div>
        </div>
        <div class="module-score-right">{int(correct)}/{int(total)}</div>
    </div>
    """

def module_label_to_focus_action(m: str, acc: float, t: float, plan: float, total_q: float):
    """
    ✅ 把“复盘四步法”落成可执行建议：
    - 每个模块输出：现状 + 1个动作（不要一堆鸡汤）
    """
    tips = []
    # 速度
    if plan and t > plan + 2:
        tips.append(f"<span class='pill'>超时</span>本模块用时 <b>{int(t)}m</b>，比计划 <b>+{int(t-plan)}m</b>。下次给自己设置“<b>单题/单篇上限</b>”，超过就跳。")

    # 正确率
    if acc >= 0.8:
        tips.append(f"<span class='pill'>强项</span>正确率 <b>{acc:.0%}</b>，保持即可，重点放在<b>提速</b>与<b>降低粗心</b>。")
    elif acc < 0.6:
        tips.append(f"<span class='pill'>短板</span>正确率 <b>{acc:.0%}</b>，建议把错题按<b>三类错因</b>拆开：不会/不熟/审题坑，并只挑一个点改。")
    else:
        tips.append(f"<span class='pill'>可提升</span>正确率 <b>{acc:.0%}</b>，属于“能靠训练稳定涨”的区间。")

    # 模块专属动作（按你之前那套建议）
    if m == "资料分析":
        tips.append("动作：<b>每篇资料限时6分钟</b>，超过先跳；每天15分钟只练<b>速算（增长率/基期/比重/平均）</b>。")
    elif m == "数量关系":
        tips.append("动作：<b>每题60秒上限</b>；只保留你最稳的<b>3类题型</b>训练，其余题型直接“秒放”，把时间还给言语/资料。")
    elif m in ["言语-逻辑填空", "言语-片段阅读"]:
        tips.append("动作：每天20题专项；错题只写一句：<b>错在语境/搭配/关键词（转折因果）</b>，下次遇到同坑能秒避。")
    elif m in ["政治理论", "常识判断"]:
        tips.append("动作：不背大书；每天10分钟刷题，把错题压成<b>1行卡片关键词</b>（法条/时政点）。")
    elif m.startswith("判断-"):
        tips.append("动作：图推/类比/定义优先稳分；逻辑判断遇到耗时题设置<b>90秒上限</b>，超过先跳。")

    return "<div class='tip-box'>" + "<br>".join(tips) + "</div>"

def compute_next_day_plan(row: pd.Series):
    """
    ✅ 自动生成“明天练什么”（三条即可）
    逻辑：
    - 找出正确率最低的模块（或超时最多的模块）
    - 永远给：资料提速 + 言语专项 + 数量策略 或 短板专项
    """
    # 计算 acc / time diff
    items = []
    for m in LEAF_MODULES:
        acc = float(row.get(f"{m}_正确率", 0))
        t = float(row.get(f"{m}_用时", 0))
        plan = float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
        diff = t - plan if plan else 0
        items.append((m, acc, diff))

    # 最低正确率模块
    worst_acc = sorted(items, key=lambda x: x[1])[0]
    # 最大超时模块
    worst_time = sorted(items, key=lambda x: x[2], reverse=True)[0]

    tasks = []
    tasks.append("资料分析：15分钟限时速算（增长率/基期/比重/平均数），目标“更快不更错”。")
    tasks.append("言语理解：逻辑填空20题（每题标注：语境/搭配/转折因果关键词）。")
    if worst_acc[0] == "数量关系" or worst_time[0] == "数量关系":
        tasks.append("数量关系：只练你最稳的1个题型10题 + 每题60秒上限；其余题型直接放弃训练。")
    else:
        tasks.append(f"短板专项：{worst_acc[0]} 10-20题（只做同一类型，做到“看见就会”）。")
    return tasks, worst_acc, worst_time

# ==========================================
# 6. 页面：🏠 数字化看板
# ==========================================
if menu == "🏠 数字化看板":
    st.title("📊 数字化深度诊断")
    if df.empty:
        st.info("👋 欢迎！请先前往【录入成绩】开始你的第一套模考。")
    else:
        latest = df.iloc[-1]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("最新得分", f"{latest['总分']:.1f}",
                  delta=f"{latest['总分'] - df.iloc[-2]['总分']:.1f}" if len(df) > 1 else None)
        c2.metric("正确率", f"{(latest['总正确数'] / max(latest['总题数'], 1)):.1%}")
        c3.metric("平均分 (近5次)", f"{df.tail(5)['总分'].mean():.1f}")
        c4.metric("刷题套数", f"{len(df)}")

        st.markdown("##### 🚀 模块动态分析 (对比上一场)")
        if len(df) > 1:
            prev = df.iloc[-2]
            diffs = {}
            for m in LEAF_MODULES:
                diffs[m] = float(latest.get(f"{m}_正确率", 0)) - float(prev.get(f"{m}_正确率", 0))

            best_m = max(diffs, key=diffs.get)
            worst_m = min(diffs, key=diffs.get)

            a1, a2 = st.columns(2)
            with a1:
                st.markdown(f"""
                <div class="analysis-box bg-gradient-green">
                    <div class="analysis-title">🌟 进步之星 (正确率 +{diffs[best_m]:.1%})</div>
                    <div class="analysis-val">{best_m}</div>
                </div>
                """, unsafe_allow_html=True)
            with a2:
                st.markdown(f"""
                <div class="analysis-box bg-gradient-red">
                    <div class="analysis-title">⚠️ 需关注 (正确率 {diffs[worst_m]:.1%})</div>
                    <div class="analysis-val">{worst_m}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("完成至少两套模考后解锁动态分析。")

        st.markdown("---")
        col_l, col_r = st.columns([1, 1.3])

        with col_l:
            st.subheader("🕸️ 能力雷达")
            fig = go.Figure(go.Scatterpolar(
                r=[float(latest.get(f"{m}_正确率", 0)) for m in LEAF_MODULES],
                theta=LEAF_MODULES, fill='toself',
                line_color='#2563eb'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=8))),
                height=350, margin=dict(t=20, b=20, l=40, r=40)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.subheader("📈 分数分布")
            fig_hist = px.histogram(df, x="总分", nbins=10, color_discrete_sequence=['#3b82f6'])
            fig_hist.update_layout(height=350, margin=dict(t=20, b=20), xaxis_title="分数区间", yaxis_title="次数")
            st.plotly_chart(fig_hist, use_container_width=True)

# ==========================================
# 7. 页面：📑 单卷详情（加入“复盘建议 + 计划vs实际 + 明日训练”）
# ==========================================
elif menu == "📑 单卷详情":
    if df.empty:
        st.info("暂无数据")
    else:
        st.title("📋 单卷深度复盘")

        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择历史模考", sel_list, label_visibility="collapsed")
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("得分", f"{row['总分']:.1f}")
        m2.metric("正确率", f"{(row['总正确数'] / max(row['总题数'], 1)):.1%}")
        m3.metric("总用时", f"{int(row['总用时'])} min")
        score_per_min = float(row['总分']) / max(float(row['总用时']), 1)
        m4.metric("得分效率", f"{score_per_min:.2f} 分/min")
        st.markdown('</div>', unsafe_allow_html=True)

        # ✅ 新增：复盘建议（按模块自动生成）
        st.subheader("🧠 本卷自动复盘建议（按数据生成）")
        # 选出：最低正确率Top3 + 超时Top3
        stats = []
        for m in LEAF_MODULES:
            acc = float(row.get(f"{m}_正确率", 0))
            t = float(row.get(f"{m}_用时", 0))
            plan = float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
            total = float(row.get(f"{m}_总题数", 0))
            stats.append((m, acc, t, plan, total, (t-plan) if plan else 0))

        worst_by_acc = sorted(stats, key=lambda x: x[1])[:3]
        worst_by_time = sorted(stats, key=lambda x: x[5], reverse=True)[:3]

        cA, cB = st.columns(2)
        with cA:
            st.markdown("<div class='mini-header'>正确率最低 Top3</div>", unsafe_allow_html=True)
            for (m, acc, t, plan, total, diff) in worst_by_acc:
                st.markdown(module_label_to_focus_action(m, acc, t, plan, total), unsafe_allow_html=True)
        with cB:
            st.markdown("<div class='mini-header'>超时最多 Top3</div>", unsafe_allow_html=True)
            for (m, acc, t, plan, total, diff) in worst_by_time:
                st.markdown(module_label_to_focus_action(m, acc, t, plan, total), unsafe_allow_html=True)

        # ✅ 新增：明天训练计划（3条即可）
        st.subheader("✅ 明天怎么练（只给3条，能执行）")
        tasks, worst_acc, worst_time = compute_next_day_plan(row)
        st.markdown(f"""
        <div class="custom-card">
            <div class="mini-header">训练清单</div>
            <ol style="margin:0 0 0 18px;">
                <li>{tasks[0]}</li>
                <li>{tasks[1]}</li>
                <li>{tasks[2]}</li>
            </ol>
            <div style="margin-top:10px;color:#64748b;font-size:0.85rem;">
                重点短板：<b>{worst_acc[0]}</b>（正确率 {worst_acc[1]:.0%}）；
                主要时间黑洞：<b>{worst_time[0]}</b>（超时 {worst_time[2]:.0f} 分钟）
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ✅ 原来的模块卡片布局保留（加上计划用时）
        col_left, col_mid, col_right = st.columns(3)

        with col_left:
            st.markdown('<div class="mini-header">政治常识</div>', unsafe_allow_html=True)
            for m in ["政治理论", "常识判断"]:
                st.markdown(render_styled_card(
                    m,
                    row[f"{m}_正确数"], row[f"{m}_总题数"],
                    row[f"{m}_用时"], row[f"{m}_正确率"],
                    plan_time=row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0))
                ), unsafe_allow_html=True)

            st.markdown('<div class="mini-header">言语理解</div>', unsafe_allow_html=True)
            for sub in ["言语-逻辑填空", "言语-片段阅读"]:
                st.markdown(render_styled_card(
                    sub,
                    row[f"{sub}_正确数"], row[f"{sub}_总题数"],
                    row[f"{sub}_用时"], row[f"{sub}_正确率"],
                    plan_time=row.get(f"{sub}_计划用时", PLAN_TIME.get(sub, 0))
                ), unsafe_allow_html=True)

            st.markdown('<div class="mini-header">数量关系</div>', unsafe_allow_html=True)
            m = "数量关系"
            st.markdown(render_styled_card(
                m,
                row[f"{m}_正确数"], row[f"{m}_总题数"],
                row[f"{m}_用时"], row[f"{m}_正确率"],
                plan_time=row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0))
            ), unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="mini-header">判断推理</div>', unsafe_allow_html=True)
            judgement_subs = ["判断-图形推理", "判断-定义判断", "判断-类比推理", "判断-逻辑判断"]
            for sub in judgement_subs:
                st.markdown(render_styled_card(
                    sub,
                    row[f"{sub}_正确数"], row[f"{sub}_总题数"],
                    row[f"{sub}_用时"], row[f"{sub}_正确率"],
                    plan_time=row.get(f"{sub}_计划用时", PLAN_TIME.get(sub, 0))
                ), unsafe_allow_html=True)

            st.markdown('<div class="mini-header">资料分析</div>', unsafe_allow_html=True)
            m = "资料分析"
            st.markdown(render_styled_card(
                m,
                row[f"{m}_正确数"], row[f"{m}_总题数"],
                row[f"{m}_用时"], row[f"{m}_正确率"],
                plan_time=row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0))
            ), unsafe_allow_html=True)

        # ✅ 新增：导出“本卷复盘摘要”方便你复制到朋友圈/备考群/笔记
        with st.expander("📤 导出本卷复盘摘要（复制到笔记）", expanded=False):
            md = []
            md.append(f"### {row['日期']} | {row['试卷']}")
            md.append(f"- 得分：{row['总分']:.1f} | 正确率：{(row['总正确数']/max(row['总题数'],1)):.1%} | 用时：{int(row['总用时'])}min")
            md.append(f"- 明天训练：1）{tasks[0]} 2）{tasks[1]} 3）{tasks[2]}")
            md.append("")
            md.append("**模块Top问题（自动）**")
            md.append(f"- 正确率最低：{', '.join([x[0] for x in worst_by_acc])}")
            md.append(f"- 超时最多：{', '.join([x[0] for x in worst_by_time])}")
            st.code("\n".join(md), language="markdown")

# ==========================================
# 8. 页面：🧠 复盘记录（把“三类错因 + 下次动作”真正存下来）
# ==========================================
elif menu == "🧠 复盘记录":
    st.title("🧠 复盘记录（四步法落地）")
    if df.empty:
        st.info("你还没录入任何套卷，先去【录入成绩】。")
    else:
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择要复盘的套卷", sel_list)
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]

        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.markdown("#### ✅ 复盘规则：每个模块只填“错因三类 + 一句话原因 + 下次动作”")
        st.caption("错因三类：①不会（知识点缺失）②不熟（方法/速算/步骤）③审题/选项坑（粗心/关键词/单位）")

        # 默认给你一个“建议优先复盘列表”：正确率最低的4个 + 超时最多的2个（去重）
        stats = []
        for m in LEAF_MODULES:
            acc = float(row.get(f"{m}_正确率", 0))
            t = float(row.get(f"{m}_用时", 0))
            plan = float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
            stats.append((m, acc, t - plan if plan else 0))
        pick = []
        pick += [x[0] for x in sorted(stats, key=lambda x: x[1])[:4]]
        pick += [x[0] for x in sorted(stats, key=lambda x: x[2], reverse=True)[:2]]
        pick = list(dict.fromkeys(pick))  # 去重保序

        st.info(f"系统建议你优先复盘：{ '、'.join(pick) }（先解决最影响提分/时间的部分）")

        with st.form("review_form"):
            date = row["日期"]
            paper = row["试卷"]

            chosen_modules = st.multiselect(
                "选择要记录复盘的模块（建议先选系统推荐）",
                LEAF_MODULES,
                default=pick
            )

            for m in chosen_modules:
                st.markdown(f"---\n### {m}")
                total = int(row.get(f"{m}_总题数", 0))
                correct = int(row.get(f"{m}_正确数", 0))
                wrong = max(total - correct, 0)

                c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                with c1:
                    wrong_count = st.number_input("错题数（可改）", 0, 999, wrong, key=f"w_{m}")
                with c2:
                    e1 = st.number_input("错因①不会", 0, 999, 0, key=f"e1_{m}")
                with c3:
                    e2 = st.number_input("错因②不熟", 0, 999, 0, key=f"e2_{m}")
                with c4:
                    e3 = st.number_input("错因③审题坑", 0, 999, 0, key=f"e3_{m}")

                reason = st.text_input("一句话原因（越短越好）", key=f"r_{m}",
                                       placeholder="例：基期现期看反 / 转折句没抓 / 速算失误")
                action = st.text_input("下次动作（只写1个动作）", key=f"a_{m}",
                                       placeholder="例：资料每篇6分钟上限；数量每题60秒上限；填空每天20题")

            submitted = st.form_submit_button("💾 保存本卷复盘记录", type="primary", use_container_width=True)
            if submitted:
                new_rows = []
                for m in chosen_modules:
                    new_rows.append({
                        "日期": date,
                        "试卷": paper,
                        "模块": m,
                        "错题数": int(st.session_state.get(f"w_{m}", 0)),
                        "错因1_知识点不会": int(st.session_state.get(f"e1_{m}", 0)),
                        "错因2_方法不熟": int(st.session_state.get(f"e2_{m}", 0)),
                        "错因3_审题选项坑": int(st.session_state.get(f"e3_{m}", 0)),
                        "一句话原因": st.session_state.get(f"r_{m}", ""),
                        "下次动作": st.session_state.get(f"a_{m}", ""),
                    })

                rdf2 = pd.concat([rdf, pd.DataFrame(new_rows)], ignore_index=True)
                save_reviews(rdf2, un)
                rdf = rdf2
                st.success("已保存！你下次复习只要按“下次动作”执行即可。")
                time.sleep(0.6)
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("📚 历史复盘库（可筛选）")
        if rdf.empty:
            st.caption("还没有复盘记录。")
        else:
            f1, f2, f3 = st.columns([1, 1, 2])
            with f1:
                f_paper = st.selectbox("按试卷筛选", ["全部"] + sorted(rdf["试卷"].dropna().astype(str).unique().tolist()))
            with f2:
                f_mod = st.selectbox("按模块筛选", ["全部"] + LEAF_MODULES)
            with f3:
                keyword = st.text_input("关键词搜索（原因/动作）", placeholder="例：基期、速算、转折、60秒…")

            view = rdf.copy()
            if f_paper != "全部":
                view = view[view["试卷"].astype(str) == f_paper]
            if f_mod != "全部":
                view = view[view["模块"].astype(str) == f_mod]
            if keyword.strip():
                k = keyword.strip()
                view = view[
                    view["一句话原因"].astype(str).str.contains(k, na=False) |
                    view["下次动作"].astype(str).str.contains(k, na=False)
                ]

            st.dataframe(view.sort_values(["日期", "试卷", "模块"], ascending=[False, False, True]),
                         use_container_width=True, hide_index=True)

# ==========================================
# 9. 页面：📊 趋势分析（原样保留 + 更稳健）
# ==========================================
elif menu == "📊 趋势分析":
    st.title("📈 模考趋势走势")
    if df.empty:
        st.info("暂无数据")
    else:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        plot_df = df.copy()
        plot_df['场次'] = plot_df.apply(lambda x: f"{x['日期']}\n{x['试卷']}", axis=1)

        fig = px.line(plot_df, x='场次', y='总分', markers=True, text='总分', title="总分走势")
        fig.update_traces(textposition="top center", line_color="#2563eb",
                          marker=dict(size=8, color='white', line=dict(width=2, color='#2563eb')))
        fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f1f5f9'))
        st.plotly_chart(fig, use_container_width=True)

        st.caption("模块正确率波动")
        module_cols = [f"{m}_正确率" for m in LEAF_MODULES if f"{m}_正确率" in plot_df.columns]
        if module_cols:
            module_trends = plot_df[['场次'] + module_cols].melt(id_vars='场次', var_name='模块', value_name='正确率')
            module_trends['模块'] = module_trends['模块'].str.replace('_正确率', '')
            fig2 = px.line(module_trends, x='场次', y='正确率', color='模块', markers=True)
            fig2.update_layout(height=320)
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("🗓️ 历史成绩明细")
        display_df = df[['日期', '试卷', '总分', '总正确数', '总题数', '总用时']].copy()
        display_df['正确率'] = (display_df['总正确数'] / display_df['总题数']).map(lambda x: f"{x:.1%}" if x else "0.0%")
        st.dataframe(display_df.sort_values('日期', ascending=False), use_container_width=True, hide_index=True)

# ==========================================
# 10. 页面：✏️ 录入成绩（加入计划用时保存 + 更稳健）
# ==========================================
elif menu == "✏️ 录入成绩":
    st.subheader("🖋️ 录入试卷成绩")
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    with st.form("input_score"):
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷全称", placeholder="例如：2026国考副省 / 粉笔组卷xxx")
        date = c2.date_input("考试日期")
        st.divider()

        entry = {"日期": date, "试卷": paper}
        tc, tq, tt, ts = 0, 0, 0, 0

        # 录入布局
        for m, config in MODULE_STRUCTURE.items():
            if config["type"] == "direct":
                st.markdown(f"**📌 {m}**")
                sc1, sc2, sc3 = st.columns([1, 1, 1])
                mq = sc1.number_input("对题数", 0, config["total"], 0, key=f"q_{m}")
                mt = sc2.number_input("用时 (min)", 0, 180, int(PLAN_TIME.get(m, 5)), key=f"t_{m}")
                mp = sc3.number_input("计划用时 (min)", 0, 180, int(PLAN_TIME.get(m, 5)), key=f"p_{m}")

                entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = config["total"], mq, mt
                entry[f"{m}_正确率"] = mq / config["total"] if config["total"] > 0 else 0
                entry[f"{m}_计划用时"] = mp

                tc += mq
                tq += config["total"]
                tt += mt
                ts += mq * FIXED_WEIGHT
            else:
                st.markdown(f"**📌 {m}**")
                sub_cols = st.columns(len(config["subs"]))
                for idx, (sm, stot) in enumerate(config["subs"].items()):
                    with sub_cols[idx]:
                        st.caption(f"{sm}")
                        sq = st.number_input("对题", 0, stot, 0, key=f"sq_{sm}")
                        st_time = st.number_input("实际min", 0, 180, int(PLAN_TIME.get(sm, 5)), key=f"st_{sm}")
                        st_plan = st.number_input("计划min", 0, 180, int(PLAN_TIME.get(sm, 5)), key=f"sp_{sm}")

                        entry[f"{sm}_总题数"], entry[f"{sm}_正确数"], entry[f"{sm}_用时"] = stot, sq, st_time
                        entry[f"{sm}_正确率"] = sq / stot if stot > 0 else 0
                        entry[f"{sm}_计划用时"] = st_plan

                        tc += sq
                        tq += stot
                        tt += st_time
                        ts += sq * FIXED_WEIGHT
            st.markdown("---")

        if st.form_submit_button("🚀 提交存档", type="primary", use_container_width=True):
            if not paper:
                st.error("请输入试卷名称")
            else:
                entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
                df2 = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                df2 = ensure_schema(df2)
                save_data(df2, un)
                st.success("数据已存档")
                time.sleep(0.8)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 11. 页面：⚙️ 数据管理（原样保留 + 更稳健）
# ==========================================
elif menu == "⚙️ 数据管理":
    st.title("⚙️ 数据中心")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        del_target = st.selectbox("选择要删除的记录", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1))

        if st.button("🗑️ 确认删除该记录", type="secondary"):
            df2 = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) != del_target]
            save_data(df2, un)
            st.success("删除成功")
            time.sleep(0.5)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 12. 页面：🛡️ 管理后台（原样保留）
# ==========================================
elif menu == "🛡️ 管理后台" and role == 'admin':
    st.title("🛡️ 权限管理中心")
    users = load_users()

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    t_list, t_add, t_edit = st.tabs(["👥 用户列表", "➕ 新增用户", "🔧 账号维护"])

    with t_list:
        u_table = pd.DataFrame([{"账号": k, "昵称": v['name'], "角色": v['role']} for k, v in users.items()])
        st.table(u_table)

    with t_add:
        with st.form("add_user"):
            new_u = st.text_input("新账号ID")
            new_n = st.text_input("新用户昵称")
            new_p = st.text_input("初始密码", type="password")
            new_r = st.selectbox("角色", ["user", "admin"])
            if st.form_submit_button("确认创建"):
                if new_u in users:
                    st.error("该账号已存在")
                elif new_u:
                    users[new_u] = {"name": new_n, "password": hash_pw(new_p), "role": new_r}
                    save_users(users)
                    st.success("创建成功")
                    st.rerun()

    with t_edit:
        target_u = st.selectbox("选择目标用户", list(users.keys()))
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("修改昵称", value=users[target_u]['name'])
            new_pwd = st.text_input("重置密码 (留空不修改)", type="password")
            if st.button("更新资料"):
                users[target_u]['name'] = new_name
                if new_pwd:
                    users[target_u]['password'] = hash_pw(new_pwd)
                save_users(users)
                st.success("更新成功")
        with col2:
            st.warning("危险操作")
            if st.button("🔥 彻底删除此账号"):
                if target_u == 'admin':
                    st.error("无法删除主管理员")
                else:
                    del users[target_u]
                    save_users(users)
                    st.success("已删除")
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
