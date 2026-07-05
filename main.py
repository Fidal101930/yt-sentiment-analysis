from googleapiclient.discovery import build

API_KEY = "AIzaSyAVhtbN49xlgHjij0x7cpj05GrpQKzMmgQ"

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

print("Connection successful!")

url = input("Enter YouTube video URL: ")
video_id = url.split("v=")[1].split("&")[0]

print("Video ID:", video_id)

request = youtube.commentThreads().list(
    part="snippet",
    videoId=video_id,
    maxResults=100
)

response = request.execute()