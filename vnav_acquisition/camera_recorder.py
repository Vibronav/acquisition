import cv2
import pyaudio
import numpy as np
import time
import wave
from moviepy.editor import VideoFileClip, AudioFileClip
import tempfile
import os

# Video ve ses ayarları
frame_width = 1920
frame_height = 1080
fps = 30
audio_rate = 48000
record_seconds = 6  # Her bir kayıt süresi (saniye)

# Global değişkenler
p = None
stream = None

def initialize_camera():
    video_capture = cv2.VideoCapture(1)  # USB kameranın indexi
    if not video_capture.isOpened():
        print("Kamera bağlanamadı. Yeniden deniyor...")
        time.sleep(1)  # Bağlantı sağlamak için kısa bir bekleme
        video_capture.open(1)
        if not video_capture.isOpened():
            raise RuntimeError("Kamera bağlantısı sağlanamadı!")

    # Set camera resolution to Full HD
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    
    # Check if the resolution has been set correctly
    actual_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera resolution set to {actual_width}x{actual_height}")
    
    return video_capture

def initialize_audio():
    global p, stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=audio_rate, input=True, frames_per_buffer=2048)
    return p, stream

def record_segment(segment_num):
    frames = []
    video_capture = initialize_camera()
    initialize_audio()

    # Geçici dosyalar
    video_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    audio_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    
    # Video kaydını başlat
    video_filename = video_tempfile.name
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 formatı için codec
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

    print(f"Kayıt {segment_num} başladı...")

    start_time = time.time()
    recording = True
    while recording:
        ret, frame = video_capture.read()
        if ret:
            # Resmi yeniden boyutlandırma
            frame = cv2.resize(frame, (frame_width, frame_height))
            out.write(frame)
            cv2.imshow('frame', frame)  # Küçük bir pencerede gösterim

            # Pencereyi küçük tutarak performansı artırabilir
            cv2.resizeWindow('frame', 640, 360)  # Küçük pencere boyutu
            
            # Ses kaydı
            data = stream.read(2048, exception_on_overflow=False)
            frames.append(data)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # 'q' tuşuna basılınca kayıt durur
                recording = False
            elif key == ord('w'):  # 'w' tuşuna basılınca yeni segment başlar
                print("Yeni segment başlatılıyor...")
                recording = False

        else:
            print("Kamera bağlantısı kaybedildi, yeniden bağlanıyor...")
            video_capture = initialize_camera()  # Kamerayı yeniden başlat

    # Temizlik işlemleri
    print(f"Kayıt {segment_num} bitti.")
    video_capture.release()
    out.release()
    stream.stop_stream()
    stream.close()
    
    # Ses dosyasını kaydet
    wave_filename = audio_tempfile.name
    wave_file = wave.open(wave_filename, 'wb')
    wave_file.setnchannels(1)
    wave_file.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wave_file.setframerate(audio_rate)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()

    # Video ve sesi birleştir
    final_filename = f'final_output_{segment_num}.mp4'
    video_clip = VideoFileClip(video_filename)
    audio_clip = AudioFileClip(wave_filename)
    
    # Ses ve videoyu birleştir
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(final_filename, codec='libx264', audio_codec='aac')

    # Geçici dosyaları temizlemek için kısa bir bekleme süresi ekleyin
    time.sleep(2)  # 2 saniye bekleme süresi

    # Geçici dosyaları temizle
    try:
        os.remove(video_filename)
        os.remove(wave_filename)
    except PermissionError:
        print(f"Dosyayı silme hatası: {video_filename} veya {wave_filename} dosyası hala kullanımda.")
    
    # Ekran penceresini kapat
    cv2.destroyWindow('frame')

# Döngü ile kayıt yap
try:
    segment_num = 1
    while True:
        record_segment(segment_num)
        segment_num += 1
finally:
    if stream is not None:
        stream.stop_stream()
        stream.close()
    if p is not None:
        p.terminate()
    cv2.destroyAllWindows()
