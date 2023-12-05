import socket
import argparse
import threading
import sys
import hashlib
import time
import logging
import os


#TODO: Implement P2PTracker

def tracker():
    # create logs.log file
    logging.basicConfig(filename="logs.log", format="%(message)s", filemode="a")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # python3 PCPClient.py -folder folder1 -transfer_port 8880 -name client_1

    # get the local hostname of the server
    host = "127.0.0.1"

    # Initiate port number
    port = 5100

    # Create a socket instance
    # Bind host and port to the socket
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tracker_socket.bind((host,port))

    sockets = []
    tracker_socket.listen(10)

    # (index, hash, ip, port)
    check_list = []
    chunk_list = []

    def connection(cli,):
        my_client = cli
        while True:
            response = my_client.recv(1024).decode()
            response = response.split(',')
            found = False
            if response[0] == "LOCAL_CHUNKS":
                for chunk in check_list:
                    if chunk[0] == response[1] and chunk[1] == response[2]:
                        chunk_list.append((response[1], response[2], response[3], response[4]))
                        chunk_list.append(chunk)
                        found = True
                        break
                if found == False:
                    check_list.append((response[1], response[2], response[3], response[4]))
            elif response[0] == "WHERE_CHUNK":
                m = "GET_CHUNK_FROM," + response[1] + ","
                for chunk in chunk_list:
                    if chunk[0] == response[1]:
                        if found == False:
                            m += chunk[1]
                            found = True
                        m += "," + chunk[2] + "," + chunk[3]
                if found == False:
                    m = "CHUNK_LOCATION_UNKNOWN," + response[1]
                time.sleep(2)
                my_client.send(m.encode())
                m = "P2PTracker," + m
                m.replace("127.0.0.1", "localhost")
                logger.info(m)

    while True:
        sockets.append(tracker_socket.accept()[0])
        new_thread = threading.Thread(target=connection, args=(sockets[len(sockets) - 1],))
        new_thread.start()

if __name__ == "__main__":
    tracker()
