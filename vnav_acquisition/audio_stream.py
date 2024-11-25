import time
import paramiko
import threading
import numpy as np


class Streamer():
    def __init__(self):
        # SSH bağlantısı için gerekli bilgiler
        self.hostname = 'raspberrypi.local'
        self.port = 22
        self.username = 'pi'
        self.password = 'VibroNav'

        self.data_channel1 = []
        self.data_channel2 = []

        self.CHUNK = 512
        self.RATE = 44100

        self.isRunning = False
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.hostname, self.port, self.username, self.password)
            ftp_client=client.open_sftp()
            ftp_client.put("./audio_stream_in_pi.py","/home/pi/audio_stream.py")
            ftp_client.close()
            self.isRunning = True

        except BaseException as e:
            print("Failed to initialize audio streamer", e)

    def ssh_command(self, command):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname, self.port, self.username, self.password)

        stdin, stdout, stderr = client.exec_command(command)
        return  stdout

    def start_recording(self):
        result = None 
        while result == None:
            try:
                result = self.ssh_command("python3 /home/pi/audio_stream.py")
            except BaseException as e:
                print("RaspberryPi Audio Streaming Error: ", e)
        return result 


    def data_listener(self,stdout,):
        while True:
            data = stdout.read(self.CHUNK * 8)
            if len(data) == self.CHUNK * 8:
                data = np.frombuffer(data, dtype=np.int32)
                self.data_channel1 = data[::2]
                self.data_channel2 = data[1::2]




if __name__ == "__main__":
    streamer = Streamer()
    stdout = streamer.start_recording()
    threading.Thread(target=streamer.data_listener, args=(stdout,), daemon=True).start()
    while True:
        print(streamer.data_channel1)
        time.sleep(0.1)
