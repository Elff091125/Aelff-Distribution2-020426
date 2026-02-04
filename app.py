from __future__ import annotations

import os
import io
import re
import csv
import json
import uuid
import random
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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


APP_TITLE = "Regulatory Command Center (RCC) — v3.2"
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
MIN_IMPORT_COLUMNS = ["SupplierID", "Deliverdate", "CustomerID", "Model", "Number"]

KEYWORD_DEFAULT_COLOR = "#FF7F50"  # coral


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
        "dataset_manager": "Dataset Manager",
        "data_source": "Dataset Source",
        "use_default": "Use default dataset",
        "paste": "Paste dataset",
        "upload": "Upload dataset",
        "paste_here": "Paste CSV / JSON / JSONL / Text here",
        "upload_file": "Upload file (CSV / JSON / TXT)",
        "preview_count": "Preview rows",
        "preview": "Preview",
        "import": "Import",
        "cancel": "Cancel staged preview",
        "raw_preview": "Raw preview",
        "std_preview": "Standardized preview",
        "issues_only": "Show issue rows only",
        "mapping": "Column mapping",
        "mapping_help": "If headers don't match, map source columns to canonical fields.",
        "import_report": "Import report",
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
        "wow_indicators": "WOW Indicators",
        "data_health_score": "Data Health Score",
        "concentration_risk": "Concentration Risk",
        "anomaly_beacons": "Anomaly Beacons",
        "wow_graphs": "WOW Graphs",
        "sankey_title": "Supply-Chain Symphony Sankey",
        "network_title": "Interactive Distribution Network (Click nodes)",
        "pulse_title": "Temporal Pulse + Anomaly Beacons",
        "mosaic_title": "Customer–Model Mosaic Heatmap",
        "wow_plus": "WOW+ Visuals",
        "pareto_title": "Pareto Power Wall (80/20)",
        "lorenz_title": "Lorenz Curve + Gini Index",
        "treemap_title": "Category Landscape Treemap",
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
        "format_detected": "Detected format",
        "confidence": "Standardization confidence",
        "cannot_import": "Cannot import until required fields are mapped",
        "imported": "Imported standardized dataset into active session dataset.",
        "staged_ready": "Staged preview is ready. Review and click Import.",
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
        "dataset_manager": "資料集管理",
        "data_source": "資料來源",
        "use_default": "使用預設資料集",
        "paste": "貼上資料集",
        "upload": "上傳資料集",
        "paste_here": "在此貼上 CSV / JSON / JSONL / 文字",
        "upload_file": "上傳檔案（CSV / JSON / TXT）",
        "preview_count": "預覽筆數",
        "preview": "預覽",
        "import": "匯入",
        "cancel": "取消暫存預覽",
        "raw_preview": "原始預覽",
        "std_preview": "標準化預覽",
        "issues_only": "僅顯示問題列",
        "mapping": "欄位對應",
        "mapping_help": "若欄位名稱不一致，請將來源欄位對應到標準欄位。",
        "import_report": "匯入報告",
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
        "wow_indicators": "WOW 指標",
        "data_health_score": "資料健康分數",
        "concentration_risk": "集中風險",
        "anomaly_beacons": "異常燈塔",
        "wow_graphs": "WOW 圖表",
        "sankey_title": "供應鏈交響 Sankey",
        "network_title": "互動式配送網路（點擊節點）",
        "pulse_title": "時間脈動＋異常燈塔",
        "mosaic_title": "客戶–型號 馬賽克熱圖",
        "wow_plus": "WOW+ 圖表",
        "pareto_title": "帕累托能量牆（80/20）",
        "lorenz_title": "洛倫茲曲線＋基尼係數",
        "treemap_title": "分類地景 Treemap",
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
        "format_detected": "偵測格式",
        "confidence": "標準化信心分數",
        "cannot_import": "必要欄位尚未對應完成，無法匯入",
        "imported": "已將標準化資料集匯入本次 Session。",
        "staged_ready": "暫存預覽已就緒，請確認後按下匯入。",
    },
}


def _t(lang: str, key: str) -> str:
    lang = lang if lang in T else "en"
    return T[lang].get(key, key)


def normalize_smart_quotes(text: str) -> str:
    # IMPORTANT: only use this AFTER parsing CSV, not before.
    return (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("，", ",")
    )


def strip_dataset_prefix(text: str) -> str:
    # Handle cases like "Datasets:SupplierID,Deliverdate,..."
    s = (text or "").lstrip()
    s = re.sub(r"^(datasets?|data)\s*:\s*", "", s, flags=re.IGNORECASE)
    return s


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
    env = get_env_key(provider)
    if env:
        return "configured", "env"
    ses = get_session_key(provider)
    if ses:
        return "configured", "session"
    return "missing", "missing"


def any_provider_configured() -> bool:
    for p in PROVIDERS:
        s, _ = provider_status(p)
        if s == "configured":
            return True
    return False


# -----------------------------------
# Themes (same 20 painter themes as prior versions; abbreviated here)
# -----------------------------------

def painter_themes() -> Dict[str, Dict[str, Dict[str, str]]]:
    # (Same palette set as v3.1, unchanged)
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


def apply_theme_css(theme_name: str, mode: str) -> None:
    themes = painter_themes()
    if theme_name not in themes:
        theme_name = list(themes.keys())[0]
    mode = "dark" if mode == "dark" else "light"
    tok = themes[theme_name][mode]
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
      div[data-testid="stVerticalBlockBorderWrapper"],
      section[data-testid="stSidebar"] > div {{
        background: var(--rcc-glass) !important;
        border: 1px solid var(--rcc-border) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(14px);
      }}
      h1,h2,h3,h4,h5,h6,p,li,label,span,div {{ color: var(--rcc-text); }}
      .rcc-muted {{ color: var(--rcc-muted) !important; }}
      .stButton > button {{ border-radius: 12px; border: 1px solid var(--rcc-border); }}
      .stButton > button[kind="primary"] {{
        background: var(--rcc-accent) !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
      }}
      .rcc-keyword {{ color: var(--rcc-coral); font-weight: 650; }}
      .rcc-chip {{
        display:inline-block; padding: 6px 10px; border-radius: 999px;
        border: 1px solid var(--rcc-border); background: rgba(255,255,255,0.18);
        margin-right: 8px; font-size: 12px;
      }}
      .rcc-ind {{
        padding: 12px 12px; border-radius: 14px; border: 1px solid var(--rcc-border);
        background: rgba(255,255,255,0.16);
      }}
      .js-plotly-plot .plotly .main-svg {{ background: transparent !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# -----------------------------------
# Dataset parsing + standardization
# -----------------------------------

ALIASES = {
    "supplierid": "SupplierID", "supplier_id": "SupplierID", "supplier": "SupplierID", "vendor": "SupplierID",
    "deliverdate": "Deliverdate", "deliver_date": "Deliverdate", "deliverydate": "Deliverdate", "delivery_date": "Deliverdate", "date": "Deliverdate",
    "customerid": "CustomerID", "customer_id": "CustomerID", "customer": "CustomerID", "client": "CustomerID",
    "licenseno": "LicenseNo", "license_no": "LicenseNo", "license": "LicenseNo", "permit": "LicenseNo",
    "category": "Category", "product_category": "Category", "device_category": "Category",
    "udid": "UDID", "udi": "UDID", "primary_di": "UDID",
    "devicename": "DeviceNAME", "device_name": "DeviceNAME", "device": "DeviceNAME", "product": "DeviceNAME",
    "lotno": "LotNO", "lot_no": "LotNO", "lot": "LotNO", "batch": "LotNO",
    "serno": "SerNo", "ser_no": "SerNo", "serial": "SerNo", "serialno": "SerNo", "serial_no": "SerNo",
    "model": "Model", "modelno": "Model", "model_no": "Model",
    "number": "Number", "qty": "Number", "quantity": "Number", "units": "Number", "count": "Number",
}


def detect_format(text: str) -> str:
    s = (text or "").strip()
    if not s:
        return "empty"
    if s.startswith("{") or s.startswith("["):
        return "json"
    lines = s.splitlines()
    if len(lines) >= 2 and sum(1 for ln in lines[:10] if ln.strip().startswith("{")) >= 2:
        return "jsonl"
    return "csv_or_text"


def parse_jsonl(text: str) -> Tuple[pd.DataFrame, List[str]]:
    warnings: List[str] = []
    rows = []
    for i, ln in enumerate((text or "").splitlines()):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except Exception as e:
            warnings.append(f"JSONL line {i+1} parse failed: {e}")
    return pd.DataFrame(rows), warnings


def headerless_csv_to_required(text: str) -> Optional[pd.DataFrame]:
    try:
        lines = [ln for ln in (text or "").splitlines() if ln.strip()]
        if len(lines) < 2:
            return None
        first = lines[0]
        if any(col.lower() in first.lower() for col in REQUIRED_COLUMNS):
            return None
        buf = io.StringIO(text)
        df = pd.read_csv(buf, header=None, engine="python")
        if df.shape[1] == len(REQUIRED_COLUMNS):
            df.columns = REQUIRED_COLUMNS[:]
            return df
        return None
    except Exception:
        return None


def parse_dataset_text(text: str) -> Tuple[pd.DataFrame, List[str], str]:
    """
    FIXED: CSV parsing is performed on RAW text (no smart-quote normalization),
    to avoid breaking fields like “xxx” that become "xxx" with trailing characters.
    """
    warnings: List[str] = []
    text_raw = (text or "").strip()
    if not text_raw:
        return pd.DataFrame(), ["Empty input"], "empty"

    # strip optional prefix like "Datasets:"
    text_raw = strip_dataset_prefix(text_raw)

    fmt = detect_format(text_raw)

    if fmt == "json":
        try:
            # JSON can be normalized safely
            obj = json.loads(normalize_smart_quotes(text_raw))
            if isinstance(obj, dict) and "data" in obj and isinstance(obj["data"], list):
                obj = obj["data"]
            if isinstance(obj, dict):
                obj = [obj]
            return pd.DataFrame(obj), warnings, "json"
        except Exception as e:
            warnings.append(f"JSON parse failed; will try CSV. Reason: {e}")
            fmt = "csv_or_text"

    if fmt == "jsonl":
        df, w = parse_jsonl(normalize_smart_quotes(text_raw))
        return df, w, "jsonl"

    # Try headerless canonical CSV
    df_hdrless = headerless_csv_to_required(text_raw)
    if df_hdrless is not None:
        return df_hdrless, ["Parsed as headerless CSV; assigned canonical headers."], "csv(headerless)"

    # CSV parse (RAW; no smart quote conversion)
    try:
        buf = io.StringIO(text_raw)

        # Use python engine; keep default quoting rules (quotes are ASCII only).
        # This is safe because we no longer convert curly quotes into ASCII quotes.
        df = pd.read_csv(buf, engine="python")
        return df, warnings, "csv"
    except Exception as e:
        warnings.append(f"CSV parse failed: {e}")

        # Last-resort: disable quote parsing so stray ASCII quotes won't break.
        try:
            buf2 = io.StringIO(text_raw)
            df2 = pd.read_csv(buf2, engine="python", quoting=csv.QUOTE_NONE, on_bad_lines="skip")
            warnings.append("Parsed with QUOTE_NONE fallback; some rows may have been skipped.")
            return df2, warnings, "csv(QUOTE_NONE)"
        except Exception as e2:
            warnings.append(f"CSV QUOTE_NONE fallback failed: {e2}")

    return pd.DataFrame(), warnings + ["Unable to parse input"], "unknown"


def standardize_dataset(
    df: pd.DataFrame,
    source_label: str,
    user_mapping: Optional[Dict[str, str]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    report: Dict[str, Any] = {
        "source": source_label,
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "mapping_used": {},
        "warnings": [],
        "coercions": {},
        "missing_required": [],
        "confidence": 0,
        "dropped_rows": 0,
    }

    if df is None or df.empty:
        out = pd.DataFrame(columns=REQUIRED_COLUMNS + ["_row_id", "_source", "_import_ts", "_quality_flags", "_Deliverdate_dt"])
        report["warnings"].append("Empty dataset")
        report["missing_required"] = MIN_IMPORT_COLUMNS[:]
        report["confidence"] = 0
        return out, report

    dff = df.copy()
    dff.columns = [str(c).strip() for c in dff.columns]

    # Auto mapping
    lower_cols = {c.lower().strip(): c for c in dff.columns}
    auto_map: Dict[str, str] = {}

    for canon in REQUIRED_COLUMNS:
        if canon in dff.columns:
            auto_map[canon] = canon
            continue
        # Alias match
        for key, canon2 in ALIASES.items():
            if canon2 == canon and key in lower_cols:
                auto_map[canon] = lower_cols[key]
                break
        if canon not in auto_map and canon.lower() in lower_cols:
            auto_map[canon] = lower_cols[canon.lower()]

    mapping = dict(auto_map)
    if user_mapping:
        for canon, src in user_mapping.items():
            if canon in REQUIRED_COLUMNS and src and src in dff.columns:
                mapping[canon] = src

    report["mapping_used"] = mapping

    out = pd.DataFrame()
    for canon in REQUIRED_COLUMNS:
        src = mapping.get(canon)
        if src and src in dff.columns:
            out[canon] = dff[src]
        else:
            out[canon] = ""

    extras = [c for c in dff.columns if c not in set(mapping.values())]
    for c in extras:
        out[c] = dff[c]

    out["_row_id"] = [uuid.uuid4().hex for _ in range(len(out))]
    out["_source"] = source_label
    out["_import_ts"] = report["ts"]
    out["_quality_flags"] = ""

    # Normalize/clean strings AFTER parse (safe)
    def _clean(s: Any) -> str:
        s = "" if s is None or (isinstance(s, float) and pd.isna(s)) else str(s)
        s = s.strip()
        return normalize_smart_quotes(s)

    for c in ["SupplierID", "Deliverdate", "CustomerID", "LicenseNo", "Category", "UDID", "DeviceNAME", "LotNO", "SerNo", "Model"]:
        out[c] = out[c].map(_clean)

    # Coerce Number
    def _to_float(x: Any) -> Optional[float]:
        s = _clean(x)
        if not s:
            return None
        s = s.replace(",", "")
        s = re.sub(r"[^\d\.\-]", "", s)
        try:
            return float(s)
        except Exception:
            return None

    coerced = out["Number"].map(_to_float)
    bad_num = int(coerced.isna().sum())
    out["Number"] = coerced.fillna(0.0).astype(float)
    if bad_num:
        report["coercions"]["Number_invalid_to_0"] = bad_num
        out.loc[coerced.isna(), "_quality_flags"] = (out.loc[coerced.isna(), "_quality_flags"] + "|bad_number").str.strip("|")

    # Parse Deliverdate
    def _parse_date(x: Any) -> Optional[pd.Timestamp]:
        s = _clean(x)
        if not s:
            return None
        s2 = re.sub(r"[^\d\-\/]", "", s)
        try:
            if re.fullmatch(r"\d{8}", s2):
                return pd.to_datetime(s2, format="%Y%m%d", errors="coerce")
            return pd.to_datetime(s2, errors="coerce")
        except Exception:
            return None

    out["_Deliverdate_dt"] = out["Deliverdate"].map(_parse_date)
    bad_date = int(out["_Deliverdate_dt"].isna().sum())
    if bad_date:
        report["coercions"]["Deliverdate_unparseable"] = bad_date
        out.loc[out["_Deliverdate_dt"].isna(), "_quality_flags"] = (out.loc[out["_Deliverdate_dt"].isna(), "_quality_flags"] + "|bad_date").str.strip("|")

    # Duplicate flag
    try:
        dup = out.duplicated(subset=REQUIRED_COLUMNS, keep="first")
        dup_n = int(dup.sum())
        if dup_n:
            report["coercions"]["duplicates_flagged"] = dup_n
            out.loc[dup, "_quality_flags"] = (out.loc[dup, "_quality_flags"] + "|duplicate").str.strip("|")
    except Exception:
        pass

    # Missing required minimal fields
    missing_required = []
    for c in MIN_IMPORT_COLUMNS:
        if c not in out.columns:
            missing_required.append(c)
        elif c == "Number":
            continue
        else:
            if (out[c].astype(str).str.strip() == "").all():
                missing_required.append(c)
    report["missing_required"] = missing_required

    mapped_count = sum(1 for c in REQUIRED_COLUMNS if c in mapping and mapping[c] in dff.columns)
    required_ok = len(missing_required) == 0
    date_ok_ratio = float(out["_Deliverdate_dt"].notna().mean()) if len(out) else 0.0
    num_ok_ratio = float((out["Number"] > 0).mean()) if len(out) else 0.0

    conf = 0
    conf += int(60 * (mapped_count / max(1, len(REQUIRED_COLUMNS))))
    conf += 20 if required_ok else 0
    conf += int(10 * date_ok_ratio)
    conf += int(10 * num_ok_ratio)
    report["confidence"] = min(100, conf)

    return out, report


def load_default_dataset(path: str = DEFAULT_DATASET_PATH) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
    warnings: List[str] = []
    if not os.path.exists(path):
        empty = pd.DataFrame(columns=REQUIRED_COLUMNS)
        std, rep = standardize_dataset(empty, source_label="default")
        return std, [f"Default dataset not found: {path}"], rep

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        df, w, fmt = parse_dataset_text(content)
        warnings.extend(w)
        std, rep = standardize_dataset(df, source_label="default")
        rep["detected_format"] = fmt
        rep["parse_warnings"] = warnings
        return std, warnings, rep
    except Exception as e:
        empty = pd.DataFrame(columns=REQUIRED_COLUMNS)
        std, rep = standardize_dataset(empty, source_label="default")
        return std, [f"Failed to load default dataset: {e}"], rep


def dataset_quality_report(df: pd.DataFrame, parse_warnings: List[str]) -> Dict[str, Any]:
    if df is None or df.empty:
        return {
            "rows": 0,
            "missing_cols": REQUIRED_COLUMNS,
            "parse_warnings": parse_warnings or ["Empty dataset"],
            "duplicates": 0,
            "unparsed_dates": 0,
            "nonpositive_qty": 0,
            "issue_rows": 0,
        }

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    duplicates = int(df.duplicated(subset=REQUIRED_COLUMNS, keep="first").sum()) if all(c in df.columns for c in REQUIRED_COLUMNS) else int(df.duplicated().sum())
    unparsed_dates = int(df.get("_Deliverdate_dt", pd.Series(dtype="datetime64[ns]")).isna().sum()) if "_Deliverdate_dt" in df.columns else 0
    nonpositive_qty = int((df["Number"] <= 0).sum()) if "Number" in df.columns else 0
    issue_rows = int((df.get("_quality_flags", pd.Series([""] * len(df))).astype(str).str.strip() != "").sum()) if "_quality_flags" in df.columns else 0

    return {
        "rows": int(len(df)),
        "missing_cols": missing_cols,
        "parse_warnings": parse_warnings or [],
        "duplicates": duplicates,
        "unparsed_dates": unparsed_dates,
        "nonpositive_qty": nonpositive_qty,
        "issue_rows": issue_rows,
    }


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    if df is None or df.empty:
        return {"rows": 0, "unique_suppliers": 0, "unique_customers": 0, "total_units": 0}
    return {
        "rows": int(len(df)),
        "unique_suppliers": int(df["SupplierID"].nunique()) if "SupplierID" in df.columns else 0,
        "unique_customers": int(df["CustomerID"].nunique()) if "CustomerID" in df.columns else 0,
        "total_units": float(df["Number"].sum()) if "Number" in df.columns else 0.0,
    }


# -----------------------------------
# Distribution analytics + graphs
# -----------------------------------

def filter_df(
    df: pd.DataFrame,
    suppliers: List[str],
    customers: List[str],
    licenses: List[str],
    models: List[str],
    date_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]],
    qty_range: Optional[Tuple[float, float]],
) -> pd.DataFrame:
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
    if qty_range and "Number" in dff.columns:
        lo, hi = qty_range
        dff = dff[(dff["Number"] >= lo) & (dff["Number"] <= hi)]
    return dff


def compute_anomalies_count(df: pd.DataFrame, freq: str = "D") -> int:
    if df is None or df.empty or "_Deliverdate_dt" not in df.columns:
        return 0
    dff = df.dropna(subset=["_Deliverdate_dt"]).copy()
    if dff.empty:
        return 0
    ts = dff.set_index("_Deliverdate_dt")["Number"].resample(freq).sum().reset_index()
    ts = ts.sort_values("_Deliverdate_dt")
    ts["ma"] = ts["Number"].rolling(7, min_periods=2).mean()
    residual = ts["Number"] - ts["ma"].fillna(ts["Number"].mean())
    denom = residual.std() if residual.std() and residual.std() > 0 else 1.0
    z = (residual / denom).abs()
    return int((z >= 2.5).sum())


def data_health_score(q: Dict[str, Any]) -> int:
    if not q or q.get("rows", 0) == 0:
        return 0
    rows = max(1, int(q.get("rows", 0)))
    score = 100
    score -= 15 * len(q.get("missing_cols", []))
    score -= int(35 * (q.get("unparsed_dates", 0) / rows))
    score -= int(25 * (q.get("duplicates", 0) / rows))
    score -= int(25 * (q.get("nonpositive_qty", 0) / rows))
    score -= 5 * len(q.get("parse_warnings", []))
    return max(0, min(100, score))


def concentration_risk(df: pd.DataFrame) -> Dict[str, Any]:
    if df is None or df.empty or "Number" not in df.columns:
        return {"top_supplier": None, "share": 0.0, "top_customer": None, "customer_share": 0.0}
    total = float(df["Number"].sum()) if float(df["Number"].sum()) > 0 else 0.0
    if total <= 0:
        return {"top_supplier": None, "share": 0.0, "top_customer": None, "customer_share": 0.0}
    s = df.groupby("SupplierID")["Number"].sum().sort_values(ascending=False)
    c = df.groupby("CustomerID")["Number"].sum().sort_values(ascending=False)
    top_s, share_s = (s.index[0], float(s.iloc[0]) / total) if len(s) else (None, 0.0)
    top_c, share_c = (c.index[0], float(c.iloc[0]) / total) if len(c) else (None, 0.0)
    return {"top_supplier": top_s, "share": share_s, "top_customer": top_c, "customer_share": share_c}


def build_sankey(df: pd.DataFrame, top_n: int = 30) -> Optional["go.Figure"]:
    if go is None or df is None or df.empty:
        return None
    agg = (
        df.groupby(["SupplierID", "LicenseNo", "Model", "CustomerID"], as_index=False)["Number"]
        .sum()
        .sort_values("Number", ascending=False)
        .head(max(10, top_n))
    )
    suppliers = agg["SupplierID"].unique().tolist()
    licenses = agg["LicenseNo"].unique().tolist()
    models = agg["Model"].unique().tolist()
    customers = agg["CustomerID"].unique().tolist()
    nodes = suppliers + licenses + models + customers
    idx = {n: i for i, n in enumerate(nodes)}

    def link_sum(cols: List[str]) -> pd.DataFrame:
        return agg.groupby(cols, as_index=False)["Number"].sum()

    l1 = link_sum(["SupplierID", "LicenseNo"])
    l2 = link_sum(["LicenseNo", "Model"])
    l3 = link_sum(["Model", "CustomerID"])

    sources, targets, values = [], [], []
    for _, r in l1.iterrows():
        sources.append(idx[r["SupplierID"]]); targets.append(idx[r["LicenseNo"]]); values.append(float(r["Number"]))
    for _, r in l2.iterrows():
        sources.append(idx[r["LicenseNo"]]); targets.append(idx[r["Model"]]); values.append(float(r["Number"]))
    for _, r in l3.iterrows():
        sources.append(idx[r["Model"]]); targets.append(idx[r["CustomerID"]]); values.append(float(r["Number"]))

    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=14, thickness=14, line=dict(color="rgba(0,0,0,0.15)", width=0.5), label=nodes),
        link=dict(source=sources, target=targets, value=values),
    )])
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=520)
    return fig


def build_temporal_pulse(df: pd.DataFrame, freq: str = "D") -> Optional["go.Figure"]:
    if go is None or df is None or df.empty or "_Deliverdate_dt" not in df.columns:
        return None
    dff = df.dropna(subset=["_Deliverdate_dt"]).copy()
    if dff.empty:
        return None
    ts = dff.set_index("_Deliverdate_dt")["Number"].resample(freq).sum().reset_index()
    ts = ts.sort_values("_Deliverdate_dt")
    ts["ma"] = ts["Number"].rolling(7, min_periods=2).mean()
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
            x=ano["_Deliverdate_dt"], y=ano["Number"], mode="markers", name="Anomaly",
            marker=dict(size=10, color="rgba(255,99,71,0.9)", line=dict(width=1, color="rgba(0,0,0,0.2)"))
        ))
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=420)
    return fig


def build_mosaic_heatmap(df: pd.DataFrame, top_n_customers: int = 25, top_n_models: int = 20) -> Optional["go.Figure"]:
    if go is None or df is None or df.empty:
        return None
    cust = df.groupby("CustomerID")["Number"].sum().sort_values(ascending=False).head(top_n_customers).index
    mod = df.groupby("Model")["Number"].sum().sort_values(ascending=False).head(top_n_models).index
    dff = df[df["CustomerID"].isin(cust) & df["Model"].isin(mod)].copy()
    if dff.empty:
        return None
    pivot = dff.pivot_table(index="CustomerID", columns="Model", values="Number", aggfunc="sum", fill_value=0)
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Blues",
        hoverongaps=False,
    ))
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=520)
    return fig


def build_classic_charts(df: pd.DataFrame, top_n: int = 12) -> Dict[str, Any]:
    charts: Dict[str, Any] = {}
    if px is None or df is None or df.empty:
        return charts
    if "_Deliverdate_dt" in df.columns:
        dff = df.dropna(subset=["_Deliverdate_dt"]).copy()
        if not dff.empty:
            ts = dff.groupby("_Deliverdate_dt", as_index=False)["Number"].sum().sort_values("_Deliverdate_dt")
            charts["timeline"] = px.area(ts, x="_Deliverdate_dt", y="Number", title="")
    mod = df.groupby("Model", as_index=False)["Number"].sum().sort_values("Number", ascending=False).head(top_n)
    charts["model_dist"] = px.pie(mod, names="Model", values="Number", title="")
    cust = df.groupby("CustomerID", as_index=False)["Number"].sum().sort_values("Number", ascending=False).head(top_n)
    charts["top_customers"] = px.bar(cust, x="CustomerID", y="Number", title="")
    lic = df.groupby("LicenseNo", as_index=False)["Number"].sum().sort_values("Number", ascending=False).head(top_n)
    charts["license_usage"] = px.bar(lic, x="LicenseNo", y="Number", title="")
    for _, fig in charts.items():
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)
    return charts


# -----------------------------------
# NEW: Interactive distribution network graph (vis-network)
# SupplierID > LicenseNo > Model > CustomerID
# Click node -> details shown in embedded panel
# -----------------------------------

def build_distribution_network_html(df: pd.DataFrame, top_n_edges: int = 200) -> str:
    """
    Returns an HTML string rendering an interactive hierarchical network.
    This is self-contained and shows node details on click inside the HTML panel.
    """
    if df is None or df.empty:
        return "<div style='padding:12px'>No data.</div>"

    # Aggregate path weights
    agg = (
        df.groupby(["SupplierID", "LicenseNo", "Model", "CustomerID"], as_index=False)["Number"]
        .sum()
        .sort_values("Number", ascending=False)
        .head(max(30, top_n_edges))
    )

    # Node metadata
    def summarize_node(col: str) -> Dict[str, Dict[str, Any]]:
        g = df.groupby(col)["Number"].sum().sort_values(ascending=False)
        out = {}
        for k, v in g.items():
            out[str(k)] = {"total_units": float(v)}
        return out

    meta_supplier = summarize_node("SupplierID")
    meta_license = summarize_node("LicenseNo")
    meta_model = summarize_node("Model")
    meta_customer = summarize_node("CustomerID")

    # Build nodes set with type and totals
    nodes: Dict[str, Dict[str, Any]] = {}
    def add_node(node_id: str, label: str, ntype: str, total: float):
        if node_id in nodes:
            return
        color = {
            "supplier": "#2563eb",
            "license": "#7c3aed",
            "model": "#f59e0b",
            "customer": "#16a34a",
        }.get(ntype, "#64748b")
        nodes[node_id] = {
            "id": node_id,
            "label": label,
            "group": ntype,
            "color": color,
            "value": max(1.0, total),
            "title": f"{ntype.upper()}: {label}<br>Total Units: {total:.0f}",
            "total_units": total,
            "type": ntype,
        }

    # Build edges
    edges = []
    for _, r in agg.iterrows():
        s = str(r["SupplierID"]); l = str(r["LicenseNo"]); m = str(r["Model"]); c = str(r["CustomerID"])
        w = float(r["Number"])

        add_node(f"S::{s}", s, "supplier", meta_supplier.get(s, {}).get("total_units", w))
        add_node(f"L::{l}", l, "license", meta_license.get(l, {}).get("total_units", w))
        add_node(f"M::{m}", m, "model", meta_model.get(m, {}).get("total_units", w))
        add_node(f"C::{c}", c, "customer", meta_customer.get(c, {}).get("total_units", w))

        edges.append({"from": f"S::{s}", "to": f"L::{l}", "value": w, "title": f"{s} → {l}<br>Units: {w:.0f}"})
        edges.append({"from": f"L::{l}", "to": f"M::{m}", "value": w, "title": f"{l} → {m}<br>Units: {w:.0f}"})
        edges.append({"from": f"M::{m}", "to": f"C::{c}", "value": w, "title": f"{m} → {c}<br>Units: {w:.0f}"})

    nodes_list = list(nodes.values())

    # Embed vis-network (CDN) + a detail panel
    html = f"""
    <div style="display:flex; gap:12px; width:100%; height:560px;">
      <div id="net" style="flex: 3; border:1px solid rgba(0,0,0,0.10); border-radius:12px; background: rgba(255,255,255,0.25);"></div>
      <div style="flex: 1.2; border:1px solid rgba(0,0,0,0.10); border-radius:12px; padding:12px; background: rgba(255,255,255,0.18); overflow:auto;">
        <div style="font-weight:700; margin-bottom:8px;">Node Details</div>
        <div id="details" style="font-family: ui-sans-serif, system-ui; font-size: 13px;">
          Click a node to view details here.
        </div>
        <hr style="opacity:0.25"/>
        <div style="font-size:12px; opacity:0.8;">
          Graph: SupplierID → LicenseNo → Model → CustomerID<br/>
          Edges shown: {min(len(agg), top_n_edges)} paths (top by volume)
        </div>
      </div>
    </div>

    <script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <link href="https://unpkg.com/vis-network@9.1.2/styles/vis-network.min.css" rel="stylesheet" />

    <script>
      const nodes = new vis.DataSet({json.dumps(nodes_list, ensure_ascii=False)});
      const edges = new vis.DataSet({json.dumps(edges, ensure_ascii=False)});

      const container = document.getElementById('net');
      const data = {{ nodes, edges }};

      const options = {{
        physics: {{
          enabled: true,
          stabilization: {{ iterations: 120 }},
          barnesHut: {{ gravitationalConstant: -12000, springLength: 120, springConstant: 0.02 }}
        }},
        interaction: {{
          hover: true,
          tooltipDelay: 150,
          navigationButtons: true
        }},
        nodes: {{
          shape: "dot",
          scaling: {{ min: 8, max: 34 }},
          font: {{ size: 14, face: "Inter, ui-sans-serif, system-ui" }},
          borderWidth: 1
        }},
        edges: {{
          smooth: true,
          scaling: {{ min: 1, max: 10 }},
          color: {{ color: "rgba(0,0,0,0.25)", highlight: "rgba(0,0,0,0.55)" }}
        }},
        groups: {{
          supplier: {{ color: {{ background: "#2563eb", border: "rgba(0,0,0,0.25)" }} }},
          license:  {{ color: {{ background: "#7c3aed", border: "rgba(0,0,0,0.25)" }} }},
          model:    {{ color: {{ background: "#f59e0b", border: "rgba(0,0,0,0.25)" }} }},
          customer: {{ color: {{ background: "#16a34a", border: "rgba(0,0,0,0.25)" }} }},
        }}
      }};

      const network = new vis.Network(container, data, options);

      function esc(s) {{
        return (s ?? "").toString()
          .replaceAll("&","&amp;")
          .replaceAll("<","&lt;")
          .replaceAll(">","&gt;");
      }}

      network.on("click", function(params) {{
        const details = document.getElementById("details");
        if (!params.nodes || params.nodes.length === 0) {{
          details.innerHTML = "Click a node to view details here.";
          return;
        }}
        const id = params.nodes[0];
        const n = nodes.get(id);
        if (!n) {{
          details.innerHTML = "Node not found.";
          return;
        }}
        details.innerHTML = `
          <div style="font-weight:800; font-size:14px; margin-bottom:6px;">${{esc(n.type).toUpperCase()}}</div>
          <div><b>ID:</b> ${{esc(n.label)}}</div>
          <div><b>Total Units:</b> ${{Math.round(n.total_units)}}</div>
          <div style="margin-top:8px; opacity:0.9;"><b>Tip:</b> Use zoom/pan to explore paths.</div>
        `;
      }});
    </script>
    """
    return html


# -----------------------------------
# UI Blocks
# -----------------------------------

def status_strip(lang: str) -> None:
    st.markdown(f"### {_t(lang, 'status_strip')}")
    chips = []
    for p in PROVIDERS:
        status, src = provider_status(p)
        if status == "configured" and src == "env":
            label = f"{p.upper()}: {_t(lang, 'configured_env')}"
        elif status == "configured" and src == "session":
            label = f"{p.upper()}: {_t(lang, 'configured_session')}"
        else:
            label = f"{p.upper()}: {_t(lang, 'missing')}"
        chips.append(f"<span class='rcc-chip'>{label}</span>")

    df = st.session_state.get("dataset_df_active")
    rows = int(len(df)) if isinstance(df, pd.DataFrame) else 0
    chips.append(f"<span class='rcc-chip'>DATA: {rows} rows</span>")

    pipeline_state = st.session_state.get("pipeline_state", {"status": "idle"})
    chips.append(f"<span class='rcc-chip'>{_t(lang,'agent_pipeline')}: {pipeline_state.get('status','idle')}</span>")

    st.markdown("".join(chips), unsafe_allow_html=True)


def wow_header_controls() -> None:
    with st.sidebar:
        st.markdown(f"## {APP_TITLE}")
        current_lang = st.session_state.get("lang", "en")
        sel_lang = st.selectbox(_t(current_lang, "language"), options=["en", "zh-TW"], index=0 if current_lang == "en" else 1)
        st.session_state["lang"] = sel_lang

        themes = list(painter_themes().keys())
        current_theme = st.session_state.get("theme_name", themes[0])
        current_mode = st.session_state.get("theme_mode", "light")

        theme_name = st.selectbox(_t(sel_lang, "theme"), options=themes, index=themes.index(current_theme) if current_theme in themes else 0)
        mode = st.radio(_t(sel_lang, "mode"), options=["light", "dark"], index=0 if current_mode == "light" else 1,
                        horizontal=True, format_func=lambda x: _t(sel_lang, x))

        colj1, colj2 = st.columns([1, 1])
        with colj1:
            if st.button(_t(sel_lang, "jackpot"), use_container_width=True):
                theme_name = random.choice(themes)
        with colj2:
            st.caption(f"{theme_name} / {_t(sel_lang, mode)}")

        st.session_state["theme_name"] = theme_name
        st.session_state["theme_mode"] = mode


def wow_indicator_dock(lang: str, df: pd.DataFrame, q: Dict[str, Any]) -> None:
    st.markdown(f"## {_t(lang, 'wow_indicators')}")
    score = data_health_score(q)
    conc = concentration_risk(df)
    anom = compute_anomalies_count(df, freq="D")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='rcc-ind'><b>{_t(lang,'data_health_score')}</b><br><span style='font-size:28px'>{score}</span>/100</div>", unsafe_allow_html=True)
        st.progress(score / 100.0)
        st.caption(f"{_t(lang,'missing_cols')}: {len(q.get('missing_cols',[]))} | issue rows: {q.get('issue_rows',0)}")

    with c2:
        top_s = conc.get("top_supplier")
        share = conc.get("share", 0.0)
        top_c = conc.get("top_customer")
        share_c = conc.get("customer_share", 0.0)
        st.markdown(
            f"<div class='rcc-ind'><b>{_t(lang,'concentration_risk')}</b><br>"
            f"Top Supplier: <b>{top_s or '-'}</b> ({share:.0%})<br>"
            f"Top Customer: <b>{top_c or '-'}</b> ({share_c:.0%})</div>",
            unsafe_allow_html=True
        )
        st.progress(min(1.0, max(0.0, share)))

    with c3:
        st.markdown(
            f"<div class='rcc-ind'><b>{_t(lang,'anomaly_beacons')}</b><br>"
            f"<span style='font-size:28px'>{anom}</span> / detected</div>",
            unsafe_allow_html=True
        )
        st.caption("Based on rolling mean residual z-threshold (|z|≥2.5).")


def dataset_manager(lang: str) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
    st.markdown(f"## {_t(lang, 'dataset_manager')}")

    source = st.radio(
        _t(lang, "data_source"),
        options=[_t(lang, "use_default"), _t(lang, "paste"), _t(lang, "upload")],
        horizontal=True,
        index=0
    )

    preview_n = st.select_slider(_t(lang, "preview_count"), options=[20, 50, 100, 200, 500], value=20)
    issues_only = st.toggle(_t(lang, "issues_only"), value=False)

    if "dataset_df_active" not in st.session_state:
        st.session_state["dataset_df_active"] = pd.DataFrame(columns=REQUIRED_COLUMNS + ["_row_id", "_source", "_import_ts", "_quality_flags", "_Deliverdate_dt"])
        st.session_state["dataset_parse_warnings_active"] = []
        st.session_state["dataset_standardize_report_active"] = {"source": "none", "confidence": 0}

    if source == _t(lang, "use_default"):
        if st.session_state.get("_default_loaded_active") is not True:
            std, warnings, rep = load_default_dataset(DEFAULT_DATASET_PATH)
            st.session_state["dataset_df_active"] = std
            st.session_state["dataset_parse_warnings_active"] = warnings
            st.session_state["dataset_standardize_report_active"] = rep
            st.session_state["_default_loaded_active"] = True

            for k in ["dataset_stage_raw", "dataset_stage_std", "dataset_stage_report", "dataset_stage_warnings", "dataset_stage_detected_fmt", "dataset_stage_user_mapping"]:
                st.session_state.pop(k, None)
    else:
        st.session_state["_default_loaded_active"] = False

        uploaded_text = ""
        filename = "paste"

        if source == _t(lang, "paste"):
            uploaded_text = st.text_area(_t(lang, "paste_here"), height=180, placeholder="CSV header + rows, JSON array, or JSONL lines")
            filename = "paste"
        else:
            up = st.file_uploader(_t(lang, "upload_file"), type=["csv", "json", "txt", "jsonl"])
            if up is not None:
                uploaded_text = try_read_text_file(up)
                filename = getattr(up, "name", "upload")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button(_t(lang, "preview"), type="primary", use_container_width=True):
                df_raw, warnings, detected_fmt = parse_dataset_text(uploaded_text)

                st.session_state["dataset_stage_raw"] = df_raw
                st.session_state["dataset_stage_warnings"] = warnings
                st.session_state["dataset_stage_detected_fmt"] = detected_fmt

                user_mapping = st.session_state.get("dataset_stage_user_mapping", {})
                std, rep = standardize_dataset(df_raw, source_label=filename, user_mapping=user_mapping)
                rep["detected_format"] = detected_fmt
                rep["parse_warnings"] = warnings
                st.session_state["dataset_stage_std"] = std
                st.session_state["dataset_stage_report"] = rep
                st.success(_t(lang, "staged_ready"))

        with col2:
            rep = st.session_state.get("dataset_stage_report")
            can_import = isinstance(rep, dict) and len(rep.get("missing_required", [])) == 0
            if st.button(_t(lang, "import"), use_container_width=True, disabled=not can_import):
                std = st.session_state.get("dataset_stage_std")
                rep2 = st.session_state.get("dataset_stage_report", {})
                warnings2 = rep2.get("parse_warnings", []) if isinstance(rep2, dict) else []
                if isinstance(std, pd.DataFrame):
                    st.session_state["dataset_df_active"] = std
                    st.session_state["dataset_parse_warnings_active"] = warnings2
                    st.session_state["dataset_standardize_report_active"] = rep2
                    st.success(_t(lang, "imported"))
                else:
                    st.error("No staged dataset to import.")

        with col3:
            if st.button(_t(lang, "cancel"), use_container_width=True):
                for k in ["dataset_stage_raw", "dataset_stage_std", "dataset_stage_report", "dataset_stage_warnings", "dataset_stage_detected_fmt", "dataset_stage_user_mapping"]:
                    st.session_state.pop(k, None)

        # Mapping UI if needed
        rep = st.session_state.get("dataset_stage_report")
        raw = st.session_state.get("dataset_stage_raw")
        if isinstance(rep, dict) and isinstance(raw, pd.DataFrame) and not raw.empty:
            missing_required = rep.get("missing_required", [])
            if missing_required:
                st.markdown(f"### {_t(lang, 'mapping')}")
                st.caption(_t(lang, "mapping_help"))
                cols = list(raw.columns)
                user_mapping: Dict[str, str] = st.session_state.get("dataset_stage_user_mapping", {})

                mapping_inputs = {}
                for canon in REQUIRED_COLUMNS:
                    default_src = user_mapping.get(canon, "")
                    auto_src = rep.get("mapping_used", {}).get(canon, "")
                    preselect = default_src or auto_src
                    options = [""] + cols
                    idx = options.index(preselect) if preselect in options else 0
                    mapping_inputs[canon] = st.selectbox(f"{canon}  ←", options=options, index=idx, key=f"map_{canon}")

                if st.button("Apply mapping + Re-standardize"):
                    st.session_state["dataset_stage_user_mapping"] = mapping_inputs
                    std, rep2 = standardize_dataset(raw, source_label=rep.get("source", "staged"), user_mapping=mapping_inputs)
                    rep2["detected_format"] = rep.get("detected_format", "unknown")
                    rep2["parse_warnings"] = st.session_state.get("dataset_stage_warnings", [])
                    st.session_state["dataset_stage_std"] = std
                    st.session_state["dataset_stage_report"] = rep2
                    st.rerun()

                st.error(f"{_t(lang, 'cannot_import')}: {missing_required}")

    stage_std = st.session_state.get("dataset_stage_std")
    stage_raw = st.session_state.get("dataset_stage_raw")
    stage_rep = st.session_state.get("dataset_stage_report")

    active_df = st.session_state.get("dataset_df_active")
    active_warnings = st.session_state.get("dataset_parse_warnings_active", [])
    active_rep = st.session_state.get("dataset_standardize_report_active", {})

    tab_raw, tab_std = st.tabs([_t(lang, "raw_preview"), _t(lang, "std_preview")])

    with tab_raw:
        df_show = stage_raw if isinstance(stage_raw, pd.DataFrame) else active_df
        if issues_only and isinstance(df_show, pd.DataFrame) and "_quality_flags" in df_show.columns:
            df_show = df_show[df_show["_quality_flags"].astype(str).str.strip() != ""]
        st.markdown(f"### {_t(lang, 'dataset_preview')}")
        st.dataframe((df_show.head(preview_n) if isinstance(df_show, pd.DataFrame) else pd.DataFrame()), use_container_width=True)

    with tab_std:
        df_show = stage_std if isinstance(stage_std, pd.DataFrame) else active_df
        rep_show = stage_rep if isinstance(stage_rep, dict) else active_rep
        warnings_show = (rep_show.get("parse_warnings", []) if isinstance(rep_show, dict) else []) or active_warnings

        fmt = rep_show.get("detected_format", "unknown") if isinstance(rep_show, dict) else "unknown"
        conf = rep_show.get("confidence", 0) if isinstance(rep_show, dict) else 0

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"**{_t(lang, 'format_detected')}:** {fmt}")
            st.markdown(f"**{_t(lang, 'confidence')}:** {conf}/100")
        with c2:
            st.markdown(f"### {_t(lang, 'import_report')}")
            st.write(rep_show if isinstance(rep_show, dict) else {})
            if warnings_show:
                st.warning("\n".join([f"- {w}" for w in warnings_show]))

        if issues_only and isinstance(df_show, pd.DataFrame) and "_quality_flags" in df_show.columns:
            df_show = df_show[df_show["_quality_flags"].astype(str).str.strip() != ""]
        st.dataframe((df_show.head(preview_n) if isinstance(df_show, pd.DataFrame) else pd.DataFrame()), use_container_width=True)

    q_active = dataset_quality_report(active_df, active_warnings)
    return active_df, q_active, active_rep


def distribution_filters(lang: str, df: pd.DataFrame) -> Dict[str, Any]:
    st.markdown(f"## {_t(lang, 'filters')}")
    if df is None or df.empty:
        st.info("No dataset loaded.")
        return {"suppliers": [], "customers": [], "licenses": [], "models": [], "date_range": None, "qty_range": None, "top_n": 30}

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

    date_range = None
    if "_Deliverdate_dt" in df.columns and df["_Deliverdate_dt"].notna().any():
        dmin = pd.to_datetime(df["_Deliverdate_dt"].min()).date()
        dmax = pd.to_datetime(df["_Deliverdate_dt"].max()).date()
        dr = st.date_input(_t(lang, "date_range"), value=(dmin, dmax), min_value=dmin, max_value=dmax)
        if isinstance(dr, tuple) and len(dr) == 2:
            date_range = (pd.to_datetime(dr[0]), pd.to_datetime(dr[1]))

    qty_range = None
    qmin = float(df["Number"].min()) if "Number" in df.columns else 0.0
    qmax = float(df["Number"].max()) if "Number" in df.columns else 0.0
    if qmax > qmin:
        qr = st.slider(_t(lang, "qty_range"), min_value=float(qmin), max_value=float(qmax), value=(float(qmin), float(qmax)))
        qty_range = qr

    top_n = st.slider(_t(lang, "top_n"), min_value=10, max_value=300, value=int(st.session_state.get("flt_top_n", 30)), step=5)

    if st.button(_t(lang, "reset_filters")):
        for k in ["flt_suppliers", "flt_customers", "flt_licenses", "flt_models", "flt_top_n"]:
            st.session_state.pop(k, None)
        st.rerun()

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
# Pages (Distribution Lab implemented; other pages kept minimal)
# -----------------------------------

def page_distribution_lab(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_distribution')}")
    status_strip(lang)

    df_active, q_active, _ = dataset_manager(lang)

    k = compute_kpis(df_active)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(_t(lang, "rows"), k["rows"])
    c2.metric(_t(lang, "unique_suppliers"), k["unique_suppliers"])
    c3.metric(_t(lang, "unique_customers"), k["unique_customers"])
    c4.metric(_t(lang, "total_units"), f"{k['total_units']:.0f}")

    with st.expander(_t(lang, "data_quality"), expanded=False):
        st.write(q_active)
        warnings = st.session_state.get("dataset_parse_warnings_active", [])
        if warnings:
            st.warning("\n".join([f"- {w}" for w in warnings]))

    wow_indicator_dock(lang, df_active, q_active)

    flt = distribution_filters(lang, df_active)
    dff = filter_df(df_active, **{k: flt[k] for k in ["suppliers", "customers", "licenses", "models", "date_range", "qty_range"]})

    st.markdown("---")
    tab1, tab3 = st.tabs([_t(lang, "wow_graphs"), _t(lang, "classic_charts")])

    with tab1:
        st.markdown(f"## {_t(lang, 'network_title')}")
        top_edges = st.slider("Top paths (by volume) in network", min_value=50, max_value=1000, value=200, step=50)
        html = build_distribution_network_html(dff, top_n_edges=top_edges)
        components.html(html, height=600, scrolling=False)

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
        fig3 = build_mosaic_heatmap(dff, top_n_customers=25, top_n_models=20)
        if fig3 is not None:
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Heatmap unavailable or no data after filtering.")

    with tab3:
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


def page_command_center(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_command_center')}")
    status_strip(lang)
    st.markdown("Regulatory Dashboard placeholder (kept as in prior scaffold).")


def page_settings_keys(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_settings')}")
    status_strip(lang)
    st.session_state.setdefault("api_keys", {})
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
            if st.button(_t(lang, "clear_key"), key=f"clear_{p}"):
                st.session_state["api_keys"][p] = ""
                st.rerun()
        else:
            st.warning(_t(lang, "missing"))
            key_in = st.text_input(_t(lang, "enter_key"), type="password", key=f"key_in_{p}")
            if st.button(_t(lang, "save_key"), key=f"save_{p}", type="primary"):
                if key_in.strip():
                    st.session_state["api_keys"][p] = key_in.strip()
                    st.rerun()
                else:
                    st.error("Empty key.")


def page_agents_studio(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_agents')}")
    status_strip(lang)
    st.info("Agents Studio scaffold kept; unchanged from prior version.")


def page_ai_note_keeper(lang: str) -> None:
    st.markdown(f"# {_t(lang, 'nav_note_keeper')}")
    status_strip(lang)
    online = any_provider_configured()
    st.caption(_t(lang, "online_mode") if online else _t(lang, "offline_mode"))
    if not online:
        st.warning(_t(lang, "not_configured_ai"))
    st.info("AI Note Keeper scaffold kept; unchanged from prior version.")


# -----------------------------------
# Main
# -----------------------------------

def init_session_defaults() -> None:
    st.session_state.setdefault("lang", "en")
    st.session_state.setdefault("theme_name", list(painter_themes().keys())[0])
    st.session_state.setdefault("theme_mode", "light")
    st.session_state.setdefault("api_keys", {})
    st.session_state.setdefault("pipeline_state", {"status": "idle", "last_run": None})


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    init_session_defaults()

    wow_header_controls()
    lang = st.session_state.get("lang", "en")
    apply_theme_css(st.session_state.get("theme_name"), st.session_state.get("theme_mode"))

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
