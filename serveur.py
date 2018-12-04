import argparse
import socket
import sys
import os
from datetime import datetime

def sendEmail(user):
	print (user)

def getEmail(user):
	print (user)

def getStatistic(user):
	print (user)

def auth(user, password):
	if os.path.isdir(user):
		try:
			config = open(user + "/" + "config.txt", "r")
		except IOError:
			return False
		passwordBDD = config.readline()
		if password == passwordBDD:
			return True
		else:
			return False
	return False

def register(user, password):
	if os.path.isdir(user):
		return False
	os.mkdir(user, 755);
	config = open(user + "/" + "config.txt", "w")
	config.write(password)
	config.close()
	return True

def checkInfo(login):
	login = login.decode("utf-8")
	login = login.split(":")
	if login[2] == "1":
		return auth(login[0], login[1])
	else:
		return register(login[0], login[1])

def runServer(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = ("0.0.0.0", port)
	print('starting up on {} port {}'.format(*server_address))
	try:
		sock.bind(server_address)
		sock.listen(5)
	except socket.error as e:
		WriteLog(str(e))
		sys.exit(84)
	while True:
		print('waiting for a connection')
		auth = 0
		connection, client_address = sock.accept()
		try:
			print('connection from', client_address)
			while True and auth == 0:
				login = connection.recv(1024)
				print(login)
				if not login:
					break
				auth = checkInfo(login)
				if auth == False:
					connection.send(bytes("403", encoding= 'utf-8'))
			print("Utilisateur connecte")
			connection.send(bytes("200", encoding= 'utf-8'))
			while(True):
				data = connection.recv(1024).decode("utf-8")
				if data == '1':
					sendEmail(login[0])
				elif data == '2':
					getEmail(login[0])
				elif data == "3":
					getStatistic(login[0])
				else:
					break
				print (data)
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


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--port", action="store", dest="port", type=int, default=8080)
	port = vars(parser.parse_args())["port"]
	runServer(port)
	sys.exit(0)
