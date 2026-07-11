import requests

# Change this to your computer's IP address
BASE_URL = "http://127.0.0.1:5000"

def analyze_video(video_url):
    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={"video_url": video_url}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Server returned {response.status_code}"
            }

    except Exception as e:
        return {
            "error": str(e)
        }