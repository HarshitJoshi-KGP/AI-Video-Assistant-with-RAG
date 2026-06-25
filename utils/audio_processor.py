import os
from typing import List

import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ==========================================================
# Download YouTube Audio
# ==========================================================

def download_youtube_audio(url: str) -> str:

    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,

        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,

        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        },

        # Uncomment if cookies are required
        # "cookiefile": "cookies.txt",

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            wav_file = (
                os.path.splitext(
                    ydl.prepare_filename(info)
                )[0]
                + ".wav"
            )

            if not os.path.exists(wav_file):
                raise RuntimeError(
                    "Download finished but WAV file was not created."
                )

            return wav_file

    except yt_dlp.utils.DownloadError as e:
        raise RuntimeError(f"YouTube DownloadError:\n{e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected Error:\n{e}")