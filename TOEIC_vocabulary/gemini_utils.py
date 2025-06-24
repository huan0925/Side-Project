import json
import logging

def extract_toeic_words_with_gemini(gemini_model, transcript_text, video_title):
    if not transcript_text:
        logging.error("字幕內容為空，無法提取單字")
        return []
    system_prompt = f"""
    ### Role
    你是一位專業的英文老師，現在需要協助我考TOEIC，我希望我可以達到 990 分

    ### Goal
    請從影片字幕中提取50個最適合TOEIC考試的重要英文單字，若有超過50個請提供我要達到990需要會的高級單字。

    
    ### Role
    1. 選擇TOEIC考試中常出現的商業、科技、學術相關單字
    2. 優先選擇中高級難度的單字（不要太基礎的如 "the", "and"）
    3. 包含不同詞性（名詞、動詞、形容詞、副詞）
    4. 每個單字提供：英文單字、中文意思、詞性、例句
    
    ### Output
    {{
        "words": [
            {{
                "word": "management",
                "chinese": "管理",
                "part_of_speech": "noun",
                "example": "Good management is essential for business success."
            }}
        ]
    }}
    *Notice: 請確保回傳正確的JSON格式，包含恰好50個單字。*

    Video trascript: {transcript_text}
    """
    try:
        # messages = [
        #     {"role": "system", "content": system_prompt},
        #     {"role": "user", "content": transcript_text[:3000]}
        # ]
        response = gemini_model.generate_content(system_prompt)
        result_text = response.text
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end]
        elif "```" in result_text:
            json_start = result_text.find("```") + 3
            json_end = result_text.rfind("```")
            result_text = result_text[json_start:json_end]
        words_data = json.loads(result_text.strip())
        logging.info(f"成功提取 {len(words_data['words'])} 個單字")
        return words_data['words']
    except Exception as e:
        logging.error(f"使用 Gemini 提取單字時發生錯誤: {e}")
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