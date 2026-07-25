import os
import io

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from io import BytesIO

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image as CoreImage

from youtube_utils import fetch_comments, analyze_sentiment


class MainScreen(BoxLayout):

    def analyze(self):
        url = self.ids.video_url.text.strip()

        if not url:
            self.ids.result.text = "Please enter a YouTube URL."
            return

        self.ids.result.text = "Analyzing..."

        try:

            # Fetch comments
            comments = fetch_comments(url)

            # Analyze sentiment
            df = analyze_sentiment(comments)

            sentiment_counts = df["Sentiment"].value_counts()

            positive = int(sentiment_counts.get("Positive", 0))
            neutral = int(sentiment_counts.get("Neutral", 0))
            negative = int(sentiment_counts.get("Negative", 0))

            # -----------------------
            # Create Pie Chart
            # -----------------------
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

            image = CoreImage(BytesIO(buffer.read()), ext="png")

            self.ids.chart_image.texture = image.texture

            plt.close()

            # -----------------------
            # Display Results
            # -----------------------
            result_text = (
                f"Total Comments : {len(df)}\n"
                f"Positive       : {positive}\n"
                f"Neutral        : {neutral}\n"
                f"Negative       : {negative}\n\n"
                "----------- COMMENTS -----------\n\n"
            )

            for item in df.head(20).to_dict(orient="records"):

                result_text += (
                    f"Sentiment : {item['Sentiment']}\n"
                    f"Comment   : {item['Comment']}\n"
                    "--------------------------------------\n"
                )

            self.ids.result.text = result_text

        except Exception as e:
            self.ids.result.text = str(e)


class YouTubeSentimentApp(App):

    def build(self):
        kv_file = os.path.join(
            os.path.dirname(__file__),
            "sentiment.kv"
        )

        return Builder.load_file(kv_file)


if __name__ == "__main__":
    YouTubeSentimentApp().run()