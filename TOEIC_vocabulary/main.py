import os
import smtplib
import schedule
import time
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TOEICWordExtractor:
    def __init__(self):
        # API 設定
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Email 設定
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')  # App Password
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        # 初始化 APIs
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # TOEIC 常見單字庫（用於驗證）
        self.toeic_keywords = [
            'business', 'management', 'finance', 'marketing', 'conference',
            'schedule', 'appointment', 'deadline', 'budget', 'profit',
            'customer', 'client', 'service', 'quality', 'efficient',
            'technology', 'innovation', 'development', 'research', 'analysis'
        ]

    def search_youtube_videos(self, query="AI artificial intelligence", max_results=5):
        """搜尋 YouTube 上的 AI 相關最新影片"""
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                order='date',  # 按日期排序，獲取最新影片
                type='video',
                videoDuration='medium',  # 中等長度影片
                relevanceLanguage='en'   # 英文影片
            ).execute()
            
            videos = []
            for item in search_response['items']:
                video_info = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:200],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video_info)
            
            logging.info(f"找到 {len(videos)} 部影片")
            return videos
            
        except Exception as e:
            logging.error(f"搜尋 YouTube 影片時發生錯誤: {e}")
            return []

    def get_video_transcript(self, video_id):
        """獲取影片字幕"""
        try:
            # 優先獲取英文字幕
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 嘗試獲取英文字幕
            try:
                transcript = transcript_list.find_transcript(['en'])
                transcript_data = transcript.fetch()
            except:
                # 如果沒有英文字幕，嘗試自動生成的字幕
                transcript = transcript_list.find_generated_transcript(['en'])
                transcript_data = transcript.fetch()
            
            # 合併所有文字
            full_text = ' '.join([item['text'] for item in transcript_data])
            logging.info(f"成功獲取字幕，長度: {len(full_text)} 字符")
            return full_text
            
        except Exception as e:
            logging.error(f"獲取影片字幕時發生錯誤: {e}")
            return None

    def extract_toeic_words_with_gemini(self, transcript_text, video_title):
        """使用 Gemini 從字幕中提取 TOEIC 單字"""
        prompt = f"""
        請從以下影片字幕中提取50個最適合TOEIC考試的重要英文單字。

        影片標題: {video_title}
        影片字幕: {transcript_text[:3000]}  # 限制字數避免 token 超限

        請按照以下要求：
        1. 選擇TOEIC考試中常出現的商業、科技、學術相關單字
        2. 優先選擇中高級難度的單字（不要太基礎的如 "the", "and"）
        3. 包含不同詞性（名詞、動詞、形容詞、副詞）
        4. 每個單字提供：英文單字、中文意思、詞性、例句

        請用以下JSON格式回傳：
        {{
            "words": [
                {{
                    "word": "management",
                    "chinese": "管理",
                    "part_of_speech": "noun",
                    "example": "Good management is essential for business success."
                }}
            ]
        }}

        請確保回傳正確的JSON格式，包含恰好50個單字。
        """

        try:
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text
            
            # 清理回應文字，提取JSON部分
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end]
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.rfind("```")
                result_text = result_text[json_start:json_end]
            
            words_data = json.loads(result_text.strip())
            logging.info(f"成功提取 {len(words_data['words'])} 個單字")
            return words_data['words']
            
        except Exception as e:
            logging.error(f"使用 Gemini 提取單字時發生錯誤: {e}")
            return []

    def create_email_content(self, words, video_info):
        """建立email內容"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .word-item {{ 
                    border: 1px solid #ddd; 
                    margin: 10px 0; 
                    padding: 15px; 
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }}
                .word {{ font-size: 18px; font-weight: bold; color: #2196F3; }}
                .chinese {{ color: #FF9800; font-weight: bold; }}
                .pos {{ color: #9C27B0; font-style: italic; }}
                .example {{ color: #555; margin-top: 5px; }}
                .video-info {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📚 每日TOEIC單字學習 - {current_date}</h1>
            </div>
            
            <div class="content">
                <div class="video-info">
                    <h3>🎥 今日學習影片</h3>
                    <p><strong>標題:</strong> {video_info['title']}</p>
                    <p><strong>發布時間:</strong> {video_info['published_at'][:10]}</p>
                    <p><strong>YouTube連結:</strong> <a href="https://www.youtube.com/watch?v={video_info['video_id']}">觀看影片</a></p>
                </div>
                
                <h3>📝 今日50個TOEIC重點單字</h3>
        """
        
        for i, word_info in enumerate(words, 1):
            html_content += f"""
                <div class="word-item">
                    <div class="word">{i}. {word_info['word']}</div>
                    <div class="chinese">中文: {word_info['chinese']}</div>
                    <div class="pos">詞性: {word_info['part_of_speech']}</div>
                    <div class="example">例句: {word_info['example']}</div>
                </div>
            """
        
        html_content += """
                <div style="margin-top: 30px; padding: 15px; background-color: #fff3cd; border-radius: 5px;">
                    <p><strong>💡 學習建議:</strong></p>
                    <ul>
                        <li>建議觀看完整影片來了解單字的實際使用情境</li>
                        <li>每天複習5-10個單字，加深記憶</li>
                        <li>嘗試在日常對話中使用這些單字</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

    def send_email(self, subject, html_content):
        """發送email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logging.info("Email 發送成功！")
            return True
            
        except Exception as e:
            logging.error(f"發送 Email 時發生錯誤: {e}")
            return False

    def daily_word_extraction(self):
        """每日單字萃取主流程"""
        logging.info("開始每日單字萃取流程...")
        
        # 1. 搜尋最新 AI 相關影片
        videos = self.search_youtube_videos()
        if not videos:
            logging.error("無法找到合適的影片")
            return
        
        # 2. 嘗試從影片中獲取字幕和萃取單字
        for video in videos:
            transcript = self.get_video_transcript(video['video_id'])
            if transcript:
                # 3. 使用 Gemini 萃取 TOEIC 單字
                words = self.extract_toeic_words_with_gemini(transcript, video['title'])
                
                if len(words) >= 30:  # 至少要有30個單字才發送
                    # 4. 建立並發送 email
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    subject = f"📚 每日TOEIC單字學習 - {current_date}"
                    email_content = self.create_email_content(words[:50], video)  # 確保只取50個
                    
                    if self.send_email(subject, email_content):
                        logging.info("今日單字學習 email 發送完成！")
                        return
                    else:
                        logging.error("Email 發送失敗")
                else:
                    logging.warning(f"從影片 {video['title']} 中萃取的單字數量不足")
            else:
                logging.warning(f"無法獲取影片 {video['title']} 的字幕")
        
        logging.error("所有影片都無法成功萃取足夠的單字")

def main():
    # 設定環境變數檢查
    required_env_vars = [
        'YOUTUBE_API_KEY', 'GEMINI_API_KEY', 
        'SENDER_EMAIL', 'SENDER_PASSWORD', 'RECIPIENT_EMAIL'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"請設定以下環境變數: {', '.join(missing_vars)}")
        return
    
    extractor = TOEICWordExtractor()
    
    # 設定每日排程 - 早上8點執行
    schedule.every().day.at("08:00").do(extractor.daily_word_extraction)
    
    print("TOEIC 每日單字學習系統已啟動！")
    print("將在每天早上 8:00 自動發送單字學習 email")
    print("按 Ctrl+C 停止程式")
    
    # 如果要立即測試，取消下面這行的註解
    extractor.daily_word_extraction()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
    except KeyboardInterrupt:
        print("\n程式已停止")

if __name__ == "__main__":
    main()