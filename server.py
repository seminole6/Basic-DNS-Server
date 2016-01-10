from socket import *
import select
import os
import os.path
import pickle

from threading import Thread
import threading
from record import *

commands = ["help", "put","get","del","browse","exit"]
database = []
local_type = "b"
serverdb = ""
lock = threading.Lock()
rend,wend  = os.pipe()

#main accepts the write end of the pipe for children processes
def main(wend,Type):

	# this is so the server can have access to its type
	global local_type
	global serverdb
	local_type = Type

	#port number of 0 allows computer to self assign port
	serverPort = 0
	serverSocket = socket(AF_INET,SOCK_STREAM)
	serverSocket.bind(('localhost',serverPort))
	ipAddr,port = serverSocket.getsockname()

	#formatting for string to be sent through the pipe
	piped_info = "%s %s\n" % (str(local_type),str(port))
	
	#from piping example, this allows is to send info through pipe
	whand = os.fdopen(wend,'a',0)
   	whand.write(piped_info)
	load()

	#print 'The server is ready to receive at port %s' %str(port)
	serverSocket.listen(1)
	#serverSocket.setblocking(0)

	#print os.getpid()
	while True:
		#wait for user to connect
		connectionSocket, addr = serverSocket.accept()

		# information about user connecting
		ipAddr, port  = addr
		print "Connected to a user at IP address: %s" %ipAddr

		#create new thread once user is connected
		t = Thread(target=handler, args=(connectionSocket,serverSocket ))
		t.start()
			

def handler(connectionSocket,serverSocket):
	#infinite loop for user commands, until connection is done
	while True:

		
		initial_user_input = connectionSocket.recv(1024)
		print "Client > Server: " + initial_user_input

		user_input = initial_user_input.split(' ')
		if(user_input[0] == "111"):
			connectionSocket.send("200 COS")
			continue

		elif(user_input[0] == "222"): #put command
			put(user_input,connectionSocket)
			continue

		elif(user_input[0] == "333"): #get command
			get(user_input,connectionSocket)
			continue

		elif(user_input[0] == "555"): #delete command
			Del(user_input,connectionSocket)
			continue
		elif(user_input[0] == "444"): #browse command
			browse(user_input[0],connectionSocket)
			continue
		elif(user_input[0] == "888"): #done command
			connectionSocket.send("889 DNE")
			connectionSocket.close()
			exit(0)
		else:
			connectionSocket.send("121 ERR - Please input a proper command")
			continue

def load():
	global database
	global local_type
	global lock
	global serverdb

	serverdb = local_type
	serverdb += "_database.pkl"

	#check if database file exists
	if(os.path.isfile(serverdb)==False):
		return
		#print "\nThe DNS database currently does not exist, a new Database will be created when a record is inserted\n"

	else:
		#loads the database file into the database array, we will save the file in each method
		#lock accounts for people
		lock.acquire()
		f=open(serverdb,'r+') 
		database = pickle.load(f)
		f.close()	
		lock.release()


#put: this command is used to add name records to the name service database. 
#It takes three arguments: name, value, and type, in that order; they constitute the three fields of a name record. 
#After receiving this name record information, the client sends this name record to the server, which enters the record to its name service database. 
#If a record of the same name and type already exists, update the record with the new value.
def put(user_input,connectionSocket):
	# TODO: need to check to make sure there aren't too many args
	global database
	global lock
	global serverdb

	lock.acquire()
		#add the new record to the database if it exists
		#check arguments
		#if(len(user_input) > 4):
		#	connectionSocket.send("\n121: Input Error - Too many arguemnts. The put command takes three arguments: NAME, VALUE, and TYPE.")
		#	return;
	try:
		updated = 0
		new_record = record(user_input[2],user_input[3])


		#if user input has name and type already in the database, the entry will be updated
		if(search(user_input[2]) >= 0):
			database[search(user_input[2])] = new_record
			updated = 1
		#else the new record will be added
		else:
			database.append(new_record)

		f = open(serverdb,'w+')
		pickle.dump(database,f)
		f.close()

		if(updated == 1):
			connectionSocket.send("607 PUP " + user_input[2])
		else:
			connectionSocket.send("606 PIN " + user_input[2])


	#accounts for improper input of user commands for put i.e not enough commands provided. 
	#The user will be prompted to re enter a command on the client side.
	except IndexError:
		connectionSocket.send("121 ERR - Too few arguments. The put command takes three arguments: NAME, VALUE, and TYPE. Please re-enter the message in the proper format")
	
	lock.release()


#get: this command is used to send a query to the server database. It takes two arguments: name and type, in that order. 
#Upon receiving a query, if a record with the name and type is found, the server returns the record value to the client. 
#Otherwise, it returns a "not found" error message.
def get(user_input,connectionSocket):
	# TODO: need to check to make sure there aren't too many args
	global database
	global lock

	lock.acquire()
	name = user_input[2]

		#if the database contains the entry return the entry to the client
	r = search(user_input[2])
	if(r >= 0):
		connectionSocket.send("610 ENT " + user_input[2] + " " + database[r].value)

		#else return the "not found" error
	else:
			connectionSocket.send("505 ERR " + name + " NOT FOUND")
	lock.release()




#delete: this command is used to remove a name record from the database. It takes two arguments: name and type, in that order. 
#Upon receiving a query, if a record with the name and type is 2 found, the server removes the record and sends a positive feedback.
#Otherwise, it returns a "not found" error message.
def Del(user_input,connectionSocket):
	# TODO: need to check to make sure there aren't too many args
	global database
	global lock
	global serverdb

	lock.acquire()
	if (len(database) == 0):
		connectionSocket.send("609 ERR DATABASE EMPTY")
		return;
	#try catch to account for the user not entering enough information
	
		#check arguments
		#if(len(user_input) > 3):
		#	connectionSocket.send("121 Input Error - Too many arguemnts. The delete command takes two arguments: NAME and TYPE")
		#	return

	name = user_input[2]
		#for loop to see if the entry wanting to be delete is in the database
	for i in range(len(database)):
		if(database[i].name == name):
			database.pop(i)
			f= open(serverdb,'w+')
			pickle.dump(database,f)
			f.close()
			connectionSocket.send("608 EDE " + name + " DELETED")
			lock.release()
			return

	#if the entry is not found, the user will get a not found error
	connectionSocket.send("505 ERR " + name + " NOT FOUND")
	lock.release()

#browse: with no argument. This command is used to retrieve all current name records in the database. 
#Upon receiving a browse request, the server returns the name and type fields of all records, the value field is not included.
#If the database is empty, the server returns a "database is empty" error message.
def browse(user_input,connectionSocket):
	global database
	global lock

	#check arguments
	#check to see if the database is empty
	lock.acquire()

	if(len(database) == 0):
		connectionSocket.send("609 ERR DATABASE EMPTY")

	else:
		# doesn't print properly, only prints first .send()
		# format for quick access to array, no need to do for i in rage
		complete_entry = "611 AEN \n----Name----\n"
		for entry in database:
			complete_entry += entry.name + "\n"
			
		connectionSocket.send(complete_entry)

	lock.release()

#helper method for the put method to see if an entity exists in the database
def search(name):

	#check to see if the entry in the database exists, if not -1 will be returned
	if(len(database)==0):
		return -1;

	for i in range(len(database)):
		if(database[i].name == name):
			return i;
				

#boilerplate code to launch the main functions
if __name__ == '__main__':
	main(wend,Type)

