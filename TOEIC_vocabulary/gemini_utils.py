import json
import logging

def extract_toeic_words_with_gemini(gemini_model, transcript_text, video_title):
    prompt = f"""
    請從以下影片字幕中提取50個最適合TOEIC考試的重要英文單字。
    影片標題: {video_title}
    影片字幕: {transcript_text[:3000]}
    請按照以下要求：
    1. 選擇TOEIC考試中常出現的商業、科技、學術相關單字
    2. 優先選擇中高級難度的單字（不要太基礎的如 "the", "and"）
    3. 包含不同詞性（名詞、動詞、形容詞、副詞）
    4. 每個單字提供：英文單字、中文意思、詞性、例句
    請用以下JSON格式回傳：
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
    請確保回傳正確的JSON格式，包含恰好50個單字。
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
        words_data = json.loads(result_text.strip())
        logging.info(f"成功提取 {len(words_data['words'])} 個單字")
        return words_data['words']
    except Exception as e:
        logging.error(f"使用 Gemini 提取單字時發生錯誤: {e}")
        return [] 