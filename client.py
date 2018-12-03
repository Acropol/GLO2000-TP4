import argparse
import socket
import smtplib
import getpass
from email.mime.text import MIMEText


def displayMenu():
    print("Menu de connexion")
    print("1. Se connecter")
    print("2. Creer un compte")

def AboutUser():
    username = input('Utilisateur : ')
    password = getpass.getpass('Password : ')

def Login():
    AboutUser()

def AddUser():
    AboutUser()

if __name__ == '__main__':
    flag = 42
    while flag != 1 and flag != 2:
        displayMenu()
        try:
            flag = int(input(''))
        except Exception as ex:
            flag = 42
    if flag == 1:
        Login()
    else:
        AddUser()
