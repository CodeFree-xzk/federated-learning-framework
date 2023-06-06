from server.Server import *


class Server_FedAvg(Server):

    def main(self):
        m = int(self.args.num_users * self.args.frac)

        while time.time() - self.start_time < self.args.limit_time:
            sample_clients = np.random.choice(range(self.args.num_users), m, replace=False)

            for client in sample_clients:
                logger.debug("dispatch model to client#{}", client)
                self.sendData(client)
                logger.debug("dispatch completed")

            weights = []
            cache = []
            wait = set(sample_clients)
            while wait:
                model, client_idx = self.receiveUpdate()
                logger.debug("received model from client#{}", client_idx)
                cache.append(model.state_dict())
                weights.append(self.local_data_sizes[client_idx])
                wait.remove(client_idx)

            self.aggregation(cache, weights)

            self.test()
