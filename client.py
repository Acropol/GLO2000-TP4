import socket
import getpass
import sys

import argparse

def sendEmail():
	destination = input("Destinataire : ")
	sujet = input("Sujet : ")
	corps = input("Corps : ")
	return  destination + ":" + sujet + ":" + corps

def getEmail(listemail, client_socket):
	data = listemail.split(":")
	#if len(data)  < 2:
	#	print (data[0])
	#	print ("Erreur de recuperation des emails")
	print ("Vous avez %d courriels dans votre boite de reception" % (len(data) - 1))
	if len(data) - 1 != 0:
		i = 1
		while (i < len(data)):
			print ("%d. [SUJET] %s" %(i,data[i]))
			i += 1
		value = input("Tapez le numero du mail pour lire le mail\n")
		client_socket.send(bytes(value , encoding= 'utf-8'))
		data = client_socket.recv(512).decode("utf-8").split(':')
		if len(data) < 2 :
			print ("Erreur de reception")
		else:
			print (data[1])
	input("Appuyez sur une touche pour revenir au menu principal\n")

def getStatistic(data):
	data = data.decode("utf-8").split(":")
	if len(data) != 3:
		print("Erreur lors de la récuperation des donnees")
		return
	files = data[2].split(",")
	if data[0] != '0':
		print("%s courriels dans la boite de reception" %(len(files)))
	print("Utilisation de la boite de reception : %s octets" %(data[0]))

	if len(files) == 1 and files[0] == '':
		print ("Vous n'avez pas de courriels")
	else:
		i = 1
		for item in files:
			print ("%d. [SUJET] => %s" %(i, item))
			i += 1
	input("Appuyez sur une touche pour revenir au menu principal\n")

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
				email = sendEmail()
				print ("Patientez svp : cela pourrai prendre plusieurs secondes")
				try:
					client_socket.send(bytes(email, encoding='utf-8'))
				except:
					sys.exit(0)
				data = client_socket.recv(512).decode("utf-8").split(':')
				if len(data) > 1:
					print(data[1])
			elif value == '2':
				listemail = client_socket.recv(512).decode("utf-8")
				getEmail(listemail, client_socket)
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
		#passwordCrypt = sha256(user[1].encode()).hexdigest()
		#auth = user[0] + ":" + passwordCrypt + ":"+ str(flag)
		auth = user[0] + ":" + user[1] + ":"+ str(flag)
		client_socket.send(bytes(auth, encoding= 'utf-8'))
		data = client_socket.recv(512)
		data = data.decode("utf-8").split(':')
		if data[0] == "200":
			print("Bonjour %s" %(user[0]))
			break
		print(data[1])
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
