import socket


class SocketPool:
    connections = {}

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def send(self, data):
        pass

    def receive(self):
        total_length = int.from_bytes(self.conn.recv(8), byteorder="big")
        print("{}bytes data to be received".format(total_length))
        cur_length = 0
        total_data = b''
        while cur_length < total_length:
            data = self.conn.recv(1024)
            cur_length += len(data)
            total_data += data
        print("receive completed")
        print(total_data)
        return total_data

    @staticmethod
    def sendData(sc_idx, data):
        print("sending data to client#{}".format(sc_idx))
        SocketPool.connections[sc_idx].send(data)
        pass

    @staticmethod
    def receiveModel(sc_idx):
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
            count += 1

        return data_sizes


if __name__ == '__main__':
    SocketPool.register(1)
    SocketPool.receiveModel(0)
