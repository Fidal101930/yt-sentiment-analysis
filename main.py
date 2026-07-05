from googleapiclient.discovery import build

API_KEY = "AIzaSyAVhtbN49xlgHjij0x7cpj05GrpQKzMmgQ"

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

print("Connection successful!")