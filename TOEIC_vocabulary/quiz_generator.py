import json
import logging
from typing import List, Dict, Any

def generate_toeic_quiz(gemini_model, words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

def format_quiz_for_email(quiz_questions: List[Dict[str, Any]]) -> str:
    """
    將考題格式化為 HTML 格式的郵件內容
    
    Args:
        quiz_questions: 考題列表
        
    Returns:
        HTML 格式的郵件內容
    """
    if not quiz_questions:
        return ""
        
    email_content = """
    <h3>練習題：</h3>
    <ol>
    """
    
    for i, question in enumerate(quiz_questions, 1):
        email_content += f"""
        <li>
            <p>{question['question']}</p>
            <p>A) {question['options']['A']}</p>
            <p>B) {question['options']['B']}</p>
            <p>C) {question['options']['C']}</p>
            <p>D) {question['options']['D']}</p>
            <p><strong>正確答案：{question['correct_answer']}</strong></p>
            <p>解釋：{question['explanation']}</p>
        </li>
        """
    
    email_content += """
    </ol>
    """
    
    return email_content 