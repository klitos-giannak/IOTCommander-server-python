import os
import socket
import select
import fcntl
import struct
import json
from json import JSONDecodeError

"""
This script is meant to be run as a service. Its purpose is to make the device running it, discoverable by other devices
in the local network

This is achieved the following way. It binds to a specific port under UDP in all available network interfaces in order
to be able to receive network broadcast packages.
When it receives a json string containing "action" = "discover", it responds with a json containing the key "deviceName"
with value the hostname of the running device, thus revealing the IP the device holds on the network
"""

PORT_TO_BIND = 9977


def get_ip(if_name):
    """Try to find and return the ip(version 4) that the given network interface holds.
    This method will return empty string if an IP address is not found"""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        found_ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(if_name[:15], "utf8"))
        )[20:24])
    except IOError:
        return ""
    finally:
        s.close()
    return found_ip


def parse_broadcast_message(to_parse: str):
    """Parse the given string as a json and return a dictionary with the json's contents"""
    try:
        decoded: dict = json.loads(to_parse)
        if decoded is not None:
            return decoded
    except JSONDecodeError:
        return None


# Read the system's available network interfaces
network_interfaces = os.listdir('/sys/class/net/')
network_interfaces.remove('lo')

print('\nFound Network Interfaces:')
[print(net_interface + ' ' + get_ip(net_interface)) for net_interface in network_interfaces]

hostname = socket.gethostname()
discoverResponse = '{"deviceName":"' + hostname + '"}'

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

broadcastSocket.bind(('', PORT_TO_BIND))
print("\n\nBroadcast Server started: listening to port " + str(PORT_TO_BIND) + "\n")

while 1:
    (rfd, wfd, efd) = select.select([broadcastSocket], [], [])
    if broadcastSocket in rfd:
        (message, address) = broadcastSocket.recvfrom(1024)
        decodedMessage = message.decode().rstrip('\n')
        ip = str(address[0])
        port = str(address[1])
        print("In <-" + ip + ":" + port + " : " + decodedMessage)

        parsedMessage = parse_broadcast_message(decodedMessage)

        if parsedMessage['action'] == "discover":
            print('action "discover" found. Responding...')
            outgoingMessage = discoverResponse.encode()
            broadcastSocket.sendto(outgoingMessage, address)
            print("Out -> " + ip + ":" + port + " : " + discoverResponse)
