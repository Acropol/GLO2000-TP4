import socket
import getpass
from email.mime.text import MIMEText

def runSock(flag):
    import socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    while 1:
        #data = client_socket.recv(512)
        user = AboutUser()
        auth = user[0] + ":" + user[1] + ":"+ str(flag)
        client_socket.send(bytes(auth, encoding= 'utf-8'))
        #client_socket.send(bytes(user[1], encoding= 'utf-8'))
        data = client_socket.recv(512)
        #if flag == 1:
        #    Login()
        #else:
        #    AddUser()

def displayMenu():
    print("Menu de connexion")
    print("1. Se connecter")
    print("2. Creer un compte")

def AboutUser():
    login = []
    username = input('Utilisateur : ')
    password = getpass.getpass('Password : ')
    login.append(username)
    login.append(password)
    return login

if __name__ == '__main__':
    flag = 42
    while flag != 1 and flag != 2:
        displayMenu()
        try:
            flag = int(input(''))
        except Exception as ex:
            flag = 42
    runSock(flag)
