import torch
from loguru import logger
from client.Clients import Clients


class Clients_FedSA(Clients):

    def localTrain(self, net):
        net.train()
        # train and update
        optimizer = None
        if self.args.optimizer == 'sgd':
            optimizer = torch.optim.SGD(net.parameters(), lr=self.args.lr, momentum=self.args.momentum, )
        elif self.args.optimizer == 'adam':
            optimizer = torch.optim.Adam(net.parameters(), lr=self.args.lr)

        Predict_loss = 0
        for i in range(self.args.local_ep):

            for batch_idx, (images, labels) in enumerate(self.ldr_train):
                images, labels = images.to(self.args.device), labels.to(self.args.device)
                net.zero_grad()
                log_probs = net(images)['output']
                loss = self.loss_func(log_probs, labels)
                loss.backward()
                optimizer.step()

                Predict_loss += loss.item()

        if self.verbose:
            info = '\nUser predict Loss={:.4f}'.format(Predict_loss / (self.args.local_ep * len(self.ldr_train)))
            print(info)
        return net.state_dict()

    def main(self):
        while True:
            model = self.receiveFromServer()
            logger.debug("received model from server")
            model.to(self.args.device)
            self.localTrain(model)
            logger.debug("training finished")
            self.uploadToServer(model)
            logger.debug("upload model successfully")
