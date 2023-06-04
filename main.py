from model.Nets import *
from server.Server_FedAvg import Server_FedAvg
from utils.options import args_parser

if __name__ == '__main__':
    args = args_parser()
    net_glob = CNNCifar(args)
    server = Server_FedAvg(args, None, net_glob)
    server.dispatch(0)

