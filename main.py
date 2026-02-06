import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
import hashlib
import time
from typing import Dict, List, Tuple

# =========================================================
# 0. Page config
# =========================================================
st.set_page_config(page_title="行测 Pro Max", layout="wide", page_icon="🚀")

# =========================================================
# 1. Global UI (Responsive + Modern, 全浅色主题)
# =========================================================
st.markdown("""
<style>
/* ---------------- Base ---------------- */
:root{
  --bg: #f4f6f9;
  --ink: #0b1220;
  --muted: #64748b;
  --border: rgba(148,163,184,0.22);
  --glass: #ffffff;
  --shadow: 0 18px 55px rgba(15,23,42,0.10);
  --shadow2: 0 10px 30px rgba(15,23,42,0.08);
  --radius: 18px;
  --radius2: 22px;
  --blue: #3b82f6;
  --green: #10b981;
  --red: #ef4444;
  --orange:#f59e0b;
}

.block-container{
  padding-top: 1.05rem !important;
  padding-bottom: 1.0rem !important;
  max-width: 1250px;
}
.stApp{
  background: var(--bg);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
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
    radial-gradient(700px 360px at 8% 5%, rgba(191,219,254,0.9), transparent 55%),
    radial-gradient(800px 420px at 92% 15%, rgba(167,243,208,0.7), transparent 60%),
    linear-gradient(135deg, #ffffff 0%, #e0edff 42%, #ffffff 100%);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  color: var(--ink);
  margin-bottom: 14px;
}
.hero-title{
  font-size: 1.42rem;
  font-weight: 950;
  letter-spacing: -0.03em;
  margin-bottom: 6px;
}
.hero-sub{
  color: var(--muted);
  font-size: 0.93rem;
  line-height: 1.45;
}
.hero-badges{ margin-top: 10px; display:flex; gap:8px; flex-wrap: wrap; }
.badge{
  display:inline-flex; align-items:center; gap:6px;
  padding: 6px 10px; border-radius: 999px;
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.22);
  color: var(--ink); font-size: 0.78rem;
}

/* ---------------- Cards ---------------- */
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

/* 之前的深色卡片，统一改成浅色高亮卡 */
.card-dark{
  background: #ffffff;
  border-radius: var(--radius);
  border: 1px solid rgba(59,130,246,0.30);
  box-shadow: 0 18px 55px rgba(37,99,235,0.18);
  padding: 14px 16px;
}

/* ---------------- KPI ---------------- */
.kpi-wrap{ display:flex; gap:10px; flex-wrap:wrap; margin-top: 10px; }
.kpi{
  flex: 1 1 190px;
  border-radius: 16px;
  padding: 12px 12px;
  background: #f8fafc;
  border: 1px solid rgba(148,163,184,0.35);
}
.kpi .k{ font-size: 0.80rem; color: var(--muted); }
.kpi .v{ font-size: 1.36rem; font-weight: 950; margin-top: 2px; letter-spacing:-0.02em; color: var(--ink); }
.kpi .d{ font-size: 0.78rem; color: var(--muted); margin-top: 4px; }

/* ---------------- Titles ---------------- */
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

/* ---------------- Pills / Tips（浅色） ---------------- */
.tip-box{
  background: #f8fafc;
  color: var(--ink);
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--border);
  margin: 10px 0;
  line-height: 1.48;
  font-size: 0.92rem;
  box-shadow: var(--shadow2);
}
.tip-mod{
  font-weight: 900;
  font-size: 0.95rem;
  margin-bottom: 4px;
}
.pill{
  display:inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.74rem;
  margin-right: 6px;
  border: 1px solid rgba(148,163,184,0.45);
  background: rgba(191,219,254,0.55);
  color: var(--ink);
}

/* ---------------- Module cards ---------------- */
.module-card{
  background: #ffffff;
  padding: 10px 14px;
  border-radius: 16px;
  margin-bottom: 10px;
  border: 1px solid rgba(148,163,184,0.20);
  display:flex; justify-content:space-between; align-items:center;
  box-shadow: 0 10px 28px rgba(15,23,42,0.06);
}
.module-left{ display:flex; flex-direction:column; }
.module-name{ font-weight: 950; color:#0f172a; font-size: 0.95rem; letter-spacing:-0.01em; }
.module-meta{ font-size: 0.78rem; color:#64748b; margin-top: 2px; }
.module-right{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-weight: 950; font-size: 1.05rem; }

.bL-red{ border-left: 5px solid var(--red); background: #fef2f2; }
.bL-green{ border-left: 5px solid var(--green); background: #ecfdf5; }
.bL-blue{ border-left: 5px solid var(--blue); background: #eff6ff; }

/* ---------------- Inputs & Buttons ---------------- */
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea{
  border-radius: 14px !important;
}
div.stButton > button{
  border-radius: 14px !important;
  font-weight: 850 !important;
}
div.stButton > button[kind="primary"]{
  padding: 0.62rem 0.95rem !important;
}

/* ---------------- Charts spacing ---------------- */
div[data-testid="stPlotlyChart"]{ margin-top: -6px; }

/* ==================================================
   Responsive: Mobile
   ================================================== */
@media (max-width: 700px){
  .block-container{ padding-top: 0.75rem !important; padding-left: 0.75rem !important; padding-right: 0.75rem !important; }
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

# =========================================================
# 2. Config
# =========================================================
USERS_FILE = "users_db.json"
FIXED_WEIGHT = 0.8
GOAL_SCORE = 75.0

MODULE_STRUCTURE = {
    "政治理论": {"type": "direct", "total": 15},
    "常识判断": {"type": "direct", "total": 15},
    "言语理解": {"type": "parent", "subs": {"言语-逻辑填空": 10, "言语-片段阅读": 15}},
    "数量关系": {"type": "direct", "total": 15},
    "判断推理": {"type": "parent", "subs": {"判断-图形推理": 5, "判断-定义判断": 10, "判断-类比推理": 10, "判断-逻辑判断": 10}},
    "资料分析": {"type": "direct", "total": 20},
}

PLAN_TIME = {
    "政治理论": 5,
    "常识判断": 5,
    "言语-逻辑填空": 18,
    "言语-片段阅读": 22,
    "数量关系": 25,
    "判断-图形推理": 5,
    "判断-定义判断": 8,
    "判断-类比推理": 7,
    "判断-逻辑判断": 10,
    "资料分析": 25,
}

DEFAULT_STRATEGY = {
    "数量_每题上限秒": 60,
    "资料_每篇上限分钟": 6,
    "逻辑_每题上限秒": 90,
    "数量_只做简单题": True,
    "资料_超时先跳": True,
    "复盘_统计天数": 30,
}

REVIEW_SCHEMA = [
    "日期", "试卷", "模块", "错题数",
    "错因1_知识点不会", "错因2_方法不熟", "错因3_审题选项坑",
    "一句话原因", "下次动作"
]

def get_leaf_modules() -> List[str]:
    leaves = []
    for k, v in MODULE_STRUCTURE.items():
        if v["type"] == "direct":
            leaves.append(k)
        else:
            leaves.extend(v["subs"].keys())
    return leaves

LEAF_MODULES = get_leaf_modules()

# =========================================================
# 3. Storage helpers
# =========================================================
def hash_pw(pw: str) -> str:
    return hashlib.sha256(str(pw).encode()).hexdigest()

def data_file(un: str) -> str:
    return f"data_storage_{un}.csv"

def review_file(un: str) -> str:
    return f"review_notes_{un}.csv"

def strategy_file(un: str) -> str:
    return f"strategy_{un}.json"

def checkin_file(un: str) -> str:
    return f"checkin_{un}.json"

def build_all_columns() -> List[str]:
    cols = ["日期", "试卷", "总分", "总正确数", "总题数", "总用时"]
    for m in LEAF_MODULES:
        cols.extend([f"{m}_总题数", f"{m}_正确数", f"{m}_用时", f"{m}_正确率", f"{m}_计划用时"])
    return cols

def ensure_schema(df: pd.DataFrame) -> pd.DataFrame:
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

    num_cols = [c for c in df.columns if any(c.endswith(s) for s in ["_正确数", "_总题数", "_用时", "_正确率", "_计划用时"]) or c in ["总分", "总正确数", "总题数", "总用时"]]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df

def load_data(un: str) -> pd.DataFrame:
    path = data_file(un)
    if os.path.exists(path):
        df = pd.read_csv(path, encoding="utf-8")
        return ensure_schema(df)
    return ensure_schema(pd.DataFrame())

def save_data(df: pd.DataFrame, un: str):
    df = ensure_schema(df)
    df.to_csv(data_file(un), index=False, encoding="utf-8-sig")

def load_users() -> Dict:
    if not os.path.exists(USERS_FILE):
        d = {"admin": {"name": "管理员", "password": hash_pw("admin123"), "role": "admin"}}
        save_users(d)
        return d
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(d: Dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def load_reviews(un: str) -> pd.DataFrame:
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
    for c in REVIEW_SCHEMA:
        if c not in rdf.columns:
            rdf[c] = ""
    rdf = rdf[REVIEW_SCHEMA]
    rdf.to_csv(review_file(un), index=False, encoding="utf-8-sig")

def load_strategy(un: str) -> Dict:
    path = strategy_file(un)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                s = json.load(f)
            for k, v in DEFAULT_STRATEGY.items():
                if k not in s:
                    s[k] = v
            return s
        except Exception:
            pass
    return dict(DEFAULT_STRATEGY)

def save_strategy(un: str, s: Dict):
    with open(strategy_file(un), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

def load_checkin(un: str) -> Dict:
    """
    checkin schema:
    {
      "streak": int,
      "last_date": "YYYY-MM-DD",
      "today_tasks_source": "auto_week_plan" | "custom",
      "today_tasks": [{"title":..., "done": bool}, ...]
    }
    """
    path = checkin_file(un)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if "streak" not in d: d["streak"] = 0
            if "last_date" not in d: d["last_date"] = ""
            if "today_tasks" not in d: d["today_tasks"] = []
            if "today_tasks_source" not in d: d["today_tasks_source"] = "auto_week_plan"
            return d
        except Exception:
            pass
    return {"streak": 0, "last_date": "", "today_tasks_source": "auto_week_plan", "today_tasks": []}

def save_checkin(un: str, d: Dict):
    with open(checkin_file(un), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

# =========================================================
# 4. UI helpers + logic helpers
# =========================================================
def status_class(acc: float) -> str:
    if acc >= 0.8:
        return "bL-green"
    if acc < 0.6:
        return "bL-red"
    return "bL-blue"

def render_module_card(name: str, correct: float, total: float, duration: float, acc: float, plan: float) -> str:
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
    单卷提示卡：顶部先显示模块名，然后是标签+建议。
    """
    tips = []
    if plan and t > plan + 2:
        tips.append(f"<span class='pill'>超时</span>用时 <b>{int(t)}m</b>，比计划 <b>+{int(t-plan)}m</b>。设置上限→超时先跳。")

    if acc >= 0.8:
        tips.append(f"<span class='pill'>强项</span>正确率 <b>{acc:.0%}</b>，重点：提速 + 降低粗心。")
    elif acc < 0.6:
        tips.append(f"<span class='pill'>短板</span>正确率 <b>{acc:.0%}</b>，错题拆三类：不会/不熟/审题坑，并只改一个动作。")
    else:
        tips.append(f"<span class='pill'>可提升</span>正确率 <b>{acc:.0%}</b>，属于训练就能稳定涨的区间。")

    # 专属动作
    if m == "资料分析":
        per_block = int(strategy.get("资料_每篇上限分钟", 6))
        skip = bool(strategy.get("资料_超时先跳", True))
        skip_txt = "（超时先跳）" if skip else ""
        tips.append(f"动作：<b>每篇限时{per_block}分钟</b>{skip_txt}；每天15分钟练<b>速算（增长率/基期/比重/平均）</b>。")
    elif m == "数量关系":
        sec = int(strategy.get("数量_每题上限秒", 60))
        easy_only = bool(strategy.get("数量_只做简单题", True))
        easy_txt = "（只做简单题）" if easy_only else ""
        tips.append(f"动作：<b>每题{sec}秒上限</b>{easy_txt}；只保留你最稳的<b>3类题型</b>训练，其余秒放。")
    elif m in ["言语-逻辑填空", "言语-片段阅读"]:
        tips.append("动作：每天20题专项；错题只写一句：<b>语境/搭配/转折因果关键词</b>，下次遇坑能秒避。")
    elif m in ["政治理论", "常识判断"]:
        tips.append("动作：每天10分钟刷题；错题压成<b>1行卡片关键词</b>（法条/时政点）。")
    elif m == "判断-逻辑判断":
        sec = int(strategy.get("逻辑_每题上限秒", 90))
        tips.append(f"动作：设置<b>{sec}秒上限</b>；难题先跳，优先稳图推/类比/定义。")
    elif m.startswith("判断-"):
        tips.append("动作：图推/类比/定义优先稳分；复杂题设置上限，超过先跳。")

    # 这里加上模块标题，让你一眼看到是哪个模块的问题
    return "<div class='tip-box'><div class='tip-mod'>" + m + "</div>" + "<br>".join(tips) + "</div>"

def compute_summary(df: pd.DataFrame):
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None
    delta = float(latest["总分"]) - float(prev["总分"]) if prev is not None else None
    acc = float(latest["总正确数"]) / max(float(latest["总题数"]), 1)
    return latest, delta, acc

def compute_next_day_plan(row: pd.Series, strategy: Dict):
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
# 5. Login
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("""
        <div class="hero">
          <div class="hero-title">🚀 行测 Pro Max</div>
          <div class="hero-sub">把“模考”变成可复制的提分流程：<b>看板 → 复盘 → 动作 → 训练计划</b></div>
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
# 6. Main load
# =========================================================
un = st.session_state.u_info["un"]
role = st.session_state.u_info["role"]
df = load_data(un)
rdf = load_reviews(un)
strategy = load_strategy(un)
checkin = load_checkin(un)

# Sidebar
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
            "🗓️ 本周训练计划",
            "📊 趋势分析",
            "✏️ 录入成绩",
            "⚙️ 数据管理",
            "⚙️ 策略设置",
        ] + (["🛡️ 管理后台"] if role == "admin" else [])
    )
    st.markdown("---")
    if st.button("安全退出", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# =========================================================
# 7. Pages（后面的逻辑保持不变）
# =========================================================
if menu == "🏠 数字化看板":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">📊 数字化看板</div>
      <div class="hero-sub">只盯两件事：<b>稳定得分</b> + <b>控制时间</b>。系统会定位短板与时间黑洞。</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("👋 你还没有录入任何模考。先去【录入成绩】录一套，系统会自动生成复盘建议。")
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

        days = int(strategy.get("复盘_统计天数", 30))
        cause_df, mod_df = review_analytics(rdf, days)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='mini-header'>复盘错因统计（近 {days} 天）</div>", unsafe_allow_html=True)
        if cause_df.empty:
            st.caption("暂无复盘记录。去【复盘记录】填几条，系统会自动画图。")
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

elif menu == "📑 单卷详情":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">📑 单卷详情</div>
      <div class="hero-sub">系统自动输出：<b>短板 Top3</b>、<b>超时 Top3</b>、<b>每模块 1 个动作</b>、<b>明天训练 3 条</b></div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("暂无数据。先去【录入成绩】。")
    else:
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择历史模考", sel_list)
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("得分", f"{float(row['总分']):.1f}")
        c2.metric("正确率", f"{float(row['总正确数'])/max(float(row['总题数']),1):.1%}")
        c3.metric("总用时", f"{int(row['总用时'])} min")
        c4.metric("得分效率", f"{float(row['总分'])/max(float(row['总用时']),1):.2f} 分/min")
        st.markdown("</div>", unsafe_allow_html=True)

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

        left, right = st.columns(2)
        with left:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>正确率最低 Top3</div>", unsafe_allow_html=True)
            for m, accm, t, plan, total, diff in worst_by_acc:
                st.markdown(module_tip(m, accm, t, plan, strategy), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='mini-header'>超时最多 Top3</div>", unsafe_allow_html=True)
            for m, accm, t, plan, total, diff in worst_by_time:
                st.markdown(module_tip(m, accm, t, plan, strategy), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        tasks, worst_acc, worst_time = compute_next_day_plan(row, strategy)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='mini-header'>✅ 明天怎么练（只给3条，能执行）</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <ol style="margin: 0 0 0 18px;">
          <li>{tasks[0]}</li>
          <li>{tasks[1]}</li>
          <li>{tasks[2]}</li>
        </ol>
        <div class="small-muted" style="margin-top:10px;">
          重点短板：<b>{worst_acc[0]}</b>（正确率 {worst_acc[1]:.0%}）；
          时间黑洞：<b>{worst_time[0]}</b>（超时 {worst_time[2]:.0f} 分钟）
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 模块卡片（电脑端3列，手机端自动堆叠）
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

        with st.expander("📤 导出本卷复盘摘要（复制到笔记）", expanded=False):
            md = []
            md.append(f"### {row['日期']} | {row['试卷']}")
            md.append(f"- 得分：{float(row['总分']):.1f} | 正确率：{float(row['总正确数'])/max(float(row['总题数']),1):.1%} | 用时：{int(row['总用时'])}min")
            md.append(f"- 明天训练：1）{tasks[0]} 2）{tasks[1]} 3）{tasks[2]}")
            md.append("")
            md.append("**模块Top问题（自动）**")
            md.append(f"- 正确率最低：{', '.join([x[0] for x in worst_by_acc])}")
            md.append(f"- 超时最多：{', '.join([x[0] for x in worst_by_time])}")
            st.code("\n".join(md), language="markdown")

elif menu == "🧠 复盘记录":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">🧠 复盘记录</div>
      <div class="hero-sub">每套卷只做一件事：把错题归因为<b>不会 / 不熟 / 审题坑</b>，并写<b>下次只改1个动作</b>。</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("你还没录入套卷，先去【录入成绩】。")
    else:
        sel_list = df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1).tolist()[::-1]
        sel = st.selectbox("选择要复盘的套卷", sel_list)
        row = df[df.apply(lambda x: f"{x['日期']} | {x['试卷']}", axis=1) == sel].iloc[0]

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
                st.text_input("下次动作（只写1个）", key=f"a_{m}", placeholder="例：资料每篇6分钟上限；数量每题60秒上限；填空每天20题")

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
                        "下次动作": st.session_state.get(f"a_{m}", ""),
                    })
                rdf2 = pd.concat([rdf, pd.DataFrame(rows)], ignore_index=True)
                save_reviews(rdf2, un)
                st.success("已保存！下次复习只看“下次动作”。")
                time.sleep(0.7)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

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
                keyword = st.text_input("关键词搜索（原因/动作）", placeholder="例：基期、速算、转折、60秒…")

            view = rdf.copy()
            if f_paper != "全部":
                view = view[view["试卷"].astype(str) == f_paper]
            if f_mod != "全部":
                view = view[view["模块"].astype(str) == f_mod]
            if keyword.strip():
                k = keyword.strip()
                view = view[
                    view["一句话原因"].astype(str).str.contains(k, na=False) |
                    view["下次动作"].astype(str).str.contains(k, na=False)
                ]
            st.dataframe(view.sort_values(["日期", "试卷", "模块"], ascending=[False, False, True]),
                         use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "✅ 今日任务":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">✅ 今日任务</div>
      <div class="hero-sub">把训练做成“可打卡”的流程：完成=连续天数 +1。任务默认来自本周计划，你也可以自定义。</div>
    </div>
    """, unsafe_allow_html=True)

    wp = build_week_plan(df, strategy) if not df.empty else []
    today_str = datetime.now().date().isoformat()

    # 若今天任务为空或日期变化，自动刷新来源（auto）
    if (not checkin.get("today_tasks")) or (checkin.get("today_tasks_date") != today_str):
        checkin["today_tasks"] = get_today_tasks_from_week_plan(wp)
        checkin["today_tasks_source"] = "auto_week_plan"
        checkin["today_tasks_date"] = today_str
        save_checkin(un, checkin)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-header'>今日清单</div>", unsafe_allow_html=True)
    st.caption(f"日期：{today_str}｜来源：{checkin.get('today_tasks_source','auto_week_plan')}｜连续打卡：{int(checkin.get('streak',0))} 天")

    tasks = checkin.get("today_tasks", [])
    if not tasks:
        st.info("暂无任务。先录入成绩生成周计划，或在下方自定义任务。")
    else:
        changed = False
        for i, t in enumerate(tasks):
            key = f"task_{i}"
            done_now = st.checkbox(t["title"], value=bool(t.get("done", False)), key=key)
            if done_now != bool(t.get("done", False)):
                tasks[i]["done"] = done_now
                changed = True

        # 保存 + streak
        if st.button("💾 保存打卡", type="primary", use_container_width=True):
            checkin["today_tasks"] = tasks
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

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='mini-header'>生成规则</div>", unsafe_allow_html=True)
        st.write("每天固定三件事：**资料速算 15min** + **言语填空 20题** + **短板/超时专项**。")
        st.caption("你可以在【策略设置】里调上限（数量秒/资料分钟/逻辑秒）与放弃策略。")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='mini-header'>7 天任务清单</div>", unsafe_allow_html=True)
        for d in wp:
            with st.expander(f"📅 {d['日期']}  | 重点：{d['重点模块']}", expanded=False):
                st.markdown("\n".join([f"- {x}" for x in d["任务"]]))
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("📤 导出周计划（复制到备忘录）", expanded=False):
            lines = ["## 本周训练计划（自动生成）"]
            for d in wp:
                lines.append(f"\n### {d['日期']}（重点：{d['重点模块']}）")
                for t in d["任务"]:
                    lines.append(f"- {t}")
            st.code("\n".join(lines), language="markdown")

elif menu == "📊 趋势分析":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">📊 趋势分析</div>
      <div class="hero-sub">看趋势只看两件事：<b>总分稳步上升</b> + <b>短板不再崩盘</b></div>
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

elif menu == "✏️ 录入成绩":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">✏️ 录入成绩</div>
      <div class="hero-sub">录入后系统会在【单卷详情】自动生成复盘建议，在【本周训练计划】生成 7 天任务。</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    with st.form("input_score"):
        c1, c2 = st.columns(2)
        paper = c1.text_input("试卷全称", placeholder="例如：粉笔组卷xxx / 省考模考第X套")
        date = c2.date_input("考试日期")
        st.divider()

        entry = {"日期": date, "试卷": paper}
        tc, tq, tt, ts = 0, 0, 0, 0

        for m, config in MODULE_STRUCTURE.items():
            if config["type"] == "direct":
                st.markdown(f"**📌 {m}**")
                a, b, c = st.columns([1, 1, 1])
                mq = a.number_input("对题数", 0, config["total"], 0, key=f"q_{m}")
                mt = b.number_input("实际用时(min)", 0, 180, int(PLAN_TIME.get(m, 5)), key=f"t_{m}")
                mp = c.number_input("计划用时(min)", 0, 180, int(PLAN_TIME.get(m, 5)), key=f"p_{m}")

                entry[f"{m}_总题数"] = config["total"]
                entry[f"{m}_正确数"] = mq
                entry[f"{m}_用时"] = mt
                entry[f"{m}_正确率"] = mq / config["total"] if config["total"] > 0 else 0
                entry[f"{m}_计划用时"] = mp

                tc += mq
                tq += config["total"]
                tt += mt
                ts += mq * FIXED_WEIGHT
            else:
                st.markdown(f"**📌 {m}**")
                sub_cols = st.columns(len(config["subs"]))
                for idx, (sm, stot) in enumerate(config["subs"].items()):
                    with sub_cols[idx]:
                        st.caption(sm)
                        sq = st.number_input("对题", 0, stot, 0, key=f"sq_{sm}")
                        st_time = st.number_input("实(min)", 0, 180, int(PLAN_TIME.get(sm, 5)), key=f"st_{sm}")
                        st_plan = st.number_input("计(min)", 0, 180, int(PLAN_TIME.get(sm, 5)), key=f"sp_{sm}")

                        entry[f"{sm}_总题数"] = stot
                        entry[f"{sm}_正确数"] = sq
                        entry[f"{sm}_用时"] = st_time
                        entry[f"{sm}_正确率"] = sq / stot if stot > 0 else 0
                        entry[f"{sm}_计划用时"] = st_plan

                        tc += sq
                        tq += stot
                        tt += st_time
                        ts += sq * FIXED_WEIGHT
            st.markdown("---")

        if st.form_submit_button("🚀 提交存档", type="primary", use_container_width=True):
            if not paper:
                st.error("请输入试卷名称")
            else:
                entry.update({"总分": round(ts, 2), "总正确数": tc, "总题数": tq, "总用时": tt})
                df2 = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                df2 = ensure_schema(df2)
                save_data(df2, un)
                st.success("数据已存档")
                time.sleep(0.7)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown("<div class='mini-header'>放弃/优先策略</div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        easy_only = st.toggle("数量：只做简单题（推荐）", value=bool(strategy.get("数量_只做简单题", True)))
    with b2:
        data_skip = st.toggle("资料：超时先跳（推荐）", value=bool(strategy.get("资料_超时先跳", True)))

    st.markdown("<div class='mini-header'>复盘统计范围</div>", unsafe_allow_html=True)
    days = st.slider("看板错因统计：统计最近多少天", 7, 120, int(strategy.get("复盘_统计天数", 30)), step=1)

    if st.button("💾 保存策略", type="primary", use_container_width=True):
        strategy["数量_每题上限秒"] = int(qsec)
        strategy["资料_每篇上限分钟"] = int(rmin)
        strategy["逻辑_每题上限秒"] = int(lsec)
        strategy["数量_只做简单题"] = bool(easy_only)
        strategy["资料_超时先跳"] = bool(data_skip)
        strategy["复盘_统计天数"] = int(days)
        save_strategy(un, strategy)
        st.success("已保存！系统建议会按你的策略生成。")
        time.sleep(0.6)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

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
