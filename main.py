import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
import hashlib
import time

# ======================================================
# 1. 页面配置（手机友好）
# ======================================================
st.set_page_config(
    page_title="行测 Pro Max",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="collapsed"
)

# ======================================================
# 2. 全局 UI 样式（重点）
# ======================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Inter","PingFang SC","Microsoft YaHei",sans-serif;
}

.stApp {
    background: linear-gradient(180deg,#f8fafc 0%,#f1f5f9 100%);
}

/* 卡片 */
.custom-card {
    background: #ffffff;
    padding: 1.4rem 1.6rem;
    border-radius: 14px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.06);
    margin-bottom: 1.2rem;
}

/* 模块卡片 */
.module-detail-card {
    background: #ffffff;
    padding: 14px 18px;
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 6px solid #e5e7eb;
    transition: all .25s ease;
}
.module-detail-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 26px rgba(0,0,0,0.08);
}

.module-name {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
}
.module-meta {
    font-size: .8rem;
    color: #64748b;
}
.module-score-right {
    font-size: 1.2rem;
    font-weight: 800;
}

/* 分区标题 */
.section-divider {
    background: linear-gradient(90deg,#e0f2fe,#f8fafc);
    padding: 10px 16px;
    border-radius: 10px;
    margin: 26px 0 16px;
    font-weight: 700;
    color: #0f172a;
    border-left: 6px solid #3b82f6;
}

/* 状态色 */
.status-green { border-left-color:#22c55e!important; }
.status-red { border-left-color:#ef4444!important; }
.status-blue { border-left-color:#3b82f6!important; }

/* 移动端 */
@media (max-width:768px){
    .custom-card{padding:1rem}
    .module-detail-card{flex-direction:column;align-items:flex-start}
    .module-score-right{align-self:flex-end}
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# 3. 数据结构
# ======================================================
USERS_FILE = "users_db.json"
FIXED_WEIGHT = 0.8

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
        "subs": {
            "判断-图形推理": 5,
            "判断-定义判断": 10,
            "判断-类比推理": 10,
            "判断-逻辑判断": 10
        }
    },
    "资料分析": {"type": "direct", "total": 20}
}

def get_leaf_modules():
    res=[]
    for k,v in MODULE_STRUCTURE.items():
        if v["type"]=="direct": res.append(k)
        else: res+=list(v["subs"].keys())
    return res

LEAF_MODULES = get_leaf_modules()

# ======================================================
# 4. 工具函数
# ======================================================
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        d={"admin":{"name":"管理员","password":hash_pw("admin123"),"role":"admin"}}
        with open(USERS_FILE,"w",encoding="utf-8") as f:
            json.dump(d,f,ensure_ascii=False,indent=2)
        return d
    with open(USERS_FILE,"r",encoding="utf-8") as f:
        return json.load(f)

def save_users(d):
    with open(USERS_FILE,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

def load_data(u):
    path=f"data_{u}.csv"
    if os.path.exists(path):
        df=pd.read_csv(path)
        df["日期"]=pd.to_datetime(df["日期"]).dt.date
        return df
    return pd.DataFrame()

def save_data(df,u):
    df.to_csv(f"data_{u}.csv",index=False,encoding="utf-8-sig")

def render_card(name, correct, total, time_, acc):
    status="status-blue"
    if acc>=0.8: status="status-green"
    elif acc<0.6: status="status-red"
    return f"""
    <div class="module-detail-card {status}">
        <div>
            <div class="module-name">{name}</div>
            <div class="module-meta">正确率 {acc:.1%} · 用时 {int(time_)} min</div>
        </div>
        <div class="module-score-right">{int(correct)} / {int(total)}</div>
    </div>
    """

# ======================================================
# 5. 登录
# ======================================================
if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:
    c1,c2=st.columns([1,1.2])
    with c1:
        st.markdown("## 🚀 行测 Pro Max\n#### 模考复盘数字系统")
    with c2:
        st.markdown('<div class="custom-card">',unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["登录","注册"])

with tab1:
    u = st.text_input("账号", key="login_user")
    p = st.text_input("密码", type="password", key="login_pwd")
    if st.button("进入系统", type="primary"):
        users = load_users()
        if u in users and users[u]["password"] == hash_pw(p):
            st.session_state.login = True
            st.session_state.user = {"un": u, **users[u]}
            st.rerun()
        else:
            st.error("账号或密码错误")

with tab2:
    nu = st.text_input("新账号", key="reg_user")
    nn = st.text_input("昵称", key="reg_name")
    np = st.text_input("密码", type="password", key="reg_pwd")
    if st.button("注册"):
        users = load_users()
        if nu in users:
            st.error("账号已存在")
        elif not (nu and nn and np):
            st.warning("请填写完整信息")
        else:
            users[nu] = {
                "name": nn,
                "password": hash_pw(np),
                "role": "user"
            }
            save_users(users)
            st.success("注册成功，请返回登录")


# ======================================================
# 6. 主界面
# ======================================================
un=st.session_state.user["un"]
role=st.session_state.user["role"]
df=load_data(un)

with st.sidebar:
    st.markdown(f"### 👋 {st.session_state.user['name']}")
    menu=st.radio("导航",["🏠 看板","📊 趋势","📑 单卷","✏️ 录入","⚙️ 数据"])
    if role=="admin": st.radio("",["🛡️ 管理"])
    st.divider()
    if st.button("退出登录"):
        st.session_state.login=False
        st.rerun()

# ======================================================
# 7. 看板
# ======================================================
if menu=="🏠 看板":
    st.title("📊 学习看板")
    if df.empty: st.info("暂无数据")
    else:
        latest=df.iloc[-1]
        st.markdown('<div class="custom-card">',unsafe_allow_html=True)
        cols=st.columns(4)
        cols[0].metric("得分",f"{latest['总分']:.1f}")
        cols[1].metric("正确率",f"{latest['总正确数']/latest['总题数']:.1%}")
        cols[2].metric("用时",f"{latest['总用时']} min")
        cols[3].metric("模考次数",len(df))
        st.markdown("</div>",unsafe_allow_html=True)

        fig=go.Figure(go.Scatterpolar(
            r=[latest[f"{m}_正确率"] for m in LEAF_MODULES],
            theta=LEAF_MODULES,
            fill="toself"
        ))
        fig.update_layout(height=380)
        st.plotly_chart(fig,use_container_width=True)

# ======================================================
# 8. 趋势
# ======================================================
elif menu=="📊 趋势":
    st.title("📈 成绩趋势")
    if df.empty: st.info("暂无数据")
    else:
        df["显示"]=df.apply(lambda x:f"{x['日期']}\n{x['试卷']}",axis=1)
        fig=px.line(df,x="显示",y="总分",markers=True)
        fig.update_layout(height=360)
        st.plotly_chart(fig,use_container_width=True)

# ======================================================
# 9. 单卷
# ======================================================
elif menu=="📑 单卷":
    if df.empty: st.info("暂无数据")
    else:
        sel=st.selectbox("选择试卷",df.apply(lambda x:f"{x['日期']} | {x['试卷']}",axis=1))
        row=df[df.apply(lambda x:f"{x['日期']} | {x['试卷']}",axis=1)==sel].iloc[0]
        for m,cfg in MODULE_STRUCTURE.items():
            st.markdown(f'<div class="section-divider">{m}</div>',unsafe_allow_html=True)
            if cfg["type"]=="direct":
                st.markdown(render_card(
                    m,row[f"{m}_正确数"],row[f"{m}_总题数"],
                    row[f"{m}_用时"],row[f"{m}_正确率"]
                ),unsafe_allow_html=True)
            else:
                for sm in cfg["subs"]:
                    st.markdown(render_card(
                        sm,row[f"{sm}_正确数"],row[f"{sm}_总题数"],
                        row[f"{sm}_用时"],row[f"{sm}_正确率"]
                    ),unsafe_allow_html=True)

# ======================================================
# 10. 录入
# ======================================================
elif menu=="✏️ 录入":
    st.subheader("✍️ 录入成绩")
    with st.form("f"):
        paper=st.text_input("试卷名称")
        date=st.date_input("日期")
        entry={"日期":date,"试卷":paper}
        tc=tq=tt=ts=0
        for m,cfg in MODULE_STRUCTURE.items():
            st.markdown(f"**{m}**")
            if cfg["type"]=="direct":
                c1,c2=st.columns(2)
                q=c1.number_input("对题",0,cfg["total"],0,key=m)
                t=c2.number_input("用时",0,200,5,key=m+"t")
                entry[f"{m}_总题数"]=cfg["total"]
                entry[f"{m}_正确数"]=q
                entry[f"{m}_用时"]=t
                entry[f"{m}_正确率"]=q/cfg["total"]
                tc+=q; tq+=cfg["total"]; tt+=t; ts+=q*FIXED_WEIGHT
            else:
                for sm,stot in cfg["subs"].items():
                    q=st.number_input(f"{sm} 对题",0,stot,0,key=sm)
                    t=st.number_input(f"{sm} 用时",0,200,5,key=sm+"t")
                    entry[f"{sm}_总题数"]=stot
                    entry[f"{sm}_正确数"]=q
                    entry[f"{sm}_用时"]=t
                    entry[f"{sm}_正确率"]=q/stot
                    tc+=q; tq+=stot; tt+=t; ts+=q*FIXED_WEIGHT
        if st.form_submit_button("保存"):
            entry.update({"总分":round(ts,2),"总正确数":tc,"总题数":tq,"总用时":tt})
            df=pd.concat([df,pd.DataFrame([entry])])
            save_data(df,un)
            st.success("保存成功")
            time.sleep(1)
            st.rerun()

# ======================================================
# 11. 数据
# ======================================================
elif menu=="⚙️ 数据":
    if not df.empty:
        st.dataframe(df,use_container_width=True)

