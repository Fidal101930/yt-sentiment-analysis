import pandas as pd
from textblob import TextBlob
from googleapiclient.discovery import build

# Replace with your YouTube API key
API_KEY = "AIzaSyDtjIOy69Zl7-bG3MHljKSFPE05bsgAWmc"

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


def get_video_id(video_url):
    if "v=" in video_url:
        return video_url.split("v=")[1].split("&")[0]
    else:
        raise Exception("Invalid YouTube URL")


def fetch_comments(video_url):
    video_id = get_video_id(video_url)

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    while request:
        response = request.execute()

        for item in response["items"]:
            comments.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )

        request = youtube.commentThreads().list_next(
            request,
            response
        )

    return comments


def get_sentiment(comment):
    polarity = TextBlob(comment).sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"


def analyze_sentiment(comments):
    df = pd.DataFrame(comments, columns=["Comment"])
    df["Sentiment"] = df["Comment"].apply(get_sentiment)
    return df