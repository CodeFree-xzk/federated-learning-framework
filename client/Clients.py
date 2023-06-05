import pickle
import socket
from loguru import logger


class Clients:
    def __init__(self):
        self.socket = None
        self.addr = ('127.0.0.1', 8080)

        self.trainConfig = None

    def register(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('connected to the server...')
        self.socket.connect(self.addr)
        logger.info("connected to the server successfully")
        logger.info("sending data size to server...")
        data_size = 100
        self.uploadToServer(data_size)
        logger.info("send completed")

    def localTrain(self):
        pass

    def uploadToServer(self, data):
        binary_data = pickle.dumps(data)
        len_data = len(binary_data).to_bytes(8, byteorder="big")
        self.socket.send(len_data)
        self.socket.sendall(binary_data)

    def receiveFromServer(self):
        total_length = int.from_bytes(self.socket.recv(8), byteorder="big")
        logger.info("{} bytes data to be received".format(total_length))
        cur_length = 0
        total_data = bytes()
        while cur_length < total_length:
            data = self.socket.recv(1024)
            cur_length += len(data)
            total_data += data
        logger.info("receive completed")
        total_data = pickle.loads(total_data)
        # print(total_data)
        # print(type(total_data))
        return total_data

    def main(self):
        pass


def hotUpdate(self):
    pass


if __name__ == '__main__':
    client = Clients()
    client.register()
    client.receiveFromServer()
