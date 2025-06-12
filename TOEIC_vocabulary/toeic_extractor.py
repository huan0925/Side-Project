import os
import logging
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from googleapiclient.discovery import build
from email_utils import create_email_content, send_email
from youtube_utils import search_youtube_videos, simple_get_video_transcript
from gemini_utils import extract_toeic_words_with_gemini

class TOEICWordExtractor:
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        self.toeic_keywords = [
            'business', 'management', 'finance', 'marketing', 'conference',
            'schedule', 'appointment', 'deadline', 'budget', 'profit',
            'customer', 'client', 'service', 'quality', 'efficient',
            'technology', 'innovation', 'development', 'research', 'analysis'
        ]

    def daily_word_extraction(self):
        logging.info("開始每日單字萃取流程...")
        videos = search_youtube_videos(self.youtube)
        if not videos:
            logging.error("無法找到合適的影片")
            return
        for video in videos:
            transcript = simple_get_video_transcript(video['video_id'])
            if transcript:
                words = extract_toeic_words_with_gemini(self.gemini_model, transcript, video['title'])
                if len(words) >= 30:
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    subject = f"📚 每日TOEIC單字學習 - {current_date}"
                    email_content = create_email_content(words[:50], video)
                    if send_email(subject, email_content, self.sender_email, self.sender_password, self.recipient_email):
                        logging.info("今日單字學習 email 發送完成！")
                        return
                    else:
                        logging.error("Email 發送失敗")
                else:
                    logging.warning(f"從影片 {video['title']} 中萃取的單字數量不足")
            else:
                logging.warning(f"無法獲取影片 {video['title']} 的字幕")
        logging.error("所有影片都無法成功萃取足夠的單字") 