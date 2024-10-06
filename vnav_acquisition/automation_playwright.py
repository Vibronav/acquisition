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
from dobot import connect_robot, enable_robot, move_to_position  # Dobot fonksiyonlarını import etme


# Jabra PanaCast 20 cihaz adları
video_source = "Jabra PanaCast 20"  # Video cihazının adı
audio_device_name = "Mikrofon (Jabra PanaCast 20)"  # Ses cihazının adı

# Video ve ses ayarları
frame_width = 1920
frame_height = 1080
fps = 30
audio_rate = 48000

# Kayıtların yapılacağı dizin
video_output_dir = r"C:\Users\ucunb.DESKTOP-JEKP035.000\OneDrive\Masaüstü\acquisition-master2\vnav_acquisition\videos"

def start_recording(output_filepath):
    command = [
        'ffmpeg',
        '-f', 'dshow',  # Windows için DirectShow
        '-rtbufsize', '1G',  # Buffer boyutunu artırın
        '-video_size', f"{frame_width}x{frame_height}",
        '-framerate', str(fps),
        '-i', f"video={video_source}",  # Video cihazının adı
        '-f', 'dshow',  # Windows için DirectShow
        '-i', f"audio={audio_device_name}",  # Ses cihazının adı
        '-ar', str(audio_rate),
        '-ac', '1',  # Mono ses
        '-c:v', 'libx264',  
        '-c:a', 'libopus',  # Use Opus codec
        '-b:a', '256k',  # High-quality audio bitrate
        '-preset', 'fast',
        '-filter:a', 'loudnorm',  # Optional: Normalize audio
        '-async', '1',  # Synchronize audio with video
        '-strict', 'experimental',  
        output_filepath
    ]
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    return process

    #print(f"Ses ve video kaydediliyor: {output_filepath}")
    #subprocess.run(command, check=True)
    #print(f"Ses ve video kaydı tamamlandı: {output_filepath}")
def stop_recording(process):
    if process.stdin:
        # Send 'q' to the ffmpeg process to stop recording gracefully
        process.stdin.write(b'q')
        process.stdin.flush()
        process.wait(timeout=1)
    else:
        print("Error: Process stdin is None")

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

def synchronize_audio_video(audio_video_directory):
    audio_files = glob.glob(os.path.join(audio_video_directory, '*.wav'))
    video_files = glob.glob(os.path.join(audio_video_directory, '*.mp4'))

    for audio_file in audio_files:
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        corresponding_video_file = os.path.join(audio_video_directory, base_name + '.mp4')
        
        if corresponding_video_file in video_files:
            try:
                result = add_audio_annotations(corresponding_video_file, audio_file, audio_file.replace('.wav', '_annotations.json'))
                print(f'Synchronization successful for {base_name}: {result}')
            except Exception as e:
                print(f'Error synchronizing {base_name}: {str(e)}')
        else:
            print(f'No matching video file found for {base_name}')

def run_automation(username, material, speed=None, position_type=None, p1=None, p2=None, p3=None, num_iterations=None):
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


        page.wait_for_timeout(5000)
        
        # Dobot ile bağlantı kuruluyor
        dashboard, move = connect_robot()
        enable_robot(dashboard)
        time.sleep(2)
        
        if num_iterations is None:
            num_iterations = 12  # Default value if not provided
        
        if speed is not None:  # If speed parameter is provided
            if speed == "slow":
                speed_value = 10
            elif speed == "medium":
                speed_value = 15
            elif speed == "fast":
                speed_value = 25
            else:
                speed_value = 15  # Default value if the speed string is not recognized
        
        dashboard.SpeedFactor(speed_value)
        
            # Dobot'un hareketlerini tanımlıyoruz (interface ile  çalıştırmak için)   
        if position_type == "Only Up and Down":  # If position_type is provided
            P1 = p1  # Initial position from GUI
            P2 = None # Initial position from GUI  
            P3 = p3  # Initial position from GUI
        elif position_type == "Up, Down, Forward":
            P1 = p1  # Initial position from GUI
            P2 = p2  # Initial position from GUI  
            P3 = p3  # Initial position from GUI
            
        if position_type is None:    # Dobot'un hareketlerini tanımlıyoruz (interface olmadan çalıştırmak için)   
            P1 = (275, 150, 110, 0)  # X, Y, Z, R
            P2 = (P1[0], P1[1], 110, P1[3])  # X, Y, Z, R
            P3 = (P1[0], P1[1], 70, P1[3])  # X, Y, Z, R
        
        for i in range(num_iterations):
            try:
                # Başlangıçta video kaydı başlat
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                output_filename = f"output_{timestamp}.mp4"
                output_filepath = os.path.join(video_output_dir, output_filename)

                # Dobot'un hareketlerini tanımlıyoruz
                # Gelen pozisyonlar arayüzden çekiliyor
                # Yeni pozisyonlar ikinci döngü için
                print(f"Speed set to {speed_value}%")
                # Move to P1
                move_to_position(dashboard, move, P1)
                time.sleep(1)  # Dobot ilk pozisyonuna geçene kadar bekle
                
                print(f"Recording {i+1}/{num_iterations} started.")
                start_recording_url = f"http://localhost:{flask_port}/start"
                #response = requests.post(start_recording_url, json={"username": username, "material": material, "speed": speed})
                #response.raise_for_status()
                print(f"Recording started via Flask application. Iteration {i+1}/{num_iterations}")
                
                # Kamera kaydını başlat
                recording_process = start_recording(output_filepath)

                page.wait_for_selector('button#rec', state='visible')
                print(f"Recording {i+1}/{num_iterations}...")
                page.click('button#rec')
                print("Record button clicked.")
  
                # Dobot'u aşağı indir
                if P2:
                    move_to_position(dashboard,move, P2)
                    time.sleep(2.71)
                #move_to_position(dashboard,move, P2)
                #time.sleep(2)
                    
                # Dobot'u aşağı indir
                move_to_position(dashboard,move, P3)
                time.sleep(2.71)
                
                # Move to P1
                move_to_position(dashboard, move, P1)
                time.sleep(2.71)  # Dobot ilk pozisyonuna geçene kadar bekle

                 # Stop button click
                page.wait_for_selector('button#stop', state='visible')
                page.click('button#stop')
                print("Stop button clicked.")
                
                # Stop recording raspberyypi
                stop_recording_url = f"http://localhost:{flask_port}/stop"
                #response = requests.get(stop_recording_url)
                #response.raise_for_status()
                print("Recording stopped via Flask application.")
                if P2 is not None:  # Eğer P2 geçerli ise
                    P1 = (P1[0] + 1, P1[1], P1[2], P1[3])
                    P2 = (P1[0], P2[1], P2[2], P2[3])  # P2 güncellenir
                    P3 = (P1[0], P3[1], P3[2], P3[3])  # P3 güncellenir
                else:  # P2 geçerli değilse
                    print("P2 kullanılmadı, sadece P1 ve P3 güncelleniyor.")
                
                # Stop recording
                time.sleep(0.91)
                stop_recording(recording_process)

                # İlk hareket setini tekrarla
                           
            except Exception as e:
                print(f"An error occurred in iteration {i+1}: {e}")
                
        
        dashboard.DisableRobot()

        print(f"Iteration {i+1} completed.")
        #print(f"All {num_iterations} loops completed.")
        context.close()
        browser.close()
        print(f"All {num_iterations} loops completed. Context and browser closed.")

if __name__ == "__main__":
    run_automation("test_user", config["materials"][0], config["speeds"][1], None, None, None, None)
    #run_automation("test_user", config["materials"][0], config["speeds"][0], "Up, Down, Forward", (350, 0, 50, 0), (350, 0, 50, 0), (350, 0, -10, 0))
