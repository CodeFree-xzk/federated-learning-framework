class Server:
    def __init__(self, args, dataset_test, dict_users, net_glob):
        self.dataset_test = dataset_test
        self.dict_users = dict_users
        self.net_glob = net_glob
        self.clients = None
        self.local_data = None
        self.ssh_pool = None
        self.round = 0
        self.args = args

        self.wandb = None
        self.comm = 0
        self.time = 0

    def dispatch(self, clientIdx, model):
        pass

    def checkUpdate(self):
        pass

    def aggregation(self):
        pass

    def test(self):
        return 0

    def log(self):
        pass
