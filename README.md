# federated-learning-framework
A federated learning framework that can be deployed on real devices, supporting both synchronous and asynchronous federated learning. 
The FedASync and FedAvg algorithms have been implemented in the project, and more federated learning algorithms will be implemented in the future. 
SocketPool implements asynchronous IO through epoll and manages all socket connections. 
The Server class encapsulates network transmission by calling SocketPool.