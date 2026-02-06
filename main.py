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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心逻辑与数据结构
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
# 3. 登录与鉴权
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

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
                else: st.error("账号或密码错误")
        with t2:
            nu = st.text_input("设置账号", key="r_u")
            nn = st.text_input("昵称", key="r_n")
            np = st.text_input("密码", type="password", key="r_p")
            if st.button("完成注册", use_container_width=True):
                users = load_users()
                if nu in users: st.error("账号已存在")
                elif nu and nn and np:
                    users[nu] = {"name": nn, "password": hash_pw(np), "role": "user"}
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

with st.sidebar:
    st.markdown(f"### 👋 Hi, {st.session_state.u_info['name']}")
    menu = st.radio("功能导航", ["🏠 数字化看板", "📊 趋势分析", "📑 单卷详情", "✏️ 录入成绩", "⚙️ 数据管理"] + (["🛡️ 管理后台"] if role == 'admin' else []))
    st.markdown("---")
    if st.button("安全退出", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# 辅助函数：渲染小卡片
def render_styled_card(name, correct, total, duration, accuracy):
    if accuracy >= 0.8: status = "status-green"
    elif accuracy < 0.6: status = "status-red"
    else: status = "status-blue"
    
    return f"""
    <div class="module-detail-card {status}">
        <div class="module-info-left">
            <div class="module-name">{name}</div>
            <div class="module-meta">{accuracy:.1%} | {int(duration)}min</div>
        </div>
        <div class="module-score-right">{int(correct)}/{int(total)}</div>
    </div>
    """

# --- 🏠 数字化看板 (功能增强) ---
if menu == "🏠 数字化看板":
    st.title("📊 数字化深度诊断")
    if df.empty:
        st.info("👋 欢迎！请先前往【录入成绩】开始你的第一套模考。")
    else:
        latest = df.iloc[-1]
        
        # 1. 顶部核心指标
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("最新得分", f"{latest['总分']:.1f}", delta=f"{latest['总分'] - df.iloc[-2]['总分']:.1f}" if len(df)>1 else None)
        c2.metric("正确率", f"{(latest['总正确数']/latest['总题数']):.1%}")
        c3.metric("平均分 (近5次)", f"{df.tail(5)['总分'].mean():.1f}")
        c4.metric("刷题套数", f"{len(df)}")
        
        # 2. 进步与退步模块分析
        st.markdown("##### 🚀 模块动态分析 (对比上一场)")
        if len(df) > 1:
            prev = df.iloc[-2]
            # 计算每个模块的正确率变化
            diffs = {}
            for m in LEAF_MODULES:
                diffs[m] = latest[f"{m}_正确率"] - prev[f"{m}_正确率"]
            
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

        # 3. 图表区域
        st.markdown("---")
        col_l, col_r = st.columns([1, 1.3])
        
        with col_l:
            st.subheader("🕸️ 能力雷达")
            fig = go.Figure(go.Scatterpolar(
                r=[latest[f"{m}_正确率"] for m in LEAF_MODULES], 
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
            # 显示分数的分布直方图，看稳定性
            fig_hist = px.histogram(df, x="总分", nbins=10, color_discrete_sequence=['#3b82f6'])
            fig_hist.update_layout(height=350, margin=dict(t=20, b=20), xaxis_title="分数区间", yaxis_title="次数")
            st.plotly_chart(fig_hist, use_container_width=True)

# --- 📑 单卷详情 (布局重构) ---
elif menu == "📑 单卷详情":
    if df.empty: st.info("暂无数据")
    else:
        st.title("📋 单卷深度复盘")
        
        # 顶部选择器和摘要
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择历史模考", sel_list, label_visibility="collapsed")
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]
        
        # 摘要栏
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("得分", f"{row['总分']:.1f}")
        m2.metric("正确率", f"{(row['总正确数']/row['总题数']):.1%}")
        m3.metric("总用时", f"{int(row['总用时'])} min")
        # 计算该卷子的时间利用率（每分钟得分）
        score_per_min = row['总分'] / max(row['总用时'], 1)
        m4.metric("得分效率", f"{score_per_min:.2f} 分/min")
        st.markdown('</div>', unsafe_allow_html=True)

        # 布局重构：电脑端三列（一屏看完），手机端自动堆叠
        # 我们手动将模块分配到三列中，以节省垂直空间
        col_left, col_mid, col_right = st.columns(3)
        
        # --- 左列：政治、常识、言语 ---
        with col_left:
            st.markdown('<div class="mini-header">政治常识</div>', unsafe_allow_html=True)
            # 政治
            st.markdown(render_styled_card("政治理论", row["政治理论_正确数"], row["政治理论_总题数"], row["政治理论_用时"], row["政治理论_正确率"]), unsafe_allow_html=True)
            # 常识
            st.markdown(render_styled_card("常识判断", row["常识判断_正确数"], row["常识判断_总题数"], row["常识判断_用时"], row["常识判断_正确率"]), unsafe_allow_html=True)
            
            st.markdown('<div class="mini-header">言语理解</div>', unsafe_allow_html=True)
            # 言语子模块
            for sub in ["言语-逻辑填空", "言语-片段阅读"]:
                st.markdown(render_styled_card(sub, row[f"{sub}_正确数"], row[f"{sub}_总题数"], row[f"{sub}_用时"], row[f"{sub}_正确率"]), unsafe_allow_html=True)
            st.markdown('<div class="mini-header">数量关系</div>', unsafe_allow_html=True)
            
            # 数量
            st.markdown(render_styled_card("数量关系", row["数量关系_正确数"], row["数量关系_总题数"], row["数量关系_用时"], row["数量关系_正确率"]), unsafe_allow_html=True)
            
 

        # --- 右列：判断推理 ---
        with col_right:
            st.markdown('<div class="mini-header">判断推理</div>', unsafe_allow_html=True)
            # 判断的所有子模块
            judgement_subs = ["判断-图形推理", "判断-定义判断", "判断-类比推理", "判断-逻辑判断"]
            for sub in judgement_subs:
                st.markdown(render_styled_card(sub, row[f"{sub}_正确数"], row[f"{sub}_总题数"], row[f"{sub}_用时"], row[f"{sub}_正确率"]), unsafe_allow_html=True)
            st.markdown('<div class="mini-header">资料分析</div>', unsafe_allow_html=True)
            
            # 资料 (大模块，放在中间显眼)
            st.markdown(render_styled_card("资料分析", row["资料分析_正确数"], row["资料分析_总题数"], row["资料分析_用时"], row["资料分析_正确率"]), unsafe_allow_html=True)

# --- 📊 趋势分析 ---
elif menu == "📊 趋势分析":
    st.title("📈 模考趋势走势")
    if df.empty: st.info("暂无数据")
    else:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        # 预处理数据：增加一个“场次”列，方便排序展示
        plot_df = df.copy()
        plot_df['场次'] = plot_df.apply(lambda x: f"{x['日期']}\n{x['试卷']}", axis=1)
        
        # 1. 总分趋势图
        fig = px.line(plot_df, x='场次', y='总分', markers=True, text='总分', title="总分走势")
        fig.update_traces(textposition="top center", line_color="#2563eb", marker=dict(size=8, color='white', line=dict(width=2, color='#2563eb')))
        fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f1f5f9'))
        st.plotly_chart(fig, use_container_width=True)
        
        # 2. 模块正确率趋势对比 (可选功能)
        st.caption("模块正确率波动")
        module_trends = plot_df[['场次'] + [f"{m}_正确率" for m in LEAF_MODULES]].melt(id_vars='场次', var_name='模块', value_name='正确率')
        module_trends['模块'] = module_trends['模块'].str.replace('_正确率', '')
        fig2 = px.line(module_trends, x='场次', y='正确率', color='模块', markers=True)
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("🗓️ 历史成绩明细")
        display_df = df[['日期', '试卷', '总分', '总正确数', '总题数', '总用时']].copy()
        display_df['正确率'] = (display_df['总正确数'] / display_df['总题数']).map(lambda x: f"{x:.1%}")
        st.dataframe(display_df.sort_values('日期', ascending=False), use_container_width=True, hide_index=True)

# --- ✏️ 录入成绩 ---
elif menu == "✏️ 录入成绩":
    st.subheader("🖋️ 录入模考成绩")
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    with st.form("input_score"):
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷全称", placeholder="例如：2024国考副省")
        date = c2.date_input("考试日期")
        st.divider()
        
        entry = {"日期": date, "试卷": paper}
        tc, tq, tt, ts = 0, 0, 0, 0
        
        # 优化录入布局
        for m, config in MODULE_STRUCTURE.items():
            if config["type"] == "direct":
                st.markdown(f"**📌 {m}**")
                sc1, sc2 = st.columns(2)
                mq = sc1.number_input("对题数", 0, config["total"], 0, key=f"q_{m}")
                mt = sc2.number_input("用时 (min)", 0, 180, 5, key=f"t_{m}")
                entry[f"{m}_总题数"], entry[f"{m}_正确数"], entry[f"{m}_用时"] = config["total"], mq, mt
                entry[f"{m}_正确率"] = mq/config["total"] if config["total"]>0 else 0
                tc+=mq; tq+=config["total"]; tt+=mt; ts+=mq*FIXED_WEIGHT
            else:
                st.markdown(f"**📌 {m}**")
                sub_cols = st.columns(len(config["subs"])) # 动态列宽
                for idx, (sm, stot) in enumerate(config["subs"].items()):
                    with sub_cols[idx]:
                        st.caption(f"{sm}")
                        sq = st.number_input("对题", 0, stot, 0, key=f"sq_{sm}")
                        st_time = st.number_input("min", 0, 180, 5, key=f"st_{sm}", label_visibility="collapsed")
                        entry[f"{sm}_总题数"], entry[f"{sm}_正确数"], entry[f"{sm}_用时"] = stot, sq, st_time
                        entry[f"{sm}_正确率"] = sq/stot if stot>0 else 0
                        tc+=sq; tq+=stot; tt+=st_time; ts+=sq*FIXED_WEIGHT
            st.markdown("---")
        
        if st.form_submit_button("🚀 提交存档", type="primary", use_container_width=True):
            if not paper: st.error("请输入试卷名称")
            else:
                entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_data(df, un)
                st.success("数据已存档")
                time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ⚙️ 数据管理 ---
elif menu == "⚙️ 数据管理":
    st.title("⚙️ 数据中心")
    if not df.empty:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        del_target = st.selectbox("选择要删除的记录", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1))
        
        if st.button("🗑️ 确认删除该记录", type="secondary"):
            df = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) != del_target]
            save_data(df, un)
            st.success("删除成功")
            time.sleep(0.5)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 🛡️ 管理后台 ---
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
                if new_u in users: st.error("该账号已存在")
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
    st.markdown('</div>', unsafe_allow_html=True)

