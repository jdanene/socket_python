import socket 
import sys
import functools

#paste: [list-of string or number] -> string
#concatenates a variable list of string and returns the concatantion in bytes
def paste(*args):
    return str.encode(functools.reduce((lambda str1,str2: str1+str2),map(str, args)))

#Global constant
HOST = "www.google.com"
HOST_IP = socket.gethostbyname(HOST) #Get the IP address of the host. 
PATH = "/"
PORT = 80 #The accessing port of the server specified to 80; the port generally open for HTTP connections for web servers. 
PROTOCOL = "HTTP/1.1"
REQUEST = paste("GET"," ",PATH," ", PROTOCOL, "\r\n","Host:"," ", HOST,"\r\n\r\n")

# socket.AF_INET -> specifies the connection type to be 4th version of the Internet Protocol (IP) aka the version commonly used today. 
# socket.SOCK_STREAM -> Allows use to make a TCP connection. 
# In general see -> http://man7.org/linux/man-pages/man2/socket.2.html for more detail. 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Open a connection 
s.connect((HOST,PORT))

#Send the request. The function `paste` already byte encodes the string so we are good here. 
s.send(REQUEST)

results = s.recv(4096) # The input is the buffer size; how much data we download at any unit of time
#Buffer the data. 
while (len(results)>0):
    print(results)
    results = s.recv(4096)
