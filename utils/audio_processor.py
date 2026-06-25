import os
from typing import List

import yt_dlp
from pydub import AudioSegment

# ==========================================================
# Configuration
# ==========================================================

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ==========================================================
# Download YouTube Audio
# ==========================================================

def download_youtube_audio(url: str) -> str:
    """
    Downloads YouTube audio and converts it to WAV.
    """

    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,

        # Uncomment if YouTube blocks downloads
        # Export cookies.txt using the
        # "Get cookies.txt LOCALLY" Chrome extension.
        # "cookiefile": "cookies.txt",

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = os.path.splitext(
                ydl.prepare_filename(info)
            )[0] + ".wav"

        return filename

    except Exception as e:
        raise RuntimeError(f"YouTube download failed:\n{e}")


# ==========================================================
# Convert Local Audio / Video to WAV
# ==========================================================

def convert_to_wav(input_path: str) -> str:
    """
    Converts any supported audio/video file into
    16kHz Mono WAV.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(input_path)

    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(output_path, format="wav")

    return output_path


# ==========================================================
# Chunk Audio
# ==========================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10
) -> List[str]:
    """
    Splits audio into smaller chunks.
    """

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    base = os.path.splitext(wav_path)[0]

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]

        chunk_path = f"{base}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    return chunks


# ==========================================================
# Complete Pipeline
# ==========================================================

def process_input(source: str) -> List[str]:
    """
    Accepts either

    • YouTube URL
    • Local audio
    • Local video

    Returns list of WAV chunks.
    """

    if source.startswith(("http://", "https://")):

        print("Downloading YouTube audio...")

        wav_path = download_youtube_audio(source)

    else:

        if not os.path.exists(source):
            raise FileNotFoundError(source)

        if source.lower().endswith(".wav"):

            print("Using existing WAV file...")

            wav_path = source

        else:

            print("Converting file to WAV...")

            wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Finished! Created {len(chunks)} chunk(s).")

    return chunks


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    source = input(
        "Enter YouTube URL or local file path:\n"
    )

    chunk_files = process_input(source)

    print("\nGenerated chunks:")

    for chunk in chunk_files:
        print(chunk)