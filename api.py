from flask import Flask, request, jsonify, render_template
from utils import fetch_comments, analyze_sentiment, get_video_details
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
import traceback

app = Flask(__name__)


# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Analyze API
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    if not data or "video_url" not in data:
        return jsonify({
            "error": "Please provide a YouTube URL."
        }), 400

    video_url = data["video_url"]

    try:

        # Video information
        video = get_video_details(video_url)

        # Comments
        comments = fetch_comments(video_url)

        if len(comments) == 0:
            return jsonify({
                "error": "No comments found."
            }), 404

        df = analyze_sentiment(comments)

        sentiment = df["Sentiment"].value_counts()

        positive = int(sentiment.get("Positive", 0))
        neutral = int(sentiment.get("Neutral", 0))
        negative = int(sentiment.get("Negative", 0))

        # Pie Chart
        plt.figure(figsize=(5, 5))

        plt.pie(
            [positive, neutral, negative],
            labels=["Positive", "Neutral", "Negative"],
            autopct="%1.1f%%",
            startangle=90,
            colors=[
                "#00E676",
                "#FFC107",
                "#F44336"
            ]
        )

        plt.title("Sentiment Distribution")

        buffer = io.BytesIO()

        plt.savefig(buffer,
                    format="png",
                    bbox_inches="tight")

        buffer.seek(0)

        chart = base64.b64encode(buffer.read()).decode()

        plt.close()

        return jsonify({

            "title": video["title"],
            "thumbnail": video["thumbnail"],
            "channel": video["channel"],
            "views": video["views"],

            "total_comments": len(df),

            "positive": positive,
            "neutral": neutral,
            "negative": negative,

            "comments": df.to_dict(orient="records"),

            "chart": chart

        })

    except Exception as e:

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

    from flask import Flask, request, jsonify, render_template

from utils import (
    fetch_comments,
    analyze_sentiment,
    get_video_details
)

app = Flask(__name__)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# ANALYZE YOUTUBE VIDEO
# ==========================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # Get JSON sent by JavaScript
        data = request.get_json()

        if not data:

            return jsonify({
                "error": "No data received"
            }), 400


        # Get YouTube URL
        video_url = data.get("video_url")


        if not video_url:

            return jsonify({
                "error": "YouTube video URL is required"
            }), 400


        print("Analyzing:", video_url)


        # ==================================
        # GET VIDEO DETAILS
        # ==================================

        video_details = get_video_details(
            video_url
        )


        if not video_details:

            return jsonify({
                "error": "Could not find video details"
            }), 400


        # ==================================
        # FETCH COMMENTS
        # ==================================

        comments = fetch_comments(
            video_url
        )


        if not comments:

            return jsonify({
                "error": "No comments found for this video"
            }), 400


        print(
            f"Fetched {len(comments)} comments"
        )


        # ==================================
        # SENTIMENT ANALYSIS
        # ==================================

        df = analyze_sentiment(
            comments
        )


        # ==================================
        # COUNT SENTIMENTS
        # ==================================

        positive = int(
            (df["Sentiment"] == "Positive").sum()
        )

        neutral = int(
            (df["Sentiment"] == "Neutral").sum()
        )

        negative = int(
            (df["Sentiment"] == "Negative").sum()
        )


        total = len(df)


        # ==================================
        # OVERALL SCORE
        # ==================================

        if total > 0:

            score = round(
                (positive / total) * 100
            )

        else:

            score = 0


        # ==================================
        # COMMENTS FOR FRONTEND
        # ==================================

        comment_list = []

        for _, row in df.iterrows():

            comment_list.append({

                "comment":
                    row["Comment"],

                "sentiment":
                    row["Sentiment"]

            })


        # ==================================
        # RESPONSE
        # ==================================

        return jsonify({

            "success": True,

            "total_comments":
                total,

            "positive":
                positive,

            "neutral":
                neutral,

            "negative":
                negative,

            "score":
                score,

            "title":
                video_details["title"],

            "channel":
                video_details["channel"],

            "published":
                video_details["published"],

            "thumbnail":
                video_details["thumbnail"],

            "views":
                video_details["views"],

            "comments":
                comment_list

        })


    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )