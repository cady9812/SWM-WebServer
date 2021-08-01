import bson


BUFSIZE = 0x1000

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
    return (sckt, result)