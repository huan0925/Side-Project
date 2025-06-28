import requests
import json

OLLAMA_CHAT_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"

# 使用 messages 格式來定義對話
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "Explain quantum physics in simple terms."},
]

request_payload = {
    "model": MODEL_NAME,
    "messages": messages, # 直接傳遞 messages 列表
    "options": {
        "num_predict": 256,
        "temperature": 0.7,
        "top_p": 0.95,
    }
}

try:
    # 向 Ollama 的 /api/chat 發送 POST 請求
    # Ollama 預設會以 streaming 方式回傳多個 JSON 物件（每一行一個 JSON）
    # 如果直接用 response.json() 會報錯，因為回傳內容不是單一 JSON，而是多行 JSON
    # 因此必須設置 stream=True，並用 iter_lines() 逐行解析每個 JSON 物件
    response = requests.post(OLLAMA_CHAT_API_URL, json=request_payload, stream=True)
    response.raise_for_status()

    # 逐行讀取 Ollama 的 streaming response，每一行都是一個 JSON 物件
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            generated_content = data.get("message", {}).get("content", "")
            print(generated_content, end="", flush=True)
    print()  # 換行

except requests.exceptions.RequestException as e:
    print(f"Error connecting to Ollama: {e}")
    print("Please ensure Ollama is running and the model is loaded.")
    print(f"Try running: ollama run {MODEL_NAME} in your terminal.")
except json.JSONDecodeError:
    print("Error decoding JSON response from Ollama.")
    print(f"Response content: {response.text}")