import time

import numpy as np

from server.Server import *

X = 2


class Server_test(Server):
    def __init__(self, args, dataset_test, net_glob):
        super().__init__(args, dataset_test, net_glob)

    def main(self):
        start_time = time.time()
        for i in range(X):
            self.dispatch(i)

        count = 0
        while count < X:
            self.receiveUpdate()
