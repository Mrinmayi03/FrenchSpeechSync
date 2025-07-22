# milestone5.py  ────────────────────────────────────────────────────────────
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_audioclips,
)
from moviepy.video.fx.speedx import speedx
from gtts import gTTS               # ★ new
import whisper_timestamped as whisper
import cv2, numpy as np, os, srt, uuid, tempfile
from datetime import timedelta
import os


# ───────── Whisper model ───────── #
model = whisper.load_model(os.getenv("WHISPER_MODEL" , "base"))


# ───────────────────────── helpers ───────────────────────── #

def format_ts(t: float) -> str:
    h, r = divmod(int(t), 3600)
    m, s = divmod(r, 60)
    return f"{h:02}:{m:02}:{s:02}"


def transcribe_to_srt(wav_path: str, srt_out: str) -> list[dict]:
    """Whisper → French SRT, returns segment list"""
    print("· Whisper transcription …")
    audio      = whisper.load_audio(wav_path)
    result     = whisper.transcribe(model, audio, language="fr")
    segments   = result["segments"]

    with open(srt_out, "w", encoding="utf-8") as fh:
        for i, seg in enumerate(segments, 1):
            fh.write(
                f"{i}\n"
                f"{format_ts(seg['start'])} --> {format_ts(seg['end'])}\n"
                f"{seg['text']}\n\n"
            )
    print(f"  ↳ SRT saved → {srt_out}")
    return segments


def french_tts(segments: list[dict], mp3_out: str) -> str:
    """gTTS in chunks → single MP3, returns its path"""
    print("· gTTS synthesis …")
    CHUNK = 4500                           # gTTS safe length
    text  = " ".join(seg["text"] for seg in segments)
    pieces = [text[i:i+CHUNK] for i in range(0, len(text), CHUNK)]
    clips  = []

    tmp_dir = tempfile.mkdtemp(prefix="gtts_")
    for idx, part in enumerate(pieces):
        part_mp3 = os.path.join(tmp_dir, f"part{idx}.mp3")
        gTTS(part, lang="fr").save(part_mp3)
        clips.append(AudioFileClip(part_mp3))

    concatenate_audioclips(clips).write_audiofile(mp3_out)
    print(f"  ↳ French MP3 saved → {mp3_out}")
    return mp3_out


def burn_subs_and_audio(video_mp4: str, mp3_fr: str, srt_path: str, out_mp4: str):
    print("· Mux video + new audio …")
    vid  = VideoFileClip(video_mp4)
    a_fr = AudioFileClip(mp3_fr)

    # duration sync
    factor = a_fr.duration / vid.duration
    if abs(factor - 1) > 0.01:
        a_fr = speedx(a_fr, factor=factor)
        adjust_srt_timing(srt_path, factor)

    # make subtitle ImageClips
    clips = []
    with open(srt_path, encoding="utf-8") as fh:
        for sub in srt.parse(fh.read()):
            img = np.zeros((100, vid.size[0], 3), dtype=np.uint8)
            cv2.putText(img, sub.content, (30, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
            clips.append(
                ImageClip(img)
                .set_duration(sub.end.total_seconds() - sub.start.total_seconds())
                .set_start(sub.start.total_seconds())
            )

    final = CompositeVideoClip([vid, *clips]).set_audio(a_fr)
    final.write_videofile(out_mp4, codec="libx264", audio_codec="aac")
    print(f"  ↳ Final video saved → {out_mp4}")


def adjust_srt_timing(srt_path: str, factor: float):
    with open(srt_path, "r", encoding="utf-8") as fh:
        subs = list(srt.parse(fh.read()))
    with open(srt_path, "w", encoding="utf-8") as fh:
        for sub in subs:
            sub.start = timedelta(seconds=sub.start.total_seconds() / factor)
            sub.end   = timedelta(seconds=sub.end.total_seconds()   / factor)
            fh.write(srt.compose([sub]))

# ───────── PUBLIC WRAPPER for run_m5.py ───────── #

from pathlib import Path               

def generate_and_mux_video(
        video_path: str,
        audio_path: str,
        subtitle_dir: str,
        output_path: str
):
    title = Path(video_path).stem

    # make sure subtitle directory exists  
    os.makedirs(subtitle_dir, exist_ok=True)

    # 1️⃣ Whisper → SRT
    srt_path = os.path.join(subtitle_dir, f"{title} fr.srt")
    segments = transcribe_to_srt(audio_path, srt_path)

    # 2️⃣ gTTS → MP3 (overwrite wav with mp3)
    mp3_path = audio_path.rsplit(".", 1)[0] + ".mp3"
    french_tts(segments, mp3_path)

    # 3️⃣ burn subs + audio
    burn_subs_and_audio(video_path, mp3_path, srt_path, output_path)
    return output_path


# ───────────────────────── main ───────────────────────── #

if __name__ == "__main__":
    try:
        original = input("Enter the *file name* (without path) of the video: ").strip()
        if not original:
            raise ValueError("Video file name cannot be empty!")

        title, _ = os.path.splitext(original)

        ROOT  = "/app/project/Milestone5"
        video = os.path.join(ROOT, "ground_truth", f"{title}.mp4")

        tmp_wav = os.path.join(ROOT, "tmp", f"{uuid.uuid4().hex}.wav")
        os.makedirs(os.path.dirname(tmp_wav), exist_ok=True)

        # 0️⃣ extract clean 16 kHz mono WAV for Whisper
        os.system(f'ffmpeg -y -i "{video}" -ac 1 -ar 16000 "{tmp_wav}"')

        srt_path  = os.path.join(ROOT, "translated_subtitle_file", f"{title} fr.srt")
        mp3_path  = os.path.join(ROOT, "translated_audio_file_french", f"{title} fr audio.mp3")
        out_video = os.path.join(ROOT, "translated_video",        f"{title} fr video.mp4")

        segments  = transcribe_to_srt(tmp_wav, srt_path)      # ✨ Whisper → SRT
        french_tts(segments, mp3_path)                        # ✨ TTS    → MP3
        burn_subs_and_audio(video, mp3_path, srt_path, out_video)

    except Exception as e:
        print("❌  Error:", e)
