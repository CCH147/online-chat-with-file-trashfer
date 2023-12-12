import socket
import threading
import os
import time
import tqdm


list_of_clients = []
list_of_users = []

PORT = 7000
HOST = "127.0.0.1"
ADDRESS = (HOST, PORT)
FORMAT = "utf-8"
file_all = []
size_all = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)


def startChat():
    print("server is working on " + HOST)

    server.listen()

    while True:
        conn, addr = server.accept()
        conn.send("NAME".encode(FORMAT))

        name = conn.recv(1024).decode(FORMAT)
        list_of_users.append(name)
        list_of_clients.append(conn)
        print(f"Name is :{name}")

        broadcastMessage(f"{name} has joined the chat!")

        conn.send("Connection successful!".encode(FORMAT))

        thread = threading.Thread(target=handle, args=(conn, name))
        thread.start()

        print(f"active connections {threading.activeCount()-1}")


def send_file(connection):
    asked_file = connection.recv(2048).decode("utf-8")
    try:
        file_size = os.path.getsize(asked_file)
        file_path = os.path.abspath(asked_file)
        print("file_name: ", asked_file)
        print("file_size: ", file_size)
        print("file_path: ", file_path)
        with open(file_path, "rb") as file:
            connection.send(f"file received!".encode("utf-8"))
            while True:
                chunk = file.readline(1024)
                connection.send(chunk)
                if not chunk:
                    connection.send(f"END".encode("utf-8"))
                    break
                print(chunk)
        file.close()
        print("\nFile sent successfully \n")
        return
    except Exception as e:
        print(e, "\n")
        print("\nSorry! Error caused.\n")
    return


def recive_file(connection):
    try:
        global file_name
        global file_size
        file_name = connection.recv(2048).decode("utf-8")
        file_size = connection.recv(2048).decode()
        print(f"File name:{file_name} ")
        print(f"File size:{file_size} ")
        with open(str(file_name), "wb") as file:
            done = False
            while not done:
                chunk = connection.recv(2048)
                if chunk == b"END":
                    break
                file.write(chunk)

        print("\nFile received and saved.\n")
        return

    except Exception as e:
        print(e, "\n")
        print("\n[ERROR] Error Occured while reciving file. \n")
    return


def remove_user(connection):
    for i in range(len(list_of_users) - 1):
        if list_of_users[i][0] == connection:
            del list_of_users[i]


def handle(conn, name):
    print(f"new connection: {name}")
    connected = True

    while connected:
        try:
            message = conn.recv(2048).decode("utf-8")

            if message == "!send_file":
                recive_file(conn)
                time.sleep(1)
                messg = f"\n\n '{name}' sent a file -> '{file_name}'.Enter file name u want +'&'+ named the file .\n"
                broadcastMessage(messg)
                continue

            if message == "!rec_file":
                """""
                conn.send("rec_file".encode('utf-8'))
                """ ""
                send_file(conn)
                print("END code send!!")
                continue

            print(f"[{name}]: {message}")
            broadcastMessage(message)

        except Exception as e:
            print(e)
            list_of_clients.remove(conn)
            remove_user(conn)
            print(len(list_of_users), "The users are here \n \n")
            conn.close()
            connected = False
            print(f"[{name}] Disconnected!. \n")
            break


def broadcastMessage(message):
    for client in list_of_clients:
        client.sendall(message.encode("utf-8"))


startChat()
