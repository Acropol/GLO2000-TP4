import socket
import getpass
import sys
from hashlib import sha256
import argparse


def sendEmail():
	print("send")

def getEmail():
	print("get")

def getStatistic(data):
	data = data.decode("utf-8")
	data = data.split(":")
	files = data[2].split(",")
	print("%s courriels dans la boite de reception" %(len(files)))
	print("%sMO utilise" %(data[0]))
	i = 1
	for item in files:
		print ("Courriel %d [SUJET] => %s" %(i, item))
		i += 1

def navigator(client_socket):
	while True:
		tab = ['1', '2', '3']
		DisplayMenuHeader()
		value = input('')
		if value == '4':
			client_socket.close()
			sys.exit(0)
		if value in tab:
			try:
				client_socket.send(bytes(value, encoding='utf-8'))
			except:
				sys.exit(0)
			if value == '1':
				sendEmail()
			elif value == '2':
				getEmail()
			elif value == "3":
				data = client_socket.recv(512)
				getStatistic(data)
		else:
			print("Commande invalide")

def runSock(flag, port):
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect(('localhost', port))
	except socket.error as e:
		print("Impossible de se connecter au serveur")
		sys.exit(42)

	while 1:
		user = AboutUser()
		passwordCrypt = sha256(user[1].encode()).hexdigest()
		auth = user[0] + ":" + passwordCrypt + ":"+ str(flag)
		client_socket.send(bytes(auth, encoding= 'utf-8'))
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
