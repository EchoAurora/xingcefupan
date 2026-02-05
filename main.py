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
    .module-detail-card {
        padding: 15px; border-radius: 10px; margin-bottom: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.03); border-left: 5px solid #3b82f6;
    }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心后端逻辑
# ==========================================
USERS_FILE = 'users_db.json'
FIXED_WEIGHT = 0.8
GOAL_SCORE = 75.0

# 定义模块顺序与层级
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

# 获取所有底层的叶子模块列表
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
# 4. 核心功能导航
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

# --- A. 数字化看板 ---
if menu == "🏠 数字化看板":
    st.title("📊 数字化深度诊断")
    if df.empty:
        st.info("💡 尚未录入数据，请前往'录入成绩'开始第一篇模考吧！")
    else:
        latest = df.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            diff = latest['总分'] - df.iloc[-2]['总分'] if len(df) > 1 else 0
            st.metric("本次总分", f"{latest['总分']:.1f}", delta=f"{diff:.1f}" if len(df)>1 else None)
        with c2:
            st.metric("全卷正确率", f"{(latest['总正确数'] / latest['总题数']):.1%}")
        with c3:
            st.metric("进面距离", f"{max(GOAL_SCORE - latest['总分'], 0):.1f}", delta_color="inverse")
        with c4:
            st.metric("总用时", f"{int(latest['总用时'])} min")
        
        st.divider()
        l_col, r_col = st.columns([1, 1])
        with l_col:
            st.subheader("🕸️ 能力模型诊断")
            fig = go.Figure(go.Scatterpolar(r=[latest[f"{m}_正确率"] for m in LEAF_MODULES], theta=LEAF_MODULES, fill='toself'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), height=380, margin=dict(l=50,r=50,t=30,b=30))
            st.plotly_chart(fig, use_container_width=True)
        with r_col:
            st.subheader("⏳ 时间性价比 (每分钟得分)")
            roi_data = []
            for m in LEAF_MODULES:
                score = latest[f"{m}_正确数"] * FIXED_WEIGHT
                time_cost = max(latest[f"{m}_用时"], 1)
                roi_data.append({"模块": m, "性价比": round(score / time_cost, 2)})
            roi_df = pd.DataFrame(roi_data).sort_values("性价比", ascending=False)
            fig_roi = px.bar(roi_df, x='性价比', y='模块', orientation='h', color='性价比', color_continuous_scale='GnBu')
            fig_roi.update_layout(height=350, showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_roi, use_container_width=True)

# --- B. 趋势分析 ---
elif menu == "📊 趋势分析":
    st.subheader("📈 历史动态走势")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.plotly_chart(px.line(df, x='日期', y='总分', markers=True), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df.sort_values('日期', ascending=False), use_container_width=True)

# --- C. 单卷详情 ---
elif menu == "📑 单卷详情":
    if df.empty: st.info("暂无数据")
    else:
        st.title("📋 单卷深度复盘")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        sel = st.selectbox("选择卷子", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1])
        row = df.iloc[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist().index(sel)]
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("# 套题总分")
        c1, c2, c3 = st.columns(3)
        c1.metric("得分", f"{row['总分']:.1f}")
        c2.metric("总正确率", f"{(row['总正确数'] / row['总题数']):.1%}")
        c3.metric("总用时", f"{int(row['总用时'])}min")

        st.subheader("🧩 模块详细数据")
        cols = st.columns(2)
        for i, m in enumerate(LEAF_MODULES):
            with cols[i % 2]:
                acc = row[f"{m}_正确率"]
                bg = "#f0fdf4" if acc >= 0.8 else ("#fef2f2" if acc < 0.6 else "#ffffff")
                st.markdown(f"""<div class="module-detail-card" style="background:{bg};">
                    <b>{m}</b><br>对题：{int(row[f'{m}_正确数'])} / {int(row[f'{m}_总题数'])} | 用时：{int(row[f'{m}_用时'])}min
                </div>""", unsafe_allow_html=True)

# --- D. 录入成绩 (支持二级目录) ---
elif menu == "✏️ 录入成绩":
    st.subheader("🖋️ 录入模考记录")
    with st.form("input_form"):
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷名称")
        date = c2.date_input("日期", datetime.now())
        st.markdown('</div>', unsafe_allow_html=True)

        entry = {"日期": date, "试卷": paper}
        tc, tq, tt, ts = 0, 0, 0, 0

        # 按顺序循环一级目录
        for main_m, config in MODULE_STRUCTURE.items():
            st.markdown(f"### 📍 {main_m}")
            if config["type"] == "direct":
                # 一级直接录入（如政治、常识）
                cols = st.columns(2)
                m_q = cols[0].number_input(f"{main_m}-对题", 0, config["total"], 0, key=f"q_{main_m}")
                m_t = cols[1].number_input(f"{main_m}-用时", 0, 180, 5, key=f"t_{main_m}")
                entry[f"{main_m}_总题数"], entry[f"{main_m}_正确数"], entry[f"{main_m}_用时"] = config["total"], m_q, m_t
                entry[f"{main_m}_正确率"] = m_q / config["total"]
                tc += m_q; tq += config["total"]; tt += m_t; ts += m_q * FIXED_WEIGHT
            else:
                # 二级目录展开（如言语、判断）
                with st.expander(f"展开录入 {main_m} 子项", expanded=False):
                    sub_cols = st.columns(2)
                    for idx, (sub_m, sub_tot) in enumerate(config["subs"].items()):
                        target_col = sub_cols[idx % 2]
                        target_col.markdown(f"**{sub_m}**")
                        sq = target_col.number_input("对题", 0, sub_tot, 0, key=f"q_{sub_m}")
                        st_time = target_col.number_input("用时", 0, 180, 10, key=f"t_{sub_m}")
                        entry[f"{sub_m}_总题数"], entry[f"{sub_m}_正确数"], entry[f"{sub_m}_用时"] = sub_tot, sq, st_time
                        entry[f"{sub_m}_正确率"] = sq / sub_tot
                        tc += sq; tq += sub_tot; tt += st_time; ts += sq * FIXED_WEIGHT
            st.divider()
        
        if st.form_submit_button("🚀 提交存档", type="primary"):
            if not paper: st.error("请填写卷子名称")
            else:
                entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df, un)
                st.success("存档成功！")
                time.sleep(0.5); st.rerun()
# --- E. 数据管理 ---
elif menu == "⚙️ 数据管理":
    st.subheader("⚙️ 数据中心")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        del_list = df.apply(lambda x: f"ID:{x.name} | {x['日期']} | {x['试卷']}", axis=1).tolist()
        to_del = st.selectbox("选择要彻底删除的记录", del_list)
        if st.button("🗑️ 确认删除单条数据"):
            idx = int(to_del.split(" | ")[0].split(":")[1])
            df = df.drop(idx).reset_index(drop=True)
            save_data(df, un)
            st.success("已删除"); time.sleep(0.5); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

# --- F. 管理后台 ---
elif menu == "🛡️ 管理后台" and role == 'admin':
    st.title("🛡️ 系统管理中心")
    users = load_users()
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("👥 用户列表")
    u_data = [{"账号": k, "昵称": v['name'], "角色": v['role']} for k, v in users.items()]
    st.table(pd.DataFrame(u_data))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🔐 修改用户密码")
    target_u = st.selectbox("选择目标账户", list(users.keys()))
    new_p = st.text_input("设置新密码", type="password")
    if st.button("⚡ 确认重置密码"):
        if new_p:
            users[target_u]['password'] = hash_pw(new_p)
            save_users(users)
            st.success(f"用户 {target_u} 的密码更新成功！")
        else: st.warning("请先输入新密码")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🚨 危险操作")
    del_u = st.selectbox("选择要注销的用户", [k for k in users.keys() if k != 'admin'])
    if st.button("🔥 彻底销毁该用户账号"):
        del users[del_u]
        save_users(users)
        p = f'data_storage_{del_u}.csv'
        if os.path.exists(p): os.remove(p)
        st.success(f"用户 {del_u} 数据已抹除")
        time.sleep(0.5); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

