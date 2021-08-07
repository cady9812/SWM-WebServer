import bson
import socket
import time

BUFSIZE = 0x1000

def create_socket():
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sckt.connect(('192.168.0.163', 9000))
            break
        except ConnectionRefusedError as e:
            time.sleep(1)
            continue
    return sckt

def recv_data(sckt):
    result = sckt.recv(1)
    sckt.setblocking(False)
    try:
        while True:
            tmp = sckt.recv(BUFSIZE)
            if not tmp:
                break
            result += tmp
    except BlockingIOError as e:
        # EAGAIN
        pass
    finally:
        sckt.setblocking(True)
    result = bson.loads(result)
    return result

def get_local_ip(server_ip="8.8.8.8"):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((server_ip, 0))
    ip = s.getsockname()[0]
    s.close()
    return ip
