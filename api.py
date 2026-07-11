from flask import Flask, request, jsonify
from utils import fetch_comments, analyze_sentiment
import traceback
import io
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "YouTube Sentiment Analysis API is running!"
    })


@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    if not data or "video_url" not in data:
        return jsonify({
            "error": "Please provide a YouTube video URL."
        }), 400

    video_url = data["video_url"]

    try:
        # Fetch YouTube comments
        comments = fetch_comments(video_url)

        if not comments:
            return jsonify({
                "error": "No comments found for this video."
            }), 404

        # Analyze sentiment
        df = analyze_sentiment(comments)

        # Count sentiments
        sentiment_counts = df["Sentiment"].value_counts()

        positive = int(sentiment_counts.get("Positive", 0))
        neutral = int(sentiment_counts.get("Neutral", 0))
        negative = int(sentiment_counts.get("Negative", 0))

        # ----------------------------
        # Create Pie Chart
        # ----------------------------
        plt.figure(figsize=(5, 5))

        plt.pie(
            [positive, neutral, negative],
            labels=["Positive", "Neutral", "Negative"],
            autopct="%1.1f%%",
            startangle=90
        )

        plt.title("Sentiment Analysis")

        buffer = io.BytesIO()

        plt.savefig(buffer, format="png")

        buffer.seek(0)

        chart = base64.b64encode(buffer.read()).decode("utf-8")

        plt.close()

        # ----------------------------
        # Response
        # ----------------------------
        result = {
            "total_comments": len(df),
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "comments": df.to_dict(orient="records"),
            "chart": chart
        }

        return jsonify(result)

    except Exception:
        traceback.print_exc()

        return jsonify({
            "error": "Internal Server Error"
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )