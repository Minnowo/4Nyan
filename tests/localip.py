import socket

import ipaddress


def wlan_ip():
    import subprocess

    result = subprocess.run("ipconfig", stdout=subprocess.PIPE, text=True).stdout.lower()
    scan = 0
    for i in result.split("\n"):
        if "wireless" in i:  # use "wireless" or wireless adapters and "ethernet" for wired connections
            scan = 1
        if scan:
            if "ipv4" in i:
                return i.split(":")[1].strip()


print(wlan_ip())

# import socket

# print(
#     [l for l in (
#         [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1],
#         [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
