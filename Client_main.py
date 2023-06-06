import json

import torch

from client.Client_FedASync import Clients_FedASync
from client.Client_FedAvg import Clients_FedAvg
from utils.get_dataset import get_dataset
from utils.options import args_parser
from utils.set_seed import set_random_seed

if __name__ == '__main__':
    args = args_parser()
    args.device = torch.device('cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
    dataset_train, dataset_test, dict_users = get_dataset(args)

    # with open("data.json", "r", encoding="utf-8") as f:
    #     data_dicts = json.load(f)
    #     data_dict = data_dicts[args.ID]

    set_random_seed(args.seed)

    client = None
    if args.algorithm == "FedASync":
        client = Clients_FedASync(args, dataset_train, idxs=[args.ID * 10000 + i for i in range(10000)])
    elif args.algorithm == "FedAvg":
        client = Clients_FedAvg(args, dataset_train, idxs=[args.ID * 10000 + i for i in range(10000)])
    client.main()
