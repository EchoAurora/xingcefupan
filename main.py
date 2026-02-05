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
        margin-bottom: 1.5rem;
    }
    
    /* 模块卡片样式 */
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
    .module-name { font-size: 1rem; font-weight: bold; margin-bottom: 5px; color: #333; }
    .module-meta { font-size: 0.8rem; color: #888; }
    .module-score-right { font-size: 1.2rem; font-weight: 800; white-space: nowrap; margin-left: 15px; }
    
    /* 模块分割标题 */
    .section-divider {
        background: #f1f5f9;
        padding: 8px 15px;
        border-radius: 8px;
        margin: 25px 0 15px 0;
        font-weight: bold;
        color: #475569;
        border-left: 4px solid #3b82f6;
    }

    /* 动态状态颜色 */
    .status-red { border-left-color: #dc3545 !important; color: #dc3545 !important; }
    .status-green { border-left-color: #28a745 !important; color: #28a745 !important; }
    .status-blue { border-left-color: #1a4da3 !important; color: #1a4da3 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心逻辑与数据处理
# ==========================================
USERS_FILE = 'users_db.json'
FIXED_WEIGHT = 0.8
GOAL_SCORE = 75.0

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

def hash_pw(pw): return hashlib.sha256(str(pw).encode()).hexdigest()
def load_users():
    if not os.path.exists(USERS_FILE):
        d = {"admin": {"name": "管理员", "password": hash_pw("admin123"), "role": "admin"}}
        save_users(d)
        return d
    with open(USERS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
def save_users(d): 
    with open(USERS_FILE, 'w', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False, indent=4)
def load_data(un):
    path = f'data_storage_{un}.csv'
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        return df
    return pd.DataFrame()
def save_data(df, un): df.to_csv(f'data_storage_{un}.csv', index=False, encoding='utf-8-sig')

# ==========================================
# 3. 登录权限验证
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("<br><br><h1>🚀 行测 Pro Max</h1><h3>复盘数字化专家</h3>", unsafe_allow_html=True)
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
                users = load_users()
                if nu in users: st.error("账号已存在")
                elif nu and nn and np:
                    users[nu] = {"name": nn, "password": hash_pw(np), "role": "user"}
                    save_users(users)
                    st.success("注册成功！")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. 主页面导航
# ==========================================
un = st.session_state.u_info['un']
role = st.session_state.u_info['role']
df = load_data(un)

with st.sidebar:
    st.markdown(f"### 👋 {st.session_state.u_info['name']}")
    menu = st.radio("功能导航", ["🏠 数字化看板", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"] + (["🛡️ 管理后台"] if role == 'admin' else []))
    st.divider()
    if st.button("安全退出"):
        st.session_state.logged_in = False
        st.rerun()

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
        <div class="module-score-right">{int(correct)} / {int(total)}</div>
    </div>
    """

# --- 📑 单卷详情 ---
if menu == "📑 单卷详情":
    if df.empty: st.info("暂无数据")
    else:
        st.title("📋 单卷深度复盘")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择历史模考", sel_list)
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("得分", f"{row['总分']:.1f}")
        c2.metric("正确率", f"{(row['总正确数']/row['总题数']):.1%}")
        c3.metric("总用时", f"{int(row['总用时'])} min")

        # 增加分割渲染逻辑
        for main_m, config in MODULE_STRUCTURE.items():
            st.markdown(f'<div class="section-divider">📍 {main_m}</div>', unsafe_allow_html=True)
            if config["type"] == "direct":
                st.markdown(render_styled_card(main_m, row[f"{main_m}_正确数"], row[f"{main_m}_总题数"], row[f"{main_m}_用时"], row[f"{main_m}_正确率"]), unsafe_allow_html=True)
            else:
                subs = list(config["subs"].keys())
                for i in range(0, len(subs), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(subs):
                            sn = subs[i+j]
                            with cols[j]:
                                st.markdown(render_styled_card(sn, row[f"{sn}_正确数"], row[f"{sn}_总题数"], row[f"{sn}_用时"], row[f"{sn}_正确率"]), unsafe_allow_html=True)

# --- 📊 趋势分析 ---
elif menu == "📊 趋势分析":
    st.title("📈 成绩趋势走势")
    if df.empty: st.info("暂无数据")
    else:
        # 按照套卷显示而不是纯时间
        plot_df = df.copy()
        plot_df['显示名称'] = plot_df.apply(lambda x: f"{x['日期']}\n{x['试卷']}", axis=1)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        fig = px.line(plot_df, x='显示名称', y='总分', markers=True, text='总分', title="历史总分走势 (按模考顺序)")
        fig.update_traces(textposition="top center", line_color="#3b82f6", marker=dict(size=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("🗓️ 历史成绩明细")
        # 美化表格，只显示核心数据
        display_df = df[['日期', '试卷', '总分', '总正确数', '总题数', '总用时']].copy()
        display_df['正确率'] = (display_df['总正确数'] / display_df['总题数']).map(lambda x: f"{x:.1%}")
        st.dataframe(display_df.sort_values('日期', ascending=False), use_container_width=True, hide_index=True)

# --- 🛡️ 管理后台 ---
elif menu == "🛡️ 管理后台" and role == 'admin':
    st.title("🛡️ 权限管理中心")
    users = load_users()
    
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
                if new_u in users: st.error("该账号已存在")
                else:
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
                if new_pwd: users[target_u]['password'] = hash_pw(new_pwd)
                save_users(users)
                st.success("更新成功")
        with col2:
            st.warning("危险操作")
            if st.button("🔥 彻底删除此账号"):
                if target_u == 'admin': st.error("无法删除主管理员")
                else:
                    del users[target_u]
                    save_users(users)
                    st.success("已删除")
                    st.rerun()

# --- 🏠 数字化看板 ---
elif menu == "🏠 数字化看板":
    st.title("📊 数字化看板")
    if df.empty: st.info("请先录入成绩")
    else:
        latest = df.iloc[-1]
        cols = st.columns(4)
        cols[0].metric("最新得分", f"{latest['总分']:.1f}")
        cols[1].metric("正确率", f"{(latest['总正确数']/latest['总题数']):.1%}")
        cols[2].metric("用时", f"{latest['总用时']}m")
        cols[3].metric("试卷次数", len(df))
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        fig = go.Figure(go.Scatterpolar(r=[latest[f"{m}_正确率"] for m in LEAF_MODULES], theta=LEAF_MODULES, fill='toself'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), height=450, title="能力雷达图")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- ✏️ 录入成绩 ---
elif menu == "✏️ 录入成绩":
    st.subheader("🖋️ 录入套卷成绩")
    with st.form("input_score"):
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷全称")
        date = c2.date_input("考试日期")
        entry = {"日期": date, "试卷": paper}
        tc, tq, tt, ts = 0, 0, 0, 0
        
        for m, config in MODULE_STRUCTURE.items():
            st.markdown(f"**{m}**")
            if config["type"] == "direct":
                sc1, sc2 = st.columns(2)
                mq = sc1.number_input("对题", 0, config["total"], 0, key=f"q_{m}")
                mt = sc2.number_input("用时(min)", 0, 180, 5, key=f"t_{m}")
                entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = config["total"], mq, mt
                entry[f"{m}_正确率"] = mq/config["total"]
                tc+=mq; tq+=config["total"]; tt+=mt; ts+=mq*FIXED_WEIGHT
            else:
                sub_cols = st.columns(2)
                for idx, (sm, stot) in enumerate(config["subs"].items()):
                    with sub_cols[idx%2]:
                        sq = st.number_input(f"{sm} 对题", 0, stot, 0, key=f"sq_{sm}")
                        st_time = st.number_input(f"{sm} 用时", 0, 180, 5, key=f"st_{sm}")
                        entry[f"{sm}_总题数"], entry[f"{sm}_正确数"], entry[f"{sm}_用时"] = stot, sq, st_time
                        entry[f"{sm}_正确率"] = sq/stot
                        tc+=sq; tq+=stot; tt+=st_time; ts+=sq*FIXED_WEIGHT
        
        if st.form_submit_button("保存套卷数据"):
            if not paper: st.error("请输入试卷名称")
            else:
                entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df, un)
                st.success("数据已存档")
                time.sleep(1); st.rerun()

# --- ⚙️ 数据管理 ---
elif menu == "⚙️ 数据管理":
    st.title("⚙️ 数据中心")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        del_target = st.selectbox("选择要删除的记录", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1))
        if st.button("确认删除该记录"):
            df = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) != del_target]
            save_data(df, un)
            st.success("删除成功")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
