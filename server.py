import socket
import threading
import sys
import datetime


#TODO: Implement all code for your server here

# Use sys.stdout.flush() after print statemtents

def server():
    # ​python3 server.py -start -port <port> -passcode <passcode>

    # get the local hostname of the server
    host = "127.0.0.1"
    # Initiate port number to passed in CLI parameter
    port = int(sys.argv[3])
    s_passcode = sys.argv[5]
    print('Server started on port ' + str(port) + '. Accepting connections')
    sys.stdout.flush()


    # Create a socket instance
    # Bind host and port to the socket
    server_socket = socket.socket()
    server_socket.bind((host, port))

    users = []
    sockets = []
    server_socket.listen(10)

    def connection(cli, user):
        my_client = cli
        my_username = user
        print(my_username + ' joined the chatroom')
        sys.stdout.flush()
        for cl in sockets:
            if cl != my_client:
                cl.send((my_username + ' joined the chatroom').encode())
        response = "Connected to " + host + " on port " + str(port)
        my_client.send(response.encode())
        while True:
            response = my_client.recv(1024).decode()
            if response.__contains__(":Exit"):
                response = "Exit"
                my_client.send(response.encode())
                print(my_username + " left the chatroom")
                sys.stdout.flush()
                for cl in sockets:
                    if cl != my_client:
                        cl.send((my_username + " left the chatroom").encode())
                break
            if response.__contains__(":)"):
                response = response.replace(":)", "[feeling happy]")
            if response.__contains__(":("):
                response = response.replace(":(", "[feeling sad]")
            if response.__contains__(":mytime"):
                response = response.replace(":mytime", str(datetime.datetime.now().ctime()))
            if response.__contains__(":+1hr"):
                time = datetime.datetime.now()
                time = datetime.datetime(time.year, time.month, time.day, time.hour + 1, time.minute, time.second, time.microsecond, time.tzinfo)
                response = response.replace(":+1hr", str(time.ctime()))
            print(my_username + ": " + response)
            sys.stdout.flush()
            for cl in sockets:
                if cl != my_client:
                    cl.send((my_username + ": " + response).encode())
        sockets.remove(my_client)
        my_client.close()

    while True:
        sockets.append(server_socket.accept()[0])

        users.append(sockets[len(sockets) - 1].recv(1024).decode())
        i = users[len(users) - 1].find(" ")

        # Get the passcode entered by the client
        c_passcode = users[len(users) - 1][0:i]
        # print("passcode: " + passcode)
        # Get the username of the client
        users[len(users) - 1] = users[len(users) - 1][i + 1:]

        # Check if the password is correct
        if c_passcode == s_passcode:
            new_thread = threading.Thread(target=connection, args=(sockets[len(sockets) - 1], users[len(users) - 1]))
            new_thread.start()
        else:
            sockets[len(sockets) - 1].send(("Incorrect passcode").encode())
            print('Incorrect passcode')
            sys.stdout.flush()
            # Close the connection
            sockets[len(sockets) - 1].close()
            sockets.remove(sockets[len(sockets) - 1])



if __name__ == "__main__":
    server()