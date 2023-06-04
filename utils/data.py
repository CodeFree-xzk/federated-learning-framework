from connection.connection import SocketPool
from utils.get_dataset import get_dataset


def allocateLocalData(args):
    dataset_train, dataset_test, dict_users = get_dataset(args)
    for client in range(args.clients_num):
        SocketPool.sendData(client, )


