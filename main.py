# -*- coding: utf-8 -*-
"""
行测 Pro Max 复盘系统（带数据备份 / 迁移功能）

主要功能：
- 账号系统（多用户）
- 成绩录入、单卷复盘、趋势分析
- 自动生成短板 / 时间黑洞 / 明日训练 / 一周训练计划
- 每日打卡（streak）
- 数据备份与导入（zip）
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
import hashlib
import time
import io
import zipfile
from typing import Dict, List, Tuple
import toml



# =========================================================
# 0. 页面配置
# =========================================================
st.set_page_config(page_title="行测 Pro Max", layout="wide", page_icon="🚀")

# =========================================================
# 1. 全局 UI（浅色 + 自适应）
# =========================================================
st.markdown("""
<style>
/* ---------------- 基础色板 ---------------- */
:root{
  --bg: #f4f6f9;
  --ink: #0b1220;
  --muted: #64748b;
  --border: rgba(148,163,184,0.22);
  --glass: rgba(255,255,255,0.85);
  --shadow: 0 18px 55px rgba(15,23,42,0.18);
  --shadow2: 0 10px 30px rgba(15,23,42,0.12);
  --radius: 18px;
  --radius2: 22px;
  --blue: #3b82f6;
  --green: #10b981;
  --red: #ef4444;
  --orange:#f59e0b;
}

.block-container{
  padding-top: 1.0rem !important;
  padding-bottom: 1.0rem !important;
  max-width: 1250px;
}
.stApp{
  background: var(--bg);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", Segoe UI, Roboto, "Helvetica Neue", Arial;
}

/* ---------------- Sidebar（浅色） ---------------- */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #ffffff 0%, #e5edff 55%, #ffffff 100%) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] *{ color: #111827 !important; }
.sidebar-title{
  font-weight: 900;
  font-size: 1.05rem;
  letter-spacing: -0.02em;
}
.sidebar-sub{ color: var(--muted); font-size: 0.83rem; }

/* ---------------- Hero（浅色渐变卡片） ---------------- */
.hero{
  border-radius: var(--radius2);
  padding: 18px 18px;
  background:
    radial-gradient(1200px 560px at 8% 5%, rgba(59,130,246,0.22), transparent 58%),
    radial-gradient(900px 480px at 92% 10%, rgba(16,185,129,0.20), transparent 52%),
    radial-gradient(700px 460px at 55% 95%, rgba(245,158,11,0.18), transparent 62%),
    linear-gradient(135deg, #e0edff 0%, #f7fbff 50%, #e9f7ff 100%);
  border: 1px solid rgba(148,163,184,0.28);
  box-shadow: 0 22px 65px rgba(15,23,42,0.18);
  color: #0f172a;
  margin-bottom: 14px;
}
.hero-title{
  font-size: 1.42rem;
  font-weight: 950;
  letter-spacing: -0.03em;
  margin-bottom: 6px;
}
.hero-sub{
  color: #475569;
  font-size: 0.93rem;
  line-height: 1.5;
}
.hero-badges{ margin-top: 10px; display:flex; gap:8px; flex-wrap: wrap; }
.badge{
  display:inline-flex; align-items:center; gap:6px;
  padding: 6px 10px; border-radius: 999px;
  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(148,163,184,0.40);
  color: var(--ink); font-size: 0.78rem;
}

/* ---------------- 通用卡片 ---------------- */
.card{
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  box-shadow: var(--shadow2);
  margin-bottom: 12px;
  backdrop-filter: blur(8px);
}
.card:hover{ box-shadow: var(--shadow); transform: translateY(-1px); transition: 0.18s; }

/* 深色卡片（仅首页 KPI 使用一点对比） */
.card-dark{
  background: linear-gradient(135deg, #1d2653 0%, #111827 100%);
  color: #e2e8f0;
  border: 1px solid rgba(148,163,184,0.48);
  box-shadow: 0 24px 70px rgba(15,23,42,0.65);
}

/* ---------------- KPI ---------------- */
.kpi-wrap{ display:flex; gap:10px; flex-wrap:wrap; margin-top: 6px; }
.kpi{
  flex: 1 1 190px;
  border-radius: 16px;
  padding: 12px 12px;
  background: rgba(15,23,42,0.12);
  border: 1px solid rgba(148,163,184,0.30);
}
.kpi .k{ font-size: 0.80rem; color: rgba(226,232,240,0.90); }
.kpi .v{ font-size: 1.36rem; font-weight: 950; margin-top: 2px; letter-spacing:-0.02em; }
.kpi .d{ font-size: 0.78rem; color: rgba(226,232,240,0.86); margin-top: 4px; }

/* ---------------- 小标题 ---------------- */
.mini-header{
  font-size: 0.82rem;
  font-weight: 950;
  color: #475569;
  margin: 12px 0 6px 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  display:flex; align-items:center;
}
.mini-header::before{
  content:'';
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  margin-right: 8px;
}
.small-muted{ color: var(--muted); font-size: 0.86rem; }

/* ---------------- 提示盒 / 标签 ---------------- */
.tip-box{
  background: #0f172a;
  color: #e2e8f0;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(148,163,184,0.45);
  margin: 8px 0;
  line-height: 1.55;
  font-size: 0.90rem;
  box-shadow: 0 18px 55px rgba(15,23,42,0.65);
}
.tip-mod{
  font-size: 0.88rem;
  font-weight: 900;
  letter-spacing:-0.01em;
  margin-bottom: 4px;
}
.pill{
  display:inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.74rem;
  margin-right: 6px;
  border: 1px solid rgba(148,163,184,0.40);
  background: rgba(148,163,184,0.20);
  color: #e2e8f0;
}

/* ---------------- 模块卡片 ---------------- */
.module-card{
  background: #ffffff;
  padding: 10px 14px;
  border-radius: 16px;
  margin-bottom: 10px;
  border: 1px solid rgba(148,163,184,0.30);
  display:flex; justify-content:space-between; align-items:center;
  box-shadow: 0 10px 28px rgba(15,23,42,0.10);
}
.module-left{ display:flex; flex-direction:column; }
.module-name{ font-weight: 950; color:#0f172a; font-size: 0.95rem; letter-spacing:-0.01em; }
.module-meta{ font-size: 0.78rem; color:#64748b; margin-top: 2px; }
.module-right{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-weight: 950; font-size: 1.05rem; }

.bL-red{ border-left: 5px solid var(--red); background: #fff7f7; }
.bL-green{ border-left: 5px solid var(--green); background: #f1fff8; }
.bL-blue{ border-left: 5px solid var(--blue); background: #f4f8ff; }

/* ---------------- 输入 / 按钮 ---------------- */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea{
  border-radius: 14px !important;
}
div.stButton > button{
  border-radius: 14px !important;
  font-weight: 850 !important;
}
div.stButton > button[kind="primary"]{
  padding: 0.62rem 0.95rem !important;
}

/* ---------------- 图表间距 ---------------- */
div[data-testid="stPlotlyChart"]{ margin-top: -4px; }

/* ---------------- 表格 ---------------- */
[data-testid="stDataFrame"]{
  border-radius: 14px;
  overflow: hidden;
}

/* ---------------- 响应式（手机） ---------------- */
@media (max-width: 700px){
  .block-container{
    padding-top: 0.75rem !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
  }
  .hero{ padding: 14px 14px; border-radius: 18px; }
  .hero-title{ font-size: 1.18rem; }
  .hero-sub{ font-size: 0.90rem; }
  .card{ padding: 12px 12px; border-radius: 16px; }
  .kpi{ flex: 1 1 140px; padding: 10px 10px; }
  .kpi .v{ font-size: 1.18rem; }
  .module-card{ padding: 10px 12px; border-radius: 14px; }
  .module-name{ font-size: 0.92rem; }
  .module-right{ font-size: 1.0rem; }
  .mini-header{ font-size: 0.78rem; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* 顶部 KPI 卡片：改成白色浅色卡片 */
.card-dark{
  background: #ffffff;
  color: #0f172a;
  border: 1px solid rgba(148,163,184,0.25);
  box-shadow: 0 8px 24px rgba(15,23,42,0.10);
}

/* KPI 小块：浅色风格 */
.kpi{
  flex: 1 1 190px;
  border-radius: 16px;
  padding: 12px 12px;
  background: #ffffff;
  border: 1px solid rgba(148,163,184,0.25);
  box-shadow: 0 8px 22px rgba(15,23,42,0.06);
}
.kpi .k{
  font-size: 0.80rem;
  color: #64748b;
}
.kpi .v{
  font-size: 1.36rem;
  font-weight: 950;
  margin-top: 2px;
  letter-spacing: -0.02em;
}
.kpi .d{
  font-size: 0.78rem;
  color: #94a3b8;
  margin-top: 4px;
}

/* 复盘提示框：浅灰背景 + 阴影，不再是黑色 */
.tip-box{
  background: #f9fafb;
  color: #0f172a;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid rgba(148,163,184,0.25);
  margin: 10px 0;
  line-height: 1.48;
  font-size: 0.92rem;
  box-shadow: 0 6px 20px rgba(15,23,42,0.06);
}

/* 标签基础样式 */
.pill{
  display:inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.74rem;
  margin-right: 6px;
  font-weight: 600;
}

/* 短板 → 红色 */
.pill-short{
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

/* 可提升 → 蓝色 */
.pill-mid{
  background: #dbeafe;
  color: #1e3a8a;
  border: 1px solid #bfdbfe;
}

/* 强项 → 绿色 */
.pill-strong{
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

/* 超时 → 橙色 */
.pill-time{
  background: #ffedd5;
  color: #c2410c;
  border: 1px solid #fed7aa;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. 配置与模块结构
# =========================================================
USERS_FILE = "users_db.json"
FIXED_WEIGHT = 0.8           # 默认：省考 / 超格 每个对题0.8分
GOAL_SCORE = 75.0            # 目标分，可按需调整

# 模块结构：大模块 / 子模块
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
    "资料分析": {"type": "direct", "total": 20},
}

# 每个子模块推荐的计划用时（分钟）
PLAN_TIME = {
    "判断-图形推理": 6.0,
    "判断-类比推理": 5.0,
    "判断-逻辑判断": 10.0,
    "判断-定义判断": 6.0,
    "资料分析": 25.0,
    "数量关系": 25.0,
    "政治理论": 5.0,
    "常识判断": 5.0,
    "言语-逻辑填空": 5.0,
    "言语-片段阅读": 12.0,
}


# ================= 试卷题量与每题分值模板 =================
# 试卷题量 & 每题分值模板（录入成绩时选择）
PAPER_TEMPLATES = {
    # 省考试卷：125题，每题0.8
    "省考套题（125题，0.8分/题）": {
        "weight": FIXED_WEIGHT,
        "totals": {
            "政治理论": 15,
            "常识判断": 15,
            "言语-逻辑填空": 10,
            "言语-片段阅读": 15,
            "数量关系": 15,
            "判断-图形推理": 5,
            "判断-定义判断": 10,
            "判断-类比推理": 10,
            "判断-逻辑判断": 10,
            "资料分析": 20,
        },
    },

    # 花生套题：120题，每题0.85
    "花生套题（120题，0.85分/题）": {
        "weight": 0.85,
        "totals": {
            "政治理论": 15,
            "常识判断": 10,
            "言语-逻辑填空": 15,
            "言语-片段阅读": 15,
            "数量关系": 15,
            "判断-图形推理": 5,
            "判断-定义判断": 10,
            "判断-类比推理": 5,
            "判断-逻辑判断": 10,
            "资料分析": 20,
        },
    },

    # 超格套题：125题，每题0.8
    "超格套题（125题，0.8分/题）": {
        "weight": FIXED_WEIGHT,
        "totals": {
            "政治理论": 15,
            "常识判断": 15,
            "言语-逻辑填空": 10,
            "言语-片段阅读": 20,
            "数量关系": 15,
            "判断-图形推理": 5,
            "判断-定义判断": 10,
            "判断-类比推理": 5,
            "判断-逻辑判断": 10,
            "资料分析": 20,
        },
    },
}



# 默认策略：数量/资料/逻辑的时间上限等
DEFAULT_STRATEGY = {
    "数量_每题上限秒": 60,        # 数量：每题时间上限（秒）
    "资料_每篇上限分钟": 6,      # 资料：每篇时间上限（分钟）
    "逻辑_每题上限秒": 90,       # 逻辑判断：每题时间上限（秒）
    "数量_只做简单题": True,     # 数量是否只做简单题
    "资料_超时先跳": True,       # 资料是否超时先跳
    "复盘_统计天数": 30,        # 看板错因统计范围（天）
    "自定义策略备注": "",        # 用户自定义策略说明（长文本）
}

# 复盘记录表的列结构
REVIEW_SCHEMA = [
    "日期", "试卷", "模块", "错题数",
    "错因1_知识点不会", "错因2_方法不熟", "错因3_审题选项坑",
    "一句话原因", "下次做法"
]

# =========================================================
# 3. 工具函数：模块 / 文件 / 存储
# =========================================================
def get_leaf_modules() -> List[str]:
    """展开所有叶子模块（直接做题的粒度）"""
    leaves = []
    for k, v in MODULE_STRUCTURE.items():
        if v["type"] == "direct":
            leaves.append(k)
        else:
            leaves.extend(v["subs"].keys())
    return leaves

LEAF_MODULES = get_leaf_modules()


def hash_pw(pw: str) -> str:
    """简单的密码哈希（sha256）"""
    return hashlib.sha256(str(pw).encode()).hexdigest()


def data_file(un: str) -> str:
    """当前用户的成绩文件路径"""
    return f"data_storage_{un}.csv"


def review_file(un: str) -> str:
    """当前用户的复盘记录文件路径"""
    return f"review_notes_{un}.csv"


def strategy_file(un: str) -> str:
    """当前用户的策略配置文件路径"""
    return f"strategy_{un}.json"


def checkin_file(un: str) -> str:
    """当前用户的打卡记录文件路径"""
    return f"checkin_{un}.json"


def build_all_columns() -> List[str]:
    """构造成绩表需要的全部列"""
    cols = ["日期", "试卷", "总分", "总正确数", "总题数", "总用时"]
    for m in LEAF_MODULES:
        cols.extend([
            f"{m}_总题数", f"{m}_正确数", f"{m}_用时",
            f"{m}_正确率", f"{m}_计划用时"
        ])
    return cols


def ensure_schema(df: pd.DataFrame) -> pd.DataFrame:
    """保证成绩表 DataFrame 至少包含需要的所有列"""
    if df is None or df.empty:
        return pd.DataFrame(columns=build_all_columns())

    need = build_all_columns()
    for c in need:
        if c not in df.columns:
            df[c] = 0

    if "日期" in df.columns:
        try:
            df["日期"] = pd.to_datetime(df["日期"]).dt.date
        except Exception:
            pass

    num_cols = [
        c for c in df.columns
        if any(c.endswith(s) for s in ["_正确数", "_总题数", "_用时", "_正确率", "_计划用时"])
        or c in ["总分", "总正确数", "总题数", "总用时"]
    ]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df


def load_data(un: str) -> pd.DataFrame:
    """读取当前用户的成绩记录"""
    path = data_file(un)
    if os.path.exists(path):
        df = pd.read_csv(path, encoding="utf-8")
        return ensure_schema(df)
    return ensure_schema(pd.DataFrame())


def save_data(df: pd.DataFrame, un: str):
    """保存当前用户的成绩记录"""
    df = ensure_schema(df)
    df.to_csv(data_file(un), index=False, encoding="utf-8-sig")


def load_users() -> Dict:
    """加载用户数据库，不存在则创建默认 admin

    admin 初始密码从 Streamlit Secrets 中的 ADMIN_DEFAULT_PASSWORD 读取：
    - 本地开发：没有 secrets 时可以自行在本地创建 users_db.json
    - 云端部署：强烈建议在 Secrets 中设置一个复杂密码
    """
    if not os.path.exists(USERS_FILE):
        if ADMIN_DEFAULT_PASSWORD is None:
            # 没有用户文件、也没有在 secrets 中配置管理员密码时，直接报错，避免生成弱密码
            raise RuntimeError(
                "首次运行检测不到 users_db.json，且未配置 ADMIN_DEFAULT_PASSWORD。\n"
                "请在 Streamlit Cloud 的 Secrets 中设置 ADMIN_DEFAULT_PASSWORD，"
                "例如：ADMIN_DEFAULT_PASSWORD='一串很长且安全的密码'。\n"
                "本地开发如果嫌麻烦，也可以自己手动创建 users_db.json。"
            )
        d = {"admin": {"name": "管理员", "password": hash_pw(ADMIN_DEFAULT_PASSWORD), "role": "admin"}}
        save_users(d)
        return d
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(d: Dict):
    """保存用户数据库"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def load_reviews(un: str) -> pd.DataFrame:
    """读取当前用户的复盘记录"""
    path = review_file(un)
    if os.path.exists(path):
        rdf = pd.read_csv(path, encoding="utf-8")
        if "日期" in rdf.columns:
            try:
                rdf["日期"] = pd.to_datetime(rdf["日期"]).dt.date
            except Exception:
                pass
        for c in REVIEW_SCHEMA:
            if c not in rdf.columns:
                rdf[c] = ""
        return rdf[REVIEW_SCHEMA]
    return pd.DataFrame(columns=REVIEW_SCHEMA)


def save_reviews(rdf: pd.DataFrame, un: str):
    """保存当前用户的复盘记录"""
    for c in REVIEW_SCHEMA:
        if c not in rdf.columns:
            rdf[c] = ""
    rdf = rdf[REVIEW_SCHEMA]
    rdf.to_csv(review_file(un), index=False, encoding="utf-8-sig")


def load_strategy(un: str) -> Dict:
    """读取当前用户的策略配置"""
    path = strategy_file(un)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                s = json.load(f)
            # 补全默认 key
            for k, v in DEFAULT_STRATEGY.items():
                if k not in s:
                    s[k] = v
            return s
        except Exception:
            pass
    return dict(DEFAULT_STRATEGY)


def save_strategy(un: str, s: Dict):
    """保存当前用户策略"""
    with open(strategy_file(un), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


def load_checkin(un: str) -> Dict:
    """读取当前用户打卡信息"""
    path = checkin_file(un)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if "streak" not in d:
                d["streak"] = 0
            if "last_date" not in d:
                d["last_date"] = ""
            if "today_tasks" not in d:
                d["today_tasks"] = []
            if "today_tasks_source" not in d:
                d["today_tasks_source"] = "auto_week_plan"
            return d
        except Exception:
            pass
    return {"streak": 0, "last_date": "", "today_tasks_source": "auto_week_plan", "today_tasks": []}


def save_checkin(un: str, d: Dict):
    """保存当前用户打卡记录"""
    with open(checkin_file(un), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


# ================== 新增：导出/导入数据包 ==================
def export_user_bundle(un: str) -> bytes:
    """
    打包当前账号的全部数据文件为 zip，并返回二进制内容。
    包含：
    - records.csv   -> 成绩（data_storage_xxx.csv）
    - reviews.csv   -> 复盘（review_notes_xxx.csv）
    - strategy.json -> 策略
    - checkin.json  -> 打卡
    """
    mapping = {
        "records.csv": data_file(un),
        "reviews.csv": review_file(un),
        "strategy.json": strategy_file(un),
        "checkin.json": checkin_file(un),
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for arc_name, real_path in mapping.items():
            if os.path.exists(real_path):
                zf.write(real_path, arc_name)
    buf.seek(0)
    return buf.read()


def import_user_bundle(un: str, uploaded_file) -> Tuple[bool, str]:
    """
    从上传的 zip 中读取标准文件名，并写回当前账号：
    - records.csv   -> 成绩
    - reviews.csv   -> 复盘
    - strategy.json -> 策略
    - checkin.json  -> 打卡
    """
    try:
        data = uploaded_file.read()
        buf = io.BytesIO(data)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()
            # 成绩
            if "records.csv" in names:
                with zf.open("records.csv") as f:
                    df = pd.read_csv(f)
                df = ensure_schema(df)
                df.to_csv(data_file(un), index=False, encoding="utf-8-sig")
            # 复盘
            if "reviews.csv" in names:
                with zf.open("reviews.csv") as f:
                    rdf = pd.read_csv(f)
                for c in REVIEW_SCHEMA:
                    if c not in rdf.columns:
                        rdf[c] = ""
                rdf[REVIEW_SCHEMA].to_csv(review_file(un), index=False, encoding="utf-8-sig")
            # 策略
            if "strategy.json" in names:
                with zf.open("strategy.json") as f:
                    s = json.load(f)
                for k, v in DEFAULT_STRATEGY.items():
                    if k not in s:
                        s[k] = v
                with open(strategy_file(un), "w", encoding="utf-8") as sf:
                    json.dump(s, sf, ensure_ascii=False, indent=2)
            # 打卡
            if "checkin.json" in names:
                with zf.open("checkin.json") as f:
                    d = json.load(f)
                with open(checkin_file(un), "w", encoding="utf-8") as cf:
                    json.dump(d, cf, ensure_ascii=False, indent=2)
        return True, "数据导入成功！已覆盖当前账号的数据。"
    except Exception as e:
        return False, f"导入失败：{e}"


# =========================================================
# 4. UI 辅助函数 + 逻辑函数
# =========================================================
def status_class(acc: float) -> str:
    """根据正确率返回模块卡片颜色"""
    if acc >= 0.8:
        return "bL-green"
    if acc < 0.6:
        return "bL-red"
    return "bL-blue"


def render_module_card(
    name: str,
    correct: float,
    total: float,
    duration: float,
    acc: float,
    plan: float
) -> str:
    """单卷详情里的模块小卡片 HTML"""
    cls = status_class(acc)
    diff = duration - plan if plan else 0
    sign = "+" if diff > 0 else ""
    plan_txt = f" | 计划{int(plan)}m ({sign}{diff:.0f}m)" if plan else ""
    return f"""
    <div class="module-card {cls}">
        <div class="module-left">
            <div class="module-name">{name}</div>
            <div class="module-meta">{acc:.1%} | {int(duration)}min{plan_txt}</div>
        </div>
        <div class="module-right">{int(correct)}/{int(total)}</div>
    </div>
    """


def module_tip(m: str, acc: float, t: float, plan: float, strategy: Dict) -> str:
    """
    根据模块、正确率、用时和策略，生成一段『复盘建议文字 + 彩色标签』HTML。
    - 短板：红色 pill-short
    - 可提升：蓝色 pill-mid
    - 强项：绿色 pill-strong
    - 超时：橙色 pill-time
    """
    tips = []

    # 超时提示（橙色 pill）
    if plan and t > plan + 2:
        tips.append(
            f"<span class='pill pill-time'>超时</span>"
            f"用时 <b>{int(t)}m</b>，比计划 <b>+{int(t - plan)}m</b>。设置上限→超时先跳。"
        )

    # 正确率提示（红 / 蓝 / 绿）
    if acc < 0.6:
        tips.append(
            f"<span class='pill pill-short'>短板</span>"
            f"正确率 <b>{acc:.0%}</b>，错题拆三类：不会/不熟/审题坑，并只改一个做法。"
        )
    elif acc >= 0.8:
        tips.append(
            f"<span class='pill pill-strong'>强项</span>"
            f"正确率 <b>{acc:.0%}</b>，重点：提速 + 降低粗心。"
        )
    else:
        tips.append(
            f"<span class='pill pill-mid'>可提升</span>"
            f"正确率 <b>{acc:.0%}</b>，属于训练就能稳定涨的区间。"
        )

    # ====== 各模块专属做法（保持你原来的逻辑，只是接在新样式后） ======
    if m == "资料分析":
        per_block = int(strategy.get("资料_每篇上限分钟", 6))
        skip = bool(strategy.get("资料_超时先跳", True))
        skip_txt = "（超时先跳）" if skip else ""
        tips.append(
            f"做法：<b>每篇限时{per_block}分钟</b>{skip_txt}；"
            f"每天15分钟练<b>速算（增长率/基期/比重/平均）</b>。"
        )
    elif m == "数量关系":
        sec = int(strategy.get("数量_每题上限秒", 60))
        easy_only = bool(strategy.get("数量_只做简单题", True))
        easy_txt = "（只做简单题）" if easy_only else ""
        tips.append(
            f"做法：<b>每题{sec}秒上限</b>{easy_txt}；"
            f"只保留你最稳的<b>3类题型</b>训练，其余秒放。"
        )
    elif m in ["言语-逻辑填空", "言语-片段阅读"]:
        tips.append(
            "做法：每天20题专项；错题只写一句："
            "<b>语境/搭配/转折因果关键词</b>，下次遇坑能秒避。"
        )
    elif m in ["政治理论", "常识判断"]:
        tips.append(
            "做法：每天10分钟刷题；错题压成<b>1行卡片关键词</b>（法条/时政点）。"
        )
    elif m == "判断-逻辑判断":
        sec = int(strategy.get("逻辑_每题上限秒", 90))
        tips.append(
            f"做法：设置<b>{sec}秒上限</b>；难题先跳，优先稳图推/类比/定义。"
        )
    elif m.startswith("判断-"):
        tips.append(
            "做法：图推/类比/定义优先稳分；复杂题设置上限，超过先跳。"
        )

    return "<div class='tip-box'>" + "<br>".join(tips) + "</div>"

def compute_summary(df: pd.DataFrame):
    """返回最新一套卷的 summary 信息"""
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None
    delta = float(latest["总分"]) - float(prev["总分"]) if prev is not None else None
    acc = float(latest["总正确数"]) / max(float(latest["总题数"]), 1)
    return latest, delta, acc


def compute_next_day_plan(row: pd.Series, strategy: Dict):
    """基于单卷 row + 策略，生成“明天怎么练”的 3 条建议"""
    items = []
    for m in LEAF_MODULES:
        acc = float(row.get(f"{m}_正确率", 0))
        t = float(row.get(f"{m}_用时", 0))
        plan = float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
        diff = t - plan if plan else 0
        items.append((m, acc, diff))

    worst_acc = sorted(items, key=lambda x: x[1])[0]
    worst_time = sorted(items, key=lambda x: x[2], reverse=True)[0]

    tasks = [
        "资料分析：15分钟限时速算（增长率/基期/比重/平均数），目标“更快不更错”。",
        "言语理解：逻辑填空20题（每题标注：语境/搭配/转折因果关键词）。",
    ]

    if worst_acc[0] == "数量关系" or worst_time[0] == "数量关系":
        sec = int(strategy.get("数量_每题上限秒", 60))
        tasks.append(f"数量关系：只练你最稳的1个题型10题 + 每题{sec}秒上限；其余题型放弃训练。")
    else:
        tasks.append(f"短板专项：{worst_acc[0]} 10-20题（只做同一类型，做到“看见就会”）。")

    return tasks, worst_acc, worst_time


def build_week_plan(df: pd.DataFrame, strategy: Dict) -> List[Dict]:
    """根据最近三套卷，构造一周训练计划（每天固定 3 件事）"""
    if df.empty:
        return []

    recent = df.tail(3)
    acc_scores = {m: [] for m in LEAF_MODULES}
    time_over = {m: [] for m in LEAF_MODULES}

    for _, row in recent.iterrows():
        for m in LEAF_MODULES:
            acc_scores[m].append(float(row.get(f"{m}_正确率", 0)))
            plan = float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
            t = float(row.get(f"{m}_用时", 0))
            time_over[m].append((t - plan) if plan else 0)

    avg_acc = {m: sum(v) / max(len(v), 1) for m, v in acc_scores.items()}
    avg_over = {m: sum(v) / max(len(v), 1) for m, v in time_over.items()}

    worst_acc_mods = [x[0] for x in sorted(avg_acc.items(), key=lambda x: x[1])[:3]]
    worst_over_mods = [x[0] for x in sorted(avg_over.items(), key=lambda x: x[1], reverse=True)[:2]]

    focus_list = list(dict.fromkeys(worst_acc_mods + worst_over_mods))
    if not focus_list:
        focus_list = ["言语-逻辑填空"]

    sec = int(strategy.get("数量_每题上限秒", 60))
    block = int(strategy.get("资料_每篇上限分钟", 6))
    logic_sec = int(strategy.get("逻辑_每题上限秒", 90))

    plan = []
    for i in range(7):
        focus = focus_list[i % len(focus_list)]
        day = (datetime.now().date() + timedelta(days=i)).isoformat()

        base = [
            "资料分析：15分钟速算训练（增长率/基期/比重/平均数）",
            "言语：逻辑填空20题（错因标注：语境/搭配/转折因果）",
        ]

        if focus == "数量关系":
            base.append(f"数量：保留题型10题 + 每题{sec}秒上限（其余秒放）")
        elif focus == "资料分析":
            base.append(f"资料：做2篇限时（每篇{block}分钟，上限跳题）")
        elif focus == "判断-逻辑判断":
            base.append(f"逻辑判断：10题，单题{logic_sec}秒上限，难题先跳")
        else:
            base.append(f"专项：{focus} 10-20题（只做同一类型）")

        plan.append({"日期": day, "重点模块": focus, "任务": base})
    return plan


def get_today_tasks_from_week_plan(week_plan: List[Dict]) -> List[Dict]:
    """从周计划中抽取“今天任务”"""
    today = datetime.now().date().isoformat()
    for d in week_plan:
        if d["日期"] == today:
            return [{"title": t, "done": False} for t in d["任务"]]
    if week_plan:
        return [{"title": t, "done": False} for t in week_plan[0]["任务"]]
    return []


def update_streak(checkin: Dict):
    """
    streak 规则：
    - 若今天完成所有任务 → streak +1（与昨天连续则+1，否则重置为1）
    - 若没完成，不变
    """
    today = datetime.now().date()
    today_str = today.isoformat()

    tasks = checkin.get("today_tasks", [])
    if not tasks:
        return checkin

    all_done = all(bool(x.get("done", False)) for x in tasks)
    if not all_done:
        return checkin

    last = checkin.get("last_date", "")
    if last:
        try:
            last_d = datetime.fromisoformat(last).date()
        except Exception:
            last_d = None
    else:
        last_d = None

    if last_d is None:
        checkin["streak"] = 1
    else:
        if (today - last_d).days == 1:
            checkin["streak"] = int(checkin.get("streak", 0)) + 1
        elif (today - last_d).days == 0:
            checkin["streak"] = int(checkin.get("streak", 0))
        else:
            checkin["streak"] = 1

    checkin["last_date"] = today_str
    return checkin


def review_analytics(rdf: pd.DataFrame, days: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    返回：
    - 错因汇总（不会/不熟/审题坑）
    - 模块错题数 Top
    """
    if rdf.empty:
        return pd.DataFrame(), pd.DataFrame()
    cutoff = datetime.now().date() - timedelta(days=days)
    x = rdf.copy()
    try:
        x["日期"] = pd.to_datetime(x["日期"]).dt.date
    except Exception:
        pass
    x = x[x["日期"] >= cutoff]

    if x.empty:
        return pd.DataFrame(), pd.DataFrame()

    cause = pd.DataFrame([{
        "错因": "不会", "数量": pd.to_numeric(x["错因1_知识点不会"], errors="coerce").fillna(0).sum()
    }, {
        "错因": "不熟", "数量": pd.to_numeric(x["错因2_方法不熟"], errors="coerce").fillna(0).sum()
    }, {
        "错因": "审题坑", "数量": pd.to_numeric(x["错因3_审题选项坑"], errors="coerce").fillna(0).sum()
    }])

    mod = x.copy()
    mod["错题数"] = pd.to_numeric(mod["错题数"], errors="coerce").fillna(0)
    mod_sum = mod.groupby("模块", as_index=False)["错题数"].sum().sort_values("错题数", ascending=False).head(10)

    return cause, mod_sum


# =========================================================
# 5. 登录逻辑
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("""
        <div class="hero">
          <div class="hero-title">🚀 行测 Pro Max</div>
          <div class="hero-sub">
            把“模考”变成可复制的提分流程：<b>看板 → 复盘 → 做法 → 训练计划</b><br>
            不再纠结做几套卷，而是每套卷都能换成稳定的分数。
          </div>
          <div class="hero-badges">
            <div class="badge">🧠 复盘四步法</div>
            <div class="badge">⏱️ 时间黑洞定位</div>
            <div class="badge">🗓️ 一键周计划</div>
            <div class="badge">✅ 今日任务打卡</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔑 登录", "📝 快速注册"])
        with t1:
            u = st.text_input("账号", key="l_u")
            p = st.text_input("密码", type="password", key="l_p")
            if st.button("进入系统", type="primary", use_container_width=True):
                users = load_users()
                if u in users and users[u]["password"] == hash_pw(p):
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
                    st.success("注册成功！请切回登录。")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================================================
# 6. 主体加载
# =========================================================
un = st.session_state.u_info["un"]
role = st.session_state.u_info["role"]
df = load_data(un)
rdf = load_reviews(un)
strategy = load_strategy(un)
checkin = load_checkin(un)

# 侧边栏
with st.sidebar:
    st.markdown(f"<div class='sidebar-title'>👋 Hi, {st.session_state.u_info['name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sidebar-sub'>连续打卡：<b>{int(checkin.get('streak',0))}</b> 天</div>", unsafe_allow_html=True)
    st.caption("行测复盘系统 · 提分靠流程")

    menu = st.radio(
        "功能导航",
        [
            "🏠 数字化看板",
            "📑 单卷详情",
            "🧠 复盘记录",
            "✅ 今日任务",
            "⏱️ 做题计时器",          
            "🗓️ 本周训练计划",
            "📊 趋势分析",
            "✏️ 录入成绩",
            "⚙️ 数据管理",
            "📂 数据备份 / 迁移",
            "⚙️ 策略设置",
        ] + (["🛡️ 管理后台"] if role == "admin" else [])
    )

    st.markdown("---")
    if st.button("安全退出", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# =========================================================
# 7. 各页面
# =========================================================
# ------------------- 数字化看板 -------------------
if menu == "🏠 数字化看板":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">📊 数字化看板</div>
      <div class="hero-sub">只盯两件事：<b>稳定得分</b> + <b>控制时间</b>。系统会自动定位短板与时间黑洞。</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("👋 你还没有录入任何模考。先去【✏️ 录入成绩】录一套，系统会自动生成复盘建议。")
    else:
        latest, delta, acc = compute_summary(df)
        delta_txt = f"较上次 {delta:+.1f}" if delta is not None else "首套记录"

        st.markdown(f"""
        <div class="card card-dark">
          <div class="kpi-wrap">
            <div class="kpi">
              <div class="k">最新得分</div>
              <div class="v">{float(latest['总分']):.1f}</div>
              <div class="d">{delta_txt}</div>
            </div>
            <div class="kpi">
              <div class="k">正确率</div>
              <div class="v">{acc:.0%}</div>
              <div class="d">总正确 {int(latest['总正确数'])}/{int(latest['总题数'])}</div>
            </div>
            <div class="kpi">
              <div class="k">总用时</div>
              <div class="v">{int(latest['总用时'])}m</div>
              <div class="d">效率 {float(latest['总分'])/max(float(latest['总用时']),1):.2f} 分/min</div>
            </div>
            <div class="kpi">
              <div class="k">近5次均分</div>
              <div class="v">{df.tail(5)['总分'].mean():.1f}</div>
              <div class="d">累计套数 {len(df)}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # 自动复盘一眼看：最低正确率 & 最大超时
        stats = []
        for m in LEAF_MODULES:
            accm = float(latest.get(f"{m}_正确率", 0))
            t = float(latest.get(f"{m}_用时", 0))
            plan = float(latest.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
            stats.append((m, accm, (t-plan) if plan else 0))
        worst_acc = sorted(stats, key=lambda x: x[1])[0]
        worst_time = sorted(stats, key=lambda x: x[2], reverse=True)[0]

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.warning(f"🎯 当前短板：{worst_acc[0]}（正确率 {worst_acc[1]:.0%}）")
        with c2:
            st.warning(f"⏱️ 时间黑洞：{worst_time[0]}（超时 {worst_time[2]:.0f} 分钟）")
        st.markdown("</div>", unsafe_allow_html=True)

        # 图表
        col_l, col_r = st.columns([1, 1.25])
        with col_l:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>能力雷达</div>", unsafe_allow_html=True)
            fig = go.Figure(go.Scatterpolar(
                r=[float(latest.get(f"{m}_正确率", 0)) for m in LEAF_MODULES],
                theta=LEAF_MODULES, fill="toself"
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9))),
                height=350, margin=dict(t=20, b=10, l=30, r=30)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>分数稳定性</div>", unsafe_allow_html=True)
            fig_hist = px.histogram(df, x="总分", nbins=10)
            fig_hist.update_layout(height=350, margin=dict(t=10, b=10), xaxis_title="分数区间", yaxis_title="次数")
            st.plotly_chart(fig_hist, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # 复盘错因统计（过去N天）
        days = int(strategy.get("复盘_统计天数", 30))
        cause_df, mod_df = review_analytics(rdf, days)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='mini-header'>复盘错因统计（近 {days} 天）</div>", unsafe_allow_html=True)
        if cause_df.empty:
            st.caption("暂无复盘记录。去【🧠 复盘记录】填几条，系统会自动画图。")
        else:
            cc1, cc2 = st.columns([1, 1.15])
            with cc1:
                figc = px.pie(cause_df, values="数量", names="错因", hole=0.45)
                figc.update_layout(height=320, margin=dict(t=10, b=10))
                st.plotly_chart(figc, use_container_width=True)
            with cc2:
                figm = px.bar(mod_df, x="错题数", y="模块", orientation="h")
                figm.update_layout(height=320, margin=dict(t=10, b=10))
                st.plotly_chart(figm, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------- 单卷详情 -------------------
elif menu == "📑 单卷详情":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">📑 单卷详情</div>
      <div class="hero-sub">系统自动输出：<b>短板 Top3</b>、<b>超时 Top3</b>、<b>每模块 1 个做法</b>、<b>明天训练 3 条</b></div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("暂无数据。先去【录入成绩】。")
    else:

        # =============== 选择试卷 ===============
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择历史模考", sel_list)
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]

        # =============== 顶部汇总 ===============
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("得分", f"{float(row['总分']):.1f}")
        c2.metric("正确率", f"{float(row['总正确数'])/max(float(row['总题数']),1):.1%}")
        c3.metric("总用时", f"{int(row['总用时'])} min")
        c4.metric("效率", f"{float(row['总分'])/max(float(row['总用时']),1):.2f} 分/min")
        st.markdown("</div>", unsafe_allow_html=True)

        # =============== 计算模块表现 ===============
        stats = []
        for m in LEAF_MODULES:
            accm = float(row.get(f"{m}_正确率", 0))
            t = float(row.get(f"{m}_用时", 0))
            plan = float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
            total = float(row.get(f"{m}_总题数", 0))
            diff = (t - plan) if plan else 0
            stats.append((m, accm, t, plan, total, diff))

        worst_by_acc = sorted(stats, key=lambda x: x[1])[:3]
        worst_by_time = sorted(stats, key=lambda x: x[5], reverse=True)[:3]

        # =============== 左右两栏 Top3 ===============
        left, right = st.columns(2)

        # ------- 左：正确率最低 -------
        with left:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>正确率最低 Top3</div>", unsafe_allow_html=True)

            for m, accm, t, plan, total, diff in worst_by_acc:
                st.markdown(
                    f"""
                    <div style='font-weight:700;
                                margin-top:8px;
                                margin-bottom:4px;
                                color:#0f172a;
                                font-size:0.93rem;'>
                        {m} ｜ 正确率 {accm:.0%} ｜ 用时 {int(t)}min
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(module_tip(m, accm, t, plan, strategy), unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ------- 右：超时最多 -------
        with right:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>超时最多 Top3</div>", unsafe_allow_html=True)

            for m, accm, t, plan, total, diff in worst_by_time:
                st.markdown(
                    f"""
                    <div style='font-weight:700;
                                margin-top:8px;
                                margin-bottom:4px;
                                color:#0f172a;
                                font-size:0.93rem;'>
                        {m} ｜ 正确率 {accm:.0%} ｜ 用时 {int(t)}min ｜ 超时 {diff:.0f}min
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(module_tip(m, accm, t, plan, strategy), unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # =============== 关键：下面这一行必须放在 “with left/right” 之后！ ===============
        tasks, worst_acc, worst_time = compute_next_day_plan(row, strategy)

        # =============== 明天怎么练 ===============
        st.markdown("<div class='card'>", unsafe_allow_html=True)
   

        st.markdown(f"""
        <ol style="margin: 0 0 0 18px;">

        <div class='small-muted' style='margin-top:10px;'>
            重点短板：<b>{worst_acc[0]}</b>（正确率 {worst_acc[1]:.0%}）；
            时间黑洞：<b>{worst_time[0]}</b>（超时 {worst_time[2]:.0f} 分钟）
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 模块卡片（3 列：政治常识言语 / 数量资料 / 判断）
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>政治 / 常识 / 言语</div>", unsafe_allow_html=True)
            for m in ["政治理论", "常识判断", "言语-逻辑填空", "言语-片段阅读"]:
                st.markdown(render_module_card(
                    m,
                    row.get(f"{m}_正确数", 0), row.get(f"{m}_总题数", 0),
                    row.get(f"{m}_用时", 0), row.get(f"{m}_正确率", 0),
                    float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
                ), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>数量 / 资料</div>", unsafe_allow_html=True)
            for m in ["数量关系", "资料分析"]:
                st.markdown(render_module_card(
                    m,
                    row.get(f"{m}_正确数", 0), row.get(f"{m}_总题数", 0),
                    row.get(f"{m}_用时", 0), row.get(f"{m}_正确率", 0),
                    float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
                ), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>判断推理</div>", unsafe_allow_html=True)
            for m in ["判断-图形推理", "判断-定义判断", "判断-类比推理", "判断-逻辑判断"]:
                st.markdown(render_module_card(
                    m,
                    row.get(f"{m}_正确数", 0), row.get(f"{m}_总题数", 0),
                    row.get(f"{m}_用时", 0), row.get(f"{m}_正确率", 0),
                    float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
                ), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # 导出当前卷复盘摘要，方便复制到笔记
        with st.expander("📤 导出本卷复盘摘要（复制到笔记）", expanded=False):
            md = []
            md.append(f"### {row['日期']} | {row['试卷']}")
            md.append(f"- 得分：{float(row['总分']):.1f} | 正确率：{float(row['总正确数'])/max(float(row['总题数']),1):.1%} | 用时：{int(row['总用时'])}min")
            md.append(f"- 明天训练：1）{tasks[0]}  2）{tasks[1]}  3）{tasks[2]}")
            md.append("")
            md.append("**模块Top问题（自动）**")
            md.append(f"- 正确率最低：{', '.join([x[0] for x in worst_by_acc])}")
            md.append(f"- 超时最多：{', '.join([x[0] for x in worst_by_time])}")
            st.code("\n".join(md), language="markdown")

# ------------------- 复盘记录 -------------------
elif menu == "🧠 复盘记录":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">🧠 复盘记录</div>
      <div class="hero-sub">每套卷只做一件事：把错题归因为<b>不会 / 不熟 / 审题坑</b>，并写<b>下次只改1个做法</b>。</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("你还没录入套卷，先去【✏️ 录入成绩】。")
    else:
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择要复盘的套卷", sel_list)
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]

        # 系统建议优先复盘的模块
        stats = []
        for m in LEAF_MODULES:
            accm = float(row.get(f"{m}_正确率", 0))
            t = float(row.get(f"{m}_用时", 0))
            plan = float(row.get(f"{m}_计划用时", PLAN_TIME.get(m, 0)))
            stats.append((m, accm, (t - plan) if plan else 0))

        pick = []
        pick += [x[0] for x in sorted(stats, key=lambda x: x[1])[:4]]
        pick += [x[0] for x in sorted(stats, key=lambda x: x[2], reverse=True)[:2]]
        pick = list(dict.fromkeys(pick))

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.info(f"系统建议你优先复盘：{ '、'.join(pick) }（先解决最影响提分/时间的部分）")
        st.caption("错因三类要可执行：不会=知识缺；不熟=套路/速算；审题坑=关键词/单位/基期现期。")
        st.markdown("</div>", unsafe_allow_html=True)

        # 复盘表单
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.form("review_form"):
            date = row["日期"]
            paper = row["试卷"]
            chosen = st.multiselect("选择要记录复盘的模块", LEAF_MODULES, default=pick)

            for m in chosen:
                st.markdown(f"---\n### {m}")
                total = int(row.get(f"{m}_总题数", 0))
                correct = int(row.get(f"{m}_正确数", 0))
                wrong = max(total - correct, 0)

                c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                with c1:
                    st.number_input("错题数", 0, 999, wrong, key=f"w_{m}")
                with c2:
                    st.number_input("不会", 0, 999, 0, key=f"e1_{m}")
                with c3:
                    st.number_input("不熟", 0, 999, 0, key=f"e2_{m}")
                with c4:
                    st.number_input("审题坑", 0, 999, 0, key=f"e3_{m}")

                st.text_input("一句话原因", key=f"r_{m}", placeholder="例：基期现期看反 / 转折句没抓 / 速算失误")
                st.text_input("下次做法（只写1个）", key=f"a_{m}", placeholder="例：资料每篇6分钟上限；数量每题60秒上限；填空每天20题")

            submit = st.form_submit_button("💾 保存本卷复盘记录", type="primary", use_container_width=True)
            if submit:
                rows = []
                for m in chosen:
                    rows.append({
                        "日期": date,
                        "试卷": paper,
                        "模块": m,
                        "错题数": int(st.session_state.get(f"w_{m}", 0)),
                        "错因1_知识点不会": int(st.session_state.get(f"e1_{m}", 0)),
                        "错因2_方法不熟": int(st.session_state.get(f"e2_{m}", 0)),
                        "错因3_审题选项坑": int(st.session_state.get(f"e3_{m}", 0)),
                        "一句话原因": st.session_state.get(f"r_{m}", ""),
                        "下次做法": st.session_state.get(f"a_{m}", ""),
                    })
                rdf2 = pd.concat([rdf, pd.DataFrame(rows)], ignore_index=True)
                save_reviews(rdf2, un)
                st.success("已保存！以后复习只看“下次做法”。")
                time.sleep(0.7)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # 历史复盘库
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='mini-header'>📚 历史复盘库</div>", unsafe_allow_html=True)
        if rdf.empty:
            st.caption("还没有复盘记录。")
        else:
            f1, f2, f3 = st.columns([1, 1, 2])
            with f1:
                f_paper = st.selectbox("按试卷筛选", ["全部"] + sorted(rdf["试卷"].dropna().astype(str).unique().tolist()))
            with f2:
                f_mod = st.selectbox("按模块筛选", ["全部"] + LEAF_MODULES)
            with f3:
                keyword = st.text_input("关键词搜索（原因/做法）", placeholder="例：基期、速算、转折、60秒…")

            view = rdf.copy()
            if f_paper != "全部":
                view = view[view["试卷"].astype(str) == f_paper]
            if f_mod != "全部":
                view = view[view["模块"].astype(str) == f_mod]
            if keyword.strip():
                k = keyword.strip()
                view = view[
                    view["一句话原因"].astype(str).str.contains(k, na=False) |
                    view["下次做法"].astype(str).str.contains(k, na=False)
                ]
            st.dataframe(view.sort_values(["日期", "试卷", "模块"], ascending=[False, False, True]),
                         use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------- 今日任务（可编辑） -------------------
elif menu == "✅ 今日任务":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">✅ 今日任务</div>
      <div class="hero-sub">把训练做成“可打卡”的流程：完成=连续天数 +1。默认来自本周计划，也可以自己改。</div>
    </div>
    """, unsafe_allow_html=True)

    wp = build_week_plan(df, strategy) if not df.empty else []
    today_str = datetime.now().date().isoformat()

    # 如果还没生成今日任务，或日期变化，则刷新为自动周计划
    if (not checkin.get("today_tasks")) or (checkin.get("today_tasks_date") != today_str):
        checkin["today_tasks"] = get_today_tasks_from_week_plan(wp)
        checkin["today_tasks_source"] = "auto_week_plan"
        checkin["today_tasks_date"] = today_str
        save_checkin(un, checkin)

    # 今日清单卡片
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-header'>今日清单</div>", unsafe_allow_html=True)
    st.caption(f"日期：{today_str}｜来源：{checkin.get('today_tasks_source','auto_week_plan')}｜连续打卡：{int(checkin.get('streak',0))} 天")

    tasks = checkin.get("today_tasks", [])
    if not tasks:
        st.info("暂无任务。先录入成绩生成周计划，或在下方自定义任务。")
    else:
        # 支持直接编辑任务文字 + 勾选完成状态
        new_tasks = []
        for i, t in enumerate(tasks):
            col1, col2 = st.columns([0.12, 0.88])
            with col1:
                done_now = st.checkbox(
                    "",
                    value=bool(t.get("done", False)),
                    key=f"task_done_{i}"
                )
            with col2:
                title_now = st.text_input(
                    "",
                    value=t.get("title", ""),
                    key=f"task_title_{i}",
                    label_visibility="collapsed",
                    placeholder="输入任务内容，例如：资料分析2篇（每篇6分钟上限）"
                )
            new_tasks.append({"title": title_now, "done": done_now})

        if st.button("💾 保存打卡", type="primary", use_container_width=True):
            checkin["today_tasks"] = new_tasks
            checkin = update_streak(checkin)
            save_checkin(un, checkin)
            st.success(f"已保存！当前连续打卡：{int(checkin.get('streak',0))} 天")
            time.sleep(0.6)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 自定义任务
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-header'>自定义任务</div>", unsafe_allow_html=True)
    new_task = st.text_input("新增一条任务", placeholder="例：资料分析2篇（每篇6分钟上限）")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("➕ 添加到今日清单", use_container_width=True):
            if new_task.strip():
                checkin["today_tasks"].append({"title": new_task.strip(), "done": False})
                checkin["today_tasks_source"] = "custom"
                checkin["today_tasks_date"] = today_str
                save_checkin(un, checkin)
                st.success("已添加")
                time.sleep(0.4)
                st.rerun()
    with c2:
        if st.button("🧹 清空今日清单", use_container_width=True):
            checkin["today_tasks"] = []
            save_checkin(un, checkin)
            st.success("已清空")
            time.sleep(0.4)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
# ------------------- 做题计时器 -------------------
elif menu == "⏱️ 做题计时器":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">⏱️ 做题计时器</div>
      <div class="hero-sub">
        按照你本场的做题顺序，系统帮你：<b>实时正计时</b>，并对照<b>各模块计划用时</b>，防止前面做嗨了后面时间崩盘。
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ============ Flip Clock 风格 CSS，模拟翻页钟视觉 ============
    flip_css = """
    <style>
    .flip-clock-wrapper {
        display:flex;
        gap:12px;
        justify-content:center;
        align-items:center;
    }
    .flip-card {
        background:#000;
        border-radius:16px;
        box-shadow:0 16px 40px rgba(0,0,0,0.7);
        padding:8px 10px;
    }
    .flip-card-inner {
        position:relative;
        color:#f5f5f5;
        font-family:"SF Mono","Consolas","Menlo",monospace;
        font-weight:800;
        display:flex;
        justify-content:center;
        align-items:center;
        padding:0 22px;
    }
    /* 中间分割线：模拟上下两半的翻页 */
    .flip-card-inner::before {
        content:"";
        position:absolute;
        left:0;
        right:0;
        top:50%;
        height:1px;
        background:rgba(255,255,255,0.22);
    }
    /* 简单的上下明暗渐变，增加“翻页块”质感 */
    .flip-card-inner::after {
        content:"";
        position:absolute;
        left:0;
        right:0;
        top:0;
        bottom:0;
        background:linear-gradient(
            to bottom,
            rgba(255,255,255,0.10),
            transparent 46%,
            transparent 54%,
            rgba(0,0,0,0.45)
        );
        border-radius:16px;
        opacity:0.9;
        pointer-events:none;
    }
    .flip-digit-large { font-size:90px; }
    .flip-digit-xlarge { font-size:150px; }
    .flip-separator {
        color:#f5f5f5;
        font-family:"SF Mono","Consolas","Menlo",monospace;
        font-weight:800;
        margin:0 4px;
    }
    .flip-separator-large { font-size:90px; }
    .flip-separator-xlarge { font-size:150px; }
    </style>
    """
    st.markdown(flip_css, unsafe_allow_html=True)

    # 1）整理所有“叶子模块”（实际做题粒度）
    leaf_modules = []
    for m, cfg in MODULE_STRUCTURE.items():
        if cfg["type"] == "direct":
            leaf_modules.append(m)
        else:
            leaf_modules.extend(list(cfg["subs"].keys()))

    # 你的默认顺序（可自改）
    default_order = [
        "判断-图形推理",
        "判断-类比推理",
        "判断-逻辑判断",
        "判断-定义判断",
        "资料分析",
        "数量关系",
        "政治理论",
        "常识判断",
        "言语-逻辑填空",
        "言语-片段阅读",
    ]
    default_order = [m for m in default_order if m in leaf_modules]

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # ① 选择做题顺序
    st.markdown("#### ① 选择本套卷的做题顺序")
    st.caption("按你计划的顺序依次点选模块（多选框会按点击顺序记住顺序）。")

    order = st.multiselect(
        "做题顺序（点击顺序 = 实际顺序）",
        options=leaf_modules,
        default=default_order,
        key="timer_order_modules",
    )

    if not order:
        st.info("先从上面的多选框里选出本套卷的做题顺序。")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        import pandas as _pd

        # 如果顺序变化了，重置计次相关状态，避免错位
        if "timer_order_snapshot" not in st.session_state:
            st.session_state.timer_order_snapshot = order
        elif st.session_state.timer_order_snapshot != order:
            st.session_state.timer_order_snapshot = order
            st.session_state.timer_lap_index = 0
            st.session_state.timer_lap_data = {}
            st.session_state.timer_last_lap_total_sec = 0.0
            st.session_state.timer_running = False
            st.session_state.timer_start_ts = None
            st.session_state.timer_elapsed_sec = 0.0

        # ② 各模块计划用时（可修改）—— 用 expander 可折叠
        with st.expander("② 各模块计划用时（可手动修改）", expanded=True):
            st.caption("默认值来自 PLAN_TIME，你可以根据本场卷子的难度和感觉微调。")

            plan_rows = []
            total_plan_min = 0.0

            for idx, name in enumerate(order, start=1):
                cols = st.columns([1, 3, 2])

                with cols[0]:
                    st.markdown(f"**{idx}**")
                with cols[1]:
                    st.markdown(name)
                default_plan = float(PLAN_TIME.get(name, 5))
                with cols[2]:
                    plan_min = st.number_input(
                        "计划min",
                        min_value=0.0,
                        max_value=200.0,
                        value=default_plan,
                        step=0.5,
                        key=f"timer_plan_{name}",
                        label_visibility="collapsed",
                    )
                total_plan_min += plan_min
                plan_rows.append(
                    {"顺序": idx, "模块": name, "计划用时(min)": plan_min}
                )

            cum = 0.0
            for row in plan_rows:
                cum += row["计划用时(min)"]
                row["累计至此(min)"] = cum

            plan_df = _pd.DataFrame(plan_rows)
            st.caption(
                f"按当前设置，这套卷按照计划做完大约需要 **{total_plan_min:.1f} 分钟**。"
            )
            st.dataframe(plan_df, use_container_width=True, hide_index=True)

        # ---------- 初始化计次数据 ----------
        if "timer_lap_index" not in st.session_state:
            st.session_state.timer_lap_index = 0  # 当前要记录的模块索引
        if "timer_lap_data" not in st.session_state:
            st.session_state.timer_lap_data = {}  # 模块 -> 秒
        if "timer_last_lap_total_sec" not in st.session_state:
            st.session_state.timer_last_lap_total_sec = 0.0

        # 专注模式：只显示翻页计时器 + 控制按钮
        focus_mode = st.checkbox(
            "🔍 专注模式：只显示翻页计时器和控制按钮（适合做题时使用）",
            value=False,
        )

        # ---------- 初始化计时器状态 ----------
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
        if "timer_start_ts" not in st.session_state:
            st.session_state.timer_start_ts = None
        if "timer_elapsed_sec" not in st.session_state:
            st.session_state.timer_elapsed_sec = 0.0

        # 控制按钮：开始 / 暂停 / 重置 / 计次
        c1, c2, c3, c4 = st.columns(4)
        start_clicked = c1.button("▶️ 开始 / 继续", use_container_width=True)
        pause_clicked = c2.button("⏸️ 暂停", use_container_width=True)
        reset_clicked = c3.button("⏹️ 重置计时", use_container_width=True)
        lap_clicked = c4.button("✅ 本模块完成 / 记录用时", use_container_width=True)

        now_ts = time.time()

        # 开始 / 继续
        if start_clicked:
            if not st.session_state.timer_running:
                st.session_state.timer_running = True
                st.session_state.timer_start_ts = now_ts

        # 暂停
        if pause_clicked and st.session_state.timer_running:
            st.session_state.timer_running = False
            if st.session_state.timer_start_ts is not None:
                st.session_state.timer_elapsed_sec += (
                    now_ts - st.session_state.timer_start_ts
                )
                st.session_state.timer_start_ts = None

        # 重置
        if reset_clicked:
            st.session_state.timer_running = False
            st.session_state.timer_start_ts = None
            st.session_state.timer_elapsed_sec = 0.0
            st.session_state.timer_last_lap_total_sec = 0.0
            st.session_state.timer_lap_index = 0
            st.session_state.timer_lap_data = {}

        # 当前总用时（秒）
        elapsed = st.session_state.timer_elapsed_sec
        if st.session_state.timer_running and st.session_state.timer_start_ts is not None:
            elapsed += now_ts - st.session_state.timer_start_ts

        # 计次：记录当前模块用时（按顺序依次记录）
        if lap_clicked:
            current_idx = st.session_state.timer_lap_index
            if current_idx < len(order):
                module_name = order[current_idx]
                last_total = st.session_state.timer_last_lap_total_sec
                lap_dur = max(0.0, elapsed - last_total)
                st.session_state.timer_lap_data[module_name] = lap_dur
                st.session_state.timer_last_lap_total_sec = elapsed
                st.session_state.timer_lap_index = current_idx + 1

        # ---------- 生成“计划 vs 实际”表 ----------
        rows_for_show = []
        for row in plan_rows:
            name = row["模块"]
            plan_min = row["计划用时(min)"]
            act_sec = st.session_state.timer_lap_data.get(name)
            if act_sec is not None:
                act_min = act_sec / 60.0
                diff = act_min - plan_min
            else:
                act_min = None
                diff = None
            rows_for_show.append(
                {
                    "顺序": row["顺序"],
                    "模块": name,
                    "计划用时(min)": plan_min,
                    "实际用时(min)": None if act_min is None else round(act_min, 1),
                    "偏差(min)": None if diff is None else round(diff, 1),
                }
            )
        actual_df = _pd.DataFrame(rows_for_show)

        # ---------- 翻页风格大计时器（mm:ss） ----------
        elapsed_int = int(elapsed)
        mm, ss = divmod(elapsed_int, 60)

        digit_class = "flip-digit-xlarge" if focus_mode else "flip-digit-large"
        sep_class = "flip-separator-xlarge" if focus_mode else "flip-separator-large"

        container_style = (
            "height:calc(100vh - 140px);display:flex;align-items:center;justify-content:center;"
            if focus_mode
            else "margin:26px 0;display:flex;justify-content:center;"
        )

        timer_html = f"""
        <div style='{container_style}'>
          <div class="flip-clock-wrapper">
            <div class="flip-card">
              <div class="flip-card-inner {digit_class}">{mm:02d}</div>
            </div>
            <div class="{sep_class}">:</div>
            <div class="flip-card">
              <div class="flip-card-inner {digit_class}">{ss:02d}</div>
            </div>
          </div>
        </div>
        """
        st.markdown(timer_html, unsafe_allow_html=True)

        # ---------- 实际用时表（可折叠） ----------
        if not focus_mode:
            with st.expander("③ 实际用时（按模块自动记录）", expanded=True):
                st.dataframe(actual_df, use_container_width=True, hide_index=True)
                st.caption("完成一个模块时点一次「本模块完成 / 记录用时」，系统会自动把该段时间记到当前模块。")

        # ---------- 一键导入到「录入成绩」 ----------
        def _build_timer_export(plan_rows, lap_data):
            plan_minutes = {r["模块"]: r["计划用时(min)"] for r in plan_rows}
            actual_minutes = {}
            for name, sec in lap_data.items():
                actual_minutes[name] = round(sec / 60.0, 1)
            return plan_minutes, actual_minutes

        export_clicked = st.button("💾 将本次计划/用时导入到「✏️ 录入成绩」", use_container_width=True)
        if export_clicked:
            plan_minutes, actual_minutes = _build_timer_export(
                plan_rows, st.session_state.timer_lap_data
            )
            st.session_state["timer_to_input"] = {
                "plan": plan_minutes,
                "actual": actual_minutes,
            }
            # 修改侧边栏菜单选项（依赖上面给 menu 设置了 key="menu"）
            st.session_state["menu"] = "✏️ 录入成绩"
            st.success("已将本次计划用时 & 实际用时写入缓存，并跳转到「✏️ 录入成绩」。")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # 自动刷新形成“正计时”效果
        if st.session_state.timer_running:
            time.sleep(1)
            st.rerun()


# ------------------- 本周训练计划 -------------------
elif menu == "🗓️ 本周训练计划":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">🗓️ 本周训练计划</div>
      <div class="hero-sub">系统基于最近 3 套卷：自动挑出短板&时间黑洞，并生成 7 天可执行清单。</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("还没有成绩数据，先去【录入成绩】。")
    else:
        wp = build_week_plan(df, strategy)

        # ---------- 生成规则说明 ----------
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='mini-header'>生成规则</div>", unsafe_allow_html=True)
        st.write("每天固定三件事：**资料速算 15min** + **言语填空 20题** + **短板/超时专项**。")
        st.caption("你可以在【策略设置】里调上限（数量秒 / 资料分钟 / 逻辑秒）与放弃策略。")
        st.markdown("</div>", unsafe_allow_html=True)

        # ---------- 7 天任务清单（这里改成可编辑） ----------
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='mini-header'>7 天任务清单</div>", unsafe_allow_html=True)

        for idx, d in enumerate(wp):
            with st.expander(f"📅 {d['日期']}  | 重点：{d['重点模块']}", expanded=False):
                # 系统自动生成的默认文本
                default_text = "\n".join([f"- {x}" for x in d["任务"]])

                st.caption("下面是系统自动生成的当天训练任务，你可以在文本框中自由修改后执行或复制。")

                # 用 text_area 展示，并允许你手动修改；不影响下面“📤 导出周计划”的自动逻辑
                _ = st.text_area(
                    "当天训练任务（可修改）",
                    value=default_text,
                    height=150,
                    key=f"week_plan_day_{idx}",
                )

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------- 导出周计划（原有功能，保持不变） ----------
        with st.expander("📤 导出周计划（复制到备忘录）", expanded=False):
            lines = ["## 本周训练计划（自动生成）"]
            for d in wp:
                lines.append(f"\n### {d['日期']}（重点：{d['重点模块']}）")
                for t in d["任务"]:
                    lines.append(f"- {t}")
            st.code("\n".join(lines), language="markdown")

    # ---------- 新增：行测数据复盘 GPT Prompt，一键复制 ----------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-header'>行测数据复盘 · GPT 一键 Prompt</div>", unsafe_allow_html=True)

    st.caption("步骤：在本网站导出历史数据 → 上传到 GPT → 直接复制下方 Prompt 使用。")

    # 用三单引号包裹你的完整 Prompt（内容保持不动）
    prompt_text = '''你是一个“数据驱动型行测学习教练 GPT”，专门基于用户上传的【个人行测历史数据】进行深度复盘、能力诊断与提分方案设计。

你的核心价值不是讲题，而是：
- 从真实做题数据中识别“稳定弱点”
- 区分“不会” vs “会但慢” vs “会但不稳”
- 给出可执行、可量化、可复盘的提分路径

━━━━━━━━━━━━━━━━━━
【一、数据使用总原则】

当用户上传行测数据文件后：

1. 你必须假设：
   - 数据来自真实考试或高仿练习
   - 数据结构反映了用户真实能力，而不是偶然发挥

2. 你必须：
   - 优先基于数据结论说话
   - 禁止在未分析数据前给泛泛建议

3. 所有结论都要能回答一句话：
   👉 “你是从哪一类数据看出这个问题的？”

━━━━━━━━━━━━━━━━━━
【二、强制执行的数据分析流程】

在用户上传数据后，必须严格按以下顺序输出内容：

━━━━━━━━
① 数据结构确认（简要）
- 用几句话说明你识别到的数据字段（如：模块、题型、正确率、耗时、作答次数、错因等）
- 明确哪些字段被用于判断：准确率 / 时间 / 波动性 / 错误集中度

━━━━━━━━
② 行测能力画像（核心输出）

你必须从【三个维度】给出用户画像：

A. 模块层面（数量 / 逻辑 / 资料 / 言语 / 常识）
- 哪些模块是“稳定得分源”
- 哪些模块是“高投入低回报”

B. 题型层面（如：工程问题、削弱题、主旨题等）
- 明确列出：
  - 高错误率 + 高出现频率的“致命题型”
  - 正确率不低，但耗时异常的“拖分题型”

C. 行为层面（考试习惯）
- 是否存在：
  - 前期过慢，后期崩盘
  - 容易在某类题上反复犹豫
  - 同类题表现波动极大（不稳定）

━━━━━━━━
③ 出题人视角诊断（必须有）

基于数据，你要回答：
- 命题人是通过哪类题，持续“收割”用户分数的？
- 用户最容易被哪一类“伪直觉 / 伪技巧”欺骗？

━━━━━━━━
④ 核心问题归因（重点）

你必须将问题归因为以下三类之一（可多选）：
- 认知模型错误（理解方向不对）
- 决策路径冗长（会，但不考试化）
- 熟练度不足（对，但不稳定）

并且：
- 每一个归因，必须绑定【具体数据证据】

━━━━━━━━
⑤ 个性化提分策略（可执行）

你要给出一个【分阶段训练方案】：

▌阶段一：止血（短期 7–10 天）
- 明确：哪些题型应暂时放弃 / 快速跳过
- 哪些模块是“当前最容易拉分的”

▌阶段二：结构重建（中期）
- 针对 1–2 个核心弱题型
- 重建“识别信号 → 决策路径”
- 明确每类题的“考试级最优解法”

▌阶段三：稳定性训练（长期）
- 如何通过复盘减少波动
- 如何用数据判断“真的学会了”

━━━━━━━━━━━━━━━━━━
【三、讲解与教学要求】

在涉及具体题型或能力缺陷时：

1. 必须使用高度贴切的直觉类比
   - 把抽象逻辑 / 数量关系 / 资料判断
   - 转化为具体、可想象的现实场景
   - 类比要完整、有故事、有因果

2. 所有方法必须是：
   - 考试可执行
   - 时间友好
   - 能被反复复盘验证

━━━━━━━━━━━━━━━━━━
【四、递归复盘机制（非常重要）】

在每一次分析结尾，你必须：

1. 向用户提出 3–5 个【基于其数据的精准追问】
   - 用来确认你对问题判断是否准确
   - 同时检测用户是否真正理解自己的问题

2. 如果用户回答：
   - 否认 / 犹豫 / 不确定
   → 你必须回溯数据，重新校准判断

━━━━━━━━━━━━━━━━━━
【五、最终目标】

你的终极目标不是让用户“听懂分析”，
而是让用户在下一次做题时：

- 知道哪些题是“我的钱”
- 哪些题是“命题人给我下的套”
- 哪些题我应该毫不犹豫地放弃

你是一个用数据说话、以考试为导向的行测教练。'''

    # 展示可复制文本
    st.text_area(
        "一键复制用 Prompt（全选复制即可）",
        prompt_text,
        height=500,
    )

    st.markdown("</div>", unsafe_allow_html=True)
    # ---------- 新增部分结束 ----------

# ------------------- 趋势分析 -------------------
elif menu == "📊 趋势分析":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">📊 趋势分析</div>
      <div class="hero-sub">看趋势只看两件事：<b>总分稳步上升</b> + <b>短板不再崩盘</b>。</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("暂无数据")
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        plot_df = df.copy()
        plot_df["场次"] = plot_df.apply(lambda x: f"{x['日期']}\n{x['试卷']}", axis=1)

        fig = px.line(plot_df, x="场次", y="总分", markers=True, text="总分")
        fig.update_traces(textposition="top center")
        fig.update_layout(height=380, margin=dict(t=10, b=10), xaxis_title="", yaxis_title="总分")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='mini-header'>模块正确率波动</div>", unsafe_allow_html=True)
        module_cols = [f"{m}_正确率" for m in LEAF_MODULES if f"{m}_正确率" in plot_df.columns]
        if module_cols:
            module_trends = plot_df[["场次"] + module_cols].melt(id_vars="场次", var_name="模块", value_name="正确率")
            module_trends["模块"] = module_trends["模块"].str.replace("_正确率", "")
            fig2 = px.line(module_trends, x="场次", y="正确率", color="模块", markers=True)
            fig2.update_layout(height=360, margin=dict(t=10, b=10), yaxis_title="正确率")
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='mini-header'>历史成绩明细</div>", unsafe_allow_html=True)
        display_df = df[["日期", "试卷", "总分", "总正确数", "总题数", "总用时"]].copy()
        display_df["正确率"] = (display_df["总正确数"] / display_df["总题数"]).map(lambda x: f"{x:.1%}" if x else "0.0%")
        st.dataframe(display_df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------- 录入成绩 -------------------
elif menu == "✏️ 录入成绩":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">✏️ 录入成绩</div>
      <div class="hero-sub">录入后系统会在【📑 单卷详情】自动生成复盘建议，在【🗓️ 本周训练计划】生成 7 天任务。</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # ① 试卷题量 / 分值模板 
    paper_type = st.selectbox(
        "试卷题量配置",
        list(PAPER_TEMPLATES.keys()),
        key="paper_type_cfg",
        help="不同机构套题的题量分布和每题分值不同，这里会自动用于计算总题数和总分。"
    )
    tpl_cfg = PAPER_TEMPLATES[paper_type]
    tpl_totals = tpl_cfg["totals"]
    per_score = tpl_cfg["weight"]

    st.caption(f"当前选择：{paper_type} ｜ 每题 {per_score} 分")
    st.divider()

    # ② 录入表单
    with st.form("input_score"):
        # 基本信息
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷全称", placeholder="例如：粉笔组卷xxx / 省考模考第X套")
        date = c2.date_input("考试日期")

        s1, s2 = st.columns(2)
        state_level = s1.selectbox(
            "本套状态自评",
            [
                "未填写",
                "1 精神很差 / 很困",
                "2 有点累 / 注意力飘",
                "3 一般",
                "4 还可以",
                "5 精神很好 / 手感不错",
            ],
            index=3,
            key="state_level_this_paper",
        )
        feeling = s2.text_input(
            "本套一句话感受（可选）",
            placeholder="例：数量一开始卡住，后面心态有点炸 / 资料做完已经有点烦",
            key="feeling_this_paper",
        )

        st.divider()

        # 初始化整套卷记录
        entry = {
            "日期": date,
            "试卷": paper,
            "试卷类型": paper_type,
            "每题分值": per_score,
            "本套_状态自评": state_level,
            "本套_一句话感受": feeling,
        }

        tc, tq, tt, ts = 0, 0, 0, 0  # 总正确数 / 总题数 / 总用时 / 总分

        # ③ 逐模块录入
        for m, config in MODULE_STRUCTURE.items():
            if config["type"] == "direct":
                leaf_name = m
                # 题量：优先用模板的配置，没有就用 MODULE_STRUCTURE 默认
                total_q = int(tpl_totals.get(leaf_name, config.get("total", 0)))

                st.markdown(f"**📌 {m}**")
                a, b, c = st.columns([1, 1, 1])
                mq = a.number_input("对题数", 0, total_q, 0, key=f"q_{m}")
                mt = b.number_input(
                    "实际用时(min)",
                    0.0, 180.0,
                    float(PLAN_TIME.get(m, 5.0)),
                    step=0.5,
                    key=f"t_{m}",
                )
                mp = c.number_input(
                    "计划用时(min)",
                    0.0, 180.0,
                    float(PLAN_TIME.get(m, 5.0)),
                    step=0.5,
                    key=f"p_{m}",
                )

                entry[f"{m}_总题数"] = total_q
                entry[f"{m}_正确数"] = mq
                entry[f"{m}_用时"] = mt
                entry[f"{m}_正确率"] = mq / total_q if total_q > 0 else 0
                entry[f"{m}_计划用时"] = mp

                # 数量关系 / 资料分析：可选的“主动放弃 & 蒙猜”
                if m == "数量关系":
                    with st.expander("数量补充信息（可选）", expanded=False):
                        s_skip, s_guess = st.columns(2)
                        num_skip = s_skip.number_input(
                            "数量-主动放弃题数",
                            0, total_q, 0,
                            key="数量_主动放弃题数",
                        )
                        num_guess = s_guess.number_input(
                            "数量-蒙猜题数",
                            0, total_q, 0,
                            key="数量_蒙猜题数",
                        )
                        entry["数量关系_跳过题数"] = num_skip
                        entry["数量关系_蒙猜题数"] = num_guess

                if m == "资料分析":
                    with st.expander("资料补充信息（可选）", expanded=False):
                        s_skip2, s_guess2 = st.columns(2)
                        d_skip = s_skip2.number_input(
                            "资料-主动放弃题数",
                            0, total_q, 0,
                            key="资料_主动放弃题数",
                        )
                        d_guess = s_guess2.number_input(
                            "资料-蒙猜题数",
                            0, total_q, 0,
                            key="资料_蒙猜题数",
                        )
                        entry["资料分析_跳过题数"] = d_skip
                        entry["资料分析_蒙猜题数"] = d_guess

                # 汇总
                tc += mq
                tq += total_q
                tt += mt
                ts += mq * per_score

            else:
                # 有子模块（言语 / 判断）
                st.markdown(f"**📌 {m}**")
                sub_cols = st.columns(len(config["subs"]))
                for idx, (sm, stot) in enumerate(config["subs"].items()):
                    leaf_name = sm
                    sub_total = int(tpl_totals.get(leaf_name, stot))

                    with sub_cols[idx]:
                        st.caption(sm)
                        sq = st.number_input("对题", 0, sub_total, 0, key=f"sq_{sm}")
                        st_time = st.number_input(
                            "实(min)",
                            0.0, 180.0,
                            float(PLAN_TIME.get(sm, 5.0)),
                            step=0.5,
                            key=f"st_{sm}",
                        )
                        st_plan = st.number_input(
                            "计(min)",
                            0.0, 180.0,
                            float(PLAN_TIME.get(sm, 5.0)),
                            step=0.5,
                            key=f"sp_{sm}",
                        )

                    entry[f"{sm}_总题数"] = sub_total
                    entry[f"{sm}_正确数"] = sq
                    entry[f"{sm}_用时"] = st_time
                    entry[f"{sm}_正确率"] = sq / sub_total if sub_total > 0 else 0
                    entry[f"{sm}_计划用时"] = st_plan

                    tc += sq
                    tq += sub_total
                    tt += st_time
                    ts += sq * per_score

            st.markdown("---")

        # ④ 提交整套卷
        if st.form_submit_button("🚀 提交存档", type="primary", use_container_width=True):
            if not paper:
                st.error("请输入试卷名称")
            else:
                entry.update({
                    "总分": round(ts, 2),
                    "总正确数": tc,
                    "总题数": tq,
                    "总用时": tt,
                })
                df2 = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                df2 = ensure_schema(df2)
                save_data(df2, un)
                st.success("数据已存档")
                time.sleep(0.7)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)



# ------------------- 数据管理 -------------------
elif menu == "⚙️ 数据管理":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">⚙️ 数据管理</div>
      <div class="hero-sub">谨慎操作：删除会影响趋势图与训练计划。</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("暂无数据")
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)
        del_target = st.selectbox("选择要删除的记录", df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1))
        if st.button("🗑️ 确认删除该记录", type="secondary"):
            df2 = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) != del_target]
            save_data(df2, un)
            st.success("删除成功")
            time.sleep(0.5)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------- 数据备份 / 迁移 -------------------
elif menu == "📂 数据备份 / 迁移":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">📂 数据备份 / 迁移</div>
      <div class="hero-sub">
        支持一键导出当前账号数据为 zip，包含：成绩 / 复盘 / 策略 / 打卡。<br>
        换设备或换账号时，可以导入 zip 恢复。
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 导出
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-header'>导出当前账号数据（zip）</div>", unsafe_allow_html=True)
    st.caption("建议：重要考试前后导出一份备份到本地 / 网盘。")
    if st.button("📦 生成数据包", use_container_width=True):
        data_bytes = export_user_bundle(un)
        st.session_state["export_zip"] = data_bytes
        st.success("已生成数据包，请在下方下载。")
    if "export_zip" in st.session_state:
        st.download_button(
            label="⬇️ 下载数据包（zip）",
            data=st.session_state["export_zip"],
            file_name=f"civil_service_pro_max_{un}.zip",
            mime="application/zip",
            use_container_width=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # 导入
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-header'>导入数据包（覆盖当前账号）</div>", unsafe_allow_html=True)
    st.caption("注意：导入会覆盖当前账号的已有数据（成绩 / 复盘 / 策略 / 打卡）。")
    up = st.file_uploader("选择 zip 文件", type=["zip"])
    if up is not None:
        ok, msg = import_user_bundle(un, up)
        if ok:
            st.success(msg)
            st.info("请刷新页面以确保所有图表/统计按新数据重新计算。")
        else:
            st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- 策略设置（含自定义策略备注） -------------------
elif menu == "⚙️ 策略设置":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">⚙️ 策略设置</div>
      <div class="hero-sub">把“考场规则”写进系统：你只需按规则执行，不再纠结。</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-header'>上限策略</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        qsec = st.number_input("数量：每题上限(秒)", 20, 180, int(strategy.get("数量_每题上限秒", 60)))
    with c2:
        rmin = st.number_input("资料：每篇上限(分钟)", 3, 12, int(strategy.get("资料_每篇上限分钟", 6)))
    with c3:
        lsec = st.number_input("逻辑：每题上限(秒)", 30, 240, int(strategy.get("逻辑_每题上限秒", 90)))

    st.markdown("<div class='mini-header'>放弃 / 优先策略</div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        easy_only = st.toggle("数量：只做简单题（推荐）", value=bool(strategy.get("数量_只做简单题", True)))
    with b2:
        data_skip = st.toggle("资料：超时先跳（推荐）", value=bool(strategy.get("资料_超时先跳", True)))

    st.markdown("<div class='mini-header'>复盘统计范围</div>", unsafe_allow_html=True)
    days = st.slider("看板错因统计：统计最近多少天", 7, 120, int(strategy.get("复盘_统计天数", 30)), step=1)

    st.markdown("<div class='mini-header'>自定义策略备注（可空）</div>", unsafe_allow_html=True)
    custom_note = st.text_area(
        "例如：放弃某些题型、考试顺序、心态提醒等（会长期保存在本账号下）",
        value=strategy.get("自定义策略备注", ""),
        height=120
    )

    if st.button("💾 保存策略", type="primary", use_container_width=True):
        strategy["数量_每题上限秒"] = int(qsec)
        strategy["资料_每篇上限分钟"] = int(rmin)
        strategy["逻辑_每题上限秒"] = int(lsec)
        strategy["数量_只做简单题"] = bool(easy_only)
        strategy["资料_超时先跳"] = bool(data_skip)
        strategy["复盘_统计天数"] = int(days)
        strategy["自定义策略备注"] = custom_note
        save_strategy(un, strategy)
        st.success("已保存！系统建议会按你的策略生成。")
        time.sleep(0.6)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- 管理后台 -------------------
elif menu == "🛡️ 管理后台" and role == "admin":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">🛡️ 管理后台</div>
      <div class="hero-sub">管理员可维护账号与权限。</div>
    </div>
    """, unsafe_allow_html=True)

    users = load_users()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    t_list, t_add, t_edit = st.tabs(["👥 用户列表", "➕ 新增用户", "🔧 账号维护"])

    with t_list:
        u_table = pd.DataFrame([{"账号": k, "昵称": v["name"], "角色": v["role"]} for k, v in users.items()])
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
            new_name = st.text_input("修改昵称", value=users[target_u]["name"])
            new_pwd = st.text_input("重置密码 (留空不修改)", type="password")
            if st.button("更新资料"):
                users[target_u]["name"] = new_name
                if new_pwd:
                    users[target_u]["password"] = hash_pw(new_pwd)
                save_users(users)
                st.success("更新成功")
        with col2:
            st.warning("危险操作")
            if st.button("🔥 彻底删除此账号"):
                if target_u == "admin":
                    st.error("无法删除主管理员")
                else:
                    del users[target_u]
                    save_users(users)
                    st.success("已删除")
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)






























