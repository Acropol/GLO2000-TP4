import argparse
import socket
import sys

from datetime import datetime

def checkInfo(login):
	login = login.decode("utf-8")
	login = login.split(":")
	if login[2] == "1":
		print ("login")
	else:
		print ("register")
	return True

def runServer(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = ("0.0.0.0", port)
	print('starting up on {} port {}'.format(*server_address))
	try:
		sock.bind(server_address)
		sock.listen(5)
	except socket.error as e:
		WriteErrorLog(str(e))
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
			print("Utilisateur connecte")
			connection.send(bytes("200", encoding= 'utf-8'))
			while(True):
				data = connection.recv(1024)
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
