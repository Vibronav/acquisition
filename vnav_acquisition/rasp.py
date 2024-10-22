import paramiko
import time

# SSH connection details
hostname = 'raspberrypi'
port = 22
username = 'pi'
password = 'VibroNav'

# Function to execute a command on the Raspberry Pi via SSH
def ssh_command(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, username, password)
    
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.read().decode('utf-8').strip()

# Function to get CPU temperature
def get_cpu_temp():
    command = "vcgencmd measure_temp"
    return ssh_command(command)

# Function to get CPU usage
def get_cpu_usage():
    command = "top -bn1 | grep 'Cpu(s)'"
    return ssh_command(command)

# Function to get memory usage
def get_memory_usage():
    command = "free -h"
    return ssh_command(command)

# Function to get system uptime
def get_uptime():
    command = "uptime -p"
    return ssh_command(command)

# Function to monitor system stats
def monitor_system():
    try:
        while True:
            print("=== Raspberry Pi System Stats ===")
            # Fetch and print CPU temperature
            cpu_temp = get_cpu_temp()
            print(f"CPU Temperature: {cpu_temp}")
            
            # Fetch and print CPU usage
            cpu_usage = get_cpu_usage()
            print(f"CPU Usage: {cpu_usage}")
            
            # Fetch and print memory usage
            memory_usage = get_memory_usage()
            print(f"Memory Usage:\n{memory_usage}")
            
            # Fetch and print system uptime
            uptime = get_uptime()
            print(f"Uptime: {uptime}")
            
            print("\n---------------------------------\n")
            # Refresh every 5 seconds
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    monitor_system()
