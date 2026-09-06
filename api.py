from flask import Flask, request, jsonify, render_template
from utils import fetch_comments, analyze_sentiment, get_video_details
import traceback

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data received."
            }), 400

        video_url = data.get("video_url", "").strip()

        if not video_url:
            return jsonify({
                "success": False,
                "error": "YouTube video URL is required."
            }), 400

        print("\n====================================")
        print("ANALYZING VIDEO")
        print("URL:", video_url)
        print("====================================")

        # -----------------------------
        # 1. Get video details
        # -----------------------------
        print("\nFetching video details...")

        video = get_video_details(video_url)

        if not video:
            return jsonify({
                "success": False,
                "error": "Could not find video details."
            }), 400

        print("Video:", video["title"])

        # -----------------------------
        # 2. Fetch comments
        # -----------------------------
        print("\nFetching comments...")

        comments = fetch_comments(
            video_url,
            max_comments=10
        )

        if not comments:
            return jsonify({
                "success": False,
                "error": "No comments found for this video."
            }), 404

        print(f"Fetched {len(comments)} comments.")

        # -----------------------------
        # 3. Gemini sentiment analysis
        # -----------------------------
        print("\nRunning Gemini sentiment analysis...")

        df = analyze_sentiment(comments)

        if df.empty:
            return jsonify({
                "success": False,
                "error": "Gemini did not return any sentiment results."
            }), 500

        print("\nSentiment results:")
        print(df.to_string(index=False))

        # -----------------------------
        # 4. Count sentiments
        # -----------------------------
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

        score = round(
            (positive / total) * 100
        ) if total > 0 else 0

        # -----------------------------
        # 5. Prepare comments
        # -----------------------------
        comment_list = []

        for _, row in df.iterrows():

            comment_list.append({
                "comment": str(row["Comment"]),
                "sentiment": str(row["Sentiment"])
            })

        # -----------------------------
        # 6. Response
        # -----------------------------
        response = {

            "success": True,

            "video": {
                "title": video["title"],
                "channel": video["channel"],
                "published": video["published"],
                "thumbnail": video["thumbnail"],
                "views": video["views"]
            },

            "total_comments": total,

            "positive": positive,

            "neutral": neutral,

            "negative": negative,

            "score": score,

            "comments": comment_list
        }

        print("\n====================================")
        print("ANALYSIS COMPLETE")
        print("Positive:", positive)
        print("Neutral:", neutral)
        print("Negative:", negative)
        print("====================================\n")

        return jsonify(response)

    except Exception as e:

        print("\n====================================")
        print("FLASK ERROR")
        print("====================================")

        traceback.print_exc()

        print("====================================\n")

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )