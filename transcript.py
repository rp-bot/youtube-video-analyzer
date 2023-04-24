from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs

# Set DEVELOPER_KEY to the API key value from the APIs & Services > Credentials
# tab of the Google Cloud Console
DEVELOPER_KEY = 'your_developer_key_here'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def get_transcript(playlist_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    try:
        playlist_items = []
        next_page_token = None

        # Retrieve all playlist items for the specified playlist ID
        while True:
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            playlist_items += playlist_response['items']
            next_page_token = playlist_response.get('nextPageToken')

            if not next_page_token:
                break

        # Extract the video IDs from the playlist items
        video_ids = []
        for item in playlist_items:
            video_ids.append(item['snippet']['resourceId']['videoId'])

        # Retrieve the transcripts for each video
        transcripts = {}
        for video_id in video_ids:
            try:
                video_response = youtube.videos().list(
                    part='snippet',
                    id=video_id
                ).execute()

                video = video_response['items'][0]
                video_title = video['snippet']['title']

                transcript_response = youtube.captions().list(
                    part='id',
                    videoId=video_id
                ).execute()

                if len(transcript_response['items']) == 0:
                    transcripts[video_title] = ''
                else:
                    caption_id = transcript_response['items'][0]['id']
                    caption_response = youtube.captions().download(
                        id=caption_id,
                        tfmt='srt'
                    ).execute()

                    transcripts[video_title] = caption_response

            except HttpError as error:
                print(f'An error occurred: {error}')
                transcripts[video_title] = ''

        return transcripts

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


# Get the playlist ID from the playlist URL
url = 'https://www.youtube.com/playlist?list=your_playlist_id_here'
query = urlparse(url).query
playlist_id = parse_qs(query)['list'][0]

transcripts = get_transcript(playlist_id)
print(transcripts)
