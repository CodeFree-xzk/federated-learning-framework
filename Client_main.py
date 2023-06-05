import torch

from client.Client_FedASync import Clients_FedASync
from utils.get_dataset import get_dataset
from utils.options import args_parser
from utils.set_seed import set_random_seed

if __name__ == '__main__':
    args = args_parser()
    args.device = torch.device('cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
    dataset_train, dataset_test, dict_users = get_dataset(args)
    del dataset_test
    set_random_seed(args.seed)

    client = Clients_FedASync(args, dataset_train, idxs=[3 * 10000 + i for i in range(10000)])
    client.main()
