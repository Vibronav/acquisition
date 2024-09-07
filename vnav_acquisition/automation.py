import time
from vnav_acquisition.comm import on_rec_start, on_rec_stop
from vnav_acquisition.config import config

def start_recording(params):
    print("Starting recording with parameters:", params)
    # username parametresini de ekliyoruz
    file_name = on_rec_start(config['connection'], username='default_user', **params)
    return file_name

def stop_recording():
    recording_status = on_rec_stop()
    return recording_status

def run_automation():
    while True:
        params = {
            "speed": "medium",
            "material": "default"
        }
        file_name = start_recording(params)
        print("Recording started: ", file_name)
        
        time.sleep(10)  # Kayıt süresi, ihtiyaçlarınıza göre ayarlayabilirsiniz

        recording_status = stop_recording()
        print("Recording stopped: ", recording_status)

        time.sleep(5)  # Bir sonraki kayda başlamadan önce bekleme süresi
