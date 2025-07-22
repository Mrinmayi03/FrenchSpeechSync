# 🗣️ French Speech Sync

Upload an MP4 video, and receive the **same video with French subtitles + French audio dubbed**.

> **Built with**: FastAPI • React • Whisper • gTTS • MoviePy • AWS S3 • Docker  
> **Focuses on**: AI audio, video processing, full-stack integration, and DevOps best practices.

---

## 🚀 Project Features

✅ Upload MP4 videos via React frontend  
✅ Backend processes video with Whisper + gTTS → French audio + subtitles  
✅ Video output includes **burned subtitles** and **dubbed audio**  
✅ Secure AWS S3 storage with **presigned download links**  
✅ Fully Dockerized for easy running  
✅ Environment variables managed securely with `.env`

---

## 🛠 Tech Stack

| Layer     | Tools / Libraries                       |
|-----------|-----------------------------------------|
| Frontend  | React, Axios                             |
| Backend   | FastAPI, Boto3, uvicorn                  |
| AI/ML     | Whisper-Timestamped, gTTS (Google TTS)   |
| Video     | MoviePy, OpenCV, ffmpeg                  |
| Cloud     | AWS S3 (Presigned URLs for secure download) |
| DevOps    | Docker, `.env` environment variables     |

---

## 📂 Folder Structure

FrenchSpeechSync/
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI API
│ │ ├── milestone5.py # AI processing pipeline
│ │ ├── run_m5.py # Orchestration
│ │ ├── .env.example # Example secrets file
│ │ └── requirements.txt
│ └── Dockerfile # Backend Dockerfile
├── speaksync-frontend/ # React app
│ ├── src/App.js
│ └── Dockerfile # Frontend Dockerfile


---

## ⚙️ How to Run Locally (Docker)

### 1️⃣ Clone this repository
```bash
git clone https://github.com/<your-username>/FrenchSpeechSync.git
cd FrenchSpeechSync
```

### 2️⃣ Setup .env for AWS S3

Inside /backend/app/, copy the example and fill in your credentials:

cp .env.example .env

Variable	Purpose
AWS_ACCESS_KEY_ID	Your AWS access key
AWS_SECRET_ACCESS_KEY	Your AWS secret key
AWS_S3_BUCKET	Your S3 bucket name
AWS_REGION	e.g., us-east-2

### 3️⃣ Build & Run Backend

cd backend

docker build -t speaksync-backend .

docker run -p 8000:8000 speaksync-backend

### 4️⃣ Build & Run Frontend

cd speaksync-frontend

docker build -t speaksync-frontend .

docker run -p 3000:3000 speaksync-frontend

### 💡 How to Use

1️⃣ Go to http://localhost:3000
2️⃣ Upload your .mp4 file
3️⃣ Wait for processing
4️⃣ Click the link to download your French-translated video
