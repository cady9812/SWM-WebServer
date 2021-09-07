import bson
import socket
import time

#from private.ports import SOCKET_PORT

BUFSIZE = 0x1000
SOCKET_PORT = 9000
def create_socket():
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sckt.connect(('0.0.0.0', SOCKET_PORT))
            break
        except ConnectionRefusedError as e:
            time.sleep(1)
            continue
    
    # 본인이 웹임을 알리기 위해서
    introduce = {
        "type": "introduce",
        "detail": "web",
    }
    sckt.send(bson.dumps(introduce))
    
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
