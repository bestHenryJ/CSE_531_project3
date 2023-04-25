from time import sleep
import logging
import grpc
import sys
import banking_pb2_grpc
from banking_pb2 import MsgRequest

class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None
        # record unique ID
        self.writeSets = list()
        self.writeSets.append(0)

    # TODO: students are expected to create the Customer stub
    def createStub(self, event):
        port = "localhost:" + str(50000 + event["dest"])
        self.stub = banking_pb2_grpc.BankStub(grpc.insecure_channel(port))

    # TODO: students are expected to send out the events to the Bank
    def executeEvents(self):
        for event in self.events:
            
            self.createStub(event)

            # for "query" request should sleep 3 sec to  to guarantee all the updates are propagated among the Branch processes
            if event["interface"] == "query":
                self.executeQuery(event, 3)
                continue

            #self.writeSets.append(event["dest"]*10)
            # extract customer request from events
            request = MsgRequest(dest=event["dest"], interface=event["interface"], money=event["money"], type="customer", writeSets=self.writeSets)
            
            response = self.stub.MsgDelivery(request)

            self.writeSets = response.writeSets
            
            logger = self.configure_logger("name")
            logger.info("id {} is success finish {}".format(event["dest"], event["interface"]))

            #message = {"interface": response.interface, "balance": response.money}

            # add new result to recvMsg list
            #self.recvMsg.append(message)


    def executeQuery(self, event, time):

        sleep(time)

        logger = self.configure_logger("query")
        logger.info("id {} is querying".format(event["dest"]))

        # send new "query" requests to finish query process
        request = MsgRequest(dest=event["dest"], interface="query", money=0, type="customer", writeSets=self.writeSets)

        response = self.stub.MsgDelivery(request)

        message = {"interface": response.interface, "balance": response.money}

        self.recvMsg.append(message)

        # create output.txt file
        output = {"id":self.id,"recv":self.recvMsg}
        writeTofile = open("output.txt","a")
        writeTofile.write(str(output)+"\n")
        writeTofile.close()

    def configure_logger(self, name):
        logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

