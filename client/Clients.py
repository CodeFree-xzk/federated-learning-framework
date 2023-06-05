import pickle
import socket
import time
from abc import abstractmethod
from loguru import logger
from torch import nn
from torch.utils.data import DataLoader
from utils.get_dataset import DatasetSplit


class Clients:
    def __init__(self, args, dataset=None, idxs=None, verbose=False):
        self.socket = None
        self.addr = ('127.0.0.1', 8080)

        self.args = args
        self.loss_func = nn.CrossEntropyLoss()
        self.selected_clients = []
        self.ldr_train = DataLoader(DatasetSplit(dataset, idxs), batch_size=self.args.local_bs, shuffle=True)
        self.verbose = verbose
        self.idxs = idxs

        self.trainConfig = None
        self.register()

    def register(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('connected to the server...')
        self.socket.connect(self.addr)
        logger.info("connected to the server successfully")
        logger.info("sending data size to server...")
        data_size = 100
        self.uploadToServer(data_size)
        logger.info("send completed")

    def uploadToServer(self, data):
        binary_data = pickle.dumps(data)
        len_data = len(binary_data).to_bytes(8, byteorder="big")
        length = len(binary_data)

        binary_data = len_data + binary_data

        logger.info("sending data ({} bytes) to client...", length)
        self.socket.sendall(binary_data)
        logger.info("sending data ({} bytes) to client completely", length)

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
        return total_data

    @abstractmethod
    def localTrain(self, net):
        pass

    @abstractmethod
    def main(self):
        pass


def hotUpdate(self):
    pass


if __name__ == '__main__':
    client = Clients()
    while True:
        model = client.receiveFromServer()
        time.sleep(5)
        client.uploadToServer(model)
