import argparse
import socket
import sys

from datetime import datetime

def send_msg(socket, message):
	message = message.encode()
	socket.sendall(message)

def checkLogin(user, password):
	if user == "baptiste" and password == "test":
		WriteLog("You are now logged in " + user, 1, 1)
		return True
	else:
		WriteLog("Invalid login " + user, 0, 1)
		return False

def runServer(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("0.0.0.0", port)
    print('starting up on {} port {}'.format(*server_address))
    try:
        sock.bind(server_address)
        sock.listen(1)
    except socket.error as e:
        WriteErrorLog(str(e))
    while True:
        print('waiting for a connection')

        connection, client_address = sock.accept()
        try:
            print('connection from', client_address)

            while True:
                data = connection.recv(1024)
                print (data)
                if not data:
                    break
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
	parser.add_argument("-p", "--port", action="store", dest="port", type=int, default=1337)
	port = vars(parser.parse_args())["port"]

	runServer(port)
