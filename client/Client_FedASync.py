import copy
import torch
from loguru import logger
from client.Clients import Clients


class Clients_FedASync(Clients):

    def localTrain(self, net):
        glob_model = copy.deepcopy(net)
        net.train()
        # train and update
        if self.args.optimizer == 'sgd':
            optimizer = torch.optim.SGD(net.parameters(), lr=self.args.lr, momentum=self.args.momentum)
        elif self.args.optimizer == 'adam':
            optimizer = torch.optim.Adam(net.parameters(), lr=self.args.lr)

        Predict_loss = 0
        Penalize_loss = 0

        global_weight_collector = list(glob_model.parameters())

        for i in range(self.args.local_ep):

            for batch_idx, (images, labels) in enumerate(self.ldr_train):
                images, labels = images.to(self.args.device), labels.to(self.args.device)
                net.zero_grad()
                log_probs = net(images)['output']
                predictive_loss = self.loss_func(log_probs, labels)

                fed_prox_reg = 0.0
                for param_index, param in enumerate(net.parameters()):
                    fed_prox_reg += (
                            (self.args.prox_alpha / 2) * torch.norm((param - global_weight_collector[param_index])) ** 2)

                loss = predictive_loss + fed_prox_reg
                Predict_loss += predictive_loss.item()
                Penalize_loss += fed_prox_reg.item()

                loss.backward()
                optimizer.step()

        if self.verbose:
            info = '\nUser predict Loss={:.4f}'.format(Predict_loss / (self.args.local_ep * len(self.ldr_train)))
            info += ', Penalize loss={:.4f}'.format(Penalize_loss / (self.args.local_ep * len(self.ldr_train)))
            print(info)

        return net.state_dict()

    def main(self):
        while True:
            data = self.receiveFromServer()
            version = data["version"]
            model = data["model"]
            logger.debug("received data from server")
            model.to(self.args.device)
            self.localTrain(model)
            logger.debug("training finished")
            data = {"version": version, "model": model}
            self.uploadToServer(data)
            logger.debug("upload data successfully")

