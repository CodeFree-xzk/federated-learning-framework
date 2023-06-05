import time
from model.Nets import CNNCifar
from server.Server import *
from utils.get_dataset import get_dataset
from utils.options import args_parser
from utils.set_seed import set_random_seed


class Server_FedAvg(Server):
    def __init__(self, args, dataset_test, net_glob):
        super().__init__(args, dataset_test, net_glob)

    def main(self):
        m = int(self.args.num_users * self.args.frac)
        start_time = time.time()

        while time.time() - start_time < self.args.limit_time:
            sample_clients = np.random.choice(range(args.num_users), m, replace=False)

            for client in sample_clients:
                logger.debug("dispatch model to client#{}", client)
                self.dispatch(client)
                logger.debug("dispatch completed")

            weights = []
            cache = []
            wait = set(sample_clients)
            while wait:
                model, client_idx = self.receiveUpdate()
                logger.debug("received model from clients#{}", client_idx)
                cache.append(model.state_dict())
                weights.append(self.local_data_sizes[client_idx])
                wait.remove(client_idx)

            self.aggregation(cache, weights)

            self.test()


if __name__ == '__main__':
    args = args_parser()
    args.device = torch.device('cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
    set_random_seed(args.seed)
    dataset_train, dataset_test, dict_users = get_dataset(args)
    net_glob = CNNCifar(args)

    server = Server_FedAvg(args, dataset_test, net_glob)
    server.main()
