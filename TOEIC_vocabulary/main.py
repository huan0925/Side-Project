import os
from toeic_extractor import TOEICWordExtractor

def main():
    required_env_vars = [
        'YOUTUBE_API_KEY', 'GEMINI_API_KEY', 
        'SENDER_EMAIL', 'SENDER_PASSWORD', 'RECIPIENT_EMAIL'
    ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"請設定以下環境變數: {', '.join(missing_vars)}")
        return
    extractor = TOEICWordExtractor()
    print("TOEIC 每日單字學習系統已啟動！")
    print("請手動執行單字學習 email 發送流程")
    # 立即執行一次
    extractor.daily_word_extraction()

if __name__ == "__main__":
    main()