import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from app_client import analyze_video


class MainScreen(BoxLayout):

    def analyze(self):
        url = self.ids.video_url.text.strip()

        if not url:
            self.ids.result.text = "Please enter a YouTube URL."
            return

        self.ids.result.text = "Analyzing..."

        data = analyze_video(url)

        if "error" in data:
            self.ids.result.text = data["error"]
            return

        result_text = (
            f"Total Comments : {data['total_comments']}\n"
            f"Positive       : {data['positive']}\n"
            f"Neutral        : {data['neutral']}\n"
            f"Negative       : {data['negative']}\n\n"
            "----------- COMMENTS -----------\n\n"
        )

        # Display the first 20 comments
        for item in data["comments"][:20]:
            result_text += (
                f"Sentiment : {item['Sentiment']}\n"
                f"Comment   : {item['Comment']}\n"
                "----------------------------------------\n"
            )

        self.ids.result.text = result_text


class YouTubeSentimentApp(App):

    def build(self):
        kv_file = os.path.join(os.path.dirname(__file__), "sentiment.kv")
        return Builder.load_file(kv_file)


if __name__ == "__main__":
    YouTubeSentimentApp().run()