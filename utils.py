import pandas as pd
from textblob import TextBlob
from googleapiclient.discovery import build

# ==========================
# YouTube API Configuration
# ==========================

API_KEY = "AIzaSyDtjIOy69Zl7-bG3MHljKSFPE05bsgAWmc"

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


# ==========================
# Extract Video ID
# ==========================

def get_video_id(video_url):
    return video_url.split("v=")[1].split("&")[0]


# ==========================
# Fetch Comments
# ==========================

def fetch_comments(video_url):

    video_id = get_video_id(video_url)

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    response = request.execute()

    comments = []

    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)

    return comments


# ==========================
# Sentiment Analysis
# ==========================

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