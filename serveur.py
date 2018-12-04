import argparse
import socket
import sys
import os
import re
from os.path import getsize
from datetime import datetime

def init():
	print("****INIT SERVEUR****")
	if not os.path.isdir("./DESTERREUR"):
		try:
			os.makedirs("DESTERREUR")
		except:
			print("Check [KO]")
			sys.exit(84)
	print("Check [OK]")

def getFolderSize(listFiles, user):
	total_size = 0

	for item in listFiles:
		try:
			total_size += getsize(user + "/" + item)
		except socket.error as e:
			total_size += 0
	return total_size

def sendHome(dest):
	print("sending home")
	return "200:Message transmit"

def SendExternal(dest):
	print("Sending external via smtp")
	return "200:Message transmit"

def sendEmail(user,connection):
	data = connection.recv(1024).decode("utf-8").split(':')
	if len(data) != 3:
		return "501:Impossible d'envoyer le message"
	check = re.search('[^@]+@[^@]+\.[^@]+', data[0])
	if not check:
		return "400:Format Email incorrect"
	if "@reseauglo.ca" in user:
		return sendHome(data[0])
	else:
		return SendExternal(data[0])

def getEmail(user, connection):
	print(user)

def getStatistic(user, connection):
	onlyfiles = next(os.walk(user))[2]
	onlyfiles.remove('config.txt')
	nbfiles = str(len(onlyfiles))
	size = getFolderSize(onlyfiles, user)
	arrayfilestr = ",".join(str(x) for x in onlyfiles)

	connection.send(bytes(str(size) + ":" + str(nbfiles) + ":" + arrayfilestr , encoding= 'utf-8'))

def auth(user, password):
	global message
	if os.path.isdir(user):
		try:
			config = open(user + "/" + "config.txt", "r")
		except IOError:
			message = "Impossible d'acceder au fichier de configuration de l'utilisateur"
			return False
		passwordBDD = config.readline()
		if password == passwordBDD:
			return True
		else:
			message = "Identifiant non valide"
			return False
	message = "Identifiant non valide"
	return False

def register(user, password):
	global message
	if user == "":
		message = "Le nom d'utilisateur ne doit pas etre vide"
		return False
	check = re.search('[^@]+@[^@]+\.[^@]+', user)
	if not check:
		message = "Format Email incorrect"
		return False
	if not "@reseauglo.ca" in user:
		message = "Email incorrect, elle doit contenir @reseauglo.ca"
		return False
	if os.path.isdir(user):
		message = "L'utilisateur " + user + " existe deja"
		return False
	try:
		os.makedirs(user)
	except:
		message = "Impossible de creer l'utilisateur"
		print(message)
		return False
	try:
		path = user + "/" + "config.txt"
		print (path)
		config = open(path, "w")
		config.write(password)
		config.close()
	except:
		message = "Impossible d'ouvrir le fichier de configuration utilisateur"
		print(message)
		return False
	return True

def checkInfo(login):
	global message
	login = login.decode("utf-8")
	login = login.split(":")
	if len(login) != 3:
		message = "Requette incorrect"
		return False
	if login[2] == "1":
		return auth(login[0], login[1])
	else:
		return register(login[0], login[1])

def runServer(port):
	global message
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = ("0.0.0.0", port)
	print("****RUNNING SERVEUR****")

	try:
		sock.bind(server_address)
		sock.listen(5)
	except socket.error as e:
		WriteLog(str(e))
		sys.exit(84)
	print('starting up on {} port {}'.format(*server_address))
	while True:
		print('waiting for a connection')
		auth = 0
		connection, client_address = sock.accept()
		try:
			print('connection from', client_address)
			while True and auth == 0:
				message = "Success"
				login = connection.recv(1024)
				print(login)
				if not login:
					break
				auth = checkInfo(login)
				print(message)
				if auth == False:
					connection.send(bytes("403:"+message, encoding= 'utf-8'))
			print("Utilisateur connecte")
			connection.send(bytes("200:"+message, encoding= 'utf-8'))
			while(True):
				UserSession = login.decode("utf-8").split(":")[0]
				data = connection.recv(1024).decode("utf-8")
				if data == '1':
					response = sendEmail(UserSession, connection)
					print(response)
					connection.send(bytes(response, encoding= 'utf-8'))
				elif data == '2':
					getEmail(UserSession, connection)
				elif data == "3":
					getStatistic(UserSession, connection)
				else:
					break
				#data = connection.recv(1024).decode("utf-8")
		finally:
			connection.close()

def WriteLog(msg, type=0, display=1, exit=0):
	flags = ["ERROR", "INFO", "SUCCESS", "WARNING"]
	output = sys.stderr
	fileLog = "error.log"
	if type > 0:
		output = sys.stdout
		fileLog = "info.log"
	try:
		with open(fileLog, "a") as outfile:
			outfile.write("[" + flags[type]+ "] " + str(datetime.now()) + " " + msg + "\n")
			outfile.close()
	except IOError:
		print("Erreur : Impossible d'acceder au fichier log ", file=output)
	if display:
		print(msg, file=output)
	if exit:
		sys.exit(84)

message = ""

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--port", action="store", dest="port", type=int, default=8080)
	port = vars(parser.parse_args())["port"]
	init()
	runServer(port)
	sys.exit(0)
