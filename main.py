from model.Nets import *
from server.Server_FedAvg import Server_FedAvg
from temp.Server_test import Server_test
from utils.get_dataset import get_dataset
from utils.options import args_parser
from utils.set_seed import set_random_seed

if __name__ == '__main__':
    args = args_parser()
    args.device = torch.device('cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
    set_random_seed(args.seed)
    dataset_train, dataset_test, dict_users = get_dataset(args)
    net_glob = CNNCifar(args)
    server = Server_FedAvg(args, dataset_test, net_glob)
    server.main()

