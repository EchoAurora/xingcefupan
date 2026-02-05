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
    .stApp { background: #f8f9fa; }
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* 仿图样式的模块卡片 */
    .module-detail-card {
        background: #ffffff;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 5px solid #e5e7eb;
    }
    .module-info-left { display: flex; flex-direction: column; flex-grow: 1; }
    .module-name { font-size: 1.1rem; font-weight: bold; margin-bottom: 5px; color: #333; }
    .module-meta { font-size: 0.85rem; color: #888; }
    .module-score-right { font-size: 1.25rem; font-weight: 800; white-space: nowrap; margin-left: 15px; }
    
    /* 动态状态颜色 */
    .status-red { border-left-color: #dc3545 !important; color: #dc3545 !important; }
    .status-green { border-left-color: #28a745 !important; color: #28a745 !important; }
    .status-blue { border-left-color: #1a4da3 !important; color: #1a4da3 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心数据结构定义
# ==========================================
USERS_FILE = 'users_db.json'
FIXED_WEIGHT = 0.8
GOAL_SCORE = 75.0

# 严格定义展示与录入顺序
MODULE_STRUCTURE = {
    "政治理论": {"type": "direct", "total": 15},
    "常识判断": {"type": "direct", "total": 15},
    "言语理解": {
        "type": "parent",
        "subs": {"言语-逻辑填空": 10, "言语-片段阅读": 15}
    },
    "数量关系": {"type": "direct", "total": 15},
    "判断推理": {
        "type": "parent",
        "subs": {"判断-图形推理": 5, "判断-定义判断": 10, "判断-类比推理": 10, "判断-逻辑判断": 10}
    },
    "资料分析": {"type": "direct", "total": 20}
}

def get_leaf_modules():
    leaves = []
    for k, v in MODULE_STRUCTURE.items():
        if v["type"] == "direct": leaves.append(k)
        else: leaves.extend(v["subs"].keys())
    return leaves

LEAF_MODULES = get_leaf_modules()

# 基础函数
def hash_pw(pw): return hashlib.sha256(str(pw).encode()).hexdigest()
def load_users():
    if not os.path.exists(USERS_FILE):
        d = {"admin": {"name": "管理员", "password": hash_pw("qazwsx"), "role": "admin"}}
        save_users(d)
        return d
    with open(USERS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
def save_users(d): 
    with open(USERS_FILE, 'w', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False, indent=4)
def load_data(un):
    path = f'data_storage_{un}.csv'
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            df['日期'] = pd.to_datetime(df['日期']).dt.date
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()
def save_data(df, un): df.to_csv(f'data_storage_{un}.csv', index=False, encoding='utf-8-sig')

# ==========================================
# 3. 身份验证
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("<br><br><h1>🚀 行测 Pro Max</h1><h3>数字化复盘专家</h3>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔑 登录", "📝 快速注册"])
        with t1:
            u = st.text_input("账号", key="l_u")
            p = st.text_input("密码", type="password", key="l_p")
            if st.button("进入系统", type="primary"):
                users = load_users()
                if u in users and users[u]['password'] == hash_pw(p):
                    st.session_state.logged_in = True
                    st.session_state.u_info = {"un": u, **users[u]}
                    st.rerun()
                else: st.error("账号或密码错误")
        with t2:
            nu = st.text_input("设置账号", key="r_u")
            nn = st.text_input("昵称", key="r_n")
            np = st.text_input("密码", type="password", key="r_p")
            if st.button("完成注册"):
                if nu and nn and np:
                    users = load_users()
                    if nu in users: st.error("账号已存在")
                    else:
                        users[nu] = {"name": nn, "password": hash_pw(np), "role": "user"}
                        save_users(users)
                        st.success("注册成功！")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. 页面逻辑
# ==========================================
un = st.session_state.u_info['un']
role = st.session_state.u_info['role']
df = load_data(un)

with st.sidebar:
    st.markdown(f"### 👋 {st.session_state.u_info['name']}")
    menu = st.radio("导航", ["🏠 数字化看板", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"] + (["🛡️ 管理后台"] if role == 'admin' else []))
    if st.button("安全退出"):
        st.session_state.logged_in = False
        st.rerun()

# 辅助渲染函数：生成图片样式的 HTML 卡片
def render_styled_card(name, correct, total, duration, accuracy):
    if accuracy >= 0.8: status = "status-green"
    elif accuracy < 0.6: status = "status-red"
    else: status = "status-blue"
    
    return f"""
    <div class="module-detail-card {status}">
        <div class="module-info-left">
            <div class="module-name">{name}</div>
            <div class="module-meta">正确率: {accuracy:.1%} | 耗时: {int(duration)} min</div>
        </div>
        <div class="module-score-right">
            {int(correct)} / {int(total)}
        </div>
    </div>
    """

# --- 📑 单卷详情 (重写部分) ---
if menu == "📑 单卷详情":
    if df.empty: st.info("暂无数据，请先录入成绩。")
    else:
        st.title("📋 单卷深度复盘")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择历史卷子", sel_list)
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("得分", f"{row['总分']:.1f}")
        c2.metric("正确率", f"{(row['总正确数']/row['总题数']):.1%}")
        c3.metric("总用时", f"{int(row['总用时'])} min")

        st.subheader("模考明细 (正确数/总题数)")
        
        # 严格按照顺序循环
        for main_m, config in MODULE_STRUCTURE.items():
            if config["type"] == "direct":
                # 一级直接模块单栏显示
                st.markdown(render_styled_card(
                    main_m, row[f"{main_m}_正确数"], row[f"{main_m}_总题数"], 
                    row[f"{main_m}_用时"], row[f"{main_m}_正确率"]
                ), unsafe_allow_html=True)
            else:
                # 二级模块并排显示
                st.markdown(f"<div style='margin-top:20px; font-weight:bold; color:#555;'>📍 {main_m}</div>", unsafe_allow_html=True)
                subs = list(config["subs"].keys())
                for i in range(0, len(subs), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(subs):
                            sub_name = subs[i+j]
                            with cols[j]:
                                st.markdown(render_styled_card(
                                    sub_name, row[f"{sub_name}_正确数"], row[f"{sub_name}_总题数"], 
                                    row[f"{sub_name}_用时"], row[f"{sub_name}_正确率"]
                                ), unsafe_allow_html=True)

# --- 🏠 数字化看板 ---
elif menu == "🏠 数字化看板":
    st.title("📊 数字化深度诊断")
    if df.empty: st.info("💡 尚未录入数据")
    else:
        latest = df.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("本次总分", f"{latest['总分']:.1f}")
        with c2: st.metric("全卷正确率", f"{(latest['总正确数'] / latest['总题数']):.1%}")
        with c3: st.metric("进面距离", f"{max(GOAL_SCORE - latest['总分'], 0):.1f}")
        with c4: st.metric("总用时", f"{int(latest['总用时'])} min")
        
        st.divider()
        l_col, r_col = st.columns([1, 1])
        with l_col:
            st.subheader("🕸️ 能力模型诊断")
            fig = go.Figure(go.Scatterpolar(r=[latest[f"{m}_正确率"] for m in LEAF_MODULES], theta=LEAF_MODULES, fill='toself'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), height=380)
            st.plotly_chart(fig, use_container_width=True)
        with r_col:
            st.subheader("⏳ 时间性价比")
            roi_data = [{"模块": m, "性价比": round((latest[f"{m}_正确数"]*FIXED_WEIGHT)/max(latest[f"{m}_用时"],1), 2)} for m in LEAF_MODULES]
            roi_df = pd.DataFrame(roi_data).sort_values("性价比", ascending=False)
            st.plotly_chart(px.bar(roi_df, x='性价比', y='模块', orientation='h', color='性价比'), use_container_width=True)

# --- 📊 趋势分析 ---
elif menu == "📊 趋势分析":
    st.subheader("📈 历史走势")
    if not df.empty:
        st.plotly_chart(px.line(df, x='日期', y='总分', markers=True), use_container_width=True)
        st.dataframe(df.sort_values('日期', ascending=False), use_container_width=True)

# --- ✏️ 录入成绩 ---
elif menu == "✏️ 录入成绩":
    st.subheader("🖋️ 录入模考记录")
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷名称")
        date = c2.date_input("日期", datetime.now())
        entry = {"日期": date, "试卷": paper}
        tc, tq, tt, ts = 0, 0, 0, 0

        for main_m, config in MODULE_STRUCTURE.items():
            st.markdown(f"### 📍 {main_m}")
            if config["type"] == "direct":
                cols = st.columns(2)
                m_q = cols[0].number_input(f"{main_m}-对题", 0, config["total"], 0, key=f"in_q_{main_m}")
                m_t = cols[1].number_input(f"{main_m}-用时", 0, 180, 5, key=f"in_t_{main_m}")
                entry[f"{main_m}_总题数"], entry[f"{main_m}_正确数"], entry[f"{main_m}_用时"] = config["total"], m_q, m_t
                entry[f"{main_m}_正确率"] = m_q / config["total"]
                tc += m_q; tq += config["total"]; tt += m_t; ts += m_q * FIXED_WEIGHT
            else:
                sub_cols = st.columns(2)
                for idx, (sub_m, sub_tot) in enumerate(config["subs"].items()):
                    with sub_cols[idx % 2]:
                        st.markdown(f"**{sub_m}**")
                        sq = st.number_input("对题", 0, sub_tot, 0, key=f"in_q_{sub_m}")
                        st_time = st.number_input("用时", 0, 180, 10, key=f"in_t_{sub_m}")
                        entry[f"{sub_m}_总题数"], entry[f"{sub_m}_正确数"], entry[f"{sub_m}_用时"] = sub_tot, sq, st_time
                        entry[f"{sub_m}_正确率"] = sq / sub_tot
                        tc += sq; tq += sub_tot; tt += st_time; ts += sq * FIXED_WEIGHT

        if st.form_submit_button("🚀 提交存档", type="primary"):
            if not paper: st.error("请填写卷子名称")
            else:
                entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df, un)
                st.success("存档成功！")
                time.sleep(0.5); st.rerun()

# --- ⚙️ 数据管理 ---
elif menu == "⚙️ 数据管理":
    st.subheader("⚙️ 数据中心")
    if not df.empty:
        del_list = df.apply(lambda x: f"ID:{x.name} | {x['日期']} | {x['试卷']}", axis=1).tolist()
        to_del = st.selectbox("选择要删除的记录", del_list)
        if st.button("🗑️ 确认删除单条数据"):
            idx = int(to_del.split(" | ")[0].split(":")[1])
            df = df.drop(idx).reset_index(drop=True)
            save_data(df, un)
            st.success("已删除"); time.sleep(0.5); st.rerun()
        st.dataframe(df, use_container_width=True)

# --- 🛡️ 管理后台 ---
elif menu == "🛡️ 管理后台" and role == 'admin':
    st.title("🛡️ 管理员中心")
    users = load_users()
    st.table(pd.DataFrame([{"账号": k, "昵称": v['name'], "角色": v['role']} for k, v in users.items()]))
