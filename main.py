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
# 1. 全局配置与响应式 UI 适配
# ==========================================
st.set_page_config(page_title="行测 Pro Max", layout="wide", page_icon="🚀")

# 注入优化后的 CSS
st.markdown("""
    <style>
    /* 基础背景 */
    .stApp { background: #f8f9fa; }
    
    /* 统一的卡片容器 */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        animation: fadeIn 0.8s ease-out;
    }

    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* KPI 指标样式 */
    .m-container { text-align: center; padding: 10px; }
    .m-value { 
        font-size: 2.2rem; 
        font-weight: 800; 
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .m-label { color: #6c757d; font-size: 0.9rem; font-weight: 500; margin-top: 5px; }

    /* 按钮全宽适配 */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
    
    /* 移动端微调 */
    @media (max-width: 640px) {
        .m-value { font-size: 1.6rem; }
    }
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
# 3. 登录与游客注册
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🚀 行测 Pro Max")
        st.markdown("### 数字化备考专家\n* 📊 **深度复盘**：多维度数据可视化\n* 🔒 **隐私隔离**：私人账号独立存储\n* 📱 **全端适配**：电脑手机完美体验")
    with c2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        t_l, t_r = st.tabs(["🔑 登录", "📝 游客注册"])
        with t_l:
            u = st.text_input("用户名", key="l_u")
            p = st.text_input("密码", type="password", key="l_p")
            if st.button("立即登录", type="primary"):
                users = load_users()
                if u in users and users[u]['password'] == hash_pw(p):
                    st.session_state.logged_in = True
                    st.session_state.u_info = {"un": u, **users[u]}
                    st.rerun()
                else: st.error("用户名或密码错误")
        with t_r:
            nu = st.text_input("账号名称", key="r_u")
            nn = st.text_input("你的昵称", key="r_n")
            np = st.text_input("设置密码", type="password", key="r_p")
            if st.button("完成注册并加入"):
                if nu and nn and np:
                    users = load_users()
                    if nu in users: st.error("账号已存在")
                    else:
                        users[nu] = {"name": nn, "password": hash_pw(np), "role": "user"}
                        save_users(users)
                        st.success("注册成功！请切换登录")
                else: st.warning("请填写完整信息")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. 主程序核心功能
# ==========================================
un = st.session_state.u_info['un']
role = st.session_state.u_info['role']
df = load_data(un)

with st.sidebar:
    st.markdown(f"### 👋 {st.session_state.u_info['name']}")
    menu_list = ["🏠 复盘首页", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"]
    if role == 'admin': menu_list.append("🛡️ 管理后台")
    menu = st.radio("导航功能", menu_list)
    st.divider()
    if st.button("注销退出"):
        st.session_state.logged_in = False
        st.rerun()

# --- A. 复盘首页 ---
if menu == "🏠 复盘首页":
    st.title("📊 备考驾驶舱")
    if df.empty:
        st.info("👋 欢迎！目前还没有数据。请点击左侧'录入成绩'开始第一次复盘。")
    else:
        latest = df.iloc[-1]
        
        # 顶部 KPI 卡片
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{latest["总分"]:.1f}</div><div class="m-label">本次得分</div></div>', unsafe_allow_html=True)
        with k2: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{latest["总正确数"]}/{latest["总题数"]}</div><div class="m-label">答对/总题</div></div>', unsafe_allow_html=True)
        with k3: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{int(latest["总用时"])}<small>m</small></div><div class="m-label">总用时</div></div>', unsafe_allow_html=True)
        with k4: st.markdown(f'<div class="custom-card m-container"><div class="m-value">{len(df)}</div><div class="m-label">累计练习</div></div>', unsafe_allow_html=True)

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("📈 近期分数波动")
            fig_t = px.area(df.tail(10), x='日期', y='总分', markers=True, color_discrete_sequence=['#3b82f6'])
            fig_t.update_layout(plot_bgcolor='white', height=300, margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_t, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 模块 ROI 分析
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("⏳ 提分性价比 (分/分钟)")
            roi_data = [{"模块": m, "ROI": (latest[f"{m}_正确数"] * FIXED_WEIGHT) / max(latest[f"{m}_用时"], 1)} for m in DEFAULT_MODULES]
            roi_df = pd.DataFrame(roi_data).sort_values('ROI', ascending=False)
            st.bar_chart(roi_df.set_index("模块"), color="#1e3a8a")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("🕸️ 能力雷达")
            cats = list(DEFAULT_MODULES.keys())
            fig_r = go.Figure(go.Scatterpolar(r=[latest[f"{m}_正确率"] for m in cats], theta=cats, fill='toself', line_color='#6366f1'))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=350, margin=dict(l=40,r=40,t=40,b=40))
            st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

# --- B. 趋势分析 ---
elif menu == "📊 趋势分析":
    st.subheader("📈 历史动态演变")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.plotly_chart(px.line(df, x='日期', y='总分', markers=True, title="总分走势曲线"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

# --- C. 单卷详情 (恢复电脑双列样式) ---
elif menu == "📑 单卷详情":
    if df.empty:
        st.info("暂无数据")
    else:
        st.title("📋 单卷深度复盘")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        sel = st.selectbox("选择试卷", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
        row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(sel)]
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 🧩 模块详细得分")
        cols = st.columns(2)  # 保持电脑端双列布局
        for i, m in enumerate(DEFAULT_MODULES.keys()):
            with cols[i % 2]:
                acc = row[f"{m}_正确率"]
                correct = int(row[f"{m}_正确数"])
                total = int(row[f"{m}_总题数"])
                # 动态颜色背景与边框
                bg_color = "#f0fdf4" if acc >= 0.8 else ("#fef2f2" if acc < 0.6 else "#ffffff")
                border_color = "#22c55e" if acc >= 0.8 else ("#ef4444" if acc < 0.6 else "#3b82f6")

                st.markdown(f"""
                <div style="background:{bg_color}; padding:15px; border-radius:12px; border-left:5px solid {border_color}; margin-bottom:15px; box-shadow:0 2px 5px rgba(0,0,0,0.05)">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; font-size:1.1em; color:#333">{m}</span>
                        <span style="font-weight:bold; font-size:1.2em; color:{border_color}">{correct} / {total}</span>
                    </div>
                    <div style="font-size:0.85em; color:#666; margin-top:5px;">
                        正确率: {acc:.1%} &nbsp;|&nbsp; 耗时: {int(row[f'{m}_用时'])} min
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- D. 录入成绩 ---
elif menu == "✏️ 录入成绩":
    st.subheader("🖋️ 录入新成绩")
    with st.form("exam_input"):
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷名称", placeholder="如：2026国考地市级")
        date = c2.date_input("日期", datetime.now())
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
                m_t = r3.number_input("用时", 0, 150, 10, key=f"t_{m}")
                entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = m_tot, m_q, m_t
                entry[f"{m}_正确率"] = m_q / m_tot
                tc += m_q; tq += m_tot; tt += m_t; ts += m_q * FIXED_WEIGHT
        
        entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
        if st.form_submit_button("🚀 提交存档"):
            if not paper: st.error("请输入试卷名")
            else:
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df, un)
                st.success("存档成功！")
                time.sleep(1); st.rerun()

# --- E. 数据管理 ---
elif menu == "⚙️ 数据管理":
    st.subheader("⚙️ 数据中心")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        to_del = st.selectbox("选择要删除的记录", df.apply(lambda x: f"ID:{x.name} | {x['日期']} | {x['试卷']}", axis=1).tolist())
        if st.button("🗑️ 确认删除单条数据"):
            idx = int(to_del.split(" | ")[0].split(":")[1])
            df = df.drop(idx).reset_index(drop=True)
            save_data(df, un)
            st.success("已删除"); time.sleep(0.5); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

# --- F. 管理后台 ---
elif menu == "🛡️ 管理后台" and role == 'admin':
    st.subheader("🛡️ 系统用户管理")
    users = load_users()
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write(f"当前共有 {len(users)} 名注册用户")
    st.table([{"用户名": k, "昵称": v['name'], "角色": v['role']} for k, v in users.items()])
    del_u = st.selectbox("选择要删除的用户", [k for k in users.keys() if k != 'admin'])
    if st.button("🚨 确认彻底删除用户"):
        del users[del_u]
        save_users(users)
        st.success(f"用户 {del_u} 已清理"); time.sleep(0.5); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
