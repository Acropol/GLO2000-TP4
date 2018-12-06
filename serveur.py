import argparse
import socket
import sys
import os
import re
import smtplib
from email.mime.text import MIMEText

from os.path import getsize
from datetime import datetime
from hashlib import sha256


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

def writeMail(path, data, user):
	file = open(path, "w")
	file.write("[dest]="+data[0]+ "\n")
	file.write("[src]="+user + "\n")
	file.write("[content]="+data[2] + "\n")
	file.close()

def sendHome(data, user):
	print("sending home")
	if os.path.isdir(data[0]):
		writeMail(data[0]+"/"+data[1], data, user)
		return "200:Message transmit"
	else:
		writeMail("DESTERREUR/"+data[1], data, user)
		return "404:Utilisateur " + data[0] + " inconnu"

def SendExternal(data, user):
	print("Sending external via smtp")
	print(data)
	msg = MIMEText(data[2])
	msg["From"] = user
	msg["To"] = data[0]
	msg["Subject"] = data[1]

	try:
		smtpConnection = smtplib.SMTP(host="smtp.ulaval.ca", timeout=5)
		smtpConnection.set_debuglevel(1)
		smtpConnection.sendmail(user, data[0] , msg.as_string())
		smtpConnection.quit()
	except:
		return "400:L’envoi n’a pas pu etre effectue. "
	return "200:Message transmit"

def sendEmail(user,connection):
	data = connection.recv(1024).decode("utf-8").split(':')
	if len(data) != 3:
		return "501:Impossible d'envoyer le message"
	check = re.search('[^@]+@[^@]+\.[^@]+', data[0])
	if not check:
		return "400:Format Email incorrect"
	if "@reseauglo.ca" in data[0]:
		return sendHome(data, user)
	else:
		return SendExternal(data, user)

def getDataMail(path):
	try:
		file = open(path, "r")
		value = file.read()
	except IOError:
		return "400:Erreur lors de la recuperation du mail"
	return "200:" + value

def getEmail(path, user, connection):
	tab = []
	listEmail = "200"
	for mail in os.listdir(path):
		if mail != 'config.txt':
			listEmail += ":" + mail
			tab.append(mail)
	print(listEmail)
	connection.send(bytes(listEmail, encoding='utf-8'))
	if len(tab) != 0:
		value = connection.recv(1024).decode("utf-8")
		value = int(value) - 1
		contentMail = getDataMail(user + "/" + tab[value])
		connection.send(bytes(contentMail, encoding='utf-8'))

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

def register(user, password, passwordCrypt):
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
	test = re.search('^(?=.*?[a-zA-Z])(?=.*?[0-9]).{6,12}$', password)
	if not test:
		message = "Mot de passe incorrect (au moin 1 majuscule + 1 chiffre et [6-12] caracteres)"
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
		config.write(passwordCrypt)
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
	passwordCrypt = sha256(login[1].encode()).hexdigest()
	if len(login) != 3:
		message = "Requette incorrect"
		return False
	if login[2] == "1":
		return auth(login[0], passwordCrypt)
	else:
		return register(login[0], login[1], passwordCrypt)

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
					path = os.path.dirname(os.path.realpath(__file__))
					path = path + '/' + UserSession
					getEmail(path, UserSession, connection)
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
