class Clients:
    def getCommTime(self, idx):
        return 1

    def getTrainTime(self, idx):
        return 1

    def getTime(self, idx):
        return self.getCommTime(idx) + self.getTrainTime(idx)
