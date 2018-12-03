import socket
import getpass
import sys
from hashlib import sha256
import argparse

def navigator(client_socket):
	while True:
		tab = ['1', '2', '3', '4']
		DisplayMenuHeader()
		value = input('')
		if value in tab:
			break
	while True:
		client_socket.send(bytes(value, encoding= 'utf-8'))

def runSock(flag, port):
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect(('localhost', port))
	except socket.error as e:
		print("Impossible de se connecter au serveur")
		sys.exit(42)

	while 1:
		#data = client_socket.recv(512)
		user = AboutUser()
		passwordCrypt = sha256(user[1].encode()).hexdigest()
		auth = user[0] + ":" + passwordCrypt + ":"+ str(flag)
		client_socket.send(bytes(auth, encoding= 'utf-8'))
		#client_socket.send(bytes(user[1], encoding= 'utf-8'))
		data = client_socket.recv(512)
		data = data.decode("utf-8")
		if data == "200":
			print("Bonjour %s" %(user[0]))
			break
		print("Login Incorrect")
	navigator(client_socket)


def displayMenu():
	print("Menu de connexion")
	print("1. Se connecter")
	print("2. Creer un compte")

def DisplayMenuHeader():
	print("Menu principal")
	print("1. Envoi de courriels")
	print("2. Consultation de courriels")
	print("3. Statistiques")
	print("4. Quitter")

def AboutUser():
	login = []
	username = input('Utilisateur : ')
	password = getpass.getpass('Password : ')
	login.append(username)
	login.append(password)
	return login

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--port", action="store", dest="port", type=int, default=8080)
	port = vars(parser.parse_args())["port"]
	flag = 42
	while flag != 1 and flag != 2:
		displayMenu()
		try:
			flag = int(input(''))
		except Exception as ex:
			flag = 42
	runSock(flag, port)
