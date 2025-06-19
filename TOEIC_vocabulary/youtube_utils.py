import logging
from youtube_transcript_api import YouTubeTranscriptApi
import re
from googleapiclient.discovery import build
import os
import json
from youtube_transcript_api.formatters import TextFormatter

def search_youtube_videos(youtube, query="AI artificial intelligence", max_results=5):
    try:
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            order='date',
            type='video',
            videoDuration='medium',
            relevanceLanguage='en'
        ).execute()
        videos = []
        for item in search_response['items']:
            video_info = {
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:200],
                'published_at': item['snippet']['publishedAt']
            }
            videos.append(video_info)
        logging.info(f"找到 {len(videos)} 部影片")
        return videos
    except Exception as e:
        logging.error(f"搜尋 YouTube 影片時發生錯誤: {e}")
        return []

def get_video_info_by_url(youtube, url):
    """透過 YouTube 連結取得 video_info 字典"""
    # 支援多種 YouTube 連結格式
    match = re.search(r"(?:v=|youtu.be/)([\w-]{11})", url)
    if not match:
        logging.error("無法解析 YouTube 影片 ID")
        return None
    video_id = match.group(1)
    try:
        response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()
        if not response['items']:
            logging.error("找不到該影片資訊")
            return None
        item = response['items'][0]
        video_info = {
            'video_id': video_id,
            'title': item['snippet']['title'],
            'description': item['snippet']['description'][:200],
            'published_at': item['snippet']['publishedAt']
        }
        return video_info
    except Exception as e:
        logging.error(f"取得影片資訊時發生錯誤: {e}")
        return None


def simple_get_video_transcript(video_id):
    try:
        # 使用 get_transcript 方法來獲取字幕
        # 這會回傳一個包含字幕內容的列表 (List)
        # 列表中的每個元素都是一個字典 (Dictionary)，包含 'text', 'start', 'duration'
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # 合併所有字幕段落
        full_text = ' '.join([segment['text'] for segment in transcript])
        return full_text
    except Exception as e:
        print(f"無法獲取字幕：{e}")
        return None

def get_video_title(video_url):
    """
    從 YouTube 影片 URL 獲取影片標題
    
    Args:
        video_url: YouTube 影片 URL
        
    Returns:
        影片標題字串，如果失敗則回傳 None
    """
    try:
        # 從 URL 中提取影片 ID
        video_id = video_url.split('v=')[-1]
        
        # 建立 YouTube API 客戶端
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # 獲取影片資訊
        request = youtube.videos().list(
            part='snippet',
            id=video_id
        )
        response = request.execute()
        
        if response['items']:
            return response['items'][0]['snippet']['title']
        else:
            logging.error(f"無法獲取影片標題: {video_url}")
            return None
            
    except Exception as e:
        logging.error(f"獲取影片標題時發生錯誤: {e}")
        return None

if __name__ == "__main__":
    youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
    video_info = get_video_info_by_url(youtube, 'https://youtu.be/plbqT4dBNwo?si=JmOdhXr3Rf5T6h5h') # 有字幕
    # video_info = get_video_info_by_url(youtube, 'https://www.youtube.com/watch?v=HzhRqVUHJ5Q!') # 沒字幕
    print(video_info)
    full_context = simple_get_video_transcript(video_info['video_id'])
    print (full_context)