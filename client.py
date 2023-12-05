import socket
import threading
import sys


#TODO: Implement a client that connects to your server to chat with other clients here

# Use sys.stdout.flush() after print statemtents

def client():
    # get the local hostname of the client
    server_host = sys.argv[3]
    # Initiate port number to passed in CLI parameter
    server_port = int(sys.argv[5])
    # Get the username of the client
    username = sys.argv[7]
    # Get the password for the client (all have the password CS4400)
    password = sys.argv[9]

    # python client.py lawn-128-61-22-4.lawn.gatech.edu 5000 Client1 CS4400
    # python3 client.py -join -host <hostname> -port <port> -username <username> -passcode <passcode>



    # Create a socket instance
    # Bind host and port to the socket
    client_socket = socket.socket()
    client_socket.connect((server_host, server_port))
    sys.stdout.flush()

    client_socket.send((password + " " + username).encode())

    response = client_socket.recv(1024).decode()

    print(response)
    sys.stdout.flush()

    if response == "Incorrect passcode":
        client_socket.close()
        return

    def sending():
        while True:
            reply = input("")
            if reply == ":Exit":
                client_socket.send(reply.encode())
                break
            client_socket.send(reply.encode())

    def receiving():
        while True:
            response = client_socket.recv(1024).decode()
            if response == "Exit":
                break
            print(response)
            sys.stdout.flush()
        client_socket.close()

    sending_thread = threading.Thread(target=sending, args=())
    receiving_thread = threading.Thread(target=receiving, args=())

    sending_thread.start()
    receiving_thread.start()



if __name__ == "__main__":
    client()