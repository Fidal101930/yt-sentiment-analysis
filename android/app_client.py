import requests

BASE_URL = "http://127.0.0.1:5000"

def analyze_video(video_url):
    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={"video_url": video_url},
            timeout=30
        )

        print("Status Code:", response.status_code)
        print("Response:", response.text)

        return response.json()

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}