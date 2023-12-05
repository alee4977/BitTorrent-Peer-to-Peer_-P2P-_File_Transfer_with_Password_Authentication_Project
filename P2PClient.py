import socket
import argparse
import threading
import sys
import hashlib
import time
import logging
import os


#TODO: Implement P2PClient that connects to P2PTracker
# p2pclient.py -folder <my-folder-full-path> -transfer_port <transfer-port-num> -name <entity-name>

def client():
    logging.basicConfig(filename="logs.log", format="%(message)s", filemode="a")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Get the folder name passed in the CLI parameter
    folder_path = sys.argv[2]

    # Initiate the client port number passed in the CLI parameter
    transfer_port = int(sys.argv[4])

    # Get the client username from the CLI parameter
    entity_name = sys.argv[6]

    # Create a socket instance
    # Bind host and port to the socket
    client_socket = socket.socket()
    # client_socket.bind(("127.0.0.1",transfer_port))
    client_socket.connect(("127.0.0.1",5100))

    # Response as to whether request to conenct was accepted by server
    # response = client_socket.recv(1024).decode()
    # print(response)

    def compute_hash(filename, index):
        sha = hashlib.sha1()
        with open(folder_path  + "/" + filename, 'rb') as f:
            val = 0
            while val != b'':
                val = f.read(1024)
                sha.update(val)
        return sha.hexdigest()

    def get_chunk(ip, port, index):
        peer_socket = socket.socket()
        peer_socket.connect((ip, port))
        m = "REQUEST_CHUNK," + str(index)
        peer_socket.send(m.encode())
        m = entity_name + "," + m + "," + ip + "," + str(port)
        m = m.replace("127.0.0.1", "localhost")
        logger.info(m)
        requested_chunk = b''
        response = peer_socket.recv(1024)
        while response != b'':
            requested_chunk += response
            response = peer_socket.recv(1024)
        if os.path.exists(folder_path + "/chunk_" + str(index)) == False:
            temp = open(folder_path + "/chunk_" + str(index), 'x')
            temp.close()
        temp = open(folder_path + "/chunk_" + str(index), 'wb')
        temp.write(requested_chunk)
        temp.close()
        present_chunks.append((str(index), "chunk_" + str(index)))
        m = "LOCAL_CHUNKS," + str(index) + "," + str(compute_hash("chunk_" + str(index), index)) + ",localhost," + str(transfer_port)
        time.sleep(2)
        client_socket.send(m.encode())
        m = entity_name + "," + m
        logger.info(m)
        peer_socket.close()

    present_chunks = []

    with open(folder_path + "/local_chunks.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            line_vals = line.split(',')
            present_chunks.append((line_vals[0], line_vals[1]))

    chunks_needed = []
    total_chunks = present_chunks[len(present_chunks) - 1][0]
    for i in range(int(total_chunks)):
        chunks_needed.append(i + 1)
    for chunk in present_chunks:
        if chunk[1].__contains__("LASTCHUNK") == False:
            chunks_needed.remove(int(chunk[0]))

    for chunk in present_chunks:
        if chunk[1].__contains__("LASTCHUNK") == False:
            file_hash = compute_hash(chunk[1], chunk[0])
            m = "LOCAL_CHUNKS," + str(chunk[0]) + "," + str(file_hash) + ",localhost," + str(transfer_port)
            time.sleep(2)
            client_socket.send(m.encode())
            m = entity_name + "," + m
            logger.info(m)

    def request_chunks():
        i = 0
        while len(chunks_needed) > 0:
            time.sleep(2)
            m = "WHERE_CHUNK," + str(chunks_needed[i])
            client_socket.send(m.encode())
            m = entity_name + "," + m
            logger.info(m)
            response = client_socket.recv(1024).decode()
            response = response.split(',')
            if response[0] == "GET_CHUNK_FROM":
                ip = response[3]
                port = int(response[4])
                get_chunk(ip, port, int(response[1]))
                chunks_needed.remove(chunks_needed[i])
            if len(chunks_needed) > 0:
                i = (i + 1) % len(chunks_needed)

    def connection(cli,):
        peer = cli
        response = peer.recv(1024).decode()
        response = response.split(',')
        if response[0] == "REQUEST_CHUNK":
            i = 0;
            for chunk in present_chunks:
                if chunk[0] == response[1]:
                    new_chunk = chunk[1]
                    with open(folder_path + "/" + new_chunk, 'rb') as f:
                        peer.send(f.read())
                        peer.send(b'')
                    break
        peer.close()

    request_thread = threading.Thread(target=request_chunks, args=())
    request_thread.start()

    sockets = []
    peer_connect = socket.socket()
    peer_connect.bind(("127.0.0.1",transfer_port))
    peer_connect.listen(10)

    while True:
        new_client = peer_connect.accept()[0]
        sockets.append(new_client)
        new_thread = threading.Thread(target=connection, args=(sockets[len(sockets) - 1],))
        new_thread.start()

if __name__ == "__main__":
    client()
