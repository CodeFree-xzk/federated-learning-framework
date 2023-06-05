import pickle
import socket
import time
import selectors

from loguru import logger


class SocketPool:
    connections = {}
    sel = selectors.DefaultSelector()

    @staticmethod
    def send(conn, data, client_idx):
        binary_data = pickle.dumps(data)
        len_data = len(binary_data).to_bytes(8, byteorder="big")
        length = len(binary_data)

        binary_data = len_data + binary_data

        logger.info("sending data ({} bytes) to client#{}...", length, client_idx)
        try:
            conn.sendall(binary_data)
        except OSError as e:
            logger.error("sending failed! connection between client#{} has been closed!", client_idx)
            return
        logger.info("sending data ({} bytes) to client#{} completely", length, client_idx)

    @staticmethod
    def receive(conn, client_idx):
        try:
            bin_len = conn.recv(8)
        except ConnectionResetError as e:
            return None

        total_length = int.from_bytes(bin_len, byteorder="big")
        if total_length == 0:
            return None

        logger.info("{}bytes data to be received from client#{}", total_length, client_idx)
        cur_length = 0
        total_data = bytes()
        while cur_length < total_length:
            data = conn.recv(1024)
            cur_length += len(data)
            total_data += data
        logger.info("receive completed")
        total_data = pickle.loads(total_data)
        return total_data

    @staticmethod
    def sendData(sc_idx, data):
        SocketPool.send(SocketPool.connections[sc_idx][0], data, sc_idx)
        pass

    @staticmethod
    def receiveData():
        while True:
            try:
                events = SocketPool.sel.select()
            except OSError as e:
                logger.critical("All clients has disconnected!!!")
                raise ConnectionError("All clients has disconnected!!!")

            for key, mask in events:
                client_idx = key.data
                received_data = SocketPool.receive(key.fileobj, client_idx)
                if received_data is None:
                    logger.warning("client#{} disconnected", client_idx)
                    key.fileobj.close()
                    SocketPool.sel.unregister(key.fileobj)
                return received_data, client_idx


    @staticmethod
    def register(num):
        HOST = "127.0.0.1"
        PORT = 8080
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc.bind((HOST, PORT))
        sc.listen(1000)

        data_sizes = []

        logger.debug("waiting clients to connect...")
        count = 0
        while count < num:
            conn, addr = sc.accept()
            socketConnection = (conn, addr)
            SocketPool.connections[count] = socketConnection
            logger.info("client#{}, addr: {} connected".format(count, addr))
            data_size = SocketPool.receive(conn, count)
            logger.info("data size of client#{} is {}".format(count, data_size))
            data_sizes.append(data_size)

            SocketPool.sel.register(conn, selectors.EVENT_READ, count)
            count += 1

        sc.setblocking(False)
        logger.debug("all clients are ready")
        return data_sizes


if __name__ == '__main__':
    SocketPool.register(1)
    # time.sleep(5)
    SocketPool.receiveData()
    # SocketPool.receiveData(0)
