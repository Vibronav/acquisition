import os
import socket
import psutil
import ipaddress


def get_flask_port():
    """Reads the Flask port number from flask_port.txt (in the same directory)."""
    port_file_path = os.path.join(os.path.dirname(__file__), 'flask_port.txt')
    if os.path.exists(port_file_path):
        with open(port_file_path, 'r') as f:
            return f.read().strip()
    else:
        raise Exception("Flask port file not found.")

def get_broadcast_address():

    target_interface = "Wi-Fi"
    
    for iface, addrs in psutil.net_if_addrs().items():
        if iface != target_interface:
            continue
        for addr in addrs:
            if addr.family.name == "AF_INET" and not addr.address.startswith("127."):
                ip = int(ipaddress.IPv4Address(addr.address))
                netmask = int(ipaddress.IPv4Address(addr.netmask))
                broadcast = ip | (~netmask & 0xFFFFFFFF)
                return str(ipaddress.IPv4Address(broadcast))