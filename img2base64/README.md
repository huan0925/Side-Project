# Base64 圖片轉換器

本專案是一個簡單易用的網頁工具，讓你可以輕鬆在圖片（image）與 Base64 編碼之間互相轉換。

> 本專案是透過 Gemini 的 Canvas 生成。

## 專案簡介

- 你可以將圖片檔案上傳，立即取得對應的 Base64 字串。
- 也可以將 Base64 字串貼上，直接預覽還原成圖片。
- 適合前端開發、資料傳輸、圖片嵌入等多種應用場景。

## 功能特色

- 圖片與 Base64 互轉：支援雙向轉換，操作簡單直覺。
- 支援多種圖片格式（jpg、png、gif 等）。
- 轉換過程全在瀏覽器端進行，無需上傳伺服器，安全又快速。
- 介面美觀，支援行動裝置。

## 使用方式

1. 開啟 `index.html`。
2. 預設為「Base64 轉圖片」模式，將 Base64 字串貼上後點擊「轉換為圖片」即可預覽。
3. 點擊中間的「⇆」按鈕可切換為「圖片轉 Base64」模式，點擊「上傳圖片」選擇檔案後，Base64 字串會自動產生於左側欄位。

## 技術說明

- 本工具主要以 HTML、CSS（Tailwind）、JavaScript 製作。
- 轉換過程中，圖片轉 Base64 會用到 [FileReader API](https://developer.mozilla.org/zh-TW/docs/Web/API/FileReader/readAsDataURL)。
- Base64 轉圖片則直接將字串設為 `<img>` 的 `src` 屬性。
- **Canvas 應用**：若需進一步處理圖片（如壓縮、裁切、格式轉換），可於 JavaScript 中結合 Canvas API 進行進階操作。

## 版權授權

本專案僅供學習與個人用途，無特殊授權限制。 