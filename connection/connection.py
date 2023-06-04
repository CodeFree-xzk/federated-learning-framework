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
        print("应接收{}字节消息".format(total_length))
        cur_length = 0
        total_data = b''
        while cur_length < total_length:
            data = self.conn.recv(1024)
            cur_length += len(data)
            total_data += data
        print("接收完毕")
        print(total_data)

    @staticmethod
    def sendModel(sc_idx, model):
        SocketPool.connections[sc_idx].send(model)
        pass

    @staticmethod
    def receiveModel(sc_idx):
        SocketPool.connections[sc_idx].receive()

    @staticmethod
    def register(num):
        HOST = "127.0.0.1"
        PORT = 8080
        sc = socket.socket()
        sc.bind((HOST, PORT))
        sc.listen(1000)

        count = 0
        while count < num:
            conn, addr = sc.accept()
            socketConnection = SocketPool(conn, addr)
            SocketPool.connections[count] = socketConnection
            print("addr: {} connected".format(addr))
            count += 1


if __name__ == '__main__':
    SocketPool.register(1)
    SocketPool.receiveModel(0)
