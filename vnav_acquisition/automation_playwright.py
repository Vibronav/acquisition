import os
import time
import requests
import paramiko
import glob
from playwright.sync_api import sync_playwright
from vnav_acquisition.comm import on_rec_start, on_rec_stop
from vnav_acquisition.config import config
from sync import add_audio_annotations
from dobot import connect_robot, enable_robot, move_to_position  # Dobot fonksiyonlarını import etme
import cv2
import threading

# Global variables
recording = [False, False, False]  # Two cameras
video_writers = [None, None, None]
caps = [None, None, None]

import subprocess

def start_recording_ffmpeg(video_filename, audio_device_name):
    # Start FFmpeg process to record both video and audio
    command = [
        'ffmpeg',
        '-f', 'dshow',
        '-i', f'video="{video_filename}":audio="{audio_device_name}"',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-y',  # Overwrite output file if it exists
        f'output_{time.strftime("%Y-%m-%d_%H-%M-%S")}.mp4'
    ]
    return subprocess.Popen(command)

def stop_recording_ffmpeg(process):
    process.terminate()
    process.wait()
    print("Recording stopped and saved.")


def get_laptop_camera_index():
    # Bu fonksiyon yerleşik laptop kamerasının indeksini bulur.
    index = 0
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        cap.release()
        return index
    return None

def get_usb_camera_index():
    # Bu fonksiyon harici USB kameranın indeksini bulur.
    index = 1  # Genellikle USB kameralar 1 numarayla başlar; 0 yerleşik laptop kamerası
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        cap.release()
        return index
    return None

def start_camera_recording(camera_index, output_path):
    global recording, video_writers, caps

    # Release any existing capture
    if caps[camera_index]:
        caps[camera_index].release()
        caps[camera_index] = None

    # Open the camera
    caps[camera_index] = cv2.VideoCapture(camera_index)
    if not caps[camera_index].isOpened():
        print(f"Error: Camera {camera_index} not accessible.")
        return
    
    # Set camera resolution to 1920x1080 (Full HD)
    caps[camera_index].set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    caps[camera_index].set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    frame_width = int(caps[camera_index].get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(caps[camera_index].get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writers[camera_index] = cv2.VideoWriter(output_path, fourcc, 60.0, (frame_width, frame_height))
    recording[camera_index] = True

    def record():
        while recording[camera_index]:
            ret, frame = caps[camera_index].read()
            if not ret:
                print(f"Error: Failed to read frame from camera {camera_index}.")
                break
            video_writers[camera_index].write(frame)

    threading.Thread(target=record, daemon=True).start()

def stop_camera_recording(camera_index):
    global recording, video_writers, caps

    recording[camera_index] = False
    if caps[camera_index]:
        caps[camera_index].release()
    if video_writers[camera_index]:
        video_writers[camera_index].release()

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

def run_automation(username, material, speed, position_type, p1, p2, p3):
    setup_json_path = r'C:\Users\ucunb\OneDrive\Masaüstü\Vibronav\acquisition-master\setup.json'
    config.load_from_json(setup_json_path)
    
    laptop_camera_index = get_laptop_camera_index()
    usb_camera_index = get_usb_camera_index()
    
    if laptop_camera_index is None or usb_camera_index is None:
        print("Error: Could not find required cameras.")
        return

    with sync_playwright() as p:
        video_path = os.path.join(os.path.dirname(setup_json_path), "videos", f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4")
        record_video_dir = r'C:\Users\ucunb\OneDrive\Masaüstü\acquisition-master-yedek - Kopya - 5 - Kopya\videos'
        
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
        page.goto("http://localhost:5488")  # Adjust port if necessary
        
        # Video ve ses kaynaklarını seçmek için dropdown menüye erişim sağlayın
        video_source_dropdown = page.locator('select#videoSource')
        audio_source_dropdown = page.locator('select#audioSource')

        # Video kaynağını ayarlayın
        video_source_dropdown.select_option(label="Integrated Camera (174f:2459)")  # veya value ile: value="d7c04b2221e299301d48400e8eb6ff0ee4544b39c95c76ee878f56c955e98e82"

        # Ses kaynağını ayarlayın
        audio_source_dropdown.select_option(label="Mikrofon (Realtek(R) Audio)")  # veya value ile: value="default"

        page.fill('input#username', username)
        print("Username filled.")

        page.wait_for_selector(f'input[type="radio"][name="material"][value="{material}"]')
        page.locator(f'input[type="radio"][name="material"][value="{material}"]').check()

        page.wait_for_selector(f'input[type="radio"][name="speed"][value="{speed}"]')
        page.locator(f'input[type="radio"][name="speed"][value="{speed}"]').check()

        print("Material and speed selected.")

        num_iterations = 12
        page.wait_for_timeout(5000)

        # Dobot ile bağlantı kuruluyor
        dashboard, move = connect_robot()
        enable_robot(dashboard)
        time.sleep(2)
        
        for i in range(num_iterations):
            try:
                timestamp = time.strftime("%Y.%m.%d-%H.%M.%S")
                usb_camera_filename = os.path.join(record_video_dir, f"usb_camera_{timestamp}.mp4")
                
                # Dobot'un hareketlerini tanımlıyoruz
                # Gelen pozisyonlar arayüzden çekiliyor
                P1 = p1  # Arayüzden gelen P1
                P2 = p2 if position_type == "Up, Down, Forward" else None  # Arayüzden gelen P2
                P3 = p3  # Arayüzden gelen P3

                # Move to P1
                move_to_position(dashboard, move, P1)
                time.sleep(1)  # Dobot ilk pozisyonuna geçene kadar bekle

                # Record button click
                start_recording_url = "http://localhost:5488/start"
                response = requests.post(start_recording_url, json={"username": username, "material": material, "speed": speed})
                response.raise_for_status()
                print(f"Recording started via Flask application. Iteration {i+1}/{num_iterations}")
    
                page.wait_for_selector('button#rec', state='visible')
                print(f"Recording {i+1}/{num_iterations}...")
                page.click('button#rec')
                print("Record button clicked.")

                start_camera_recording(usb_camera_index, usb_camera_filename)
                print(f"Started recording USB camera to {usb_camera_filename}")
                
                # Dobot'u aşağı indir
                if P2:
                    move_to_position(dashboard,move, P2)
                    time.sleep(2)
                    
                # Dobot'u aşağı indir
                move_to_position(dashboard,move, P3)
                time.sleep(2)
                
                # Move to P1
                move_to_position(dashboard, move, P1)
                time.sleep(2)  # Dobot ilk pozisyonuna geçene kadar bekle

                # Stop button click
                page.wait_for_selector('button#stop', state='visible')
                page.click('button#stop')
                print("Stop button clicked.")
                
                # Stop recording
                stop_recording_url = "http://localhost:5488/stop"
                response = requests.get(stop_recording_url)
                response.raise_for_status()
                print("Recording stopped via Flask application.")
                
                stop_camera_recording(usb_camera_index)
                print(f"USB camera recording stopped and saved to {usb_camera_filename}")
                
            except Exception as e:
                print(f"An error occurred in iteration {i+1}: {e}")
      
        dashboard.DisableRobot()
        print(f"Iteration {i+1} completed.")
        context.close()
        browser.close()
        print(f"All {num_iterations} loops completed. Context and browser closed.")

if __name__ == "__main__":
    run_automation("test_user", config["materials"][1], config["speeds"][1], "Up, Down, Forward", (350, 0, 20, 0), (350, 0, 20, 0), (350, 0, -22, 0))
