import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
import sqlite3
import json

# Connect to the database and create a table
conn = sqlite3.connect('videos.sqlite3')
c = conn.cursor()


# Set DEVELOPER_KEY to the API key value from the APIs & Services > Credentials
# tab of the Google Cloud Console
DEVELOPER_KEY = os.getenv("YOUTUBE_PUBLIC_API_KEY")
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE = build(YOUTUBE_API_SERVICE_NAME,
                YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


def create_table(db, table):
    c.execute('CREATE TABLE IF NOT EXISTS transcripts (video_id TEXT, title TEXT, index_in_playlist INTEGER, transcript TEXT)')


def get_transcript(playlist_id):

    try:
        playlist_items = []
        next_page_token = None

        while True:
            playlist_response = YOUTUBE.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            playlist_items += playlist_response['items']
            next_page_token = playlist_response.get('nextPageToken')

            if not next_page_token:
                break

        videos = []
        for i, item in enumerate(playlist_items):
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            videos.append({
                "video_url": video_id,
                "video_title": video_title,
                "video_index": i
            })

        return videos

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    # Get the playlist ID from the playlist URL
    url = 'https://www.youtube.com/watch?v=XZo4xyJXCak&list=PL0o_zxa4K1BVsziIRdfv4Hl4UIqDZhXWV'
    # url = "https://www.youtube.com/playlist?list=PLzuQ4XCiINV8fZguaobNsB1BpehLLxTD3"

    query = urlparse(url).query
    playlist_id = parse_qs(query)['list'][0]
    # transcripts = get_transcript(playlist_id)
    transcript_response = YOUTUBE.captions().list(
        part='id',
        videoId="XZo4xyJXCak"
    ).execute()
    caption_id = transcript_response['items'][0]['id']
    caption_response = YOUTUBE.captions().download(
        id=caption_id,
        tfmt='srt'
    ).execute()

    transcript = caption_response
    with open("transcript_video1.srt", "w") as f:
        f.writelines(transcript)
