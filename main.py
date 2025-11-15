import random
import time
import select
import socket
import threading as th
import display

HOST = "127.0.0.1"
PORT = random.randint(6000,6010)

def get_next_port(indice : int) -> int:
    if indice < 0 or indice > 10:
        return -1
    return 6000 + indice

class server(th.Thread):

    def __init__(self,name : str,port : int,other_clients : list[tuple[str,int]],screen : display.screen):
        th.Thread.__init__(self)
        self.name = name
        self.__stop_event = th.Event()
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1',port))
        self.read_list = []
        self.port = port
        self.writable_list = []
        self.other_clients = other_clients
        self.screen : display.screen = screen.split_vertical(0.5)
        self.std_screen = screen.get_screen(0)
        self.error_screen = screen.get_screen(1)


        

    def stop(self):
        self.__stop_event.set()

    def write(self,writable : list[socket.socket],close_socket : list[socket.socket]):
        for s in writable:
            if s is self.server:
                continue
            else :
                try:
                    if s in close_socket:
                        continue
                    s.send(f"Hello from {self.name}".encode())
                except Exception as e:
                    self.error_screen.append(str(e))



    def read(self,readable : list[socket.socket]):
        remove_list = []
        for s in readable:
            if s is self.server:
                client, adresse_client = self.server.accept()
                self.read_list.append(client)
                self.writable_list.append(client)
                self.other_clients.append(adresse_client)
                self.std_screen.append(f"Connection from {adresse_client}")
            else:
                try:
                    data = s.recv(1024)
                    if data:
                        self.std_screen.append(data.decode())
                except:
                    self.std_screen.append(f"Closing connection with address {s.getpeername()}")
                    s.close()
                    self.read_list.remove(s)
                    self.writable_list.remove(s)
                    remove_list.append(s)
        return remove_list
        


    def run(self):
        self.server.setblocking(False)
        self.server.listen(1)
        self.std_screen.append(f"Server started on port : {self.port}")
        self.std_screen.append("Waiting for connection...")
        self.read_list = [self.server]
        self.writable_list : list[socket.socket] = []
        while not self.__stop_event.is_set():
            all_event = select.select(self.read_list, self.writable_list, [],3)
            readable : list[socket.socket] = all_event[0]
            writable : list[socket.socket] = all_event[1]
            exceptional : list[socket.socket] = all_event[2]
            close_socket = self.read(readable)
            self.write(writable,close_socket)
        self.server.close()

class client:
    def __init__(self,host : str,port : int,name : str, func : callable = None,screen = None):
        self.host = host
        self.port = port
        self.name = name
        self.func = func
        self.other_clients = []
        self.main_screen : display.screen = screen
        self.main_screen.split_horizontally(0.5)
        self.screen = self.main_screen.get_screen(1)
        self.server = server("Server" + self.name,PORT,self.other_clients,self.main_screen.get_screen(0))
        self.actif = True
        self.main()
        
    def main(self):
        try:
            self.server.start()
            time.sleep(1)
            self.find_server()
            while self.actif:
                try:
                    self.main_screen.draw_terminal_screen()
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    self.stop()
        except:
            self.stop()

    def stop(self):
        self.screen.append("exit")
        self.actif = False
        self.client.close()
        self.server.stop()

    def connect(self,port):
        todo = True

    def find_server(self):
        indice = 0
        while (port := self.func(indice)) != -1:
            self.main_screen.draw_terminal_screen()
            indice += 1
            if port == self.port:
                continue
            self.screen.append(f"Trying to connect to server on port {port}")
            try:
                self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.client.connect((self.host,port))
                self.client.send((f"Hello i am {self.name}").encode())
                self.screen.append(f"Connected to server on port {port}")
                self.screen.append(f"reviced: {self.client.recv(1024).decode()}")
                self.client.close()
            except ConnectionRefusedError:
                pass
            except OSError as e:
                self.screen.append(f"OSError:{e}")
            except KeyboardInterrupt:
                self.stop()



    #def __main(self):
    #    while self.actif:
    #        if keyboard.is_pressed("q"):
    #            print("exit")
    #            self.actif = False
    #            self.client.close()
    #            self.list.join()
    #            self.list_co.join()
    #            break
    #        time.sleep(0.1)

if __name__ == "__main__":
    screen = display.screen()
    C1 = client(HOST,PORT,"Client"+str(PORT),get_next_port,screen)
