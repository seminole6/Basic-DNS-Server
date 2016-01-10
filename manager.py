import os
import sys
import time
import server
from threading import Thread
from socket import *

#list of all servers supported by manager
name_servers = []

#types returned by child processes
all_types =[]

#ip address of server
ipAddr = ""
def main():

	global name_servers

	#opens up manager.in file with a for loop to add all name servers  to an array
	f = open('manager.in')
	for line in iter(f):
		name_servers.append(line)
	f.close()
	#method to fork parent process
	forking()

#this method creates forks based on how many entries there are in manager.in
#for example n entries in manager, results in n children
def forking():
	global name_servers

	#pipe to communicate between parent and child
	rend, wend = os.pipe()

	# for loop that cleans up entries add to name_servers from file
	#original entries in name_servers has a newline in it 
	for i in range(len(name_servers)):
		s = name_servers[i].split("\n")
		s = s[0]
		newpid = os.fork()
		#if entry is a child move to running servers
		if(newpid == 0):
			run_servers(wend,s)
			continue
	manage(rend)



def run_servers(wend,s): 
	#exec the child server processes 
	exec 'server.main(wend,s)'



def read_pipe(rend):
	global all_types

	#pipes over values from server 
	#this has to read done manually, attempting to do it in a loop just doesnt work
	rhand = os.fdopen(rend,'r',0)
	reading = rhand.readline()
	all_types.append(reading)

	reading = rhand.readline()
	all_types.append(reading)
	rhand.close()



#function for the parent to wait on connection from a user 
def manage(rend):
	global all_types
	global ipAddr

	#standard socket creation
	serverPort = 9550
	serverSocket = socket(AF_INET,SOCK_STREAM)
	serverSocket.bind(('localhost',serverPort))
	ipAddr,serverPort = serverSocket.getsockname()
	serverSocket.listen(1)
	#reads data from child processes
	read_pipe(rend)
	
	#print that the manager is ready for connections
	print "Manager is ready for connections on port %s" %serverPort

	while True: 
	
		connectionSocket, addr = serverSocket.accept()
		
		# information about user connecting
		ipAddr, port  = addr
		print "Connected to a user at IP address: %s" %ipAddr

		#create new thread once user is connected
		t = Thread(target=connectionHandler, args=(connectionSocket,serverSocket ))
		t.start()


#handles connections for multiple usrs
def connectionHandler(connectionSocket,serverSocket):
	while True:

		
		initial_user_input = connectionSocket.recv(1024)
		print "Client > Manager: " + initial_user_input

		user_input = initial_user_input.split(' ')

		#checking connections to see if they work
		if(user_input[0] == "111"):
			connectionSocket.send("200 COS")
			continue
		# browse command to list all types suported by manager
		elif(user_input[0] == "444"): #browse command
			list_type(connectionSocket)
			continue

		elif(user_input[0] == "777"): #type command
			request_type(user_input[2],connectionSocket)

		elif(user_input[0] == "888"): #done command
			connectionSocket.send("889 DNE")
			connectionSocket.close()
			sys.exit()

		else:
			connectionSocket.send("121 ERR - Please input a proper command")
			continue

#print all types run under the server
def list_type(connectionSocket):
	global all_types

	server1 = all_types[0].split() 
	server2 = all_types[1].split() 

	connectionSocket.send("611 AEN " + "\nTypes\n-------\n" + server1[0].upper() + "\n" + server2[0].upper() + "\n")




def request_type(server_type, connectionSocket):
	#returns the IP and port number of the specified DNS server
	global all_types
	global ipAddr
	
	server1 = all_types[0].split() 
	server2 = all_types[1].split() 

	if(server_type.upper() == server1[0].upper()): #if the type is handled by server 1
		connectionSocket.send("613 TYF " + ipAddr + " " + server1[1])
	
	elif(server_type.upper() == server2[0].upper()): #if the type is handled by server2
		connectionSocket.send("613 TYF " + ipAddr + " " + server2[1])

	else: #if that type cannot be found
		connectionSocket.send("511 ERR " + server_type + " NOT FOUND")



if __name__ == '__main__':
	main()