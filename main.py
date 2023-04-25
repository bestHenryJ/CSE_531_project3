import json
from multiprocessing import Process, pool
from time import sleep
from concurrent import futures
import sys
import grpc
import logging
import banking_pb2_grpc
from Branch import Branch
from Customer import Customer

#configure Branch Server 
def Branch_Server(branch):
    logger = configure_logger("branch")
    port = "localhost:" + str(50000 + branch.id)
    logger.info("Starting server {}. listening on {}".format(branch.id, port))

    branch.createServer()

#set up Branch process pool
def create_Branch_process_Pool(input_load):
    branchID = []
    process_pool = []

    for process in input_load:
        if process["type"] == "branch":
            branchID.append(process["id"])

    # reference to https://github.com/grpc/grpc/issues/16001 about use multiprocessing to deal with concurrent problem
    for process in input_load:
        if process["type"] == "branch":
           # self.Branch_Server(Branch(process["id"], process["balance"], branchID))
            branch_process = Process(target=Branch_Server, args=(Branch(process["id"], process["balance"], branchID),))
            process_pool.append(branch_process)
            branch_process.start()
    return process_pool

#set up Customer process pool
def create_Customer_process_Pool(input_load):
    customerProcesses = []
    for process in input_load:
        if process["type"] == "customer":
            customer_process = Process(target=Customer_Server, args=(Customer(process["id"], process["events"]),))
            customerProcesses.append(customer_process)
            customer_process.start()

    # wait all stub process to finish
    for customerProcess in customerProcesses:
        customerProcess.join()

    return customerProcesses

# another option to set up rpc server not implement yet
def rpcMethod(self, request, context):
    result = pool.apply_async(someExpensiveFunction(request))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port('[::]:50051')
    server.start()

#configure Customer Server
def Customer_Server(customer):
    logger = configure_logger("Customer")
    logger.info(" CustomerID {} is working".format(customer.id))
    customer.executeEvents()

#configure logger 
def configure_logger(name):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

if __name__ == "__main__":

    with open('input.json','r') as input_data:

        input_load = json.load (input_data)
        customerProcesses = []


        branchProcesses = []
        branchProcesses = create_Branch_process_Pool(input_load)
        
        #let all branch processes finish configuration
        sleep(1)

        customerProcesses = create_Customer_process_Pool(input_load)

        #user prompt message
        logger = configure_logger("info")
        logger.info("Stop app by ctrl + c or wait 15 minute")

