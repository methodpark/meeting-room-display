#!/usr/bin/env python3

import logging

# setup logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG, filename='./udpServer.log')
import socket
import threading
from socketserver import UDPServer, BaseRequestHandler

PORT = 55555  # randomly picked port, has to be the same in client program


# ensuring we get the correct ip address on all operating systems
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class MasterUDPServer(threading.Thread):
    def run(self):
        addr = ("", PORT)  # empty string corresponds to INADDR_ANY and means receiving from any host
        logging.info("UDP server listening on port {}".format(PORT))
        server = UDPServer(addr, Handler)
        server.serve_forever()


class Handler(BaseRequestHandler):
    my_addr = socket.getfqdn()  # returns hostname e.g. mrd-aquaria
    logging.debug(my_addr)

    def handle(self):
        request = self.request[0].strip()
        logging.info("The request is: {}".format(request))
        if request == str.encode("MRD"):  # is it our UDP client?
            socket = self.request[1]
            ip = get_ip()
            reply = "MRD %s %s" % (Handler.my_addr, ip)  # respond with hostname and IP
            socket.sendto(str.encode(reply), self.client_address)


if __name__ == "__main__":
    import os

    # start server
    logging.info("Starting new server.")
    udp_server = MasterUDPServer()
    udp_server.start()
