import pytest
import json
from unittest.mock import patch
from model_utils import extract_toeic_words_with_ollama

def test_extract_toeic_words_with_ollama():
    # 準備 mock 的 ollama.chat 回傳內容
    mock_json = [
        {
            "word": "iteration",
            "definition": "The process of repeating a process or task in order to improve it.",
            "part_of_speech": "noun",
            "example_sentence": "The software development team used an iterative approach to build the new application."
        },
        {
            "word": "sandbox",
            "definition": "A controlled environment used for testing or experimentation.",
            "part_of_speech": "noun",
            "example_sentence": "The developers created a sandbox to test the new feature without affecting the live system."
        }
    ]
    mock_response = {
        'message': {
            'content': json.dumps(mock_json)
        }
    }

    with patch('ollama.chat', return_value=mock_response):
        transcript = "This is a test transcript for TOEIC vocabulary extraction."
        words = extract_toeic_words_with_ollama(transcript)
        assert isinstance(words, list)
        assert len(words) == 2
        assert words[0]['word'] == "iteration"
        assert words[1]['word'] == "sandbox"
        assert 'example_sentence' in words[0] 