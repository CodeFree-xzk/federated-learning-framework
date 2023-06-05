import pickle
import socket
import time

from loguru import logger


class SocketPool:
    connections = {}

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def send(self, data):
        binary_data = pickle.dumps(data)
        len_data = len(binary_data).to_bytes(8, byteorder="big")

        logger.info("sending data length ({} bytes) to client...", len(binary_data))
        self.conn.send(len_data)
        logger.info("sending data length ({} bytes) to client completely", len(binary_data))

        logger.info("sending data ({} bytes) to client...", len_data)
        self.conn.sendall(binary_data)
        logger.info("sending data ({} bytes) to client completely", len_data)

    def receive(self):
        bin_len = self.conn.recv(8)
        total_length = int.from_bytes(bin_len, byteorder="big")
        logger.info("{}bytes data to be received".format(total_length))
        cur_length = 0
        total_data = bytes()
        while cur_length < total_length:
            data = self.conn.recv(1024)
            cur_length += len(data)
            total_data += data
        logger.info("receive completed")
        total_data = pickle.loads(total_data)
        return total_data

    @staticmethod
    def sendData(sc_idx, data):
        logger.info("sending data to client#{}".format(sc_idx))
        SocketPool.connections[sc_idx].send(data)
        pass

    @staticmethod
    def receiveData(sc_idx):
        logger.info("receiving data from client#{}".format(sc_idx))
        SocketPool.connections[sc_idx].receive()

    @staticmethod
    def register(num):
        HOST = "127.0.0.1"
        PORT = 8080
        sc = socket.socket()
        sc.bind((HOST, PORT))
        sc.listen(1000)

        data_sizes = []

        count = 0
        start_time = time.time()
        while count < num:
            # TODO 这里的60不能写死
            if time.time() - start_time > 60:
                logger.error("time out, please check client process and internet")
                break
            conn, addr = sc.accept()
            socketConnection = SocketPool(conn, addr)
            SocketPool.connections[count] = socketConnection
            logger.info("client#{}, addr: {} connected".format(count, addr))

            data_size = socketConnection.receive()
            logger.info("data size of client#{} is {}".format(count, data_size))
            data_sizes.append(data_size)
            count += 1

        return data_sizes


if __name__ == '__main__':
    SocketPool.register(1)
    # SocketPool.receiveData(0)
