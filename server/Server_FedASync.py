import time
import numpy as np
from loguru import logger
from server.Server import Server


class Server_FedASync(Server):
    def aggregation_FedASync(self, w_local, w_global, version):
        lag = self.round - version
        alpha = self.args.FedASync_alpha * ((lag + 1) ** -self.args.poly_a)
        for i in w_local.keys():
            w_global[i] = alpha * w_local[i] + (1 - alpha) * w_global[i]
        self.round += 1
        self.net_glob.load_state_dict(w_global)
        return w_global

    def main(self):
        m = int(self.args.num_users * self.args.frac)
        init_clients = np.random.choice(range(self.args.num_users), m, replace=False)
        init_data = {"version": self.round, "model": self.net_glob}
        for client in init_clients:
            logger.debug("dispatch model to client#{}", client)
            self.sendData(client, init_data)
            logger.debug("dispatch completed")
            self.idle_client.remove(client)

        while time.time() - self.start_time < self.args.limit_time:
            data, client_idx = self.receiveUpdate()
            model = data["model"]
            version = data["version"]
            logger.debug("received model from client#{}", client_idx)

            model.to(self.args.device)
            self.net_glob.to(self.args.device)
            self.aggregation_FedASync(model.state_dict(), self.net_glob.state_dict(), version)

            self.test()

            next_client = np.random.choice(list(self.idle_client), 1, replace=False)[0]
            self.idle_client.add(client_idx)
            logger.debug("dispatch model to client#{}...", next_client)
            data = {"version": self.round, "model": self.net_glob}
            self.sendData(next_client, data)
            logger.debug("dispatch completed")
