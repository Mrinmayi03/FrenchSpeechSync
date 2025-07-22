# app/run_m5.py  ──────────────────────────────────────────────────────────
"""
Utility that adapts the original milestone5.py pipeline so FastAPI can
pass it an uploaded MP4 and receive back the finished French‑dubbed file.
"""

import os, shutil, subprocess, uuid, tempfile
from pathlib import Path
import milestone5            # ← your unchanged milestone5.py

# -----------------------------------------------------------------------------
# Folder layout that milestone5.py still expects
# -----------------------------------------------------------------------------

M5_GROUND_TRUTH      = "ground_truth"
M5_AUDIO_FR          = "translated_audio_file_french"
M5_SUBTITLE_FOLDER   = "translated_subtitle_file"
M5_OUTPUT_FOLDER     = "translated_video"


def run(src_path: Path) -> Path:
    """
    Parameters
    ----------
    src_path : Path
        A temporary *.mp4* that FastAPI just wrote (e.g. /tmp/tmpxyz/video.mp4)

    Returns
    -------
    Path
        Final processed MP4 that contains French audio + hard‑burnt subtitles.
        This is what FastAPI subsequently uploads to S3.
    """
    # 1) Create an isolated working directory
    work = src_path.parent / f"m5_{uuid.uuid4().hex}"
    work.mkdir(parents=True, exist_ok=True)

    # 2) Build the sub‑directories milestone5 looks for
    gt_dir   = work / M5_GROUND_TRUTH
    fr_a_dir = work / M5_AUDIO_FR
    sub_dir  = work / M5_SUBTITLE_FOLDER
    out_dir  = work / M5_OUTPUT_FOLDER
    for d in (gt_dir, fr_a_dir, sub_dir, out_dir):
        d.mkdir()

    title = src_path.stem                     # e.g. “youtube_video”
    vid_path = gt_dir   / f"{title}.mp4"      # ground_truth/youtube_video.mp4
    wav_path = fr_a_dir / f"{title} fr audio.wav"
    srt_path = sub_dir  / f"{title} fr.srt"
    final_mp4 = out_dir / f"{title} fr video.mp4"

    # 3) Copy the uploaded MP4 where milestone5 expects it
    shutil.copyfile(src_path, vid_path)

    # 4) Create a dummy WAV ( English → WAV ) so milestone5 can transcribe
    cmd = [
        "ffmpeg", "-y", "-i", str(vid_path),
        "-ac", "1", "-ar", "16000", "-c:a", "pcm_f32le", str(wav_path),
    ]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5) Call the single public helper your current milestone5.py exposes
    #    (generate_and_mux_video does *everything* inside)
    milestone5.generate_and_mux_video(
        video_path=str(vid_path),
        audio_path=str(wav_path),
        subtitle_dir=str(sub_dir),
        output_path=str(final_mp4)
    )

    return final_mp4
