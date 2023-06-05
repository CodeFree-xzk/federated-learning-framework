import time

from server.Server import *


class Server_FedAvg(Server):
    def __init__(self, args, dataset_test, net_glob):
        super().__init__(args, dataset_test, net_glob)
        self.m = int(self.args.client_nums * self.args.frac)
        self.cache = [None for _ in range(self.m)]

    def main(self):
        start_time = time.time()

        while time.time() - start_time < self.args.limit_time:
            sample_clients = np.random.choice(self.idle_client, self.m, replace=False)

            for client in sample_clients:
                logger.debug("dispatch model to client#{}", client)
                self.dispatch(client)
                logger.debug("dispatch completed")

            weights = []
            wait = set(sample_clients)
            while wait:
                model, client_idx = self.receiveUpdate()
                logger.debug("received model from clients#{}", client_idx)
                self.cache.append(model)
                weights.append(self.local_data_sizes[client_idx])
                wait.remove(client_idx)

            self.aggregation(self.cache, weights)

            self.test()
