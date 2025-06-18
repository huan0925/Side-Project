import os
from toeic_extractor import TOEICWordExtractor
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler, Event
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging.models import TextMessage
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent, 
    TextMessage, 
    TextSendMessage,
    ImageSendMessage)
from linebot.exceptions import InvalidSignatureError
import logging
import google.generativeai as genai
import json

# 加載環境變數
load_dotenv()

# 檢查必要的環境變數
required_env_vars = [
    'YOUTUBE_API_KEY', 'GEMINI_API_KEY', 
    'LINE_TOKEN', 'LINE_SECRET'
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"請設定以下環境變數: {', '.join(missing_vars)}")

# 初始化 LINE Bot API
line_token = os.getenv('LINE_TOKEN')
line_secret = os.getenv('LINE_SECRET')
line_bot_api = LineBotApi(line_token)
handler = WebhookHandler(line_secret)

# 創建 Flask 應用
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# 設置一個路由來處理 LINE Webhook 的回調請求
@app.route("/", methods=['POST'])
def callback():
    # 取得 X-Line-Signature 標頭
    signature = request.headers['X-Line-Signature']

    # 取得請求的原始內容
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # 驗證簽名並處理請求
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 設置一個事件處理器來處理 TextMessage 事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: Event):
    reply_token = event.reply_token
    if event.message.type == "text":
        user_message = event.message.text  # 使用者的訊息
        app.logger.info(f"收到的訊息: {user_message}")

        try:
            # 创建 TOEICWordExtractor 实例
            extractor = TOEICWordExtractor()
            # 直接设置 URL 并处理
            extractor.url = user_message
            result = extractor.word_extraction_specific_video()
            
            if result['success']:
                # 如果消息太长，需要分段发送
                message = result['message']
                if len(message) > 2000:  # LINE 消息长度限制
                    messages = [message[i:i+2000] for i in range(0, len(message), 2000)]
                    for msg in messages:
                        line_bot_api.reply_message(reply_token, TextSendMessage(text=msg))
                        reply_token = None  # 只对第一条消息使用 reply_token
                else:
                    line_bot_api.reply_message(reply_token, TextSendMessage(text=message))
            else:
                line_bot_api.reply_message(reply_token, TextSendMessage(text=result['message']))
        except Exception as e:
            app.logger.error(f"處理影片時發生錯誤: {str(e)}")
            line_bot_api.reply_message(reply_token, TextSendMessage(text=f"發生錯誤：{str(e)}"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)