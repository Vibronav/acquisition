import os
import time
import requests
import glob
from playwright.sync_api import sync_playwright
from vnav_acquisition.comm import on_rec_start, on_rec_stop
from vnav_acquisition.config import config
from sync import add_audio_annotations
import cv2
import threading
import subprocess
import paramiko
from datetime import datetime

# Jabra PanaCast 20 cihaz adları
video_source = "Jabra PanaCast 20"  # Video cihazının adı
audio_device_name = "Mikrofon (Jabra PanaCast 20)"  # Ses cihazının adı

# Video ve ses ayarları
frame_width = 1920
frame_height = 1080
fps = 30
audio_rate = 48000
record_seconds = 9.35  # Her bir kayıt süresi (saniye)

# Kayıtların yapılacağı dizin
video_output_dir = r"C:\Users\ucunb.DESKTOP-JEKP035.000\OneDrive\Masaüstü\acquisition-master2\videos"

def record_audio_video(output_filename, duration):
    # Dosya yolunu ayarlayın
    output_filepath = os.path.join(video_output_dir, output_filename)
    
    command = [
    'ffmpeg',
    '-f', 'dshow',  
    '-rtbufsize', '1G',  
    '-video_size', f"{frame_width}x{frame_height}",
    '-r', str(fps),  # Frame rate düzeltmesi için -r kullan
    '-i', f"video={video_source}",  
    '-f', 'dshow',  
    '-i', f"audio={audio_device_name}",  
    '-ar', str(audio_rate),
    '-ac', '1',  
    '-t', str(duration),
    '-c:v', 'libx264',  
    '-c:a', 'libopus',  # Use Opus codec
    '-b:a', '256k',  # High-quality audio bitrate
    '-preset', 'fast',
    '-filter:a', 'loudnorm',  # Optional: Normalize audio
    '-async', '1',  # Synchronize audio with video
    '-strict', 'experimental',  
    output_filename
]

    
    print(f"Ses ve video kaydediliyor: {output_filepath}")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"Ses ve video kaydı tamamlandı: {output_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Error while executing FFmpeg: {e}")

def get_flask_port():
    port_file_path = os.path.join(os.path.dirname(__file__), 'flask_port.txt')
    if os.path.exists(port_file_path):
        with open(port_file_path, 'r') as f:
            port = f.read().strip()
            return port
    else:
        raise Exception("Flask port file not found.")
    
def establish_ssh_connection(host, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        print("SSH connection established.")
        return ssh
    except Exception as e:
        print(f"Failed to establish SSH connection: {str(e)}")
        return None

def run_automation(username, material, speed, position_type, p1, p2, p3):
    setup_json_path = r'C:\Users\ucunb.DESKTOP-JEKP035.000\OneDrive\Masaüstü\acquisition-master2\setup.json'
    config.load_from_json(setup_json_path)
    
    flask_port = get_flask_port()

    with sync_playwright() as p:
        video_path = os.path.join(os.path.dirname(setup_json_path), "videos", f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4")
        record_video_dir = os.path.join(os.path.dirname(setup_json_path), "videos")
        
        try:
            os.makedirs(record_video_dir, exist_ok=True)
            print(f"Video directory created: {record_video_dir}")
        except Exception as e:
            print(f"Failed to create video directory: {str(e)}")
            return
        
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            permissions=["camera", "microphone"],
            record_video_dir=record_video_dir,
            record_video_size={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        page.goto(f"http://localhost:{flask_port}")
        
        video_source_dropdown = page.locator('select#videoSource')
        audio_source_dropdown = page.locator('select#audioSource')

        video_source_dropdown.select_option(label="Integrated Camera (174f:2459)")
        audio_source_dropdown.select_option(label="Mikrofon (Realtek(R) Audio)")

        page.fill('input#username', username)
        print("Username filled.")

        page.wait_for_selector(f'input[type="radio"][name="material"][value="{material}"]')
        page.locator(f'input[type="radio"][name="material"][value="{material}"]').check()

        page.wait_for_selector(f'input[type="radio"][name="speed"][value="{speed}"]')
        page.locator(f'input[type="radio"][name="speed"][value="{speed}"]').check()

        print("Material and speed selected.")

        num_iterations = 22
        page.wait_for_timeout(5000)
        
        for i in range(num_iterations):
            try:
                # Başlangıçta video kaydı başlat
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                output_filename = f"output_{timestamp}.mp4"
                recording_thread = threading.Thread(target=record_audio_video, args=(output_filename, record_seconds))
                
                # Kamera kaydını başlat
                recording_thread.start()
                
                print(f"Recording {i+1}/{num_iterations} started.")
                start_recording_url = f"http://localhost:{flask_port}/start"
                response = requests.post(start_recording_url, json={"username": username, "material": material, "speed": speed})
                response.raise_for_status()
                print(f"Recording started via Flask application. Iteration {i+1}/{num_iterations}")
    
                page.wait_for_selector('button#rec', state='visible')
                print(f"Recording {i+1}/{num_iterations}...")
                page.click('button#rec')
                print("Record button clicked.")
                
                
                time.sleep(9)
  
                # Stop button click
                page.wait_for_selector('button#stop', state='visible')
                page.click('button#stop')
                print("Stop button clicked.")
                
                # Stop recording raspberyypi
                stop_recording_url = f"http://localhost:{flask_port}/stop"
                response = requests.get(stop_recording_url)
                response.raise_for_status()
                print("Recording stopped via Flask application.")
                
                # Kamera kaydını durdurma
                recording_thread.join()  # Kamera kaydının bitmesini bekle
          
                # İlk hareket setini tekrarla
                           

            except Exception as e:
                print(f"An error occurred in iteration {i+1}: {e}")

        print(f"Iteration {i+1} completed.")
        context.close()
        browser.close()
        print(f"All {num_iterations} loops completed. Context and browser closed.")

if __name__ == "__main__":
    run_automation("test_user", config["materials"][1], config["speeds"][1], "Up, Down, Forward", (350, 0, 50, 0), (350, 0, 50, 0), (350, 0, -10, 0))