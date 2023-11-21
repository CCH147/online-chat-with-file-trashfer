import socket
import threading
import time
import os
import tqdm
from tkinter import *
from tkinter import filedialog


IP = '127.0.0.1'
PORT = 7500
FORMAT = 'latin-1'
file_name = 'demo'




def start_chat(SERVER, PORT):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    print(f'[CONNECTED] Connected to {SERVER}:{PORT} \n')
    print(f'type: !get_help to get the command info ')

    print('\n----------------------------------------------------------------------------\n')

    receive_thread = threading.Thread(
        target=receive_messages, daemon=True, args=(client,))
    receive_thread.start()

    send_thread = threading.Thread(
        target=send_messages, args=(client, USER_NAME, ))
    send_thread.start()
    


class Manual:
    
    def manual(self):
        print(f'''

    The server runs on { SERVER } at Port { PORT }

    輸入:

        !disconnect -- 離線

        !send_file -- 傳送檔案

        !active_users -- 在線用戶

        !my_info -- 用戶資訊

----------------------------------------------------------------------------\n
    ''')
    
    
    def my_info(self):
        my_ip = socket.gethostbyname(socket.gethostname())
        print(f'''
    Username: { USER_NAME }
    Your IP: { my_ip }
    Server IP: { SERVER }
    Port: { PORT }
    Connection Status: Connected

    ''')

    def send_file(self, client):
        global file_name
        self.client = client
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title='Select file', filetypes=(('.txt', '*.txt'), ('all files', '*.*')))
        file_name = os.path.basename(file_path)
        print(file_name)
        try:
            file_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as file:

                client.send(file_name.encode(('utf-8')))
                client.send(str(file_size).encode(('utf-8')))

                while True:
                    chunk = file.read(2048)
                    if not chunk:
                        break
                    client.send(chunk)
            time.sleep(1)
            print("\nFile sent successfully \n")
            return

        except Exception as e:
            print('\nSorry! Please check again ur file!.\n')
        return


    def active_users(self, client):
        self.client = client
        client.send("!active_users".encode('utf-8'))

    def recive_file(self, client):
        self.client = client
        try:
            global file_name1
            file_name1 = input("Enter file name: ")
            print(f"File name:{file_name1} ")
            with open(str(file_name1), 'wb') as file:
                done = False
                while not done:
                    chunk = client.recv(2048)
                    if chunk == b'END':
                        break
                    else:
                        file.write(chunk)
            print("\nFile received and saved.\n")
            return
        except Exception as e:
            print(e, '\n')
            print("\n[ERROR] Error Occured while reciving file. \n")
        return


def receive_messages(client):
    while True:
        data = client.recv(2048).decode('utf-8')
        new_data = data.split("#")
        if new_data[0] == '!active_users':
            print(f'\nActive Users: { new_data[1] } \n')

        elif new_data[0] == 'notify':
            print(new_data[1])

        elif new_data[0] == "message":
            if new_data[3] == 'quit':
                exit()
            else:
                print(f"\n{ new_data[1] } > {new_data[3]}")


def send_messages(client, USER_NAME):
    client.send(USER_NAME.encode('utf-8'))
    manual = Manual()
    msg = True
    while msg:
        message = input("Me > ")
        if message == '!get_help':
            manual.manual()
            continue

        elif message == "!disconnect":
            client.send("quit".encode('utf-8'))
            msg = False

        elif message[:10] == "!send_file":
            client.send(message[:11].encode('utf-8'))
            manual.send_file(client)
            time.sleep(1)
            client.send("END".encode('utf-8'))
            continue

        elif message == "!active_users":
            manual.active_users(client)

        elif message == "!my_info":
            manual.my_info()
            continue

        elif message[:10] == "!rec_file":
            client.send(message[:11].encode('utf-8'))
            manual.recive_file(client)
            continue

        client.send(message.encode('utf-8'))


if __name__ == '__main__':
    SERVER = input("Enter the server IP: ")
    USER_NAME = input("Enter username: ")
    print(f'[INFO] Trying to connect the server at  {SERVER}:{PORT} ')
    start_chat(SERVER, PORT)
