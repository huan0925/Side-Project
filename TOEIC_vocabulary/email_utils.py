from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging
from datetime import datetime

def create_email_content(words, video_info):
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

def send_email(subject, html_content, sender_email, sender_password, recipient_email):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        logging.info("Email 發送成功！")
        return True
    except Exception as e:
        logging.error(f"發送 Email 時發生錯誤: {e}")
        return False 