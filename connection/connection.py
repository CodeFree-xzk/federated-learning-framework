import pickle
import socket


class SocketPool:
    connections = {}

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def send(self, data):
        binary_data = pickle.dumps(data)
        len_data = len(binary_data).to_bytes(8, byteorder="big")
        self.conn.send(len_data)
        self.conn.sendall(binary_data)

    def receive(self):
        total_length = int.from_bytes(self.conn.recv(8), byteorder="big")
        print("{}bytes data to be received".format(total_length))
        cur_length = 0
        total_data = bytes()
        while cur_length < total_length:
            data = self.conn.recv(1024)
            cur_length += len(data)
            total_data += data
        print("receive completed")
        total_data = pickle.loads(total_data)
        return total_data

    @staticmethod
    def sendData(sc_idx, data):
        print("sending data to client#{}".format(sc_idx))
        SocketPool.connections[sc_idx].send(data)
        pass

    @staticmethod
    def receiveData(sc_idx):
        print("receiving data from client#{}".format(sc_idx))
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
        while count < num:
            conn, addr = sc.accept()
            socketConnection = SocketPool(conn, addr)
            SocketPool.connections[count] = socketConnection
            print("addr: {} connected".format(addr))

            data_size = socketConnection.receive()
            print("data size of client#{} is {}".format(count, data_size))
            data_sizes.append(data_size)
            count += 1

        return data_sizes


if __name__ == '__main__':
    SocketPool.register(1)
    # SocketPool.receiveData(0)
