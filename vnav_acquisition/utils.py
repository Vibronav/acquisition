import psutil
import ipaddress


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
        