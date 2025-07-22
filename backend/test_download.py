import requests

url = "https://speaksync-storage.s3.us-east-2.amazonaws.com/test-folder-v2/youtube_video.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAYJPJ6IGU2RG2VA5T%2F20250719%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250719T012226Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=914fa8212717eb268227b81955bc1a4e613b161753d1ace0da0601076b0d390a"
response = requests.get(url)

if response.status_code == 200:
    print("File downloaded successfully.")
else:
    print(f"Failed with status: {response.status_code}")
    print(response.text)
