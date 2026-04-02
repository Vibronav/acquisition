import os
import time
from .sound import play_chirp_signal
from .config import config

# MEMS microphone constants
MIC_NAME = "dmic_sv_shared"
CHANNEL_FMT = "stereo"
SAMPLING_RATE = 48000

# Contact microphone constants
CONTACT_MIC_SCRIPT = "aproach1_2.py"
CONTACT_MIC_DIR = "contact_microphone_python/vibronavFiles"


def start_mems(ssh, output_filename):
    """Start MEMS microphone recording using arecord."""
    print("Executing 'start_mems': Starting MEMS micro on needle")
    
    if ssh:
        print("MEMS Recording started")
        remote_path = f"{config['remote_dir']}/{output_filename}"
        mkdir_command = f"mkdir -p {os.path.dirname(remote_path)}"
        ssh.exec_command(mkdir_command)

        setup_command = f"echo 'DEVICE={MIC_NAME}\nDURATION=10\nSAMPLE_RATE={SAMPLING_RATE}\n" \
                        f"CHANNELS=2\nOUTPUT_FILE={remote_path}\nFORMAT=S32_LE' > " \
                        f"{config['remote_dir']}/recording_setup.txt"
        print("Setup command ====================================================================== \n")
        print(setup_command)
        ssh.exec_command(setup_command)
        time.sleep(0.01)

        start_command = f"bash -c 'source {config['remote_dir']}/recording_setup.txt && nohup arecord " \
                        f"-D $DEVICE -r $SAMPLE_RATE -c $CHANNELS -f $FORMAT -t wav -V {CHANNEL_FMT} " \
                        f"$OUTPUT_FILE &'"
        print("Start command ===================================================================== \n")
        print(start_command)
        ssh.exec_command(start_command)
        time.sleep(0.2)
        play_chirp_signal()
        return True
    
    return False


def start_contact(ssh, output_filename):
    """Start Contact microphone recording using aproach1.py (ADS1263 ADC)."""
    print("Executing 'start_contact': Starting Contact micro via ADS1263")
    
    if ssh:
        print("Contact microphone recording started")
        remote_path = f"{config['remote_dir']}/{output_filename}"
        mkdir_command = f"mkdir -p {os.path.dirname(remote_path)}"
        ssh.exec_command(mkdir_command)
        time.sleep(0.01)

        start_command = f"bash -c 'cd /home/pi/{CONTACT_MIC_DIR} && nohup python3 {CONTACT_MIC_SCRIPT} {remote_path} &'"
        print("Start command (Contact) ===================================================================== \n")
        print(start_command)
        ssh.exec_command(start_command)
        time.sleep(0.2)
        play_chirp_signal()
        return True
    
    return False


def stop_mems(ssh, file_name, delete=False):
    """Stop MEMS microphone recording."""
    if ssh is not None:
        print("MEMS Recording stopped on RaspberryPi")
        stop_command = f"kill -INT $(ps aux | grep '[a]record -D {MIC_NAME}' | awk '{{print $2}}')"
        ssh.exec_command(stop_command)

        remote_path = f"{config['remote_dir']}/{file_name}"
        local_path = os.path.join(config["local_dir"], file_name)
        os.makedirs(config["local_dir"], exist_ok=True)

        try:
            with ssh.open_sftp() as sftp:
                sftp.get(remote_path, local_path)
        except Exception as e:
            print(f"SFPT download error. (remote '{remote_path}', local '{local_path}'.", e)

        recording_status = os.path.isfile(local_path) and os.path.getsize(local_path)

        if delete:
            delete_command = f"rm {remote_path}"
            ssh.exec_command(delete_command)
            
        return recording_status
    
    print("SSH not connected during stopping recording")
    return False


def stop_contact(ssh, file_name, delete=False):
    """Stop Contact microphone recording (aproach1.py)."""
    if ssh is not None:
        print("Contact microphone recording stopped on RaspberryPi")
        stop_command = f"kill -INT $(ps aux | grep '[p]ython3 {CONTACT_MIC_SCRIPT}' | awk '{{print $2}}')"
        print(f"Stop command (Contact): {stop_command}")
        ssh.exec_command(stop_command)
        
        time.sleep(1)  # Wait for aproach1.py to finish saving

        remote_path = f"{config['remote_dir']}/{file_name}"
        local_path = os.path.join(config["local_dir"], file_name)
        os.makedirs(config["local_dir"], exist_ok=True)

        try:
            with ssh.open_sftp() as sftp:
                sftp.get(remote_path, local_path)
        except Exception as e:
            print(f"SFPT download error. (remote '{remote_path}', local '{local_path}'.", e)

        recording_status = os.path.isfile(local_path) and os.path.getsize(local_path)

        if delete:
            delete_command = f"rm {remote_path}"
            ssh.exec_command(delete_command)
            
        return recording_status
    
    print("SSH not connected during stopping recording")
    return False


def kill_mems_process(ssh):
    """Kill any running MEMS recording process."""
    if ssh is not None:
        print("Killing MEMS process on RaspberryPi")
        stop_command = f"kill -INT $(ps aux | grep '[a]record -D {MIC_NAME}' | awk '{{print $2}}')"
        ssh.exec_command(stop_command)


def kill_contact_process(ssh):
    """Kill any running Contact microphone recording process (aproach1.py)."""
    if ssh is not None:
        print("Killing Contact process on RaspberryPi")
        stop_command = f"kill -INT $(ps aux | grep '[p]ython3 {CONTACT_MIC_SCRIPT}' | awk '{{print $2}}')"
        ssh.exec_command(stop_command)
