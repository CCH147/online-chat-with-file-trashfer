import socket
import threading
import os
import time
import tqdm


HOST = "127.0.0.1"
PORT = 7500
FORMAT = 'latin-1'

list_of_clients = []
list_of_users = []

file_name = 'demo'


def send_file(connection):
    try:
       file_size = os.path.getsize(file_name)
       file_path = os.path.abspath(file_name)
       print("file_name: ", file_name)
       print("file_size: ", file_size)
       print("file_path: ", file_path)
       progress = tqdm.tqdm(range(int(file_size)), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
       with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(2048) 
                if not chunk:
                    break  
                connection.send(chunk)
                progress.update(len(chunk))
       time.sleep(1)
       print("\nFile sent successfully \n")
       return
    except Exception as e:
        print(e, '\n')
        print('\nSorry! This function is in development.\n')
    return
        

def recive_file(connection):
    try:
        global file_name
        global file_size
        file_name = connection.recv(2048).decode('utf-8')
        file_size= connection.recv(2048).decode()
        print(f"File name:{file_name} ")
        print(f"File size:{file_size} ")
        progress = tqdm.tqdm(range(int(file_size)), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(str(file_name), 'wb') as file:
            done = False
            while not done:
                chunk = connection.recv(2048)
                if chunk == b'END':
                    break
                else:
                    file.write(chunk)
                progress.update(len(chunk))
      
        print("\nFile received and saved.\n")

    except Exception as e:
        print(e, '\n')
        print("\n[ERROR] Error Occured while reciving file. \n")
    return




def broadcast_message(connection, message, USER_NAME, addr ):
    while True:
        if message == 'quit':
            connection.sendall(message.encode('utf-8'))  
            break
        
        num_of_clients = len(list_of_clients)
        i=0
        new_msg = ['message' ,USER_NAME, addr, message]
        message = '#'.join(new_msg)
        
        while i <= num_of_clients:
            for client in list_of_clients:
                if client != connection:
                    client.sendall(message.encode('utf-8'))     
            break
        i += 1
        return



def notify(connection, USER_NAME, addr , type):
    num_of_clients = len(list_of_clients)
    connected_text = f"\n \n!! User [ '{USER_NAME}'/{addr} ] Joined the chat. !! "
    disconnected_text = f"\n \n!! User [ '{USER_NAME}'/{addr} ] Left the chat. !! "
    file_text = f"\n \n!! User [ '{USER_NAME}'/{addr} ] Sent a file to the server. !! "
    if type == 'connected':
        i=0
        msg = ['notify' , connected_text]
        message = '#'.join(msg)
        while i <= num_of_clients:
                for client in list_of_clients:
                    if client != connection:
                        client.sendall(message.encode('utf-8'))       
                break
        i += 1
        return
    
    elif type== 'disconnected':
        i=0
        msg = ['notify' , disconnected_text]
        message = '#'.join(msg)
        while i <= num_of_clients:
                for client in list_of_clients:
                    if client != connection:
                        client.sendall(message.encode('utf-8'))           
                break
        i += 1
        return
    
    else:
        i=0
        msg = ['notify' , file_text]
        message = '#'.join(msg)
        while i <= num_of_clients:
                for client in list_of_clients:
                    if client != connection:
                        client.sendall(message.encode('utf-8'))           
                break
        i += 1
        return

    

def remove_user(connection):
    for i in range(len(list_of_users)-1):
        if list_of_users[i][0] == connection:
            del list_of_users[i]



def handel_client(connection, address):
    USER_NAME = connection.recv(2048).decode('utf-8')
    list_of_clients.append(connection)
    list_of_users.append([connection, address, USER_NAME])
    print(f'[NEW CONNECTION] {USER_NAME} at {address[0]} Connected \n')
    addr = str( address[0])

    notify(connection, USER_NAME, addr, type='connected')

    connected = True
    while connected:
        try:
            message = connection.recv(2048).decode('utf-8')
            if message == "!disconnect":
                notify(connection, USER_NAME, addr, type='disconnected')
                list_of_clients.remove(connection)
                remove_user(connection)
                connection.close()
                connected = False
                print(f"Connection Closed for [{USER_NAME}/{address[0]}]. \n")
                print(f"Active users: { len(list_of_clients) }\n")
                break


            if message[:10] == "!send_file":
                recive_file(connection)
                messg = f"\n\n'{USER_NAME}' sent a file -> '{file_name}'. If you want to recive it enter '!rec_file' .\n"
                broadcast_message(connection, messg, USER_NAME, addr)
                continue


            if message[:10]  == '!rec_file':
                send_file(connection)
                time.sleep(1)
                connection.send("END".encode())
                print("END code send!!")
                continue


            if message == '!active_users':
                num_clients = str(len(list_of_clients))
                msg = ['!active_users', num_clients]
                actv_user = '#'.join(msg)
                connection.send(actv_user.encode('utf-8'))
                continue
                        
            print(f"[{USER_NAME}/{address[0]}]: {message}")
            broadcast_message(connection, message, USER_NAME, addr) 

        except Exception as e:
            print(e)
            list_of_clients.remove(connection)
            remove_user(connection)
            print(len(list_of_users), "The users are here \n \n")
            connection.close()
            connected = False
            print(f"[{USER_NAME}/{address[0]}] Disconnected!. \n")
            break



def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST,PORT))
    server.listen(5)

    while True:
        connection, address = server.accept()

        handel_client_thread = threading.Thread(target=handel_client, args=(connection, address))
        handel_client_thread.start()



if __name__ == '__main__':
    print(f'[INFO] Server is running at {HOST} : {PORT} \n')
    start_server()


