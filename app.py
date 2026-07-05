import streamlit as st
import pandas as pd
from textblob import TextBlob
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

# -------------------------------
# YouTube API Key
# -------------------------------


youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

# -------------------------------
# Streamlit Page
# -------------------------------
st.set_page_config(
    page_title="YouTube Sentiment Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 YouTube Comment Sentiment Analyzer")

video_url = st.text_input("Enter YouTube Video URL")

# -------------------------------
# Sentiment Function
# -------------------------------
def get_sentiment(comment):
    polarity = TextBlob(comment).sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# -------------------------------
# Analyze Button
# -------------------------------
if st.button("Analyze Comments"):

    if video_url == "":
        st.error("Please enter a YouTube URL.")
    else:

        try:

            # Extract Video ID
            video_id = video_url.split("v=")[1].split("&")[0]

            with st.spinner("Fetching comments..."):

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

            # Create DataFrame
            df = pd.DataFrame(comments, columns=["Comment"])

            # Analyze Sentiment
            df["Sentiment"] = df["Comment"].apply(get_sentiment)

            # Save CSV
            df.to_csv("comments_sentiment.csv", index=False)

            st.success("Analysis Completed Successfully!")

            # -------------------------------
            # Statistics
            # -------------------------------

            st.subheader("Sentiment Summary")

            sentiment_counts = df["Sentiment"].value_counts()

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "😊 Positive",
                sentiment_counts.get("Positive", 0)
            )

            col2.metric(
                "😐 Neutral",
                sentiment_counts.get("Neutral", 0)
            )

            col3.metric(
                "😞 Negative",
                sentiment_counts.get("Negative", 0)
            )

            # -------------------------------
            # Data Table
            # -------------------------------

            st.subheader("Comments")

            st.dataframe(df)

            # -------------------------------
            # Bar Chart
            # -------------------------------

            st.subheader("Bar Chart")

            fig1, ax1 = plt.subplots(figsize=(6,4))

            ax1.bar(
                sentiment_counts.index,
                sentiment_counts.values
            )

            ax1.set_xlabel("Sentiment")
            ax1.set_ylabel("Count")
            ax1.set_title("Sentiment Analysis")

            st.pyplot(fig1)

            # -------------------------------
            # Pie Chart
            # -------------------------------

            st.subheader("Pie Chart")

            fig2, ax2 = plt.subplots(figsize=(6,6))

            ax2.pie(
                sentiment_counts.values,
                labels=sentiment_counts.index,
                autopct="%1.1f%%",
                startangle=90
            )

            ax2.set_title("Sentiment Distribution")

            st.pyplot(fig2)

            # -------------------------------
            # Word Cloud
            # -------------------------------

            st.subheader("Word Cloud")

            text = " ".join(df["Comment"])

            wordcloud = WordCloud(
                width=1000,
                height=500,
                background_color="white"
            ).generate(text)

            fig3, ax3 = plt.subplots(figsize=(12,6))

            ax3.imshow(wordcloud, interpolation="bilinear")
            ax3.axis("off")

            st.pyplot(fig3)

            # -------------------------------
            # Download CSV
            # -------------------------------

            st.download_button(
                label="📥 Download CSV",
                data=df.to_csv(index=False),
                file_name="comments_sentiment.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"Error: {e}")