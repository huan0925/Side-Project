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
    response = requests.post(OLLAMA_CHAT_API_URL, json=request_payload, stream=True)
    response.raise_for_status()

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