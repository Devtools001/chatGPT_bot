import subprocess
import os


def audioconvert(path):
    out_path = path + ".wav"
    command = [
        r'/usr/bin/ffmpeg',
        '-i', path,
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', '16000',
        out_path
    ]

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(path)

    if result.returncode:
        os.remove(out_path)
        return False
    else:
        return out_path
