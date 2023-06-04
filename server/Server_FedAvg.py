import time

from Server import Server


class Server_FedAvg(Server):
    def __init__(self, args, dataset_test, dict_users, net_glob):
        super().__init__(args, dataset_test, dict_users, net_glob)
        self.m = int(self.args.clients_num * self.args.frac)
        self.cache = [None for _ in range(self.m)]

    def main(self):
        start_time = time.time()

        while time.time() - start_time < self.args.limit_time:
            num_of_received_model = 0
            while num_of_received_model < self.m:
                model, client_idx = self.receiveUpdate()
                num_of_received_model += 1

            Server.aggregation(self.cache, [])

            self.test()

            self.log()

            sample_clients = []

            for client in sample_clients:
                self.dispatch(client, self.net_glob)
