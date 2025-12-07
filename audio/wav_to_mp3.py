#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Get the base audio directory from the environment variable
base_dir = os.environ.get('NLTL_LOCAL_AUDIO')
if not base_dir:
    print("Error: NLTL_LOCAL_AUDIO environment variable is not set.")
    sys.exit(1)

wav_dir = Path(base_dir) / 'wav'
mp3_dir = Path(base_dir) / 'mp3'

if not wav_dir.exists():
    print(f"Error: WAV directory does not exist: {wav_dir}")
    sys.exit(1)

mp3_dir.mkdir(parents=True, exist_ok=True)

    # Gather all .wav and .WAV files
wav_files = list(wav_dir.glob('*.wav')) + list(wav_dir.glob('*.WAV'))

for wav_file in wav_files:
    # Get the modification time as the timestamp
    mtime = wav_file.stat().st_mtime
    timestamp = datetime.fromtimestamp(mtime).strftime('%Y%m%d-%H%M%S')
    mp3_file = mp3_dir / f"{timestamp}.mp3"

    if mp3_file.exists():
        print(f"Skipping {wav_file.name}: {mp3_file.name} already exists.")
        continue

    print(f"Converting {wav_file.name} -> {mp3_file.name}")
    # Use ffmpeg to convert wav to mp3
    result = subprocess.run([
        'ffmpeg', '-y', '-i', str(wav_file), '-codec:a', 'libmp3lame', '-qscale:a', '2', str(mp3_file)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print(f"Error converting {wav_file.name}: {result.stderr.decode()}")
    else:
        print(f"Successfully converted {wav_file.name} to {mp3_file.name}")
