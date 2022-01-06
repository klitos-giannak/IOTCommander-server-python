import fcntl
import json
import os
import select
import socket
import struct

"""
This script is meant to be run as a service. Its purpose is to make the device running it, discoverable by other devices
in the local network

This is achieved the following way. It binds to a specific port under UDP in all available network interfaces in order
to be able to receive network broadcast packages.
When it receives a json string containing "action" = "discover", it responds with a json containing the key "deviceName"
with value the hostname of the running device, thus revealing the IP the device holds on the network
"""

PORT_TO_BIND = 9977

discover_response = ""
should_continue = True
timeout = 2  # seconds


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


def parse_broadcast_message(to_parse):
    """Parse the given string as a json and return a dictionary with the json's contents"""
    try:
        decoded = json.loads(to_parse)
        if decoded is not None:
            return decoded
    except ValueError:
        # this is a JSONDecodeError, but we are catching superclass for backwards compatibility
        return None


def initialise():
    # Read the system's available network interfaces
    network_interfaces = os.listdir('/sys/class/net/')
    network_interfaces.remove('lo')

    print('\nFound Network Interfaces:')
    for net_interface in network_interfaces:
        print(net_interface + ' ' + get_ip(net_interface))

    hostname = socket.gethostname()
    global discover_response
    discover_response = '{"deviceName":"' + hostname + '"}'


def start():
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    broadcast_socket.bind(('', PORT_TO_BIND))
    print("\n\nBroadcast Server started: listening to port " + str(PORT_TO_BIND) + "\n")

    broadcast_socket.setblocking(0)
    epoll = select.epoll()
    epoll.register(broadcast_socket.fileno(), select.EPOLLIN)
    while should_continue:
        events = epoll.poll(1)
        if not events:
            continue
        if broadcast_socket.fileno() == events[0][0]:
            (message, address) = broadcast_socket.recvfrom(1024)
            decoded_message = message.decode().rstrip('\n')
            ip = address[0]
            port = str(address[1])
            print("In <-" + ip + ":" + port + " : " + decoded_message)

            parsed_message = parse_broadcast_message(decoded_message)

            if parsed_message is not None:
                if parsed_message['action'] == "discover":
                    print('action "discover" found. Responding...')
                    outgoing_message = discover_response.encode()
                    broadcast_socket.sendto(outgoing_message, address)
                    print("Out -> " + ip + ":" + port + " : " + discover_response)

    epoll.unregister(broadcast_socket.fileno())
    epoll.close()
    broadcast_socket.close()
    print("\nBroadcast Server stopped\n")


def stop():
    global should_continue
    should_continue = False


if __name__ == "__main__":
    initialise()
    try:
        start()
    except KeyboardInterrupt:
        print("Broadcast Server interrupted")
