from utils import fetch_comments, analyze_sentiment

url = input("Enter YouTube URL: ")

try:
    comments = fetch_comments(url)
    print(f"Fetched {len(comments)} comments")

    df = analyze_sentiment(comments)
    print(df.head())

except Exception as e:
    print("ERROR:", e)