# from queue import PriorityQueue
# from Clients import Clients
#
#
# class ClientManager:
#     def __init__(self):
#         self.updateQueue = []
#         self.clients = Clients()
#
#     def addUpdate(self, clientIdx, update):
#         time = self.clients.getTime(clientIdx)
#         self.updateQueue.append(update)
#         self.updateQueue.sort(key=lambda x: x[0])
#
#     def getUpdate(self):
#         update = self.updateQueue.pop(0)
#         for i in self.updateQueue:
#             i[0] -= update[0]
#         return update[1::]
