import os
from toeic_extractor import TOEICWordExtractor
from dotenv import load_dotenv
from flask import Flask, request, abort
import threading

# v3 imports for sending messages
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage
)
# v2 imports for handling webhooks
from linebot import WebhookHandler
from linebot.models import MessageEvent, TextMessage as LegacyTextMessage
from linebot.exceptions import InvalidSignatureError

import logging
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

# 初始化 LINE Bot API (v3)
line_token = os.getenv('LINE_TOKEN')
line_secret = os.getenv('LINE_SECRET')
configuration = Configuration(access_token=line_token)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

# 初始化 Webhook Handler (v2)
handler = WebhookHandler(line_secret)

# 創建 Flask 應用
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

def handle_long_task(user_id, reply_token, user_message):
    """
    將所有耗時的任務放在這裡，在背景執行緒中運行。
    """
    try:
        extractor = TOEICWordExtractor()
        extractor.url = user_message
        result = extractor.word_extraction_specific_video()
        
        if result['success']:
            message = result['message']
            
            message_chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
            send_messages = [TextMessage(text=chunk) for chunk in message_chunks]

            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=send_messages[:5]
                )
            )

            if len(send_messages) > 5:
                for i in range(5, len(send_messages), 5):
                    messaging_api.push_message(
                        PushMessageRequest(
                            to=user_id,
                            messages=send_messages[i:i+5]
                        )
                    )
        else:
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=result['message'])]
                )
            )
    except Exception as e:
        app.logger.error(f"背景任務處理時發生錯誤: {str(e)}")
        # 可以在這裡決定是否要推播錯誤訊息給使用者
        messaging_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=f"處理您的請求時發生錯誤，請稍後再試。")]
            )
        )

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=LegacyTextMessage)
def handle_message(event):
    """
    這個函式現在只做一件事：啟動一個背景執行緒，然後立即結束。
    """
    user_id = event.source.user_id
    reply_token = event.reply_token
    user_message = event.message.text
    
    # 創建並啟動背景執行緒
    task_thread = threading.Thread(
        target=handle_long_task, 
        args=(user_id, reply_token, user_message)
    )
    task_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)