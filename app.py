import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai

app = Flask(__name__)

# --- 已填入你的金鑰 ---
LINE_ACCESS_TOKEN = '8t+7qseqMyLCE+IwZ3Krkq4QR082hZAoT46MCNavhAe28BVnOnZKtZNY8QuOtDvgN4oWvBxs01I2pRITFuom4nyeYYWytxgp4ju5/zKgvcFMIbg3SY1LZbZ4K9U91wZvmlyz+o8tyVZrbMhkDqEfpAdB04t89/1O/w1cDnyilFU='
LINE_SECRET = '7f7f6a0e096152d880c21a7c572e47f6'
GEMINI_KEY = 'AIzaSyCpzlUUddBGiq-9H4f5N0N8WZiuvoIY6ME'

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    try:
        # 呼叫 Gemini 並獲取回應
        response = model.generate_content(user_text)
        reply_text = response.text
    except Exception as e:
        reply_text = "哎呀，Gemini 腦袋打結了，請稍後再試！"
        print(f"Error: {e}")

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    # Render 環境需要動態抓取 Port
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)