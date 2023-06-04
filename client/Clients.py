import socket


class Clients:
    def __init__(self):
        self.socket = None
        self.addr = ('127.0.0.1', 8080)

        self.TrainConfig = None

    def register(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.addr)
        print('connected to the server')
        print("sending data size to server...")
        self.uploadToServer(100)
        print("send completed")


    def localTrain(self):
        pass

    def uploadToServer(self, data):
        binary_data = data.encode('utf-8')
        len_data = len(binary_data).to_bytes(8, byteorder="big")
        print(len_data)
        self.socket.send(len_data)
        self.socket.sendall(binary_data)


def hotUpdate(self):
    pass
