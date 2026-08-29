import os
import re
import json

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# CHECK API KEYS
# ============================================================

if not YOUTUBE_API_KEY:
    raise ValueError(
        "YOUTUBE_API_KEY is missing from .env"
    )

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


# ============================================================
# YOUTUBE CLIENT
# ============================================================

youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY
)


# ============================================================
# GEMINI CLIENT
# ============================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL = "gemini-3.6-flash"


# ============================================================
# GET VIDEO ID
# ============================================================

def get_video_id(video_url):

    if not video_url:
        return None

    video_url = video_url.strip()

    # Normal YouTube URL
    if "youtube.com/watch?v=" in video_url:

        return video_url.split("v=")[1].split("&")[0]

    # Short URL
    elif "youtu.be/" in video_url:

        return video_url.split("youtu.be/")[1].split("?")[0]

    # YouTube Shorts
    elif "youtube.com/shorts/" in video_url:

        return video_url.split(
            "youtube.com/shorts/"
        )[1].split("?")[0]

    return None


# ============================================================
# CLEAN COMMENT
# ============================================================

def clean_comment(comment):

    if not comment:
        return ""

    # Remove URLs
    comment = re.sub(
        r"http\S+|www\S+",
        "",
        comment
    )

    # Remove @mentions
    comment = re.sub(
        r"@\w+",
        "",
        comment
    )

    # Remove extra spaces
    comment = re.sub(
        r"\s+",
        " ",
        comment
    )

    return comment.strip()


# ============================================================
# FETCH YOUTUBE COMMENTS
# ============================================================
def fetch_comments(video_url, max_comments=100):

    video_id = get_video_id(video_url)

    print("Video ID:", video_id)

    if not video_id:
        print("ERROR: Invalid YouTube URL.")
        return []

    comments = []
    next_page_token = None

    try:

        while len(comments) < max_comments:

            request = youtube.commentThreads().list(

                part="snippet",

                videoId=video_id,

                maxResults=min(
                    100,
                    max_comments - len(comments)
                ),

                textFormat="plainText",

                pageToken=next_page_token
            )

            response = request.execute()

            print(
                "YouTube returned",
                len(response.get("items", [])),
                "comment threads"
            )

            for item in response.get("items", []):

                try:

                    comment = (
                        item["snippet"]
                        ["topLevelComment"]
                        ["snippet"]
                        ["textDisplay"]
                    )

                    comment = clean_comment(comment)

                    if comment:
                        comments.append(comment)

                except KeyError as e:

                    print(
                        "Comment structure error:",
                        e
                    )

                if len(comments) >= max_comments:
                    break

            next_page_token = response.get(
                "nextPageToken"
            )

            if not next_page_token:
                break

        comments = list(
            dict.fromkeys(comments)
        )

        print(
            "FINAL COMMENTS:",
            len(comments)
        )

        return comments

    except HttpError as e:

        print("\n========== YOUTUBE API ERROR ==========")
        print(e)
        print("=======================================\n")

        return []

    except Exception as e:

        print("\n========== GENERAL ERROR ==========")
        print(type(e).__name__)
        print(str(e))
        print("===================================\n")

        return []


# ============================================================
# GEMINI SENTIMENT ANALYSIS
# ============================================================

def analyze_batch_with_gemini(comments):

    if not comments:
        return []

    numbered_comments = []

    for index, comment in enumerate(comments):
        numbered_comments.append(
            f"{index}: {comment[:1000]}"
        )

    comment_text = "\n".join(numbered_comments)

    prompt = f"""
You are a highly accurate sentiment classifier for YouTube comments.

For every numbered comment below, classify the sentiment as exactly one of:

Positive
Neutral
Negative

Rules:

1. Positive:
   Praise, happiness, excitement, approval,
   appreciation, support, or positive emotion.

2. Negative:
   Criticism, anger, sadness, dislike,
   disappointment, hate, or negative emotion.

3. Neutral:
   Factual statements, unclear comments,
   or comments with no clear emotion.

4. Understand YouTube slang and informal language.

5. Consider emojis.

6. Consider context.

7. Consider obvious sarcasm.

8. Return exactly ONE result for every comment.

9. Keep the original index.

IMPORTANT:
Return ONLY valid JSON.
Do not add markdown.
Do not add explanations.

Required format:

[
  {{"index": 0, "sentiment": "Positive"}},
  {{"index": 1, "sentiment": "Neutral"}},
  {{"index": 2, "sentiment": "Negative"}}
]

COMMENTS:

{comment_text}
"""

    try:

        print("\nSending batch to Gemini...")

        interaction = gemini_client.interactions.create(

            model=MODEL,

            input=prompt,

            generation_config={
                "temperature": 0
            }

        )

        print("Gemini response received.")

        response_text = interaction.output_text

        if not response_text:

            print("Gemini returned an empty response.")

            return []

        print("Gemini response preview:")
        print(response_text[:500])

        # Remove accidental markdown fences
        response_text = response_text.strip()

        if response_text.startswith("```"):

            response_text = (
                response_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        results = json.loads(response_text)

        if not isinstance(results, list):

            print(
                "Gemini response is not a list."
            )

            return []

        valid_results = []

        for item in results:

            if not isinstance(item, dict):
                continue

            if (
                "index" not in item
                or "sentiment" not in item
            ):
                continue

            sentiment = item["sentiment"]

            if sentiment not in [
                "Positive",
                "Neutral",
                "Negative"
            ]:
                continue

            valid_results.append({

                "index": int(item["index"]),

                "sentiment": sentiment

            })

        print(
            f"Gemini classified "
            f"{len(valid_results)} / "
            f"{len(comments)} comments."
        )

        return valid_results

    except Exception as e:

        print("\n========== GEMINI ERROR ==========")

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        print(
            "==================================\n"
        )

        return []


# ============================================================
# COMPLETE SENTIMENT ANALYSIS
# ============================================================

def analyze_sentiment(comments):

    if not comments:

        return pd.DataFrame(
            columns=[
                "Comment",
                "Sentiment"
            ]
        )

    comments = list(
        dict.fromkeys(comments)
    )

    results = []

    # Smaller batches are safer for LLM classification.
    batch_size = 15

    for start in range(
        0,
        len(comments),
        batch_size
    ):

        batch = comments[
            start:start + batch_size
        ]

        print(
            f"\nAnalyzing comments "
            f"{start + 1} - "
            f"{start + len(batch)}"
        )

        llm_results = analyze_batch_with_gemini(
            batch
        )

        sentiment_map = {}

        for item in llm_results:

            try:

                index = int(
                    item["index"]
                )

                sentiment = item["sentiment"]

                if sentiment in [
                    "Positive",
                    "Neutral",
                    "Negative"
                ]:

                    sentiment_map[index] = sentiment

            except Exception:

                continue

        for index, comment in enumerate(batch):

            if index in sentiment_map:

                sentiment = sentiment_map[index]

            else:

                # DON'T silently hide Gemini failures.
                sentiment = "Unclassified"

            results.append({

                "Comment": comment,

                "Sentiment": sentiment

            })

    return pd.DataFrame(
        results,
        columns=[
            "Comment",
            "Sentiment"
        ]
    )


# ============================================================
# GET VIDEO DETAILS
# ============================================================

def get_video_details(video_url):

    video_id = get_video_id(video_url)

    if not video_id:
        return None

    try:

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
                item["snippet"]
                ["thumbnails"]
                ["high"]
                ["url"],

            "views":
                item["statistics"].get(
                    "viewCount",
                    "0"
                )

        }


    except Exception as e:

        print(
            "Video details error:",
            str(e)
        )

        return None