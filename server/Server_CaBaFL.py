import copy
import random
import time
import numpy as np
import torch
from loguru import logger
from server.Server import Server


def unitization(x):
    n = np.sum(x)
    if n == 0:
        return x
    else:
        return x / n


class Server_CaBaFL(Server):
    def __init__(self, args, dataset_test, net_glob):
        super().__init__(args, dataset_test, net_glob)
        self.n = 400
        self.cache_size = int(self.args.num_users * self.args.frac)
        self.cache = [copy.deepcopy(self.net_glob) for _ in range(self.cache_size)]
        self.cache_trace = [[] for _ in range(self.cache_size)]
        self.model_trace = [[] for _ in range(self.cache_size)]
        self.activation_labels = [torch.tensor([]) for _ in range(args.num_users)]
        self.global_activation = torch.zeros(self.n).to(self.args.device)
        self.update_activation(True)
        self.sim_history = []
        self.selected_count = [0 for _ in range(args.num_users)]
        self.model_record = [None for _ in range(self.args.num_users)]

    def main(self):
        init_clients = np.random.choice(range(self.args.num_users), self.cache_size, replace=False)
        init_data = {"version": self.round, "model": self.net_glob}
        for model_idx, client in enumerate(init_clients):
            logger.debug("dispatch model to client#{}", client)
            self.sendData(client, init_data)
            logger.debug("dispatch completed")
            self.idle_client.remove(client)
            self.model_record[client: int] = (model_idx, 0)

        while time.time() - self.start_time < self.args.limit_time:
            data, client_idx = self.receiveUpdate()
            model = data["model"]
            model.to(self.args.device)
            model_index, model_version = self.model_record[client_idx]
            logger.debug("received model from client#{}", client_idx)

            if self.filter(model, model_index, model_version):
                self.cache[model_index] = copy.deepcopy(model.state_dict())
                self.cache_trace = copy.deepcopy(self.model_trace[model_index])

            if model_version == self.args.T - 1:
                weight_list = self.getAggrWeight()
                self.aggregation(self.cache, weight_list)
                self.cache[model_index] = copy.deepcopy(self.net_glob.state_dict())

                self.test()

                if self.round % self.args.CF == 0:
                    self.update_activation()

            next_client = self.selectNext(model_version, model_index)

            self.model_trace[model_index].append(next_client)
            self.idle_client.add(client_idx)
            self.idle_client.remove(next_client)

            logger.debug("dispatch model to client#{}...", next_client)
            data = {"round": self.round, "model": self.net_glob if model_version == self.args.T - 1 else model}
            self.sendData(next_client, data)
            logger.debug("dispatch completed")
            self.model_record[client_idx] = None
            self.model_record[next_client] = (model_index, (model_version + 1) % self.args.T)

    def filter(self, model, model_index, model_version):
        activation = self.get_acc_act(self.model_trace[model_index])
        cos_sim = self.get_cos_sim(activation)
        self.sim_history.append(cos_sim)
        self.sim_history.sort()
        if model_version > self.args.T // 2 - 1 or \
                (self.sim_history.index(cos_sim) + 1) / len(self.sim_history) > (1 - self.args.CB):
            self.cache[model_index] = copy.deepcopy(model.state_dict())
            self.cache_trace[model_index] = copy.deepcopy(self.model_trace[model_index])

    def update_activation(self, block=False):
        pass

    def selectNext(self, model_version, model_index):
        idle_client = list(self.idle_client)
        if model_version == self.args.T - 1:
            return random.choice(idle_client)

        temp = [self.selected_count[i] for i in idle_client]
        select_range = []
        if np.var(unitization(self.selected_count)) > self.select_var_bound:
            min_value = min(temp)
            for i in self.idle_client:
                if self.selected_count[i] == min_value:
                    select_range.append(i)
        else:
            select_range = idle_client

        R = []
        acc_act = self.get_acc_act(self.model_trace[model_index])
        for idx in select_range:
            post_activation = self.activation_labels[idx] + acc_act
            r1 = self.get_cos_sim(post_activation)

            data_size = [self.local_data_sizes[i] for i in range(self.cache_size)]
            data_size[model_index] += self.local_data_sizes[idx]
            data_size_var = np.var(unitization(data_size))
            r2 = -data_size_var

            R.append([idx, 1 * r1 + r2])
        R.sort(key=lambda x: x[1], reverse=True)
        next_client = R[0][0]
        self.selected_count[next_client] += 1
        return next_client

    def getAggrWeight(self):
        sim_list = [0. for _ in range(self.cache_size)]
        for i in range(self.cache_size):
            if len(self.cache_trace[i]) != 0:
                activation = self.get_acc_act(self.cache_trace[i])
                cos_sim = self.get_cos_sim(activation)
                sim_list[i] = cos_sim

        w_sim_lst = [1. for _ in range(self.cache_size)]
        for i in range(self.cache_size):
            temp = 1 / (1 - sim_list[i])
            w_sim_lst[i] = temp

        w_ds_list = [.0 for _ in range(self.cache_size)]
        for i in range(self.cache_size):
            label_sum = 0
            for idx in self.cache_trace[i]:
                label_sum += self.local_data_sizes[idx]
            w_ds_list[i] = label_sum ** self.a

        return np.array(w_ds_list) * np.array(w_sim_lst)

    def get_cos_sim(self, vector1, vector2=None, normal=True):
        if vector2 is None:
            vector2 = self.global_activation
        if normal:
            vector1 = vector1 / np.linalg.norm(vector1)
            vector2 = vector2 / np.linalg.norm(vector2)
        dot = np.dot(vector1, vector2)
        return dot / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

    def get_acc_act(self, clients):
        activation = np.zeros(self.n)
        for clientIndex in clients:
            activation += self.activation_labels[clientIndex]
        return activation
