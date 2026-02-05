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
    /* 基础背景 */
    .stApp { background: #f8f9fa; }
    
    /* 统一的卡片容器 */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* KPI 指标样式 */
    .m-container { text-align: center; padding: 5px; }
    .m-value { 
        font-size: 2rem; 
        font-weight: 800; 
        color: #1e3a8a;
        line-height: 1.2;
    }
    .m-label { color: #64748b; font-size: 0.85rem; margin-top: 5px; }

    /* 模块详情卡片样式 (单卷详情专用) */
    .module-detail-card {
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }

    /* 按钮适配 */
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; }
    
    @media (max-width: 640px) {
        .m-value { font-size: 1.5rem; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心后端逻辑
# ==========================================
USERS_FILE = 'users_db.json'
FIXED_WEIGHT = 0.8

DEFAULT_MODULES = {
    "政治理论": {"total": 15, "plan": 5},
    "常识判断": {"total": 15, "plan": 5},
    "言语-逻辑填空": {"total": 10, "plan": 9},
    "言语-片段阅读": {"total": 15, "plan": 9},
    "数量关系": {"total": 15, "plan": 25},
    "判断-图形推理": {"total": 5, "plan": 5},
    "判断-定义判断": {"total": 10, "plan": 10},
    "判断-类比推理": {"total": 10, "plan": 5},
    "判断-逻辑判断": {"total": 10, "plan": 15},
    "资料分析": {"total": 20, "plan": 25}
}

def hash_pw(pw): return hashlib.sha256(str(pw).encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        d = {"admin": {"name": "系统管理员", "password": hash_pw("qazwsx"), "role": "admin"}}
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
# 3. 登录与注册系统
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("<br><br><h1>🚀 行测 Pro Max</h1><h3>数字化复盘专家</h3>", unsafe_allow_html=True)
        st.info("💡 系统已实现电脑/手机 UI 适配，支持私人数据隔离与管理后台。")
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
            nn = st.text_input("设置昵称", key="r_n")
            np = st.text_input("设置密码", type="password", key="r_p")
            if st.button("完成注册"):
                if nu and nn and np:
                    users = load_users()
                    if nu in users: st.error("账号已存在")
                    else:
                        users[nu] = {"name": nn, "password": hash_pw(np), "role": "user"}
                        save_users(users)
                        st.success("注册成功！请登录")
                else: st.warning("请填写完整信息")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. 主程序导航
# ==========================================
un = st.session_state.u_info['un']
role = st.session_state.u_info['role']
df = load_data(un)

with st.sidebar:
    st.markdown(f"### 👋 {st.session_state.u_info['name']}")
    menu_list = ["🏠 复盘首页", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"]
    if role == 'admin': menu_list.append("🛡️ 管理后台")
    menu = st.radio("导航菜单", menu_list)
    st.divider()
    if st.button("安全退出"):
        st.session_state.logged_in = False
        st.rerun()

# --- A. 首页 ---
if menu == "🏠 复盘首页":
    st.title("📊 个人备考看板")
    if df.empty:
        st.info("暂无数据，请先在‘录入成绩’中保存一次考试。")
    else:
        latest = df.iloc[-1]
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{latest["总分"]:.1f}</div><div class="m-label">最新得分</div></div>', unsafe_allow_html=True)
        with k2: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{latest["总正确数"]}/{latest["总题数"]}</div><div class="m-label">答对题目</div></div>', unsafe_allow_html=True)
        with k3: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{int(latest["总用时"])}<small>m</small></div><div class="m-label">本次用时</div></div>', unsafe_allow_html=True)
        with k4: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{len(df)}</div><div class="m-label">练习总数</div></div>', unsafe_allow_html=True)

        col_l, col_r = st.columns([1.5, 1])
        with col_l:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("🕸️ 模块能力分布")
            cats = list(DEFAULT_MODULES.keys())
            fig_r = go.Figure(go.Scatterpolar(r=[latest[f"{m}_正确率"] for m in cats], theta=cats, fill='toself'))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), height=350, margin=dict(l=40,r=40,t=40,b=40))
            st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        with col_r:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("💡 提分建议")
            acc_data = [(m, latest[f"{m}_正确率"]) for m in DEFAULT_MODULES]
            worst = sorted(acc_data, key=lambda x: x[1])[0]
            st.error(f"本次最弱：**{worst[0]}**")
            st.caption(f"正确率仅 {worst[1]:.1%}，建议针对性刷题。")
            st.markdown('</div>', unsafe_allow_html=True)

# --- B. 趋势分析 ---
elif menu == "📊 趋势分析":
    st.subheader("📈 历史动态走势")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.plotly_chart(px.line(df, x='日期', y='总分', markers=True, title="总分变化走势"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df.sort_values('日期', ascending=False), use_container_width=True)

# --- C. 单卷详情 (适配电脑双列与手机堆叠) ---
elif menu == "📑 单卷详情":
    if df.empty:
        st.info("暂无数据")
    else:
        st.title("📋 单卷深度复盘")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        sel = st.selectbox("选择试卷", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
        row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(sel)]
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("🧩 各模块得分明细")
        cols = st.columns(2)  # 电脑版双列，手机版自动堆叠
        for i, m in enumerate(DEFAULT_MODULES.keys()):
            with cols[i % 2]:
                acc = row[f"{m}_正确率"]
                bg = "#f0fdf4" if acc >= 0.8 else ("#fef2f2" if acc < 0.6 else "#ffffff")
                bd = "#22c55e" if acc >= 0.8 else ("#ef4444" if acc < 0.6 else "#3b82f6")
                st.markdown(f"""
                <div class="module-detail-card" style="background:{bg}; border-left:5px solid {bd};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:#333;">{m}</b>
                        <b style="color:{bd}; font-size:1.1em;">{int(row[f'{m}_正确数'])} / {int(row[f'{m}_总题数'])}</b>
                    </div>
                    <div style="font-size:0.85em; color:#666; margin-top:5px;">
                        正确率: {acc:.1%} | 耗时: {int(row[f'{m}_用时'])} min
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- D. 录入成绩 ---
elif menu == "✏️ 录入成绩":
    st.subheader("🖋️ 录入考试记录")
    with st.form("input_form"):
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷名称", placeholder="如：2025年省考一模")
        date = c2.date_input("考试日期", datetime.now())
        st.markdown('</div>', unsafe_allow_html=True)
        
        entry = {"日期": date, "试卷": paper}
        tc, tq, tt, ts = 0, 0, 0, 0
        grid = st.columns(2)
        for i, (m, specs) in enumerate(DEFAULT_MODULES.items()):
            with grid[i % 2]:
                st.markdown(f"**{m}**")
                r1, r2, r3 = st.columns(3)
                m_tot = r1.number_input("总题", 1, 50, specs['total'], key=f"tot_{m}")
                m_q = r2.number_input("对题", 0, 50, 0, key=f"q_{m}")
                m_t = r3.number_input("时间", 0, 150, 10, key=f"t_{m}")
                entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = m_tot, m_q, m_t
                entry[f"{m}_正确率"] = m_q / m_tot
                tc += m_q; tq += m_tot; tt += m_t; ts += m_q * FIXED_WEIGHT
        
        if st.form_submit_button("🚀 保存并同步", type="primary"):
            if not paper: st.error("请输入试卷名称")
            else:
                entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df, un)
                st.success("存档成功！")
                time.sleep(1); st.rerun()

# --- E. 数据管理 ---
elif menu == "⚙️ 数据管理":
    st.subheader("⚙️ 数据维护")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        del_list = df.apply(lambda x: f"ID:{x.name} | {x['日期']} | {x['试卷']}", axis=1).tolist()
        to_del = st.selectbox("选择要删除的单条记录", del_list)
        if st.button("🗑️ 确认永久删除"):
            idx = int(to_del.split(" | ")[0].split(":")[1])
            df = df.drop(idx).reset_index(drop=True)
            save_data(df, un)
            st.success("已成功删除记录")
            time.sleep(0.5); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

# --- F. 管理后台 (新增修改密码功能) ---
elif menu == "🛡️ 管理后台" and role == 'admin':
    st.title("🛡️ 管理员工作台")
    users = load_users()
    
    # 1. 用户列表展示
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("👥 用户概览")
    u_df = pd.DataFrame([{"账号": k, "姓名": v['name'], "角色": v['role']} for k, v in users.items()])
    st.table(u_df)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. 修改用户密码 (核心更新)
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🔐 修改用户密码")
    target_u = st.selectbox("选择目标用户", list(users.keys()))
    new_p = st.text_input("输入新密码", type="password", key="reset_p")
    if st.button("⚡ 立即重置密码"):
        if new_p:
            users[target_u]['password'] = hash_pw(new_p)
            save_users(users)
            st.success(f"用户 {target_u} 的密码已成功重置！")
        else: st.warning("密码不能为空")
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. 删除用户
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🚨 危险操作")
    del_u = st.selectbox("选择要移除的用户", [k for k in users.keys() if k != 'admin'])
    if st.button("🔥 彻底删除该用户及其数据"):
        del users[del_u]
        save_users(users)
        # 可选：物理删除其数据文件
        p = f'data_storage_{del_u}.csv'
        if os.path.exists(p): os.remove(p)
        st.success(f"用户 {del_u} 已被彻底清理")
        time.sleep(0.5); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
