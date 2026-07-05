import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
from wordcloud import WordCloud
from googleapiclient.discovery import build

# Replace with your YouTube API Key
API_KEY = "AIzaSyB62bPHhtRtKFLDHyf4rHg0u7wgrUvhYq4"

# Connect to YouTube API
youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

print("Connection successful!")

# Get YouTube video URL
url = input("Enter YouTube video URL: ")

# Extract Video ID
video_id = url.split("v=")[1].split("&")[0]

print("Video ID:", video_id)

# Fetch comments
request = youtube.commentThreads().list(
    part="snippet",
    videoId=video_id,
    maxResults=20,
    textFormat="plainText"
)

response = request.execute()

print("\nFetched Comments:\n")

comments = []

for item in response["items"]:
    comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    print(comment)
    comments.append(comment)

# Create DataFrame
df = pd.DataFrame(comments, columns=["Comment"])


# Function to analyze sentiment
def get_sentiment(comment):
    analysis = TextBlob(comment)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"


# Add Sentiment column
df["Sentiment"] = df["Comment"].apply(get_sentiment)

# Display results
print("\nSentiment Analysis:\n")
print(df)

# Save to CSV
df.to_csv("comments_sentiment.csv", index=False)

print("\nSentiment analysis completed successfully!")
print("File saved as: comments_sentiment.csv")

# Count each sentiment
sentiment_counts = df["Sentiment"].value_counts()

print("\nSentiment Counts:")
print(sentiment_counts)

# Create bar chart
plt.figure(figsize=(6, 5))
plt.bar(sentiment_counts.index, sentiment_counts.values)

plt.title("YouTube Comment Sentiment Analysis")
plt.xlabel("Sentiment")
plt.ylabel("Number of Comments")

plt.show()
plt.figure(figsize=(6, 6))

plt.pie(
    sentiment_counts.values,
    labels=sentiment_counts.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Sentiment Distribution")

plt.show()