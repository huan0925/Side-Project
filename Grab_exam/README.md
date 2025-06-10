# 爬蟲練習

本專案是一個自動化爬蟲工具，能夠自動抓取某網站指定考試的所有題目，並自動解析統計答案，將結果即時寫入 Word（docx）檔案，方便後續整理與複習。

## 主要功能
- 自動抓取某網站的題目內容
- 解析「開始測驗」到「答案」之間的題目描述
- 解析「統計」欄位，找出最多人選的選項作為答案
- 每抓到一題即時寫入 docx 檔案（yamol_questions.docx），不會覆蓋前面內容
- 支援自動重啟瀏覽器與斷點續抓

## 執行環境需求
- Python 3.7 以上
- Google Chrome 瀏覽器
- ChromeDriver（需與 Chrome 版本相符）

### 需要安裝的套件
```bash
pip install selenium pandas python-docx
```

## 使用說明
1. **下載 ChromeDriver**
   - 請至 [ChromeDriver 官網](https://chromedriver.chromium.org/downloads) 下載與你本機 Chrome 相同版本的驅動程式，並將其放在 PATH 目錄下。

2. **執行 main.py**
   - 進入 Grab_exam 資料夾，執行：
   ```bash
   python main.py
   ```
   - 執行後會詢問是否使用預設參數（起始題號、題目數量），可依需求輸入。

3. **產出檔案**
   - 每抓到一題，會即時寫入 `yamol_questions.docx`，內容包含題目、答案、原始網址。
   - 也會產生 json 檔作為原始備份。

## 注意事項
- 若遇到「invalid session id」等瀏覽器異常，程式會自動等待並重啟瀏覽器，從斷點繼續抓。
- 若網站結構有變動，可能需調整正則表達式或選擇器。
- 若需抓取不同考試，請修改 main.py 裡的 base_url 與起始 ID。

## 聯絡方式
如有問題或建議，請聯絡作者。 