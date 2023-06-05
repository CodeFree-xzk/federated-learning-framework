import time

import numpy as np

from server.Server import *
from utils.config import get_args

args = get_args()


class Server_test(Server):
    def __init__(self, args, dataset_test, net_glob):
        super().__init__(args, dataset_test, net_glob)

    def main(self):
        start_time = time.time()
        while True:
            for i in range(X):
                self.dispatch(i)

            wait = set(range(X))
            while wait:
                model, client_idx = self.receiveUpdate()
                wait.remove(client_idx)
