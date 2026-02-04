# Antigravity Agentic AI — WOW Workspace（SKILL）

本專案是一個部署於 Hugging Face Spaces 的 Streamlit 系統，整合多家 LLM（OpenAI / Gemini / Anthropic / Grok），並提供「多 Agent 串接」、「可編輯輸出再傳遞」、「AI Note Keeper」與「WOW UI（主題/語言/畫家風格）」等能力。

---

## 1. 核心能力（保留原功能 + 新增 WOW 功能）

### A) WOW UI
- **Light / Dark 主題模式**
- **英文 / 繁體中文 UI**
- **20 種畫家風格（含 Jackpot 隨機）**
- 視覺風格會影響整體配色、卡片、按鈕與介面氛圍

### B) 文件輸入（Document Input）
- 支援上傳：**Text / Markdown / PDF / CSV**
- PDF：預設抽取第 1 頁文字（可再擴充頁碼範圍）
- CSV：可轉為 Markdown 預覽（若安裝 pandas）
- 支援 **關鍵字掃描與高亮**（HTML 預覽）

### C) Agents 串接（Agent Chain）
- 從 `agents.yaml` 載入 agent 清單
- 使用者可在執行前針對每個 agent：
  - 修改 **prompt**
  - 修改 **max_tokens（預設 12000）**
  - 選擇 **model**
  - 調整 **temperature**
- 每個 agent 執行後：
  - 可在「文字/Markdown 檢視」查看
  - 可 **編輯輸出**（text_area）再作為下一個 agent 的輸入（Chain Input）

### D) WOW 狀態指示與儀表板
- 顯示：已載入文件數、Agent 數、執行次數、最後執行時間
- 顯示：OpenAI/Gemini/Anthropic/Grok 的 key 狀態（✅/—）

### E) API Key 輸入（安全策略）
- 若 key 已存在於環境變數（ENV），UI 只顯示「Loaded from environment (hidden)」
- 若 ENV 沒有，使用者可在網頁輸入（只存於 session，不寫入磁碟）

### F) AI Note Keeper（新功能）
- 貼上文字/Markdown → 一鍵整理成「組織化 Markdown」
- 可在 Markdown 或 Text 檢視中自由修改
- 提供 6 種 AI Magics（可自行擴充）：
  1. AI Formatting（組織化整理）
  2. AI Summary（摘要）
  3. AI Action Items（行動項目）
  4. AI Flashcards（記憶卡）
  5. AI Translate（英 ↔ 繁中）
  6. AI Keywords Highlight（使用者自訂關鍵字與顏色）

---

## 2. 檔案結構（Hugging Face Spaces）
- `app.py`：主程式（所有 UI/功能整合在單一檔案）
- `agents.yaml`：Agent 定義（可從 UI 編輯並儲存）
- `SKILL.md`：本文件
- `requirements.txt`：依賴套件

---

## 3. models 支援
UI 內建可選模型（可依需求增加）：
- OpenAI：`gpt-4o-mini`, `gpt-4.1-mini`
- Gemini：`gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-3-flash-preview`
- Anthropic：`claude-3-5-sonnet-latest`, `claude-3-5-haiku-latest`, `claude-3-opus-latest`
- Grok：`grok-4-fast-reasoning`, `grok-3-mini`

---

## 4. agents.yaml Schema（建議）
每個 agent 建議欄位：
- `name`：顯示名稱（唯一）
- `provider`：`openai|gemini|anthropic|grok`（可省略，系統可用 model 前綴推測）
- `model`：預設模型（使用者在 UI 可覆寫）
- `system_prompt`：系統提示詞
- `prompt`：使用者提示詞模板（支援 `{input}`）
- `temperature`：溫度
- `max_tokens`：最大輸出 tokens

---

## 5. 典型使用流程（建議）
1. 上傳 CSV/PDF/Text 作為上下文
2. 在 Agents 選擇要串接的 agents（例如：資料品質健檢 → KPI 設計 → 視覺化規格）
3. 使用「逐步模式」：
   - 先跑第 1 個 agent
   - 編輯輸出（修正用詞/加上限制/刪除敏感資訊）
   - 再傳到下一個 agent
4. 將成果貼進 AI Note Keeper：
   - 進一步整理、產出行動項或月報模板

---

## 6. 注意事項
- LLM 回答可能會受輸入資料品質影響；務必先做資料品質檢核
- 涉及合規/醫療器材情境時，請以「不臆測、可稽核」為準則
- 若要顯示真實 token usage/cost，需要依不同供應商回傳格式額外整合
