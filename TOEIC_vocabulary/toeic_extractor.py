import os
import logging
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
# import google.generativeai as genai
from googleapiclient.discovery import build
# from email_utils import create_email_content, send_email
from youtube_utils import search_youtube_videos, simple_get_video_transcript, get_video_title, get_video_info_by_url
from model_utils import extract_toeic_words_with_ollama
from quiz_generator import generate_toeic_quiz, format_quiz_for_email

class TOEICWordExtractor:
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        # self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        # genai.configure(api_key=self.gemini_api_key)
        self.url = None
        # self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        self.toeic_keywords = [
            'business', 'management', 'finance', 'marketing', 'conference',
            'schedule', 'appointment', 'deadline', 'budget', 'profit',
            'customer', 'client', 'service', 'quality', 'efficient',
            'technology', 'innovation', 'development', 'research', 'analysis'
        ]

    def word_extraction_specific_video(self):
        logging.info("開始處理指定影片...")
        try:
            # 获取视频信息
            video_info = get_video_info_by_url(self.youtube, self.url)
            if not video_info:
                logging.error("無法獲取影片信息")
                return False

            # 获取视频字幕
            transcript = simple_get_video_transcript(video_info['video_id'])
            if not transcript:
                logging.error("無法獲取影片字幕")
                return False

            # 提取单词
            words = extract_toeic_words_with_ollama(transcript)
            
            # 准备 LINE 消息内容
            # current_date = datetime.now().strftime("%Y-%m-%d")
            message_content = f"Video URL - {self.url}\n\n"
            message_content += f"影片標題：{video_info['title']}\n\n"
            message_content += "單字列表：\n"
            
            if not words:
                message_content += "未找到任何單字。"
            else:
                words_to_show = words[:10]
                for i, word in enumerate(words_to_show, 1):
                    message_content += f"\n{i}. {word['word']} ({word['part_of_speech']}) - {word['definition']}\n"
                    message_content += f"eg. {word['example_sentence']}\n"

            return {
                'success': True,
                'message': message_content
            }

        except Exception as e:
            logging.error(f"處理影片時發生錯誤: {str(e)}")
            return {
                'success': False,
                'message': f"處理影片時發生錯誤: {str(e)}"
            }

    def daily_word_extraction_with_quiz(self, video_url):
        try:
            # 獲取影片標題
            video_title = get_video_title(video_url)
            if not video_title:
                logging.error("無法獲取影片標題")
                return None

            # 獲取影片字幕
            transcript_text = simple_get_video_transcript(video_url)
            if not transcript_text:
                logging.error("無法獲取影片字幕")
                return None

            # 使用 Gemini 提取單字
            words = extract_toeic_words_with_ollama(self.gemini_model, transcript_text, video_title)
            if not words:
                logging.error("無法提取單字")
                return None

            # 生成考題
            quiz_questions = generate_toeic_quiz(self.gemini_model, words)
            if not quiz_questions:
                logging.error("無法生成考題")
                return None

            # 準備郵件內容
            email_content = f"""
            <h2>今日 TOEIC 單字學習</h2>
            <p>影片標題：{video_title}</p>
            
            <h3>單字列表：</h3>
            <ul>
            """
            
            for word in words:
                email_content += f"""
                <li>
                    <strong>{word['word']}</strong> ({word['part_of_speech']}) - {word['chinese']}<br>
                    例句：{word['example']}
                </li>
                """
            
            email_content += """
            </ul>
            """
            
            # 加入考題內容
            email_content += format_quiz_for_email(quiz_questions)

            return {
                'subject': f'TOEIC 單字學習 - {video_title}',
                'content': email_content
            }
        except Exception as e:
            logging.error(f"處理影片時發生錯誤: {e}")
            return None

    def get_video_title(self, video_url):
        # Implementation of get_video_title method
        pass

    def generate_toeic_quiz(self, words):
        # Implementation of generate_toeic_quiz method
        pass

    def send_email_with_content(self, subject, content, recipient_email):
        # Implementation of send_email_with_content method
        pass

    def send_daily_word_extraction_email(self):
        # Implementation of send_daily_word_extraction_email method
        pass

    def set_video_url(self, url):
        self.url = url
        return self.word_extraction_specific_video() 