import subprocess
import os
import time

def _ffprobe_start_time(path, select):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", select,
        "-show_entries", "stream=start_time",
        "-of", "csv=p=0",
        path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip() != ""]
    return float(lines[-1]) if lines else None
    

def cut_video(path):
    start_time = time.time()
    v_start = _ffprobe_start_time(path, "v:0")
    a_start = _ffprobe_start_time(path, "a:0")

    delta = a_start - v_start
    tmp = path.replace(".mp4", "_cut.mp4")
    print(delta)

    if delta == 0:
        return
    
    cut_seconds = max(v_start, a_start)

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", path,
        "-ss", f'{cut_seconds:.6f}',
        "-map", "0",
        "-c:v", "libx264",
        "-c:a", "copy",
        "-fflags", "+genpts",
        "-movflags", "+faststart",
        tmp
    ]
    
    subprocess.run(cmd, check=True)
    os.replace(tmp, path)
    print(f'Video cutting completed in {time.time() - start_time:.2f} seconds')
    return