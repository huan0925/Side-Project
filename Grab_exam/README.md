# 線上測驗爬蟲（Playwright 版）

本專案是一個自動化爬蟲工具，能夠自動抓取「某線上測驗」網站指定考試的所有題目，並自動解析統計答案，將結果即時寫入 Word（docx）檔案，方便後續整理與複習。

## 主要功能
- 自動抓取某線上測驗網站的題目內容
- 解析「開始測驗」到「答案」之間的題目描述
- 解析「統計」欄位，找出最多人選的選項作為答案
- 每抓到一題即時寫入 docx 檔案（yamol_questions_11401.docx），不會覆蓋前面內容
- 支援失敗自動重試與斷點續抓
- 內建反爬蟲繞過技巧（自訂 User-Agent、隨機等待、模擬滾動）

## 執行環境需求
- Python 3.7 以上
- Google Chrome 或 Chromium（Playwright 會自動安裝）
- [Playwright](https://playwright.dev/python/)

### 需要安裝的套件
```bash
pip install playwright python-docx
playwright install chromium
```

## 使用說明
1. **下載與安裝 Playwright**
   - 安裝 Python 套件與瀏覽器驅動：
     ```bash
     pip install playwright python-docx
     playwright install chromium
     ```

2. **執行 main_playwright.py**
   - 進入 Grab_exam 資料夾，執行：
     ```bash
     python main_playwright.py
     ```
   - 執行後會詢問是否使用預設參數（起始題號、題目數量），可依需求輸入。

3. **產出檔案**
   - 每抓到一題，會即時寫入 `questions.docx`，內容包含題目、答案、原始網址。

## 反爬蟲繞過說明
- **自訂 User-Agent**：讓瀏覽器看起來更像一般用戶，降低被網站偵測為自動化的機率。
- **隨機 sleep**：每題載入後隨機等待 1~2 秒，模擬真人行為。
- **模擬滾動頁面**：每題載入後自動滾動到底再滾回頂部，觸發 JS 載入與反爬蟲檢查。

## 為什麼從 Selenium 切換為 Playwright？
- **速度更快**：Playwright 架構現代，指令傳遞與瀏覽器啟動都比 Selenium 快。
- **等待與同步更聰明**：Playwright 針對現代網頁的動態載入有更好的等待機制，減少不必要的 sleep。
- **反爬蟲繞過能力更強**：Playwright 預設就會隱藏自動化特徵（如 navigator.webdriver），更不容易被網站偵測。
- **API 更現代**：Playwright 支援多分頁、事件監控、模擬人類行為等功能，開發體驗更好。
- **資源管理更好**：Playwright 可以快速建立/銷毀分頁，資源利用率高。

> **總結**：Playwright 更適合現代動態網頁的自動化抓取，速度快、穩定性高、反爬能力強，是 Selenium 的升級選擇。

## 注意事項
- 若網站結構有變動，可能需調整正則表達式或選擇器。
- 若需抓取不同考試，請修改 main_playwright.py 裡的 base_url 與起始 ID。

## 聯絡方式
如有問題或建議，請聯絡作者。 