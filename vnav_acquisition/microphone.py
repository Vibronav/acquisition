import os
import shlex
import time
from .sound import play_chirp_signal
from .config import config

# MEMS microphone constants
MIC_NAME = "dmic_sv_shared"
CHANNEL_FMT = "stereo"
SAMPLING_RATE = 48000
REMOTE_MEMS_HELPER = "/home/pi/mems_continuous_recorder.py"
MEMS_RECORD_START_BYTES = {}

# Contact microphone constants
CONTACT_MIC_SCRIPT = "aproach1_2.py"
CONTACT_MIC_DIR = "contact_microphone_python/vibronavFiles"


def _read_stdout(stdout):
    return stdout.read().decode("utf-8", errors="replace").strip()


def _exec_checked(ssh, command, label):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    stdout_text = _read_stdout(stdout)
    stderr_text = stderr.read().decode("utf-8", errors="replace").strip()
    if exit_status != 0:
        print(f"{label} failed with status {exit_status}: {stderr_text or stdout_text}")
        return None
    return stdout_text


def ensure_mems_continuous(ssh):
    """Start the MEMS capture process once and keep it running."""
    if ssh is None:
        return False

    remote_dir = shlex.quote(config['remote_dir'])
    mkdir_command = f"mkdir -p {remote_dir}"
    ssh.exec_command(mkdir_command)
    start_command = (
        f"python3 {REMOTE_MEMS_HELPER} start "
        f"--remote-dir {remote_dir} "
        f"--device {shlex.quote(MIC_NAME)} "
        f"--sample-rate {SAMPLING_RATE} "
        f"--channels 2 "
        f"--format S32_LE"
    )
    result = _exec_checked(ssh, start_command, "MEMS continuous start")
    return result is not None


def _mark_mems_position(ssh):
    remote_dir = shlex.quote(config['remote_dir'])
    mark_command = (
        f"python3 {REMOTE_MEMS_HELPER} mark "
        f"--remote-dir {remote_dir} "
        f"--channels 2"
    )
    result = _exec_checked(ssh, mark_command, "MEMS mark")
    if result is None:
        return None
    try:
        return int(result.splitlines()[-1])
    except (ValueError, IndexError):
        print(f"Invalid MEMS mark output: {result}")
        return None


def _set_mems_recording_state(ssh, is_recording):
    remote_dir = shlex.quote(config['remote_dir'])
    command = "begin-recording" if is_recording else "end-recording"
    state_command = f"python3 {REMOTE_MEMS_HELPER} {command} --remote-dir {remote_dir}"
    return _exec_checked(ssh, state_command, f"MEMS {command}") is not None


def start_mems(ssh, output_filename):
    """Mark the current position of the continuous MEMS recording."""
    print("Executing 'start_mems': Marking MEMS recording start")
    
    if ssh:
        if not ensure_mems_continuous(ssh):
            return False
        if not _set_mems_recording_state(ssh, True):
            return False

        start_byte = _mark_mems_position(ssh)
        if start_byte is None:
            _set_mems_recording_state(ssh, False)
            return False

        MEMS_RECORD_START_BYTES[output_filename] = start_byte
        print("MEMS Recording started")
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
    """Save a WAV segment from the continuous MEMS recording."""
    if ssh is not None:
        print("Saving MEMS recording segment from RaspberryPi")
        start_byte = MEMS_RECORD_START_BYTES.pop(file_name, None)
        if start_byte is None:
            print(f"No MEMS start marker for {file_name}")
            return False

        end_byte = _mark_mems_position(ssh)
        if end_byte is None:
            _set_mems_recording_state(ssh, False)
            return False
        
        remote_path = f"{config['remote_dir']}/{file_name}"
        remote_path_quoted = shlex.quote(remote_path)
        mkdir_command = f"mkdir -p {shlex.quote(os.path.dirname(remote_path))}"
        ssh.exec_command(mkdir_command)
        remote_dir = shlex.quote(config['remote_dir'])
        save_command = (
            f"python3 {REMOTE_MEMS_HELPER} save "
            f"--remote-dir {remote_dir} "
            f"--sample-rate {SAMPLING_RATE} "
            f"--channels 2 "
            f"--start-byte {start_byte} "
            f"--end-byte {end_byte} "
            f"--output-file {remote_path_quoted}"
        )
        save_output = _exec_checked(ssh, save_command, "MEMS segment save")
        if save_output is None:
            _set_mems_recording_state(ssh, False)
            return False

        _set_mems_recording_state(ssh, False)

        local_path = os.path.join(config["local_dir"], file_name)
        os.makedirs(config["local_dir"], exist_ok=True)

        try:
            with ssh.open_sftp() as sftp:
                sftp.get(remote_path, local_path)
        except Exception as e:
            print(f"SFPT download error. (remote '{remote_path}', local '{local_path}'.", e)

        recording_status = os.path.isfile(local_path) and os.path.getsize(local_path)

        if delete:
            delete_command = f"rm {remote_path_quoted}"
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
        stop_command = f"python3 {REMOTE_MEMS_HELPER} stop --remote-dir {shlex.quote(config['remote_dir'])}"
        ssh.exec_command(stop_command)


def kill_contact_process(ssh):
    """Kill any running Contact microphone recording process (aproach1.py)."""
    if ssh is not None:
        print("Killing Contact process on RaspberryPi")
        stop_command = f"kill -INT $(ps aux | grep '[p]ython3 {CONTACT_MIC_SCRIPT}' | awk '{{print $2}}')"
        ssh.exec_command(stop_command)
