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
# 1. 全局配置与样式美化
# ==========================================
st.set_page_config(page_title="行测 Pro Max · 行测复盘系统", layout="wide", page_icon="🚀")

# 自定义 CSS：动效、卡片、渐变
st.markdown("""
    <style>
    /* 全局字体与背景 */
    .stApp {
        background: linear-gradient(to bottom right, #f8f9fa, #e9ecef);
    }
    
    /* 动画定义 */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* 卡片样式 */
    .css-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeIn 0.8s ease-out;
    }
    .css-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* 指标样式 */
    .metric-container {
        text-align: center;
        padding: 10px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* 侧边栏美化 */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eee;
    }
    
    /* 按钮美化 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心数据与用户管理系统
# ==========================================
USERS_FILE = 'users.json'
GOAL_SCORE = 100.0
FIXED_WEIGHT = 0.8

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

# --- 用户管理函数 ---
def hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        # 初始化默认管理员
        default_users = {
            "admin": {"name": "admin", "password": hash_password("123456"), "role": "admin"}
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False)
        return default_users
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users_data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False)

def register_user(username, name, password):
    users = load_users()
    if username in users:
        return False, "用户名已存在"
    users[username] = {
        "name": name,
        "password": hash_password(password),
        "role": "user"
    }
    save_users(users)
    return True, "注册成功，请登录"

def delete_user(username_to_delete):
    users = load_users()
    if username_to_delete in users:
        if users[username_to_delete]['role'] == 'admin':
            return False, "无法删除管理员账号"
        del users[username_to_delete]
        save_users(users)
        # 尝试删除该用户的数据文件
        user_data_file = f'data_storage_{username_to_delete}.csv'
        if os.path.exists(user_data_file):
            os.remove(user_data_file)
        return True, "用户及其数据已删除"
    return False, "用户不存在"

# --- 业务数据函数 ---
def get_db_file(username):
    return f'data_storage_{username}.csv'

def load_data(username):
    db_file = get_db_file(username)
    if os.path.exists(db_file):
        try:
            df = pd.read_csv(db_file)
            df['日期'] = pd.to_datetime(df['日期']).dt.date
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(df, username):
    df.to_csv(get_db_file(username), index=False, encoding='utf-8-sig')

# ==========================================
# 3. 身份验证界面 (Login / Register)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

if not st.session_state.logged_in:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🚀 行测 Pro Max")
        st.markdown("### 数字化备考专家")
        st.markdown("""
        * 📊 **全维度数据分析**：雷达图、趋势线、ROI分析
        * 🔒 **私人数据隔离**：每个账号独立存储
        * 🎨 **极致UI体验**：丝滑动效，清晰直观
        """)
    
    with col2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔑 登录", "📝 注册新账号"])
        
        with tab_login:
            login_user = st.text_input("用户名", key="l_user")
            login_pass = st.text_input("密码", type="password", key="l_pass")
            if st.button("立即登录", type="primary", use_container_width=True):
                users = load_users()
                if login_user in users and users[login_user]['password'] == hash_password(login_pass):
                    st.session_state.logged_in = True
                    st.session_state.user_info = {"username": login_user, **users[login_user]}
                    st.success("登录成功！正在跳转...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        
        with tab_reg:
            new_user = st.text_input("设置用户名 (英文/数字)", key="r_user")
            new_name = st.text_input("你的昵称", key="r_name")
            new_pass = st.text_input("设置密码", type="password", key="r_pass")
            if st.button("✨ 注册并加入", use_container_width=True):
                if new_user and new_pass and new_name:
                    success, msg = register_user(new_user, new_name, new_pass)
                    if success:
                        st.balloons()
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("请填写完整信息")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop() # 阻止运行后续代码直到登录

# ==========================================
# 4. 主应用程序 (登录后)
# ==========================================
user = st.session_state.user_info
username = user['username']
role = user.get('role', 'user')
df = load_data(username)

# --- 侧边栏 ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:10px;">
        <h2 style="margin:0;">👋 {user['name']}</h2>
        <p style="color:gray; font-size:0.8em;">身份: {'管理员' if role=='admin' else '备考生'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 根据权限显示菜单
    menu_options = ["🏠 行测复盘首页", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"]
    if role == 'admin':
        menu_options.append("🛡️ 管理员后台")
    
    menu = st.radio("功能导航", menu_options)
    
    st.divider()
    if st.button("退出登录", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_info = {}
        st.rerun()

# --- 功能A: 行测复盘首页 (增强版) ---
if menu == "🏠 行测复盘首页":
    st.title("📊 备考驾驶舱")
    
    if df.empty:
        st.info("👋 欢迎来到行测Pro Max！暂无数据，请点击左侧'录入成绩'开始你的第一次记录。")
    else:
        latest = df.iloc[-1]
        
        # 1. 核心KPI卡片 (CSS美化)
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f'<div class="metric-container"><div class="metric-value">{latest["总分"]:.1f}</div><div class="metric-label">本次得分</div></div>', unsafe_allow_html=True)
        with kpi2:
            st.markdown(f'<div class="metric-container"><div class="metric-value">{latest["总正确数"]}/{latest["总题数"]}</div><div class="metric-label">答对/总题</div></div>', unsafe_allow_html=True)
        with kpi3:
            avg_score = df['总分'].mean()
            delta = latest['总分'] - avg_score
            color = "green" if delta >= 0 else "red"
            st.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{color}">{int(latest["总用时"])}<span style="font-size:1rem">min</span></div><div class="metric-label">本次用时</div></div>', unsafe_allow_html=True)
        with kpi4:
             st.markdown(f'<div class="metric-container"><div class="metric-value">{len(df)}</div><div class="metric-label">累计刷卷数</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. 图表分析区
        col_left, col_right = st.columns([1.2, 1])
        
        with col_left:
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            st.subheader("📈 近期分数波动")
            # 漂亮的面积图
            fig_trend = px.area(df.tail(10), x='日期', y='总分', markers=True, 
                                color_discrete_sequence=['#3b82f6'])
            fig_trend.update_layout(plot_bgcolor='white', height=300, margin=dict(l=20,r=20,t=20,b=20))
            fig_trend.update_yaxes(gridcolor='#eee')
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 强弱项分析
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            st.subheader("🔍 模块强弱项分析")
            
            # 计算平均正确率
            module_cols = [col for col in df.columns if '正确率' in col]
            avg_acc = df[module_cols].mean().sort_values(ascending=False)
            
            best_mod = avg_acc.index[0].replace('_正确率', '')
            worst_mod = avg_acc.index[-1].replace('_正确率', '')
            
            c1, c2 = st.columns(2)
            c1.success(f"🌟 最强模块: **{best_mod}** ({avg_acc.iloc[0]:.1%})")
            c2.error(f"💣 需提升模块: **{worst_mod}** ({avg_acc.iloc[-1]:.1%})")
            
            # 简单的条形图展示各模块平均分
            avg_acc.index = [x.replace('_正确率', '') for x in avg_acc.index]
            st.bar_chart(avg_acc, color="#1e3a8a")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            st.subheader("🕸️ 本次能力雷达")
            categories = list(DEFAULT_MODULES.keys())
            values = [latest[f"{m}_正确率"] for m in categories]
            fig_radar = go.Figure(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#6366f1'))
            fig_radar.add_trace(go.Scatterpolar(r=[0.8]*len(categories), theta=categories, mode='lines', 
                                              name='目标线', line=dict(color='red', dash='dash')))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), 
                                  height=350, margin=dict(l=30,r=30,t=30,b=30), showlegend=False)
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ROI 分析
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            st.subheader("⏳ 提分性价比 (分/分钟)")
            roi_data = []
            for m in DEFAULT_MODULES:
                roi = (latest[f"{m}_正确数"] * FIXED_WEIGHT) / max(latest[f"{m}_用时"], 1)
                roi_data.append({'模块': m, 'ROI': roi})
            roi_df = pd.DataFrame(roi_data).sort_values('ROI', ascending=False).head(5)
            st.dataframe(roi_df, hide_index=True, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 功能B: 趋势分析 ---
elif menu == "📊 趋势分析":
    st.title("📈 历史动态演变")
    if df.empty: st.warning("数据不足")
    else:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📊 综合走势", "📋 历史全景表"])
        with tab1:
            st.plotly_chart(px.line(df, x='日期', y='总分', markers=True, title="总分变化曲线"), use_container_width=True)
            st.caption("可以选择下方模块查看具体正确率走势")
            m_sel = st.multiselect("选择对比模块", list(DEFAULT_MODULES.keys()))
            if m_sel:
                m_data = df.melt(id_vars=['日期', '试卷'], value_vars=[f"{m}_正确率" for m in m_sel], var_name='模块', value_name='正确率')
                st.plotly_chart(px.line(m_data, x='日期', y='正确率', color='模块', markers=True), use_container_width=True)
        with tab2:
            summary = df[['日期', '试卷', '总分', '总用时']].copy()
            for m in DEFAULT_MODULES: summary[m] = df[f"{m}_正确率"].apply(lambda x: f"{x:.1%}")
            st.dataframe(summary.sort_values(by='日期', ascending=False), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 功能C: 单卷详情 ---
elif menu == "📑 单卷详情":
    if df.empty: st.info("暂无数据")
    else:
        st.title("📋 单卷深度复盘")
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        sel = st.selectbox("选择试卷", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
        row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(sel)]
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🧩 模块详细得分")
        cols = st.columns(2)
        for i, m in enumerate(DEFAULT_MODULES.keys()):
            with cols[i % 2]:
                acc = row[f"{m}_正确率"]
                correct = int(row[f"{m}_正确数"])
                total = int(row[f"{m}_总题数"])
                # 动态颜色
                bg_color = "#f0fdf4" if acc >= 0.8 else ("#fef2f2" if acc < 0.6 else "#fff")
                border_color = "#22c55e" if acc >= 0.8 else ("#ef4444" if acc < 0.6 else "#3b82f6")
                
                st.markdown(f"""
                <div style="background:{bg_color}; padding:15px; border-radius:10px; border-left:5px solid {border_color}; margin-bottom:15px; box-shadow:0 2px 5px rgba(0,0,0,0.05)">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; font-size:1.1em; color:#333">{m}</span>
                        <span style="font-weight:bold; font-size:1.2em; color:{border_color}">{correct} / {total}</span>
                    </div>
                    <div style="font-size:0.85em; color:#666; margin-top:5px;">
                        正确率: {acc:.1%} &nbsp;|&nbsp; 耗时: {int(row[f'{m}_用时'])} min
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- 功能D: 录入成绩 ---
elif menu == "✏️ 录入成绩":
    st.title("🖋️ 录入新成绩")
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    with st.form("exam_input"):
        c1, c2 = st.columns(2)
        date = c1.date_input("考试日期", datetime.now())
        paper = c2.text_input("试卷名称", placeholder="例如：2026国考地市级")
        
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
        
        if st.form_submit_button("🚀 提交存档", type="primary"):
            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
            save_data(df, username)
            st.success("🎉 录入成功！正在刷新...")
            time.sleep(1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 功能E: 数据管理 ---
elif menu == "⚙️ 数据管理":
    st.title("⚙️ 数据中心")
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    if not df.empty:
        st.subheader("📂 原始数据管理")
        del_list = df.apply(lambda x: f"ID:{x.name} | {x['日期']} | {x['试卷']}", axis=1).tolist()
        to_del = st.selectbox("选择要删除的记录", del_list)
        if st.button("🗑️ 删除选中记录", type="secondary"):
            idx = int(to_del.split(" | ")[0].split(":")[1])
            save_data(df.drop(idx).reset_index(drop=True), username)
            st.success("删除成功！")
            time.sleep(0.5)
            st.rerun()
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无数据可管理")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 功能F: 管理员后台 (仅Admin可见) ---
elif menu == "🛡️ 管理员后台" and role == 'admin':
    st.title("🛡️ 系统用户管理")
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    # 1. 用户列表
    all_users = load_users()
    st.subheader(f"👥 用户列表 (共 {len(all_users)} 人)")
    
    # 转为DataFrame显示
    user_list = []
    for u, info in all_users.items():
        user_list.append({"用户名": u, "昵称": info['name'], "角色": info['role']})
    st.dataframe(pd.DataFrame(user_list), use_container_width=True)
    
    st.divider()
    
    # 2. 增加/删除用户
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("➕ 手动添加用户")
        with st.form("admin_add_user"):
            new_u = st.text_input("用户名")
            new_n = st.text_input("昵称")
            new_p = st.text_input("密码", type="password")
            if st.form_submit_button("添加"):
                if new_u and new_n and new_p:
                    succ, msg = register_user(new_u, new_n, new_p)
                    if succ: st.success(msg); time.sleep(0.5); st.rerun()
                    else: st.error(msg)
    
    with c2:
        st.subheader("❌ 删除用户")
        # 排除自己
        del_options = [u for u in all_users.keys() if u != username]
        if del_options:
            u_to_del = st.selectbox("选择要删除的用户", del_options)
            if st.button("确认删除该用户", type="primary"):
                succ, msg = delete_user(u_to_del)
                if succ: st.success(msg); time.sleep(0.5); st.rerun()
                else: st.error(msg)
        else:
            st.info("没有其他用户可删除")
            
    st.markdown('</div>', unsafe_allow_html=True)
