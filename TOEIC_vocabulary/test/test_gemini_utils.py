# TOEIC_vocabulary/tests/test_gemini_utils.py

import pytest
from TOEIC_vocabulary.model_utils import extract_toeic_words_with_gemini

class DummyGeminiModel:
    def generate_content(self, prompt):
        class DummyResponse:
            # 模擬 Gemini 回傳的 JSON 格式
            text = '''
            {
                "words": [
                    {
                        "word": "management",
                        "chinese": "管理",
                        "part_of_speech": "noun",
                        "example": "Good management is essential for business success."
                    }
                ]
            }
            '''
        return DummyResponse()

def test_extract_toeic_words_with_gemini():
    dummy_model = DummyGeminiModel()
    transcript = "Management is important in business."
    video_title = "Business Management"
    words = extract_toeic_words_with_gemini(dummy_model, transcript, video_title)
    assert isinstance(words, list)
    assert len(words) == 1
    assert words[0]['word'] == "management"
    assert words[0]['chinese'] == "管理"
    assert words[0]['part_of_speech'] == "noun"
    assert "business" in words[0]['example']