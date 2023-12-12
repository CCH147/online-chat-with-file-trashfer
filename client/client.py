import socket
import threading
import time
import os
import tqdm
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import ttk

PORT = 7000
SERVER = "127.0.0.1"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)


class GUI:
    def __init__(self):
        self.Window = Tk()
        self.Window.withdraw()

        self.login = Toplevel()
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)
        self.pls = Label(
            self.login,
            text="Please login to continue",
            justify=CENTER,
            font="Helvetica 14 bold",
        )

        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)
        self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")

        self.labelName.place(relheight=0.2, relx=0.1, rely=0.2)
        self.entryName = Entry(self.login, font="Helvetica 14")
        self.entryName.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.2)
        self.entryName.focus()
        self.go = Button(
            self.login,
            text="CONTINUE",
            font="Helvetica 14 bold",
            command=lambda: self.goAhead(self.entryName.get()),
        )

        self.go.place(relx=0.4, rely=0.55)
        self.Window.mainloop()

    def goAhead(self, name):
        self.login.destroy()
        self.layout(name)

        rcv = threading.Thread(target=self.receive)
        rcv.start()

    def layout(self, name):
        self.name = name
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550, bg="#17202A")
        self.labelHead = Label(
            self.Window,
            bg="#17202A",
            fg="#EAECEE",
            text=self.name,
            font="Helvetica 13 bold",
            pady=5,
        )

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window, width=450, bg="#ABB2B9")

        self.line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.textCons = Text(
            self.Window,
            width=20,
            height=2,
            bg="#17202A",
            fg="#EAECEE",
            font="Helvetica 14",
            padx=5,
            pady=5,
        )

        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)

        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)

        self.labelBottom.place(relwidth=1, rely=0.825)

        self.entryMsg = Entry(
            self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13"
        )

        self.entryMsg.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)

        self.entryMsg.focus()

        self.buttonMsg = Button(
            self.labelBottom,
            text="Send",
            font="Helvetica 10 bold",
            width=10,
            bg="#ABB2B9",
            command=lambda: self.sendButton(self.entryMsg.get()),
        )

        self.buttonMsg.place(relx=0.57, rely=0.008, relheight=0.06, relwidth=0.10)

        self.buttonMsg = Button(
            self.labelBottom,
            text="Send file",
            font="Helvetica 10 bold",
            width=10,
            bg="#ABB2B9",
            command=lambda: self.send_file(client),
        )
        self.buttonMsg.place(relx=0.67, rely=0.008, relheight=0.06, relwidth=0.15)

        self.buttonMsg = Button(
            self.labelBottom,
            text="rec file",
            font="Helvetica 10 bold",
            width=10,
            bg="#ABB2B9",
            command=lambda: self.recive_file(client, self.entryMsg.get()),
        )
        self.buttonMsg.place(relx=0.82, rely=0.008, relheight=0.06, relwidth=0.15)

        self.textCons.config(cursor="arrow")

        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=1, relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    def send_file(self, client):
        self.client = client
        msg = f"!send_file"
        client.send(msg.encode("utf-8"))

        global file_name
        code = f"END"
        file_path = filedialog.askopenfilename(
            title="Select file", filetypes=((".txt", "*.txt"), ("all files", "*.*"))
        )
        file_name = os.path.basename(file_path)
        print(file_name)
        try:
            file_size = os.path.getsize(file_path)
            with open(file_path, "rb") as file:
                client.send(file_name.encode(("utf-8")))
                client.send(str(file_size).encode(("utf-8")))
                while True:
                    chunk = file.read(2048)
                    if not chunk:
                        time.sleep(1)
                        client.send(code.encode())
                        print("END code send!!")
                        file.close()
                        break
                    client.send(chunk)
            print("\nFile sent successfully \n")
            return
        except Exception as e:
            print("\nSorry! Please check again ur file!.\n")
        return

    """""
    def rec_file(self,client):
        self.client = client 
        msg = f"!rec_file"
        client.send(msg.encode("utf-8"))
        return
    """ ""

    def recive_file(self, client, name):
        try:
            self.client = client
            global file_name1
            msg = f"!rec_file"
            rec_file = name.split("&", 1)
            asked_file = str(rec_file[0])
            file_name1 = rec_file[1]

            print(f"File name:{file_name1} ")

            client.send(msg.encode("utf-8"))
            client.send(asked_file.encode("utf-8"))
            with open(str(file_name1), "wb") as file:
                while True:
                    chunk = client.recv(1024)
                    print(chunk)
                    if chunk == b"END":
                        print("\nFile received and saved.\n")
                        break
                    file.write(chunk)
            file.close()
            return
        except Exception as e:
            print(e, "\n")
            print("\n[ERROR] Error Occured while reciving file. \n")
        return

    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        snd = threading.Thread(target=self.sendMessage)
        snd.start()

    def receive(self):
        while True:
            message = client.recv(1024).decode(FORMAT)

            if message == "NAME":
                client.send(self.name.encode(FORMAT))
            else:
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, message + "\n\n")

                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        message = f"{self.name}: {self.msg}"
        msg = f"{self.msg}"
        while True:
            client.send(message.encode("utf-8"))
            break


g = GUI()
