import os
from toeic_extractor import TOEICWordExtractor
from dotenv import load_dotenv
from flask import Flask, request, abort

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
@handler.add(MessageEvent, message=LegacyTextMessage)
def handle_message(event):
    user_id = event.source.user_id
    reply_token = event.reply_token
    user_message = event.message.text
    app.logger.info(f"收到的訊息: {user_message}")

    try:
        extractor = TOEICWordExtractor()
        extractor.url = user_message
        result = extractor.word_extraction_specific_video()
        
        if result['success']:
            message = result['message']
            
            # 將長訊息分割成多個 chunk
            message_chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
            send_messages = [TextMessage(text=chunk) for chunk in message_chunks]

            # 用 reply_message 發送第一批 (最多 5 個)
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=send_messages[:5]
                )
            )

            # 如果還有更多訊息，就用 push_message 推播剩下的
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
        app.logger.error(f"處理影片時發生錯誤: {str(e)}")
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=f"發生錯誤：{str(e)}")]
            )
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)