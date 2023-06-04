import copy

import numpy as np
import torch
import wandb

from server.test import test_img


class Server:
    def __init__(self, args, dataset_test, dict_users, net_glob):
        self.dataset_test = dataset_test
        self.dict_users = dict_users
        self.net_glob = net_glob
        self.clients = None
        self.local_data = None
        self.ssh_pool = None
        self.round = 0
        self.client_num = 0
        self.args = args

        self.comm = 0
        self.time = 0
        self.comm_list = []
        self.time_list = []
        self.acc = []
        self.max_avg = 0
        self.max_std = 0

    def register(self):
        pass

    def dispatch(self, client_idx, model):
        pass

    def receiveUpdate(self):
        pass

    def test(self):
        acc_test, loss_test = test_img(self.net_glob, self.dataset_test, self.args)
        self.acc.append(acc_test.item())
        if len(self.acc) >= 10:
            avg = sum(self.acc[len(self.acc) - 10::]) / 10
            if avg > self.max_avg:
                self.max_avg = avg
                self.max_std = np.std(self.acc[len(self.acc) - 10::])
        print("acc:{:.2f}, max_avg:{:.2f}, max_std:{:.2f}".format(acc_test, self.max_avg, self.max_std))
        self.time_list.append(self.time)
        self.comm_list.append(self.comm)
        wandb.log({'acc': acc_test.item(), 'max_avg': self.max_avg, 'time': self.time, "comm": self.comm})

        return acc_test.item()

    def log(self):
        pass

    def main(self):
        pass

    @staticmethod
    def aggregation(model_list, weight_list):
        w_avg = None
        total_count = sum(weight_list)

        for i in range(0, len(model_list)):
            if i == 0:
                w_avg = copy.deepcopy(model_list[0])
                for k in w_avg.keys():
                    w_avg[k] = model_list[i][k] * weight_list[i]
            else:
                for k in w_avg.keys():
                    w_avg[k] = w_avg[k] + model_list[i][k] * weight_list[i]

        for k in w_avg.keys():
            w_avg[k] = torch.div(w_avg[k], total_count)

        return w_avg
