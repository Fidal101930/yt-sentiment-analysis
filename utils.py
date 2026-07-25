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

    if "youtube.com/watch?v=" in video_url:

        return video_url.split("v=")[1].split("&")[0]


    elif "youtu.be/" in video_url:

        return video_url.split("youtu.be/")[1].split("?")[0]


    else:

        return None




# ==========================
# Fetch Comments
# ==========================

def fetch_comments(video_url):

    video_id = get_video_id(video_url)


    if not video_id:

        return []


    request = youtube.commentThreads().list(

        part="snippet",

        videoId=video_id,

        maxResults=100,

        textFormat="plainText"

    )


    response = request.execute()


    comments = []


    for item in response.get("items", []):

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

    df = pd.DataFrame(

        comments,

        columns=["Comment"]

    )


    df["Sentiment"] = df["Comment"].apply(get_sentiment)


    return df




# ==========================
# Fetch Video Details
# ==========================

def get_video_details(video_url):


    video_id = get_video_id(video_url)


    if not video_id:

        return None



    request = youtube.videos().list(

        part="snippet,statistics",

        id=video_id

    )


    response = request.execute()



    if not response.get("items"):

        return None



    item = response["items"][0]



    return {


        "title":

        item["snippet"]["title"],



        "channel":

        item["snippet"]["channelTitle"],



        "published":

        item["snippet"]["publishedAt"][:10],



        "thumbnail":

        item["snippet"]["thumbnails"]["high"]["url"],



        "views":

        item["statistics"].get(

            "viewCount",

            "0"

        )


    }