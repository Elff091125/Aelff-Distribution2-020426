
import os
import io
import re
import json
import time
import uuid
import random
import textwrap
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

try:
    import yaml  # PyYAML
except Exception:  # pragma: no cover
    yaml = None

try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception:  # pragma: no cover
    px = None
    go = None


# -----------------------------
# App constants
# -----------------------------

APP_TITLE = "Regulatory Command Center (RCC) — v3.0"
DEFAULT_DATASET_PATH = "defaultdataset.json"
DEFAULT_AGENTS_YAML_PATH = "agents.yaml"
DEFAULT_SKILL_MD_PATH = "SKILL.md"

SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "anthropic:claude-3-5-sonnet-latest",
    "anthropic:claude-3-5-haiku-latest",
    "grok-4-fast-reasoning",
    "grok-3-mini",
]

PROVIDERS = ["openai", "gemini", "anthropic", "grok"]

ENV_KEY_MAP = {
    "openai": ["OPENAI_API_KEY"],
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "grok": ["GROK_API_KEY", "XAI_API_KEY"],
}

REQUIRED_COLUMNS = [
    "SupplierID",
    "Deliverdate",
    "CustomerID",
    "LicenseNo",
    "Category",
    "UDID",
    "DeviceNAME",
    "LotNO",
    "SerNo",
    "Model",
    "Number",
]

# -----------------------------------
# Localization (EN / zh-TW)
# -----------------------------------

T = {
    "en": {
        "nav_command_center": "Command Center",
        "nav_distribution": "Distribution Lab",
        "nav_note_keeper": "AI Note Keeper",
        "nav_agents": "Agents Studio",
        "nav_settings": "Settings & Keys",
        "global_search": "Global search (context-aware)",
        "theme": "Painter Style",
        "jackpot": "Jackpot",
        "mode": "Mode",
        "light": "Light",
        "dark": "Dark",
        "language": "Language",
        "data_source": "Dataset Source",
        "use_default": "Use default dataset",
        "paste_or_upload": "Paste / Upload new dataset",
        "paste_here": "Paste CSV/JSON/Text here",
        "upload_file": "Upload file (CSV / JSON / TXT)",
        "load_dataset": "Load dataset",
        "clear_dataset": "Clear dataset",
        "dataset_preview": "Dataset preview",
        "data_quality": "Data quality",
        "missing_cols": "Missing columns",
        "parse_warnings": "Parsing warnings",
        "rows": "Rows",
        "unique_suppliers": "Unique Suppliers",
        "unique_customers": "Unique Customers",
        "total_units": "Total Units",
        "filters": "Filters",
        "date_range": "Date range",
        "qty_range": "Quantity range",
        "supplier_filter": "SupplierID",
        "customer_filter": "CustomerID",
        "license_filter": "LicenseNo",
        "model_filter": "Model",
        "top_n": "Top N",
        "reset_filters": "Reset filters",
        "wow_graphs": "WOW Graphs",
        "sankey_title": "Supply-Chain Symphony Sankey",
        "pulse_title": "Temporal Pulse + Anomaly Beacons",
        "mosaic_title": "Customer–Model Mosaic Heatmap",
        "classic_charts": "Classic Charts",
        "timeline": "Delivery Timeline",
        "model_dist": "Model Distribution",
        "top_customers": "Top Customers",
        "license_usage": "License Usage",
        "agents_yaml": "agents.yaml",
        "skill_md": "SKILL.md",
        "upload_agents_yaml": "Upload agents.yaml",
        "paste_agents_yaml": "Paste agents.yaml",
        "standardize": "Standardize",
        "import_yaml": "Import standardized YAML",
        "download_yaml": "Download standardized YAML",
        "yaml_status": "YAML status",
        "settings": "Provider keys",
        "configured_env": "Configured (env)",
        "configured_session": "Configured (session)",
        "missing": "Missing",
        "never_shown": "Never shown",
        "enter_key": "Enter API key (stored only in session)",
        "save_key": "Save key to session",
        "clear_key": "Clear session key",
        "note_input": "Paste notes (text or markdown)",
        "note_prompt": "Prompt (editable)",
        "note_model": "Model",
        "note_maxtokens": "Max tokens",
        "transform": "Transform to organized markdown",
        "ai_magics": "AI Magics",
        "ai_keywords": "AI Keywords (user-colored)",
        "keywords_list": "Keywords (comma-separated)",
        "keyword_color": "Keyword color",
        "apply_keywords": "Apply keyword highlighting",
        "output": "Output",
        "status_strip": "Status Strip",
        "agent_pipeline": "Agent Pipeline",
        "not_configured_ai": "No provider key configured. AI features will run in offline mode.",
        "offline_mode": "Offline mode",
        "online_mode": "Online mode",
    },
    "zh-TW": {
        "nav_command_center": "指揮中心",
        "nav_distribution": "配送分析實驗室",
        "nav_note_keeper": "AI 筆記整理",
        "nav_agents": "代理人工作室",
        "nav_settings": "設定與金鑰",
        "global_search": "全域搜尋（依情境）",
        "theme": "畫家風格",
        "jackpot": "轉盤",
        "mode": "模式",
        "light": "亮色",
        "dark": "暗色",
        "language": "語言",
        "data_source": "資料來源",
        "use_default": "使用預設資料集",
        "paste_or_upload": "貼上／上傳新資料集",
        "paste_here": "在此貼上 CSV/JSON/文字",
        "upload_file": "上傳檔案（CSV / JSON / TXT）",
        "load_dataset": "載入資料集",
        "clear_dataset": "清除資料集",
        "dataset_preview": "資料預覽",
        "data_quality": "資料品質",
        "missing_cols": "缺少欄位",
        "parse_warnings": "解析警告",
        "rows": "筆數",
        "unique_suppliers": "供應商數",
        "unique_customers": "客戶數",
        "total_units": "總數量",
        "filters": "篩選條件",
        "date_range": "日期範圍",
        "qty_range": "數量範圍",
        "supplier_filter": "SupplierID",
        "customer_filter": "CustomerID",
        "license_filter": "LicenseNo",
        "model_filter": "Model",
        "top_n": "前 N 名",
        "reset_filters": "重設篩選",
        "wow_graphs": "WOW 圖表",
        "sankey_title": "供應鏈交響 Sankey",
        "pulse_title": "時間脈動＋異常燈塔",
        "mosaic_title": "客戶–型號 馬賽克熱圖",
        "classic_charts": "經典圖表",
        "timeline": "配送時間趨勢",
        "model_dist": "型號分佈",
        "top_customers": "客戶排行",
        "license_usage": "許可證使用量",
        "agents_yaml": "agents.yaml",
        "skill_md": "SKILL.md",
        "upload_agents_yaml": "上傳 agents.yaml",
        "paste_agents_yaml": "貼上 agents.yaml",
        "standardize": "標準化",
        "import_yaml": "匯入標準化 YAML",
        "download_yaml": "下載標準化 YAML",
        "yaml_status": "YAML 狀態",
        "settings": "供應商金鑰",
        "configured_env": "已設定（環境）",
        "configured_session": "已設定（本次）",
        "missing": "未設定",
        "never_shown": "永不顯示",
        "enter_key": "輸入 API Key（僅存於本次 Session）",
        "save_key": "儲存到 Session",
        "clear_key": "清除 Session Key",
        "note_input": "貼上筆記（文字或 Markdown）",
        "note_prompt": "提示詞（可修改）",
        "note_model": "模型",
        "note_maxtokens": "最大 tokens",
        "transform": "轉為結構化 Markdown",
        "ai_magics": "AI 魔法",
        "ai_keywords": "AI 關鍵字（自選顏色）",
        "keywords_list": "關鍵字（逗號分隔）",
        "keyword_color": "關鍵字顏色",
        "apply_keywords": "套用關鍵字上色",
        "output": "輸出",
        "status_strip": "狀態列",
        "agent_pipeline": "代理流程",
        "not_configured_ai": "未設定任何供應商金鑰。AI 功能將以離線模式執行。",
        "offline_mode": "離線模式",
        "online_mode": "線上模式",
    },
}


# -----------------------------------
# Painter themes (20 styles, light/dark variants)
# -----------------------------------

def painter_themes() -> Dict[str, Dict[str, Dict[str, str]]]:
    # Token sets: keep compact but distinct. (You can tune palettes later without changing app logic.)
    return {
        "Da Vinci": {
            "light": {"bg1": "#f6f1e6", "bg2": "#d8c7a3", "glass": "rgba(255,255,255,0.55)", "border": "rgba(60,40,20,0.18)", "text": "#1f1a14", "muted": "#4a4036", "accent": "#8a5a2b"},
            "dark":  {"bg1": "#1a1410", "bg2": "#3b2a1c", "glass": "rgba(20,16,12,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#f3eadc", "muted": "#c8bba7", "accent": "#d0a35a"},
        },
        "Monet": {
            "light": {"bg1": "#f0fbff", "bg2": "#b7e3ff", "glass": "rgba(255,255,255,0.55)", "border": "rgba(40,90,120,0.16)", "text": "#0e2230", "muted": "#2c556b", "accent": "#2aa6c7"},
            "dark":  {"bg1": "#071b24", "bg2": "#103548", "glass": "rgba(9,24,32,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#e6f7ff", "muted": "#b8d7e6", "accent": "#58d1e6"},
        },
        "Van Gogh": {
            "light": {"bg1": "#fff6da", "bg2": "#ffd36e", "glass": "rgba(255,255,255,0.55)", "border": "rgba(40,40,80,0.16)", "text": "#1c1c2c", "muted": "#3b3b59", "accent": "#1f4aa8"},
            "dark":  {"bg1": "#0c1025", "bg2": "#1c2350", "glass": "rgba(10,14,34,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#fff2cc", "muted": "#f2d98a", "accent": "#ffd36e"},
        },
        "Picasso": {
            "light": {"bg1": "#fff1f1", "bg2": "#ffd5b8", "glass": "rgba(255,255,255,0.55)", "border": "rgba(80,40,40,0.14)", "text": "#2a1616", "muted": "#5a2f2f", "accent": "#e23d28"},
            "dark":  {"bg1": "#1d0f12", "bg2": "#3b1a22", "glass": "rgba(18,9,11,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#ffe9dd", "muted": "#f6c5a6", "accent": "#ff6a3d"},
        },
        "Frida Kahlo": {
            "light": {"bg1": "#f6fff5", "bg2": "#c7f5c8", "glass": "rgba(255,255,255,0.55)", "border": "rgba(20,70,30,0.15)", "text": "#0f2414", "muted": "#2f5a3a", "accent": "#e03a5e"},
            "dark":  {"bg1": "#07180b", "bg2": "#10361a", "glass": "rgba(7,18,9,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#eaffea", "muted": "#bfe6c3", "accent": "#ff4d73"},
        },
        "Hokusai": {
            "light": {"bg1": "#f4fbff", "bg2": "#c7e6ff", "glass": "rgba(255,255,255,0.55)", "border": "rgba(20,60,90,0.15)", "text": "#0c1f2e", "muted": "#2b536e", "accent": "#1b6fa8"},
            "dark":  {"bg1": "#061724", "bg2": "#0b2c44", "glass": "rgba(7,18,28,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#e7f5ff", "muted": "#b5d7ef", "accent": "#44b0ff"},
        },
        "Klimt": {
            "light": {"bg1": "#fff9e6", "bg2": "#f6d27a", "glass": "rgba(255,255,255,0.55)", "border": "rgba(120,80,10,0.18)", "text": "#2b200a", "muted": "#6b4f15", "accent": "#b48a00"},
            "dark":  {"bg1": "#1b1406", "bg2": "#3a2b0b", "glass": "rgba(22,16,6,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#fff3cf", "muted": "#f0d18a", "accent": "#f6d27a"},
        },
        "Kandinsky": {
            "light": {"bg1": "#f5f6ff", "bg2": "#d6d9ff", "glass": "rgba(255,255,255,0.55)", "border": "rgba(40,40,80,0.14)", "text": "#161635", "muted": "#3a3a66", "accent": "#3f5efb"},
            "dark":  {"bg1": "#0b0b20", "bg2": "#1a1a44", "glass": "rgba(10,10,24,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#eef0ff", "muted": "#c3c7ff", "accent": "#7a8cff"},
        },
        "Dalí": {
            "light": {"bg1": "#fff7f0", "bg2": "#ffd2a8", "glass": "rgba(255,255,255,0.55)", "border": "rgba(90,50,20,0.14)", "text": "#2a1b10", "muted": "#6b4024", "accent": "#7b2cbf"},
            "dark":  {"bg1": "#140a18", "bg2": "#2b1236", "glass": "rgba(16,8,20,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#ffeede", "muted": "#f3c8a6", "accent": "#c77dff"},
        },
        "Magritte": {
            "light": {"bg1": "#f2f7ff", "bg2": "#c6d7ff", "glass": "rgba(255,255,255,0.55)", "border": "rgba(30,50,90,0.14)", "text": "#0e1c35", "muted": "#314c7a", "accent": "#2f6fed"},
            "dark":  {"bg1": "#071224", "bg2": "#11254a", "glass": "rgba(8,14,26,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#e8f0ff", "muted": "#b8caff", "accent": "#73a6ff"},
        },
        "Matisse": {
            "light": {"bg1": "#fff3f7", "bg2": "#ffc1d8", "glass": "rgba(255,255,255,0.55)", "border": "rgba(90,20,40,0.14)", "text": "#2b0f18", "muted": "#6b2a3e", "accent": "#ff3b8d"},
            "dark":  {"bg1": "#1a0710", "bg2": "#3b0e22", "glass": "rgba(20,7,12,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#ffe2ee", "muted": "#ffb6d3", "accent": "#ff5ca3"},
        },
        "Rothko": {
            "light": {"bg1": "#fff5ef", "bg2": "#f6bfa5", "glass": "rgba(255,255,255,0.55)", "border": "rgba(120,40,20,0.14)", "text": "#2b120a", "muted": "#6b2f1f", "accent": "#b91c1c"},
            "dark":  {"bg1": "#1a0505", "bg2": "#3a0c0c", "glass": "rgba(18,6,6,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#ffe9dd", "muted": "#f6c5a6", "accent": "#ef4444"},
        },
        "Hopper": {
            "light": {"bg1": "#f7fbff", "bg2": "#d7e7f6", "glass": "rgba(255,255,255,0.55)", "border": "rgba(30,50,60,0.14)", "text": "#0f1b22", "muted": "#395463", "accent": "#0ea5e9"},
            "dark":  {"bg1": "#07121a", "bg2": "#0f2433", "glass": "rgba(7,14,20,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#eaf6ff", "muted": "#bfd8e6", "accent": "#38bdf8"},
        },
        "O’Keeffe": {
            "light": {"bg1": "#fff6f1", "bg2": "#ffd1c2", "glass": "rgba(255,255,255,0.55)", "border": "rgba(90,40,20,0.14)", "text": "#2a1410", "muted": "#6b3a2c", "accent": "#ea580c"},
            "dark":  {"bg1": "#140a06", "bg2": "#2b120b", "glass": "rgba(16,8,6,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#ffece4", "muted": "#ffd1c2", "accent": "#fb923c"},
        },
        "Rembrandt": {
            "light": {"bg1": "#fff6e8", "bg2": "#e7c08a", "glass": "rgba(255,255,255,0.55)", "border": "rgba(70,40,10,0.18)", "text": "#1f1408", "muted": "#5a3d18", "accent": "#7c3f00"},
            "dark":  {"bg1": "#120b05", "bg2": "#2b1a0a", "glass": "rgba(16,10,6,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#fff1d9", "muted": "#e7c08a", "accent": "#f59e0b"},
        },
        "Caravaggio": {
            "light": {"bg1": "#f7f2ef", "bg2": "#d9c7bb", "glass": "rgba(255,255,255,0.55)", "border": "rgba(30,20,20,0.14)", "text": "#1f1616", "muted": "#4a3b3b", "accent": "#111827"},
            "dark":  {"bg1": "#070707", "bg2": "#161616", "glass": "rgba(10,10,10,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#f7f2ef", "muted": "#d9c7bb", "accent": "#e5e7eb"},
        },
        "Basquiat": {
            "light": {"bg1": "#fff8e7", "bg2": "#ffe08a", "glass": "rgba(255,255,255,0.55)", "border": "rgba(60,30,0,0.14)", "text": "#251300", "muted": "#6b3d14", "accent": "#16a34a"},
            "dark":  {"bg1": "#0f0b06", "bg2": "#22180c", "glass": "rgba(12,8,6,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#fff2c6", "muted": "#ffd36e", "accent": "#22c55e"},
        },
        "Lichtenstein": {
            "light": {"bg1": "#f1f7ff", "bg2": "#cde1ff", "glass": "rgba(255,255,255,0.55)", "border": "rgba(10,30,80,0.14)", "text": "#0b1a3d", "muted": "#294a8a", "accent": "#ef4444"},
            "dark":  {"bg1": "#07112a", "bg2": "#102457", "glass": "rgba(7,12,30,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#eaf0ff", "muted": "#cde1ff", "accent": "#fb7185"},
        },
        "Turner": {
            "light": {"bg1": "#fff7ed", "bg2": "#ffd7b5", "glass": "rgba(255,255,255,0.55)", "border": "rgba(90,50,20,0.12)", "text": "#2a1b10", "muted": "#6b4024", "accent": "#f97316"},
            "dark":  {"bg1": "#120b06", "bg2": "#2a160c", "glass": "rgba(16,10,6,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#ffedd5", "muted": "#ffd7b5", "accent": "#fb923c"},
        },
        "Yayoi Kusama": {
            "light": {"bg1": "#fff5f7", "bg2": "#ffd1dc", "glass": "rgba(255,255,255,0.55)", "border": "rgba(80,20,40,0.14)", "text": "#2b0f18", "muted": "#6b2a3e", "accent": "#dc2626"},
            "dark":  {"bg1": "#14070c", "bg2": "#2b0f18", "glass": "rgba(16,7,10,0.55)", "border": "rgba(255,255,255,0.12)", "text": "#ffe2ee", "muted": "#ffd1dc", "accent": "#ef4444"},
        },
    }


KEYWORD_DEFAULT_COLOR = "#FF7F50"  # coral


# -----------------------------------
# Utilities
# -----------------------------------

def _t(lang: str, key: str) -> str:
    lang = lang if lang in T else "en"
    return T[lang].get(key, key)


def normalize_smart_quotes(text: str) -> str:
    return (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("，", ",")
    )


def try_read_text_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    raw = uploaded_file.read()
    try:
        return raw.decode("utf-8")
    except Exception:
        try:
            return raw.decode("utf-8-sig")
        except Exception:
            return raw.decode(errors="ignore")


def parse_dataset_from_text(text: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Accepts CSV/JSON/plain text.
    Returns (df, warnings).
    """
    warnings: List[str] = []
    text = (text or "").strip()
    if not text:
        return pd.DataFrame(), ["Empty input"]

    text = normalize_smart_quotes(text)

    # Try JSON first
    if text.startswith("{") or text.startswith("["):
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "data" in obj and isinstance(obj["data"], list):
                obj = obj["data"]
            if isinstance(obj, dict):
                # single record
                obj = [obj]
            df = pd.DataFrame(obj)
            return df, warnings
        except Exception as e:
            warnings.append(f"JSON parse failed, will try CSV. Reason: {e}")

    # CSV-ish: accept headerless by mapping to REQUIRED_COLUMNS if column count matches
    try:
        # Try pandas read_csv with python engine (more flexible with quotes)
        buf = io.StringIO(text)
        df = pd.read_csv(buf, engine="python")
        if df.shape[1] == len(REQUIRED_COLUMNS) and list(df.columns) != REQUIRED_COLUMNS:
            # If first row is actually data, and pandas guessed headers, try re-read without header.
            # But only do this if obvious header mismatch.
            pass
        return df, warnings
    except Exception as e:
        warnings.append(f"CSV parse failed: {e}")

    return pd.DataFrame(), warnings + ["Unable to parse as JSON or CSV"]


def load_default_dataset(path: str = DEFAULT_DATASET_PATH) -> Tuple[pd.DataFrame, List[str]]:
    warnings: List[str] = []
    if not os.path.exists(path):
        return pd.DataFrame(), [f"Default dataset not found: {path}"]

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        df, w = parse_dataset_from_text(content)
        warnings.extend(w)
        return df, warnings
    except Exception as e:
        return pd.DataFrame(), [f"Failed to load default dataset: {e}"]


def standardize_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Enforce canonical column names and types. Add missing cols as empty.
    """
    warnings: List[str] = []
    if df is None or df.empty:
        return pd.DataFrame(columns=REQUIRED_COLUMNS), ["Empty dataset"]

    # Strip/normalize column names
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Attempt best-effort mapping if columns resemble required ones
    # (minimal heuristics; extend as needed)
    col_map = {}
    lower = {c.lower(): c for c in df.columns}

    for req in REQUIRED_COLUMNS:
        if req in df.columns:
            continue
        if req.lower() in lower:
            col_map[lower[req.lower()]] = req

    if col_map:
        df = df.rename(columns=col_map)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    for c in missing:
        df[c] = ""  # empty placeholder

    # Keep only known + allow extras (extras retained but placed after required)
    extras = [c for c in df.columns if c not in REQUIRED_COLUMNS]
    df = df[REQUIRED_COLUMNS + extras]

    # Type conversions
    # Number -> numeric
    try:
        df["Number"] = pd.to_numeric(df["Number"], errors="coerce").fillna(0).astype(float)
    except Exception:
        warnings.append("Failed to coerce Number to numeric; set invalid to 0.")
        df["Number"] = 0.0

    # Deliverdate -> datetime (support YYYYMMDD)
    def _parse_date(x: Any) -> Optional[pd.Timestamp]:
        if pd.isna(x):
            return None
        s = str(x).strip()
        if not s:
            return None
        s = re.sub(r"[^\d\-\/]", "", s)
        try:
            if re.fullmatch(r"\d{8}", s):
                return pd.to_datetime(s, format="%Y%m%d", errors="coerce")
            return pd.to_datetime(s, errors="coerce")
        except Exception:
            return None

    try:
        df["_Deliverdate_dt"] = df["Deliverdate"].apply(_parse_date)
        bad = df["_Deliverdate_dt"].isna().sum()
        if bad > 0:
            warnings.append(f"Unparseable Deliverdate rows: {bad}")
    except Exception:
        warnings.append("Failed to parse Deliverdate into datetime.")

    # Clean strings
    for c in ["SupplierID", "CustomerID", "LicenseNo", "Category", "UDID", "DeviceNAME", "LotNO", "SerNo", "Model"]:
        try:
            df[c] = df[c].astype(str).fillna("").map(lambda s: s.strip())
        except Exception:
            pass

    return df, warnings


def dataset_quality_report(df: pd.DataFrame, parse_warnings: List[str]) -> Dict[str, Any]:
    if df is None or df.empty:
        return {
            "rows": 0,
            "missing_cols": REQUIRED_COLUMNS,
            "parse_warnings": parse_warnings or ["Empty dataset"],
            "duplicates": 0,
            "unparsed_dates": 0,
            "nonpositive_qty": 0,
        }

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    duplicates = int(df.duplicated(subset=REQUIRED_COLUMNS, keep="first").sum()) if all(c in df.columns for c in REQUIRED_COLUMNS) else int(df.duplicated().sum())
    unparsed_dates = int(df.get("_Deliverdate_dt", pd.Series(dtype="datetime64[ns]")).isna().sum()) if "_Deliverdate_dt" in df.columns else 0
    nonpositive_qty = int((df["Number"] <= 0).sum()) if "Number" in df.columns else 0

    return {
        "rows": int(len(df)),
        "missing_cols": missing_cols,
        "parse_warnings": parse_warnings or [],
        "duplicates": duplicates,
        "unparsed_dates": unparsed_dates,
        "nonpositive_qty": nonpositive_qty,
    }


def apply_theme_css(theme_name: str, mode: str, lang: str) -> None:
    themes = painter_themes()
    if theme_name not in themes:
        theme_name = list(themes.keys())[0]
    mode = "dark" if mode == "dark" else "light"
    tok = themes[theme_name][mode]

    # Minimal WOW glass + painter gradient + keyword coral.
    # Streamlit CSS hooks can change; keep conservative selectors.
    css = f"""
    <style>
      :root {{
        --rcc-bg1: {tok['bg1']};
        --rcc-bg2: {tok['bg2']};
        --rcc-glass: {tok['glass']};
        --rcc-border: {tok['border']};
        --rcc-text: {tok['text']};
        --rcc-muted: {tok['muted']};
        --rcc-accent: {tok['accent']};
        --rcc-coral: {KEYWORD_DEFAULT_COLOR};
      }}

      .stApp {{
        background: radial-gradient(1200px 600px at 20% 10%, rgba(255,255,255,0.20), transparent 60%),
                    linear-gradient(135deg, var(--rcc-bg1), var(--rcc-bg2));
        color: var(--rcc-text);
      }}

      /* Glass panels */
      div[data-testid="stVerticalBlockBorderWrapper"],
      section[data-testid="stSidebar"] > div {{
        background: var(--rcc-glass) !important;
        border: 1px solid var(--rcc-border) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(14px);
      }}

      /* Typography */
      h1, h2, h3, h4, h5, h6, p, li, label, span, div {{
        color: var(--rcc-text);
      }}
      small, .rcc-muted {{
        color: var(--rcc-muted) !important;
      }}

      /* Accent buttons */
      .stButton > button {{
        border-radius: 12px;
        border: 1px solid var(--rcc-border);
      }}
      .stButton > button[kind="primary"] {{
        background: var(--rcc-accent) !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
      }}

      /* Keyword highlighting */
      .rcc-keyword {{
        color: var(--rcc-coral);
        font-weight: 650;
      }}

      /* Status chips */
      .rcc-chip {{
        display:inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid var(--rcc-border);
        background: rgba(255,255,255,0.18);
        margin-right: 8px;
        font-size: 12px;
      }}

      /* Make Plotly backgrounds transparent-ish */
      .js-plotly-plot .plotly .main-svg {{
        background: transparent !important;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:2] + "*" * (len(key) - 6) + key[-4:]


def get_env_key(provider: str) -> Optional[str]:
    for name in ENV_KEY_MAP.get(provider, []):
        v = os.environ.get(name)
        if v:
            return v
    return None


def get_session_key(provider: str) -> Optional[str]:
    return st.session_state.get("api_keys", {}).get(provider)


def provider_status(provider: str) -> Tuple[str, str]:
    """
    Returns (status_label, source) where source is 'env'/'session'/'missing'
    """
    env = get_env_key(provider)
    if env:
        return "configured", "env"
    ses = get_session_key(provider)
    if ses:
        return "configured", "session"
    return "missing", "missing"


def any_provider_configured() -> bool:
    for p in PROVIDERS:
        s, src = provider_status(p)
        if s == "configured":
            return True
    return False


# -----------------------------------
# agents.yaml / SKILL.md loading & standardization
# -----------------------------------

DEFAULT_AGENTS_YAML_FALLBACK = """\
version: "1.0"
app:
  name: "RCC"
  default_language: "en"
  default_max_tokens: 12000
providers:
  openai: {}
  gemini: {}
  anthropic: {}
  grok: {}
system_prompt:
  source: "SKILL.md"
agents:
  - id: "dist_summary"
    name: "Distribution Summary"
    description: "Summarize distribution data and highlight anomalies."
    provider: "openai"
    model: "gpt-4o-mini"
    max_tokens: 12000
    input:
      format: "markdown"
      source: "dataset"
    output:
      format: "markdown"
    prompt_template: |
      You are analyzing a medical device distribution dataset.
      Produce:
      1) Executive summary
      2) Top suppliers/customers/models/licenses
      3) Time anomalies and possible explanations
      4) Compliance risks and data quality issues
pipelines:
  default:
    - dist_summary
ui_hints:
  icon: "dashboard"
"""


DEFAULT_SKILL_MD_FALLBACK = """\
# RCC SKILL.md (fallback)
You are a regulatory and distribution analytics assistant.

## Safety & Privacy
- Never request or reveal API keys or secrets.
- Treat user data as confidential.
- Do not fabricate claims; mark assumptions.

## Formatting
- Prefer structured Markdown with clear headings.
- When highlighting keywords, keep a dedicated section "Extracted Keywords".

## Language
- Follow user-selected output language (English or Traditional Chinese) when requested.
"""


def safe_load_text(path: str, fallback: str) -> str:
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return fallback


def detect_provider_from_model(model: str) -> str:
    m = (model or "").lower().strip()
    if m.startswith("gpt-") or "openai" in m:
        return "openai"
    if m.startswith("gemini-") or "google" in m:
        return "gemini"
    if m.startswith("claude") or m.startswith("anthropic:"):
        return "anthropic"
    if m.startswith("grok-") or "xai" in m:
        return "grok"
    return "openai"


def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or f"agent_{uuid.uuid4().hex[:8]}"


def standardize_agents_yaml(raw_yaml: str) -> Tuple[str, List[str]]:
    """
    Best-effort transformer from nonstandard YAML to canonical schema.
    Returns (standardized_yaml_text, warnings).
    """
    warnings: List[str] = []
    if yaml is None:
        return raw_yaml, ["PyYAML not installed; cannot standardize."]

    try:
        obj = yaml.safe_load(raw_yaml) if raw_yaml.strip() else None
    except Exception as e:
        return raw_yaml, [f"YAML parse error: {e}"]

    if obj is None:
        return DEFAULT_AGENTS_YAML_FALLBACK, ["Empty YAML; loaded fallback standard template."]

    # If it's a list, assume it's agents list
    if isinstance(obj, list):
        warnings.append("Top-level YAML is a list; wrapping into canonical schema under 'agents'.")
        obj = {"agents": obj}

    # If it has 'steps' but not agents/pipelines
    if isinstance(obj, dict) and "steps" in obj and "agents" not in obj:
        warnings.append("Detected 'steps' format; converting to agents + default pipeline.")
        steps = obj.get("steps", [])
        agents = []
        pipeline = []
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            name = step.get("name") or step.get("id") or f"Step {i+1}"
            aid = slugify(step.get("id") or name)
            model = step.get("model") or step.get("llm") or "gpt-4o-mini"
            provider = step.get("provider") or detect_provider_from_model(model)
            prompt = step.get("prompt") or step.get("instruction") or step.get("template") or ""
            agents.append(
                {
                    "id": aid,
                    "name": name,
                    "description": step.get("description", ""),
                    "provider": provider,
                    "model": model,
                    "max_tokens": int(step.get("max_tokens") or step.get("maxTokens") or 12000),
                    "input": {"format": "markdown", "source": "previous" if i > 0 else "manual"},
                    "output": {"format": "markdown"},
                    "prompt_template": prompt,
                }
            )
            pipeline.append(aid)
        obj = {
            "version": "1.0",
            "app": {"name": "RCC", "default_language": "en", "default_max_tokens": 12000},
            "providers": {p: {} for p in PROVIDERS},
            "system_prompt": {"source": "SKILL.md"},
            "agents": agents,
            "pipelines": {"default": pipeline},
        }

    # Ensure canonical wrapper
    if isinstance(obj, dict):
        if "version" not in obj:
            obj["version"] = "1.0"
            warnings.append("Missing 'version'; defaulted to 1.0.")
        if "app" not in obj:
            obj["app"] = {"name": "RCC", "default_language": "en", "default_max_tokens": 12000}
            warnings.append("Missing 'app'; added defaults.")
        if "providers" not in obj:
            obj["providers"] = {p: {} for p in PROVIDERS}
            warnings.append("Missing 'providers'; added placeholders.")
        if "system_prompt" not in obj:
            obj["system_prompt"] = {"source": "SKILL.md"}
            warnings.append("Missing 'system_prompt'; set source to SKILL.md.")
        if "agents" not in obj:
            # Try detect single agent fields
            maybe_prompt = obj.get("prompt") or obj.get("instruction") or obj.get("template")
            if maybe_prompt:
                model = obj.get("model") or "gpt-4o-mini"
                provider = obj.get("provider") or detect_provider_from_model(model)
                agent = {
                    "id": slugify(obj.get("id") or obj.get("name") or "agent"),
                    "name": obj.get("name") or "Agent",
                    "description": obj.get("description") or "",
                    "provider": provider,
                    "model": model,
                    "max_tokens": int(obj.get("max_tokens") or obj.get("maxTokens") or 12000),
                    "input": {"format": "markdown", "source": "manual"},
                    "output": {"format": "markdown"},
                    "prompt_template": maybe_prompt,
                }
                obj["agents"] = [agent]
                obj.setdefault("pipelines", {"default": [agent["id"]]})
                warnings.append("No 'agents' list found; converted single-agent YAML into canonical schema.")
            else:
                obj["agents"] = []
                warnings.append("No 'agents' found; created empty 'agents' list.")

        # Normalize agents
        agents = obj.get("agents", [])
        if isinstance(agents, dict):
            warnings.append("'agents' is a dict; wrapping into list.")
            agents = [agents]

        norm_agents = []
        seen = set()
        for a in agents:
            if not isinstance(a, dict):
                continue
            name = a.get("name") or a.get("id") or "Agent"
            aid = a.get("id") or slugify(name)
            if aid in seen:
                aid = f"{aid}_{uuid.uuid4().hex[:6]}"
                warnings.append(f"Duplicate agent id detected; renamed to {aid}.")
            seen.add(aid)

            model = a.get("model") or "gpt-4o-mini"
            provider = a.get("provider") or detect_provider_from_model(model)
            prompt = a.get("prompt_template") or a.get("prompt") or a.get("instruction") or ""

            max_tokens = a.get("max_tokens") or a.get("maxTokens") or a.get("max_output_tokens") or 12000
            try:
                max_tokens = int(max_tokens)
            except Exception:
                max_tokens = 12000
                warnings.append(f"Agent {aid}: invalid max_tokens; defaulted to 12000.")

            input_block = a.get("input") if isinstance(a.get("input"), dict) else {}
            output_block = a.get("output") if isinstance(a.get("output"), dict) else {}

            norm_agents.append(
                {
                    "id": aid,
                    "name": name,
                    "description": a.get("description", ""),
                    "provider": provider,
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": a.get("temperature", None),
                    "input": {
                        "format": input_block.get("format", "markdown"),
                        "source": input_block.get("source", "previous"),
                    },
                    "output": {"format": output_block.get("format", "markdown")},
                    "prompt_template": prompt,
                }
            )

        obj["agents"] = norm_agents

        # Pipelines
        if "pipelines" not in obj or not obj["pipelines"]:
            obj["pipelines"] = {"default": [a["id"] for a in norm_agents]}
            warnings.append("Missing 'pipelines'; generated default pipeline using agent order.")

    standardized = yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
    return standardized, warnings


# -----------------------------------
# Offline AI Note transformation (fallback)
# -----------------------------------

def extract_keywords_simple(text: str, max_k: int = 12) -> List[str]:
    """
    Simple keyword extraction: keep uppercase-ish codes, license strings, and frequent nouns-like tokens.
    """
    text = (text or "").strip()
    if not text:
        return []

    candidates = []
    # License-like / UDID-like / codes
    candidates += re.findall(r"(衛部醫器[^\s,，]{6,}號)", text)
    candidates += re.findall(r"\b\d{14}\b", text)  # UDID-like
    candidates += re.findall(r"\b[A-Z]{1,5}\d{2,6}\b", text)  # model-ish codes

    # Token frequency (naive)
    tokens = re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{4,}", text)
    freq: Dict[str, int] = {}
    for t in tokens:
        t = t.strip()
        if len(t) < 2:
            continue
        freq[t] = freq.get(t, 0) + 1
    top = [k for k, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[: max_k * 2]]

    # Combine, preserve order, unique
    out = []
    for k in candidates + top:
        if k not in out:
            out.append(k)
        if len(out) >= max_k:
            break
    return out[:max_k]


def organize_notes_offline(note_text: str, lang: str) -> str:
    kws = extract_keywords_simple(note_text, max_k=12)
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    if lang == "zh-TW":
        md = f"""# 筆記整理（離線模式）

## 摘要
- 由系統在**離線模式**下整理（未呼叫外部模型）。
- 請確認重點、責任歸屬與日期是否正確。
- 產出時間：{now}

## 重點
- （請人工補充）主要事件／決策／風險
- （請人工補充）下一步與期限

## 行動項目 / 負責人 / 到期日
| 行動 | 負責人 | 到期日 |
|---|---|---|
| （待補） | （待補） | （待補） |

## 風險與合規影響
- （待補）可能的合規風險、資料缺口、追蹤需求

## 待釐清問題
- （待補）哪些資訊缺少證據或需要確認？

## 擷取關鍵字
{chr(10).join([f"- {k}" for k in kws]) if kws else "- （無）"}

## 原始筆記
```text
{note_text.strip()}
```
"""
    else:
        md = f"""# Note Organizer (Offline Mode)

## Summary
- Produced in **offline mode** (no external model call).
- Please verify key points, ownership, and dates.
- Generated at: {now}

## Key Points
- (Fill in) Primary events / decisions / risks
- (Fill in) Next steps and deadlines

## Actions / Owners / Due Dates
| Action | Owner | Due Date |
|---|---|---|
| (TBD) | (TBD) | (TBD) |

## Risks & Compliance Impact
- (TBD) Potential compliance risks, data gaps, follow-ups

## Open Questions
- (TBD) What claims lack evidence or require confirmation?

## Extracted Keywords
{chr(10).join([f"- {k}" for k in kws]) if kws else "- (none)"}

## Original Notes
```text
{note_text.strip()}
```
"""
    return md


def highlight_keywords_html(md_text: str, keywords: List[str], color: str) -> str:
    if not md_text or not keywords:
        return md_text

    # Escape regex special chars in keywords; replace longest first to avoid partial overlap.
    kws = sorted(set([k for k in keywords if k.strip()]), key=len, reverse=True)
    out = md_text
    for k in kws:
        pattern = re.escape(k)
        out = re.sub(
            pattern,
            lambda m: f"<span class='rcc-keyword' style='color:{color};'>{m.group(0)}</span>",
            out,
        )
    return out


# -----------------------------------
# Distribution analytics
# -----------------------------------

def filter_df(df: pd.DataFrame,
              suppliers: List[str],
              customers: List[str],
              licenses: List[str],
              models: List[str],
              date_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]],
              qty_range: Optional[Tuple[float, float]]) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    dff = df.copy()
    if suppliers:
        dff = dff[dff["SupplierID"].isin(suppliers)]
    if customers:
        dff = dff[dff["CustomerID"].isin(customers)]
    if licenses:
        dff = dff[dff["LicenseNo"].isin(licenses)]
    if models:
        dff = dff[dff["Model"].isin(models)]
    if date_range and "_Deliverdate_dt" in dff.columns:
        start, end = date_range
        if start is not None:
            dff = dff[dff["_Deliverdate_dt"] >= start]
        if end is not None:
            dff = dff[dff["_Deliverdate_dt"] <= end]
    if qty_range:
        lo, hi = qty_range
        dff = dff[(dff["Number"] >= lo) & (dff["Number"] <= hi)]
    return dff


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    if df is None or df.empty:
        return {"rows": 0, "unique_suppliers": 0, "unique_customers": 0, "total_units": 0}
    return {
        "rows": int(len(df)),
        "unique_suppliers": int(df["SupplierID"].nunique()),
        "unique_customers": int(df["CustomerID"].nunique()),
        "total_units": float(df["Number"].sum()),
    }


def build_sankey(df: pd.DataFrame, top_n: int = 30) -> Optional["go.Figure"]:
    if go is None or df is None or df.empty:
        return None

    # Aggregate to reduce complexity
    agg = (
        df.groupby(["SupplierID", "LicenseNo", "Model", "CustomerID"], as_index=False)["Number"]
        .sum()
        .sort_values("Number", ascending=False)
    )
    agg = agg.head(max(5, top_n))

    # Nodes
    suppliers = agg["SupplierID"].unique().tolist()
    licenses = agg["LicenseNo"].unique().tolist()
    models = agg["Model"].unique().tolist()
    customers = agg["CustomerID"].unique().tolist()

    nodes = suppliers + licenses + models + customers
    idx = {n: i for i, n in enumerate(nodes)}

    # Links: Supplier->License, License->Model, Model->Customer
    def link_sum(cols: List[str]) -> pd.DataFrame:
        return agg.groupby(cols, as_index=False)["Number"].sum()

    l1 = link_sum(["SupplierID", "LicenseNo"])
    l2 = link_sum(["LicenseNo", "Model"])
    l3 = link_sum(["Model", "CustomerID"])

    sources = []
    targets = []
    values = []

    for _, r in l1.iterrows():
        sources.append(idx[r["SupplierID"]])
        targets.append(idx[r["LicenseNo"]])
        values.append(float(r["Number"]))
    for _, r in l2.iterrows():
        sources.append(idx[r["LicenseNo"]])
        targets.append(idx[r["Model"]])
        values.append(float(r["Number"]))
    for _, r in l3.iterrows():
        sources.append(idx[r["Model"]])
        targets.append(idx[r["CustomerID"]])
        values.append(float(r["Number"]))

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=14,
                    thickness=14,
                    line=dict(color="rgba(0,0,0,0.15)", width=0.5),
                    label=nodes,
                ),
                link=dict(source=sources, target=targets, value=values),
            )
        ]
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=520)
    return fig


def build_temporal_pulse(df: pd.DataFrame, freq: str = "D") -> Optional["go.Figure"]:
    if go is None or df is None or df.empty or "_Deliverdate_dt" not in df.columns:
        return None

    dff = df.dropna(subset=["_Deliverdate_dt"]).copy()
    if dff.empty:
        return None

    # Aggregate by time
    ts = dff.set_index("_Deliverdate_dt")["Number"].resample(freq).sum().reset_index()
    ts = ts.sort_values("_Deliverdate_dt")
    ts["ma"] = ts["Number"].rolling(7, min_periods=2).mean()

    # Anomaly: z-score-ish on residuals
    residual = ts["Number"] - ts["ma"].fillna(ts["Number"].mean())
    denom = residual.std() if residual.std() and residual.std() > 0 else 1.0
    ts["z"] = residual / denom
    ts["anomaly"] = ts["z"].abs() >= 2.5

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts["_Deliverdate_dt"], y=ts["Number"], mode="lines", name="Units"))
    fig.add_trace(go.Scatter(x=ts["_Deliverdate_dt"], y=ts["ma"], mode="lines", name="7d MA"))
    ano = ts[ts["anomaly"]]
    if not ano.empty:
        fig.add_trace(go.Scatter(
            x=ano["_Deliverdate_dt"], y=ano["Number"],
            mode="markers", name="Anomaly",
            marker=dict(size=10, color="rgba(255,99,71,0.9)", line=dict(width=1, color="rgba(0,0,0,0.2)"))
        ))
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=420)
    return fig


def build_mosaic_heatmap(df: pd.DataFrame, top_n_customers: int = 25, top_n_models: int = 20) -> Optional["go.Figure"]:
    if go is None or df is None or df.empty:
        return None

    # Top customers & models by volume
    cust = df.groupby("CustomerID")["Number"].sum().sort_values(ascending=False).head(top_n_customers).index
    mod = df.groupby("Model")["Number"].sum().sort_values(ascending=False).head(top_n_models).index
    dff = df[df["CustomerID"].isin(cust) & df["Model"].isin(mod)].copy()
    if dff.empty:
        return None

    pivot = dff.pivot_table(index="CustomerID", columns="Model", values="Number", aggfunc="sum", fill_value=0)

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Blues",
            hoverongaps=False,
        )
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=520)
    return fig


def build_classic_charts(df: pd.DataFrame, top_n: int = 12) -> Dict[str, Any]:
    charts: Dict[str, Any] = {}
    if px is None or df is None or df.empty:
        return charts

    # Timeline
    if "_Deliverdate_dt" in df.columns:
        dff = df.dropna(subset=["_Deliverdate_dt"]).copy()
        if not dff.empty:
            ts = dff.groupby("_Deliverdate_dt", as_index=False)["Number"].sum().sort_values("_Deliverdate_dt")
            charts["timeline"] = px.area(ts, x="_Deliverdate_dt", y="Number", title="")

    # Model distribution
    mod = df.groupby("Model", as_index=False)["Number"].sum().sort_values("Number", ascending=False).head(top_n)
    charts["model_dist"] = px.pie(mod, names="Model", values="Number", title="")

    # Top customers
    cust = df.groupby("CustomerID", as_index=False)["Number"].sum().sort_values("Number", ascending=False).head(top_n)
    charts["top_customers"] = px.bar(cust, x="CustomerID", y="Number", title="")

    # License usage
    lic = df.groupby("LicenseNo", as_index=False)["Number"].sum().sort_values("Number", ascending=False).head(top_n)
    charts["license_usage"] = px.bar(lic, x="LicenseNo", y="Number", title="")

    for k, fig in charts.items():
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return charts


# -----------------------------------
# UI building blocks
# -----------------------------------

def status_strip(lang: str) -> None:
    st.markdown(f"### {_t(lang, 'status_strip')}")
    chips = []

    # Provider chips
    for p in PROVIDERS:
        status, src = provider_status(p)
        if status == "configured" and src == "env":
            label = f"{p.upper()}: {_t(lang, 'configured_env')}"
        elif status == "configured" and src == "session":
            label = f"{p.upper()}: {_t(lang, 'configured_session')}"
        else:
            label = f"{p.upper()}: {_t(lang, 'missing')}"
        chips.append(f"<span class='rcc-chip'>{label}</span>")

    # Dataset chip
    df = st.session_state.get("dataset_df")
    rows = int(len(df)) if isinstance(df, pd.DataFrame) else 0
    chips.append(f"<span class='rcc-chip'>DATA: {rows} rows</span>")

    # Agent pipeline chip
    pipeline_state = st.session_state.get("pipeline_state", {"status": "idle"})
    chips.append(f"<span class='rcc-chip'>{_t(lang,'agent_pipeline')}: {pipeline_state.get('status','idle')}</span>")

    st.markdown("".join(chips), unsafe_allow_html=True)


def wow_header_controls(lang: str) -> None:
    with st.sidebar:
        st.markdown(f"## {APP_TITLE}")

        # Language
        sel_lang = st.selectbox(_t(lang, "language"), options=["en", "zh-TW"], index=0 if lang == "en" else 1)
        st.session_state["lang"] = sel_lang

        # Theme + mode
        themes = list(painter_themes().keys())
        current_theme = st.session_state.get("theme_name", themes[0])
        current_mode = st.session_state.get("theme_mode", "light")

        theme_name = st.selectbox(_t(sel_lang, "theme"), options=themes, index=themes.index(current_theme) if current_theme in themes else 0)
        mode = st.radio(_t(sel_lang, "mode"), options=["light", "dark"], index=0 if current_mode == "light" else 1, horizontal=True,
                        format_func=lambda x: _t(sel_lang, x))

        colj1, colj2 = st.columns([1, 1])
        with colj1:
            if st.button(_t(sel_lang, "jackpot"), use_container_width=True):
                theme_name = random.choice(themes)
                st.session_state["theme_name"] = theme_name
        with colj2:
            st.caption(f"{theme_name} / {_t(sel_lang, mode)}")

        st.session_state["theme_name"] = theme_name
        st.session_state["theme_mode"] = mode


def dataset_ingestion_panel(lang: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    st.markdown(f"## {_t(lang, 'data_source')}")

    use_default = st.toggle(_t(lang, "use_default"), value=st.session_state.get("use_default_dataset", True))
    st.session_state["use_default_dataset"] = use_default

    parse_warnings: List[str] = []
    df: pd.DataFrame = st.session_state.get("dataset_df", pd.DataFrame(columns=REQUIRED_COLUMNS))

    if use_default:
        if st.session_state.get("_default_loaded") is not True:
            default_df, w = load_default_dataset(DEFAULT_DATASET_PATH)
            default_df, w2 = standardize_columns(default_df)
            parse_warnings = w + w2
            st.session_state["dataset_df"] = default_df
            st.session_state["dataset_parse_warnings"] = parse_warnings
            st.session_state["_default_loaded"] = True
        else:
            parse_warnings = st.session_state.get("dataset_parse_warnings", [])
    else:
        st.session_state["_default_loaded"] = False

        st.markdown(f"### {_t(lang, 'paste_or_upload')}")
        pasted = st.text_area(_t(lang, "paste_here"), height=160, placeholder="CSV header + rows, or JSON array of records")
        uploaded = st.file_uploader(_t(lang, "upload_file"), type=["csv", "json", "txt"])

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(_t(lang, "load_dataset"), type="primary", use_container_width=True):
                content = ""
                if uploaded is not None:
                    content = try_read_text_file(uploaded)
                elif pasted.strip():
                    content = pasted
                df_new, w = parse_dataset_from_text(content)
                df_new, w2 = standardize_columns(df_new)
                parse_warnings = w + w2
                st.session_state["dataset_df"] = df_new
                st.session_state["dataset_parse_warnings"] = parse_warnings
        with col2:
            if st.button(_t(lang, "clear_dataset"), use_container_width=True):
                st.session_state["dataset_df"] = pd.DataFrame(columns=REQUIRED_COLUMNS)
                st.session_state["dataset_parse_warnings"] = ["Cleared by user"]

        parse_warnings = st.session_state.get("dataset_parse_warnings", [])

    df = st.session_state.get("dataset_df", pd.DataFrame(columns=REQUIRED_COLUMNS))
    q = dataset_quality_report(df, st.session_state.get("dataset_parse_warnings", []))

    # Quality + KPI row
    kpis = compute_kpis(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(_t(lang, "rows"), kpis["rows"])
    c2.metric(_t(lang, "unique_suppliers"), kpis["unique_suppliers"])
    c3.metric(_t(lang, "unique_customers"), kpis["unique_customers"])
    c4.metric(_t(lang, "total_units"), f"{kpis['total_units']:.0f}")

    with st.expander(_t(lang, "data_quality"), expanded=False):
        st.write({
            _t(lang, "missing_cols"): q["missing_cols"],
            _t(lang, "parse_warnings"): q["parse_warnings"],
            "duplicates": q["duplicates"],
            "unparsed_dates": q["unparsed_dates"],
            "nonpositive_qty": q["nonpositive_qty"],
        })

    st.markdown(f"### {_t(lang, 'dataset_preview')}")
    st.dataframe(df.head(50), use_container_width=True)

    return df, q


def distribution_filters(lang: str, df: pd.DataFrame) -> Dict[str, Any]:
    st.markdown(f"## {_t(lang, 'filters')}")
    if df is None or df.empty:
        st.info("No dataset loaded.")
        return {"suppliers": [], "customers": [], "licenses": [], "models": [], "date_range": None, "qty_range": None, "top_n": 20}

    # Options
    suppliers_opt = sorted([x for x in df["SupplierID"].dropna().astype(str).unique().tolist() if x.strip()])
    customers_opt = sorted([x for x in df["CustomerID"].dropna().astype(str).unique().tolist() if x.strip()])
    licenses_opt = sorted([x for x in df["LicenseNo"].dropna().astype(str).unique().tolist() if x.strip()])
    models_opt = sorted([x for x in df["Model"].dropna().astype(str).unique().tolist() if x.strip()])

    colA, colB = st.columns(2)
    with colA:
        suppliers = st.multiselect(_t(lang, "supplier_filter"), suppliers_opt, default=st.session_state.get("flt_suppliers", []))
        customers = st.multiselect(_t(lang, "customer_filter"), customers_opt, default=st.session_state.get("flt_customers", []))
    with colB:
        licenses = st.multiselect(_t(lang, "license_filter"), licenses_opt, default=st.session_state.get("flt_licenses", []))
        models = st.multiselect(_t(lang, "model_filter"), models_opt, default=st.session_state.get("flt_models", []))

    # Date range
    date_range = None
    if "_Deliverdate_dt" in df.columns and df["_Deliverdate_dt"].notna().any():
        dmin = pd.to_datetime(df["_Deliverdate_dt"].min()).date()
        dmax = pd.to_datetime(df["_Deliverdate_dt"].max()).date()
        dr = st.date_input(_t(lang, "date_range"), value=(dmin, dmax), min_value=dmin, max_value=dmax)
        if isinstance(dr, tuple) and len(dr) == 2:
            date_range = (pd.to_datetime(dr[0]), pd.to_datetime(dr[1]))

    # Qty range
    qty_range = None
    qmin = float(df["Number"].min()) if "Number" in df.columns else 0.0
    qmax = float(df["Number"].max()) if "Number" in df.columns else 0.0
    if qmax > qmin:
        qr = st.slider(_t(lang, "qty_range"), min_value=float(qmin), max_value=float(qmax), value=(float(qmin), float(qmax)))
        qty_range = qr

    top_n = st.slider(_t(lang, "top_n"), min_value=10, max_value=200, value=int(st.session_state.get("flt_top_n", 30)), step=5)

    if st.button(_t(lang, "reset_filters")):
        for k in ["flt_suppliers", "flt_customers", "flt_licenses", "flt_models", "flt_top_n"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    # Persist
    st.session_state["flt_suppliers"] = suppliers
    st.session_state["flt_customers"] = customers
    st.session_state["flt_licenses"] = licenses
    st.session_state["flt_models"] = models
    st.session_state["flt_top_n"] = top_n

    return {
        "suppliers": suppliers,
        "customers": customers,
        "licenses": licenses,
        "models": models,
        "date_range": date_range,
        "qty_range": qty_range,
        "top_n": top_n,
    }


# -----------------------------------
# Pages
# -----------------------------------

def page_distribution_lab(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_distribution')}")
    status_strip(lang)

    df, q = dataset_ingestion_panel(lang)
    flt = distribution_filters(lang, df)
    dff = filter_df(df, **{k: flt[k] for k in ["suppliers", "customers", "licenses", "models", "date_range", "qty_range"]})

    st.markdown("---")
    tab1, tab2 = st.tabs([_t(lang, "wow_graphs"), _t(lang, "classic_charts")])

    with tab1:
        st.markdown(f"## {_t(lang, 'sankey_title')}")
        fig1 = build_sankey(dff, top_n=flt["top_n"])
        if fig1 is not None:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Sankey unavailable (missing Plotly) or no data after filtering.")

        st.markdown(f"## {_t(lang, 'pulse_title')}")
        fig2 = build_temporal_pulse(dff, freq="D")
        if fig2 is not None:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Temporal chart unavailable (no parsable dates) or no data after filtering.")

        st.markdown(f"## {_t(lang, 'mosaic_title')}")
        fig3 = build_mosaic_heatmap(dff, top_n_customers=min(40, max(15, flt["top_n"])), top_n_models=min(30, max(12, flt["top_n"] // 2)))
        if fig3 is not None:
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Heatmap unavailable or no data after filtering.")

    with tab2:
        charts = build_classic_charts(dff, top_n=min(25, max(10, flt["top_n"] // 2)))
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### {_t(lang, 'timeline')}")
            if "timeline" in charts:
                st.plotly_chart(charts["timeline"], use_container_width=True)
            else:
                st.info("No timeline data.")

            st.markdown(f"### {_t(lang, 'top_customers')}")
            if "top_customers" in charts:
                st.plotly_chart(charts["top_customers"], use_container_width=True)
            else:
                st.info("No customer ranking data.")

        with c2:
            st.markdown(f"### {_t(lang, 'model_dist')}")
            if "model_dist" in charts:
                st.plotly_chart(charts["model_dist"], use_container_width=True)
            else:
                st.info("No model distribution data.")

            st.markdown(f"### {_t(lang, 'license_usage')}")
            if "license_usage" in charts:
                st.plotly_chart(charts["license_usage"], use_container_width=True)
            else:
                st.info("No license usage data.")


def page_agents_studio(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_agents')}")
    status_strip(lang)

    if yaml is None:
        st.error("PyYAML is not installed. Agents Studio requires PyYAML.")
        return

    st.markdown(f"## {_t(lang, 'agents_yaml')}")

    # Load current YAML from session or disk/fallback
    if "agents_yaml_raw" not in st.session_state:
        disk_yaml = safe_load_text(DEFAULT_AGENTS_YAML_PATH, DEFAULT_AGENTS_YAML_FALLBACK)
        st.session_state["agents_yaml_raw"] = disk_yaml
        standardized, w = standardize_agents_yaml(disk_yaml)
        st.session_state["agents_yaml_std"] = standardized
        st.session_state["agents_yaml_warnings"] = w

    colL, colR = st.columns([1, 1])

    with colL:
        st.markdown(f"### {_t(lang, 'paste_agents_yaml')}")
        pasted = st.text_area("", value="", height=160, placeholder="Paste YAML here")

        uploaded = st.file_uploader(_t(lang, "upload_agents_yaml"), type=["yaml", "yml"])

        if st.button(_t(lang, "standardize"), type="primary"):
            raw = ""
            if uploaded is not None:
                raw = try_read_text_file(uploaded)
            elif pasted.strip():
                raw = pasted
            else:
                raw = st.session_state.get("agents_yaml_raw", "")

            std, w = standardize_agents_yaml(raw)
            st.session_state["agents_yaml_raw"] = raw
            st.session_state["agents_yaml_std"] = std
            st.session_state["agents_yaml_warnings"] = w

    with colR:
        st.markdown(f"### {_t(lang, 'yaml_status')}")
        w = st.session_state.get("agents_yaml_warnings", [])
        if w:
            st.warning("\n".join([f"- {x}" for x in w]))
        else:
            st.success("Standardized YAML is ready.")

        std_text = st.session_state.get("agents_yaml_std", DEFAULT_AGENTS_YAML_FALLBACK)
        st.download_button(
            label=_t(lang, "download_yaml"),
            data=std_text.encode("utf-8"),
            file_name="agents.standardized.yaml",
            mime="text/yaml",
        )

        if st.button(_t(lang, "import_yaml")):
            # Validate minimally: must contain agents list
            try:
                obj = yaml.safe_load(std_text)
                if not isinstance(obj, dict) or "agents" not in obj:
                    st.error("Invalid standardized YAML: missing 'agents'.")
                else:
                    st.session_state["agents_yaml_active"] = std_text
                    st.success("Imported standardized YAML into active config (session).")
            except Exception as e:
                st.error(f"Import failed: {e}")

    st.markdown("### Active standardized YAML (editable)")
    edited = st.text_area("", value=st.session_state.get("agents_yaml_std", DEFAULT_AGENTS_YAML_FALLBACK), height=420)
    st.session_state["agents_yaml_std"] = edited

    st.markdown(f"## {_t(lang, 'skill_md')}")
    skill = safe_load_text(DEFAULT_SKILL_MD_PATH, DEFAULT_SKILL_MD_FALLBACK)
    st.code(skill, language="markdown")


def page_settings_keys(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_settings')}")
    status_strip(lang)

    if "api_keys" not in st.session_state:
        st.session_state["api_keys"] = {}

    st.info(_t(lang, "never_shown") + ": env keys are detected but never displayed.")

    for p in PROVIDERS:
        st.markdown(f"## {p.upper()} — {_t(lang, 'settings')}")
        env_key = get_env_key(p)
        ses_key = get_session_key(p)

        if env_key:
            st.success(f"{_t(lang, 'configured_env')}")
            st.caption(_t(lang, "never_shown"))
        elif ses_key:
            st.success(f"{_t(lang, 'configured_session')}: {mask_key(ses_key)}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(_t(lang, "clear_key"), key=f"clear_{p}"):
                    st.session_state["api_keys"][p] = ""
                    st.rerun()
            with col2:
                st.caption("Stored in session only.")
        else:
            st.warning(_t(lang, "missing"))
            key_in = st.text_input(_t(lang, "enter_key"), type="password", key=f"key_in_{p}")
            if st.button(_t(lang, "save_key"), key=f"save_{p}", type="primary"):
                if key_in.strip():
                    st.session_state["api_keys"][p] = key_in.strip()
                    st.rerun()
                else:
                    st.error("Empty key.")


def page_ai_note_keeper(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_note_keeper')}")
    status_strip(lang)

    online = any_provider_configured()
    st.caption(_t(lang, "online_mode") if online else _t(lang, "offline_mode"))
    if not online:
        st.warning(_t(lang, "not_configured_ai"))

    note = st.text_area(_t(lang, "note_input"), height=220, placeholder="Paste meeting notes / audit notes / markdown…")
    default_prompt_en = """Transform the pasted notes into organized Markdown with:
- Title
- Summary (3–7 bullets)
- Key Points
- Actions/Owners/Due Dates (table if possible)
- Risks & Compliance Impact
- Open Questions
- Extracted Keywords
Highlight keywords in coral color.
"""
    default_prompt_zh = """將貼上的筆記整理成結構化 Markdown，包含：
- 標題
- 摘要（3–7 點）
- 重點
- 行動/負責人/到期日（可用表格）
- 風險與合規影響
- 待釐清問題
- 擷取關鍵字
並以珊瑚色標示關鍵字。
"""
    prompt = st.text_area(_t(lang, "note_prompt"), height=140, value=default_prompt_zh if lang == "zh-TW" else default_prompt_en)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        model = st.selectbox(_t(lang, "note_model"), options=SUPPORTED_MODELS, index=0)
    with col2:
        max_tokens = st.number_input(_t(lang, "note_maxtokens"), min_value=256, max_value=200000, value=12000, step=256)
    with col3:
        st.caption("")

    # For this single-file app, the LLM call is intentionally not implemented to avoid fragile provider SDK dependencies.
    # Offline transformation is always available and safe.
    if st.button(_t(lang, "transform"), type="primary"):
        md = organize_notes_offline(note, lang)
        st.session_state["note_output_md"] = md

    st.markdown(f"## {_t(lang, 'ai_magics')}")
    with st.expander(_t(lang, "ai_keywords"), expanded=True):
        kws = st.text_input(_t(lang, "keywords_list"), value="")
        color = st.color_picker(_t(lang, "keyword_color"), value=KEYWORD_DEFAULT_COLOR)
        if st.button(_t(lang, "apply_keywords"), use_container_width=True):
            out = st.session_state.get("note_output_md", "")
            kw_list = [k.strip() for k in kws.split(",") if k.strip()]
            highlighted = highlight_keywords_html(out, kw_list, color)
            st.session_state["note_output_md"] = highlighted

    st.markdown(f"## {_t(lang, 'output')}")
    out = st.session_state.get("note_output_md", "")
    if out:
        # Render markdown with HTML spans for keyword highlighting
        st.markdown(out, unsafe_allow_html=True)
        st.download_button("Download markdown", data=out.encode("utf-8"), file_name="note.organized.md", mime="text/markdown")
    else:
        st.info("No output yet. Transform notes to generate organized markdown.")


def page_command_center(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_command_center')}")
    status_strip(lang)
    st.markdown(
        """
        This page is a placeholder for the Regulatory Dashboard (v2 parity) in Streamlit.
        Recommended next steps:
        - Add regulatory datasets (510k, recalls, ADR, GUDID) ingestion
        - Implement unified search + result cards
        - Add decision code distribution and severity indicators
        - Connect “Analyze” buttons to the Agent Pipeline Runner
        """
    )


# -----------------------------------
# Main
# -----------------------------------

def init_session_defaults() -> None:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    if "theme_name" not in st.session_state:
        st.session_state["theme_name"] = list(painter_themes().keys())[0]
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "light"
    if "api_keys" not in st.session_state:
        st.session_state["api_keys"] = {}
    if "pipeline_state" not in st.session_state:
        st.session_state["pipeline_state"] = {"status": "idle", "last_run": None}
    if "use_default_dataset" not in st.session_state:
        st.session_state["use_default_dataset"] = True


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    init_session_defaults()
    # Sidebar controls can change language; use current session lang for initial draw
    lang = st.session_state.get("lang", "en")
    wow_header_controls(lang)

    # Apply CSS after selection
    lang = st.session_state.get("lang", "en")
    apply_theme_css(st.session_state.get("theme_name"), st.session_state.get("theme_mode"), lang)

    # Nav
    page = st.sidebar.radio(
        "Navigation",
        options=[
            _t(lang, "nav_command_center"),
            _t(lang, "nav_distribution"),
            _t(lang, "nav_note_keeper"),
            _t(lang, "nav_agents"),
            _t(lang, "nav_settings"),
        ],
    )

    # Global search placeholder (context-aware hook)
    st.sidebar.text_input(_t(lang, "global_search"), value="", key="global_search")

    if page == _t(lang, "nav_distribution"):
        page_distribution_lab(lang)
    elif page == _t(lang, "nav_note_keeper"):
        page_ai_note_keeper(lang)
    elif page == _t(lang, "nav_agents"):
        page_agents_studio(lang)
    elif page == _t(lang, "nav_settings"):
        page_settings_keys(lang)
    else:
        page_command_center(lang)


if __name__ == "__main__":
    main()
