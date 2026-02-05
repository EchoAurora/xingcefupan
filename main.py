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
# 1. 全局配置与移动端 UI 适配
# ==========================================
st.set_page_config(page_title="行测 Pro Max", layout="wide", page_icon="🚀")

# 注入优化后的 CSS
st.markdown("""
    <style>
    /* 基础背景与字体适配 */
    .stApp { background: #f4f7f9; }
    
    /* 统一的卡片容器：适配手机内边距，移除多余嵌套 */
    .custom-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        animation: fadeIn 0.6s ease-out;
    }

    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* 手机端指标组件：自动堆叠 */
    .m-container { text-align: center; padding: 0.5rem; }
    .m-value { 
        font-size: 1.8rem; 
        font-weight: 800; 
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .m-label { color: #64748b; font-size: 0.85rem; margin-top: 4px; font-weight: 500; }

    /* 移动端间距微调 */
    @media (max-width: 640px) {
        .m-value { font-size: 1.5rem; }
        .block-container { padding-top: 1rem !important; }
    }
    
    /* 侧边栏按钮全宽 */
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心后端逻辑
# ==========================================
USERS_FILE = 'users.json'
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
        d = {"admin": {"name": "管理员", "password": hash_pw("123456"), "role": "admin"}}
        with open(USERS_FILE, 'w') as f: json.dump(d, f)
        return d
    with open(USERS_FILE, 'r') as f: return json.load(f)

def save_users(d): 
    with open(USERS_FILE, 'w', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False)

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
# 3. 登录/注册系统
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🚀 行测 Pro Max")
    tab_l, tab_r = st.tabs(["🔑 登录", "📝 游客注册"])
    
    with tab_l:
        u = st.text_input("账号", key="login_u")
        p = st.text_input("密码", type="password", key="login_p")
        if st.button("进入系统", type="primary"):
            users = load_users()
            if u in users and users[u]['password'] == hash_pw(p):
                st.session_state.logged_in = True
                st.session_state.u_info = {"un": u, **users[u]}
                st.rerun()
            else: st.error("账号或密码错误")
            
    with tab_r:
        nu = st.text_input("设置账号", key="reg_u")
        nn = st.text_input("昵称", key="reg_n")
        np = st.text_input("设置密码", type="password", key="reg_p")
        if st.button("完成注册"):
            if nu and nn and np:
                users = load_users()
                if nu in users: st.error("该账号已存在")
                else:
                    users[nu] = {"name": nn, "password": hash_pw(np), "role": "user"}
                    save_users(users)
                    st.success("注册成功！请切换到登录页进入")
            else: st.warning("请填写完整信息")
    st.stop()

# ==========================================
# 4. 主应用程序 (手机适配版)
# ==========================================
un = st.session_state.u_info['un']
role = st.session_state.u_info['role']
df = load_data(un)

with st.sidebar:
    st.markdown(f"### 👋 {st.session_state.u_info['name']}")
    menu_list = ["🏠 复盘首页", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"]
    if role == 'admin': menu_list.append("🛡️ 管理后台")
    menu = st.radio("导航", menu_list)
    st.divider()
    if st.button("安全退出"):
        st.session_state.logged_in = False
        st.rerun()

# --- 功能 A: 首页驾驶舱 ---
if menu == "🏠 复盘首页":
    st.title("📊 备考驾驶舱")
    if df.empty:
        st.info("欢迎！目前还没有数据。请先录入一次成绩，开启数字化复盘。")
    else:
        latest = df.iloc[-1]
        
        # KPI 卡片区域 (自动适配列)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{latest["总分"]:.1f}</div><div class="m-label">最新得分</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{latest["总正确数"]}/{latest["总题数"]}</div><div class="m-label">答对题数</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{int(latest["总用时"])}<small>m</small></div><div class="m-label">总耗时</div></div>', unsafe_allow_html=True)
        
        # 数据可视化
        col_l, col_r = st.columns([1.5, 1])
        with col_l:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("🕸️ 能力图谱")
            cats = list(DEFAULT_MODULES.keys())
            vals = [latest[f"{m}_正确率"] for m in cats]
            fig_r = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill='toself', line_color='#3b82f6'))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), height=320, margin=dict(l=40,r=40,t=40,b=40))
            st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_r:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("💡 提分建议")
            acc_list = [(m, latest[f"{m}_正确率"]) for m in DEFAULT_MODULES]
            worst = sorted(acc_list, key=lambda x: x[1])[0]
            st.error(f"需攻坚：**{worst[0]}**")
            st.progress(worst[1])
            st.caption(f"当前正确率仅为 {worst[1]:.1%}，建议针对性练习。")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 功能 B: 趋势分析 ---
elif menu == "📊 趋势分析":
    st.subheader("📈 历次得分走势")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.plotly_chart(px.line(df, x='日期', y='总分', markers=True), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df[['日期', '试卷', '总分']].sort_values('日期', ascending=False), use_container_width=True)
    else: st.warning("暂无数据")

# --- 功能 C: 单卷详情 ---
elif menu == "📑 单卷详情":
    if not df.empty:
        sel = st.selectbox("选择卷子", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
        row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(sel)]
        st.subheader(f"📋 {row['试卷']} 明细")
        
        for m in DEFAULT_MODULES.keys():
            acc = row[f"{m}_正确率"]
            color = "#16a34a" if acc >= 0.8 else ("#dc2626" if acc < 0.6 else "#2563eb")
            st.markdown(f"""
            <div class="custom-card" style="border-left: 5px solid {color}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:1rem;">{m}</b>
                    <span style="color:{color}; font-weight:700;">{int(row[f'{m}_正确数'])} / {int(row[f'{m}_总题数'])}</span>
                </div>
                <div style="font-size:0.85rem; color:gray; margin-top:5px;">耗时: {int(row[f'{m}_用时'])} min | 正确率: {acc:.1%}</div>
            </div>
            """, unsafe_allow_html=True)

# --- 功能 D: 录入成绩 ---
elif menu == "✏️ 录入成绩":
    st.subheader("🖋️ 录入模考记录")
    with st.form("input_form", clear_on_submit=True):
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        c_p, c_d = st.columns(2)
        paper = c_p.text_input("试卷名称", placeholder="如：2025粉笔一模")
        date = c_d.date_input("考试日期", datetime.now())
        st.markdown('</div>', unsafe_allow_html=True)
        
        entry = {"日期": date, "试卷": paper}
        tc, tq, tt, ts = 0, 0, 0, 0
        
        # 模块循环录入
        for m, specs in DEFAULT_MODULES.items():
            st.markdown(f"**{m}**")
            r1, r2, r3 = st.columns(3)
            m_tot = r1.number_input("总题", 1, 50, specs['total'], key=f"t_{m}")
            m_q = r2.number_input("对题", 0, 50, 0, key=f"q_{m}")
            m_t = r3.number_input("用时(m)", 0, 100, 10, key=f"m_{m}")
            entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = m_tot, m_q, m_t
            entry[f"{m}_正确率"] = m_q / m_tot
            tc += m_q; tq += m_tot; tt += m_t; ts += m_q * FIXED_WEIGHT
            
        entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
        if st.form_submit_button("🚀 提交并同步数据", type="primary"):
            if not paper: st.error("请输入试卷名称")
            else:
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df, un)
                st.success("存档成功！")
                time.sleep(1)
                st.rerun()

# --- 功能 E: 数据管理 ---
elif menu == "⚙️ 数据管理":
    st.subheader("⚙️ 数据中心")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.write("选择需要删除的记录：")
        del_list = df.apply(lambda x: f"索引 {x.name} | {x['日期']} | {x['试卷']}", axis=1).tolist()
        to_del = st.selectbox("选择记录", del_list)
        if st.button("❌ 确认删除记录", type="secondary"):
            idx = int(to_del.split(" | ")[0].split(" ")[1])
            df = df.drop(idx).reset_index(drop=True)
            save_data(df, un)
            st.success("记录已删除")
            time.sleep(0.5)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

# --- 功能 F: 管理后台 ---
elif menu == "🛡️ 管理后台" and role == 'admin':
    st.subheader("🛡️ 系统用户管理")
    users = load_users()
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write(f"当前共有 {len(users)} 名注册用户")
    u_list = [{"用户名": k, "昵称": v['name'], "权限": v['role']} for k, v in users.items()]
    st.table(pd.DataFrame(u_list))
    
    st.divider()
    del_u = st.selectbox("选择要移除的用户账号", [k for k in users.keys() if k != 'admin'])
    if st.button("🚨 彻底移除该用户"):
        del users[del_u]
        save_users(users)
        st.warning(f"用户 {del_u} 已被移除")
        time.sleep(0.5)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
