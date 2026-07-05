# 📊 YouTube Comment Sentiment Analysis

A Streamlit-based web application that analyzes the sentiment of YouTube video comments using the YouTube Data API and TextBlob.

## 🚀 Features

- Fetch comments from any public YouTube video
- Analyze sentiment (Positive, Neutral, Negative)
- Display sentiment statistics
- Generate:
  - 📊 Bar Chart
  - 🥧 Pie Chart
  - ☁️ Word Cloud
- Export results as a CSV file
- Interactive Streamlit web interface

---

## 🛠 Technologies Used

- Python
- Streamlit
- YouTube Data API v3
- Pandas
- TextBlob
- Matplotlib
- WordCloud
- Google API Python Client

---

## 📂 Project Structure

```
youtube-sentiment-analysis/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── comments_sentiment.csv
```

---

## 📦 Installation

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-sentiment-analysis.git
```

### Navigate to the project

```bash
cd youtube-sentiment-analysis
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configure API Key

Create a `.env` file in the project directory:

```
API_KEY=YOUR_YOUTUBE_API_KEY
```

Replace `YOUR_YOUTUBE_API_KEY` with your own API key.

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

---

## 📸 Screenshots

Add screenshots of your application here after uploading to GitHub.

---

## 📄 License

This project is for educational purposes.
