import json
import logging
import os
import requests

def extract_toeic_words_with_ollama(transcript_text, video_title):
    """
    使用 Ollama 本地 LLM 進行單字萃取
    transcript_text: 字幕內容
    video_title: 影片標題
    """
    if not transcript_text:
        logging.error("字幕內容為空，無法提取單字")
        return []
    system_prompt = f"""
    ### Role
    You are a professional English teacher specializing in TOEIC test preparation, with extensive teaching experience and a deep understanding of the vocabulary required for a TOEIC score of 990. Your mission is to help me precisely grasp the key vocabulary essential for achieving a high TOEIC score.

    ### Goal
    From the provided video subtitles, carefully select the 10 most important English words best suited for the TOEIC exam (especially for achieving a 990 target score). If there are fewer than 10 advanced words in the subtitles, please choose the words that best meet the requirements for a high TOEIC score from the existing subtitles, ensuring the selected words are most helpful for improving TOEIC performance.

    ### Chain-of-Thought (CoT)
    1.  **Word Selection Criteria**:
        * Prioritize words commonly appearing in TOEIC exam-related fields such as business, technology, workplace communication, and academic research.
        * Exclude overly basic words (e.g., "the", "and", "is") and overly obscure words.
        * Prioritize words of intermediate-advanced to advanced difficulty (CEFR B2-C2 levels), as these are key for a TOEIC 990 score.
        * Select words that have multiple parts of speech or subtle nuances in different contexts, to test depth of language comprehension.
        * Ensure the words are meaningful within the context of the subtitles.
    2.  **Word Count Limit & Quality**:
        * Strictly limit the output to 10 words.
        * Even if there are fewer than 10 advanced words in the subtitles, strive to select the words that best meet the above criteria and guarantee their high quality.
    3.  **Content Structure**:
        * Each word must include: **English word (word)**, **English explanation (english_explanation)**, **part of speech (part_of_speech)**, and an **English example sentence (example)**. **Please make sure to provide a concise English explanation for every word.** These four parts are absolutely indispensable. Example sentences should be concise and reflect the common usage of the word in a TOEIC context.

    ### Output Example
    {{
        "words": [
            {{
                "word": "facilitate",
                "english_explanation": "to make an action or process easier or more likely to happen",
                "part_of_speech": "verb",
                "example": "The new software will facilitate data analysis for our team."
            }},
            {{
                "word": "diligently",
                "english_explanation": "in a way that shows care and conscientiousness in one's work or duties",
                "part_of_speech": "adverb",
                "example": "She worked diligently to meet the project deadline."
            }},
            {{
                "word": "comprehensive",
                "english_explanation": "including or dealing with all or nearly all elements or aspects of something",
                "part_of_speech": "adjective",
                "example": "We need a comprehensive review of the current market trends."
            }}
        ]
    }}
    *Notice: Please ensure the correct JSON format is returned. **Only return** JSON, with no explanatory text or markdown code blocks. **Emphasizing again, please ensure a concise English explanation is included for every word.**
    """
    user_prompt = transcript_text

    OLLAMA_CHAT_API_URL = os.getenv('OLLAMA_CHAT_API_URL', 'http://localhost:11434/api/chat')
    MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME', 'llama3.2')
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    request_payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "options": {
            "num_predict": 8192,
            "temperature": 0.7,
            "top_p": 0.95,
        }
    }
    
    try:
        response = requests.post(OLLAMA_CHAT_API_URL, json=request_payload, stream=True)
        response.raise_for_status()
        # for line in response.iter_lines():
        #     if line:
        #         data = json.loads(line)
        #         generated_content = data.get("message", {}).get("content", "")
        #         print(generated_content, end="", flush=True)
        # print()  # 換行
        # 收集所有 streaming 回應內容
        full_content = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                full_content += data.get("message", {}).get("content", "")
        print(full_content)
        # 嘗試解析 JSON
        try:
            words_data = json.loads(full_content.strip())
            logging.info(f"成功提取 {len(words_data['words'])} 個單字 (Ollama)")
            return words_data['words']
        except Exception as e:
            logging.error(f"Ollama 回傳內容無法解析為 JSON: {e}\n內容: {full_content}")
            return []
    except Exception as e:
        logging.error(f"使用 Ollama 提取單字時發生錯誤: {e}")
        return []

def generate_toeic_quiz(gemini_model, words):
    """
    根據提取的單字生成 TOEIC 考題
    
    Args:
        gemini_model: Gemini 模型實例
        words: 單字列表，每個單字包含 word, chinese, part_of_speech, example
        
    Returns:
        包含50題考題的列表
    """
    if not words:
        logging.error("沒有單字可以生成考題")
        return []
        
    prompt = f"""
    請根據以下單字列表生成50題 TOEIC 考試風格的選擇題。
    每個題目應該包含：
    1. 題目（使用單字或其變化形式）
    2. 4個選項（A, B, C, D）
    3. 正確答案
    4. 解釋
    
    單字列表：
    {json.dumps(words, ensure_ascii=False, indent=2)}
    
    請用以下JSON格式回傳：
    {{
        "questions": [
            {{
                "question": "The company's management team has decided to _____ the project due to budget constraints.",
                "options": {{
                    "A": "terminate",
                    "B": "initiate",
                    "C": "celebrate",
                    "D": "decorate"
                }},
                "correct_answer": "A",
                "explanation": "terminate 意為終止，符合句意。其他選項：initiate（開始）、celebrate（慶祝）、decorate（裝飾）都不符合上下文。"
            }}
        ]
    }}
    要求：
    1. 題目要符合 TOEIC 考試的難度和風格
    2. 選項要合理且具有迷惑性
    3. 解釋要清楚說明為什麼是正確答案
    4. 確保生成恰好50題
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        result_text = response.text
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end]
        elif "```" in result_text:
            json_start = result_text.find("```") + 3
            json_end = result_text.rfind("```")
            result_text = result_text[json_start:json_end]
        quiz_data = json.loads(result_text.strip())
        logging.info(f"成功生成 {len(quiz_data['questions'])} 題考題")
        return quiz_data['questions']
    except Exception as e:
        logging.error(f"使用 Gemini 生成考題時發生錯誤: {e}")
        return [] 