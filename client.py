from sys import *
from socket import *

connected = False #keep track if client is connected or not
serverName = 0 #save the name of the manager or server the client is conencting to
serverPort = 0 #save the port number
clientSocket = socket(AF_INET, SOCK_STREAM) #create a socket for the client

try:
	serverName = argv[1] #pull the name (IP) or server or manager from commandline
	serverPort = int(argv[2]) #pull the port number from the commandline

except IndexError: #if there aren't enough arguments user input is wrong
	print "\nYou have not enterred the proper amount of arguments, please make sure to run the program with the server address and port number\n"
	print "Now closing client program\n"
	exit(0)

#The client program takes two inputs via command line arguments: (i) the host name of the machine on which the server program is running, 
#(ii) the port number that the server is listening at. Once the client program is started, say, by you,
# the following commands should be supported:

def main():

	#global variables for the loop, 
	global serverName
	global serverPort
	global connected
	global clientSocket
	
	#infinite loop to keep conection going until exit is typed
	while True:
		
		# if user is connecting for the first send the connection string over, that way we can get acknowledgment server is running
		if(not connected):
			
			try:
				clientSocket.connect((serverName,serverPort))
			# check to see if info is legitimate, if not kick user
			except error:
				print "\n1116: Improper hostname or port provided, please re-run the program with the correct credentials\n"
				exit(0)

			#connection message
			clientSocket.send("111 CON")

			#server returns that it has been succesfully connected
			server_statement = clientSocket.recv(1024)
			server_args = server_statement.split(" ")
			code_parse(server_args)
			#set the connection variable to true
			connected = True

		#get the commands from the user
		intro_commands = raw_input(">")

		#if user presses enter print help menu
		if(not intro_commands):
			continue
			

		intro_commands = intro_commands.lower()
		commands = intro_commands.split(' ')
		if(commands[0] == "exit"):
			clientSocket.send("888 DNE")
			server_statement = clientSocket.recv(1024)
			server_args = server_statement.split(" ")
			if(server_args[0] == "889"):
				print "Closing connection to server and closing program..."
				clientSocket.close()
				exit(0)
			clientSocket.close()
			exit(0)

		elif(commands[0] == "help"):
			Help()
			continue

		elif(commands[0] == "put"):
			if(len(commands) != 3):
				code_parse("121")
				continue
			clientSocket.send("222 PUT " + commands[1] + " " + commands[2])
			server_statement = clientSocket.recv(1024)
			server_args = server_statement.split(" ")
			code_parse(server_args)

		elif(commands[0] == "get"):
			if(len(commands) != 2):
				code_parse("121")
				continue
			clientSocket.send("333 GET " + commands[1])
			server_statement = clientSocket.recv(1024)
			server_args = server_statement.split(" ")
			code_parse(server_args)

		elif(commands[0] == "browse"):
			clientSocket.send("444 BRS")
			server_statement = clientSocket.recv(1024)
			server_args = server_statement.split(" ")
			code_parse(server_args)

		elif(commands[0] == "del"):
			if(len(commands) != 2):
				code_parse("121")
				continue
			clientSocket.send("555 DEL " + commands[1])
			server_statement = clientSocket.recv(1024)
			server_args = server_statement.split(" ")
			code_parse(server_args)


		elif(commands[0] == "type"):
			if(len(commands) != 2):
				code_parse("121")
				continue
			clientSocket.send("777 TYP " + commands[1])
			server_statement = clientSocket.recv(1024)
			server_args = server_statement.split(" ")
			code_parse(server_args)

		elif(commands[0] == "done"):
			clientSocket.send("888 DNE")
			server_args = server_statement.split(" ")
			server_statement = clientSocket.recv(1024)
			exit(0)

		else:
			print "Input Error - Please input a proper command"
			


#exit: with no argument. Upon receiving this command, the client terminates the current TCP
#connection with the server, and the client program exits.
def Exit(clientSocket):

	print"Closing connection to server and closing program"
	clientSocket.close() #this is causing an error... why????

	exit(0)

#help: this command takes no argument. It prints a list of supported commands, which are the ones in this list. 
#For each command, the output includes a brief description of its function and the syntax of usage.
def Help():
	print "\n---Client Help Menu---\n"
	print "help\n\tDisplays the help menu with a list of recognized commands.\n"
	print "exit\n\tTerminated the TCP connection with the server beforing exiting out of\n"
	print "\tthe client.\n"
	print "\n---Server Help Menu---\n"
	print "put NAME VALUE\n\tAdds a name record to the database. This command takes two arguments:\n"
	print "\t\tNAME A domain name.\n"
	print "\t\tVALUE The domain name's corresponding IP address.\n"
	print "get NAME\n\tQueries for the VALUE of a specified DNS record. This command takes one\n"
	print "\targument:\n"
	print "\t\tNAME The domain name a client is searching for.\n"
	print "del NAME\n\tDeletes a record from the database. This command takes one argument:\n"
	print "\t\tNAME The domain name of the record to be deleted.\n"
	print "browse\n\tDisplays the name and type field of all records currently stored in the\n"
	print "\tdatabase. If the database is empty will display \"database is empty\".\n"
	print "\n---Manager Help Menu---\n"
	print "type TYPE\n\tTells the manager which type the client is looking for so it can give\n" 
	print "\tthe proper information for connecting to the correct corresponding name\n"
	print "\tserver. This command takes one argument:\n"
	print "\t\tTYPE The type of records the client is looking for.\n"
	print "browse\n\tDisplays all of the different name servers and their repsective types.\n"

def code_parse(code):
	global serverName
	#preliminary protocol
	if int(code[0]) == 121: #inproper input
		print("\nInput Error - Please input a proper command\n")

	elif int(code[0]) == 200: #successful connection
		print("\n" + code[1] + ": Succesful Connection\n")

	elif int(code[0]) == 505: #entry NAME not found in database
		print("\n" + code[1] + ": %s not found\n") %code[2]

	elif int(code[0]) == 511: #name server of TYPE not found
		print("\n" + code[1] + ": %s not found\n") %code[2]

	elif int(code[0]) == 606: #new entry in database successful
		print("\n" + code[1] + ": %s entry inserted\n") %code[2]

	elif int(code[0]) == 607: #old entry in database successfully updated
		print("\n" + code[1] + ": %s entry updated\n") %code[2]

	elif int(code[0]) == 608: #entry in database successfully deleted
		print("\n" + code[1] + ": %s entry deleted\n") %code[2]

	elif int(code[0]) == 609: #the database is empty
		print("\n" + code[1] + ": The database is currently empty\n")

	elif int(code[0]) == 610: #the value of a specific entry (ack for GET)
		print("\n" + code[1] + ": The address of " + code[2] + " is " + code[3] + "\n")

	elif int(code[0]) == 611: #prints AEN or all entries (ack for BRS)
		print(code[2])

	elif int(code[0]) == 613: #the IP and port of the requested server
		print("\nPlease connect to " + serverName + " using port number " + code[3] + " to access the requested type.\n")

	elif int(code[0]) == 889: #the done command
		print("\nClosing connection and exiting client...")

	elif int(code[0]) == 1116: #connection error
		print("\n" + code[1] + ": Improper port or hostname supplied\n")

	elif int(code[0]) == 1229: #connection error
		print("\n" + code[1] + ": Connection timeout\n")

	else:
		print "Input Error - Please input a proper command"

	
	#elif:
	#	pass
	#elif:
		#pass
	#else:
		#pass"""
if __name__ == '__main__':
	main()