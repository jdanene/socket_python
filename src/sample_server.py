import socket, argparse, re, sys, functools, os, time, platform, subprocess, pytz

# TESTING IN TERMINAL AFTER YOU RUN server
# local IP = 192.168.0.104
# telnet 192.168.0.104 12001


def paste(*args):
    """
    Concatenates string (or numbers) into a single string encoded into bytes

    Args:
        *args: either strings or numbers
    Returns:
        string: The raw output string in byte format.

    Example:
    >>paste("hello", "word", 2019)
    b"helloworld2019"
    """
    return str.encode(functools.reduce((lambda str1,str2: str1+str2),map(str, args)))




def server(port = 12002, backlog = 20):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:        
        s.bind(('',port)) 

        # The parameter below is the backlog. The backlog specifies the maximum
        # number of queued connections before the server starts rejection request.
        # Hence is backlog == 0 once a connection is accepted all other connections will 
        # be rejected. The smaller the backlog the more rejections, the larger the backlog
        # the less rejections. 
        s.listen(backlog)
        while True:
            conn, addr = s.accept() 
            conn.send(str.encode('Welcome, type info \n'))
            with conn:
                while True:
                    data = conn.recv(2048)
                    if not data:
                        break
                    conn.sendall(paste("RECIEVED!! :",data))
                conn.close()

                #send the data to client
    pass 


#