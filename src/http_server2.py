import sys, types, select, argparse, re, socket
sys.path.append('./')
from http_server1 import HttpServer1
"""
Python script for a HTTP server that handles multiple connection at a time
using system select, and serves any files in the current directory if their names ends w/ .html or .htm
and the HTTP request is correct. 

Written and tested in Python 3.6

Usage: python http_server2.py [port]
    
    port: The default port to "hear" incoming connections for TCP 3-way handshake

Testing example: 
    Step 1: from shell set directory to ./src

    Step 2: from shell run the unit test
        >> pytest ../test/test_http_server1.py 

    Step 3: from the shell run
        >> python http_server2.py [port]

    Step 4: first find you local ip address from system preferences > network 
            then from the shell run
        >> telnet [local_IP] [port]

    Step 5: from the web browser type the following
        >> http://localhost:[port]/rfc2616.html
        >> http://localhost:[port]/htm4_example.html

Note: Step (4-5) verify that multiple connections can be served. 

ToDo: Not sure if need more unit tests for `test_http_server2` since i wrote none. In the
      example (step 2) I only test `test_http_server1` since `test_http_server2` imports methods from this file. 

ToDo: Since `test_http_server2` imports methods from `test_http_server1`. Once we 
      automatically output a HTML invalid page for invalid responses, then `test_http_server2`
      will do it as well. 

"""


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("port")

    if re.match('http_server2', sys.argv[0]):
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(sys.argv)

    # Assert condition that port number >= 1024.
    args.port = int(args.port)
    assert args.port >= 1024, "Port Number must be >= 1024"

    # Run HTTP server 
    HttpServer2().server(args.port)


class HttpServer2(HttpServer1):

    def __init__(self, html_path="../server_dir"):
        # Inherit the methods from HttpServer1
        HttpServer1.__init__(self, html_path = html_path) 

        # header completely found iff we see '\r\n\r\n'
        self.is_header_found = lambda data_in: bool(re.search(b'\r\n\r\n',data_in))

        # list of open sockets, list of  sockets we want to write to, hashmap to map socket to state-data
        self.open_connections = []
        self.writable_connections = []
        self.data_dict = dict()
        pass

    def parse_header(self, data_in): 
        """
        Put the header values from `data_in` into a dictionary

        :param data_in:
        :return:
        """

        # split data into header and body based on delimiter "\r\n\r\n"
        header = data_in.split(str.encode("\r\n\r\n"))[0] 
        
        # Split data into list based on delimiter "\r\n" then split again based on first occurrences of ':'
        keyval_pairs = [item.split(str.encode(':'),1) for item in header.split(str.encode("\r\n"))]
        top_line_of_header = keyval_pairs[0][0].decode().split(" ")
        keyval_pairs = keyval_pairs[1:] 
        header_dict = {entry[0].decode():entry[1].decode() for entry in keyval_pairs}

        # label and put headers from first line header into header dictionary
        header_dict["req_type"] = top_line_of_header[0]
        header_dict["req_file"] = top_line_of_header[1]
        header_dict["http_version"] = top_line_of_header[2] 
        return header_dict   

    def tcp_handshake(self, sock):
        """
        Registers new socket object and associate a data struct to it that holds state-information

        :param sock:
        :return:
        """

        # perform the accept call? 
        conn, addr = sock.accept() 
        conn.setblocking(0)

        # add accept socket to the open connections list
        self.open_connections.append(conn) 

        # create data struct that holds state information we care about for the socket
        data = types.SimpleNamespace(inb=b'', outb=None, header_seen=False)

        # use socket (aka conn) as a hash to associate the data struct to socket. 
        self.data_dict[conn] = data 
        pass

    def terminate_socket(self, sock):
        """
        Terminates a socket by deleting its data entry and deleting it from the two connection lists.

        :param sock:
        :return:
        """
        if sock in self.writable_connections: 
            self.writable_connections.remove(sock)
        if sock in self.data_dict: 
            del self.data_dict[sock]
        self.open_connections.remove(sock)
        sock.close()
        pass

    def read_socket(self, sock):
        """
        Reads client socket, finds the HTTP header from client socket, once found adds client socket
        to `self.writable_connections`

        References used:
            (1) https://julien.danjou.info/high-performance-in-python-with-zero-copy-and-the-buffer-protocol/
                - Contains information on memoryview/buffering

        :param sock:
        :return:
        """
        input_data = sock.recv(1024)
        if input_data: 
            self.data_dict[sock].inb += input_data

            # Checks if header is seen, if seem parses header and then puts response into a buffer,
            # and then sets header_seen boolean to True
            if not self.data_dict[sock].header_seen: 
                if self.is_header_found(self.data_dict[sock].inb):
                    # Associate to the socket its parsed header
                    self.data_dict[sock].header = self.parse_header(self.data_dict[sock].inb)
                    # Get appropriate HTTP response for socket put it in a buffer and then associate it to the socket
                    data_to_send = self.get_HTTP_response(self.data_dict[sock].header)
                    self.data_dict[sock].outb = memoryview(data_to_send) #Memoryview puts it in a buffer 
                    # Set boolean so we know that we can write to the socket now. 
                    self.data_dict[sock].header_seen = True

                    self.writable_connections.append(sock)
        else:  # FixMe: All the guides tell me to do this but I'm confused as to why.
            self.terminate_socket(sock)
        pass

    def write_socket(self, sock):
        """
        Sends chunks of data to client socket and terminates client when finished.

        :param sock:
        :return:
        """
        # Send a piece of data to the client from the message memoryview (aka buffer)
        sent = sock.send(self.data_dict[sock].outb)
        # Build a new memoryview (aka buffer) object pointing to the data which remains to be sent
        self.data_dict[sock].outb = self.data_dict[sock].outb[sent:]
        if not (sent > 0):
            self.terminate_socket(sock)
        pass

    def server(self, port=12000, backlog=20):
        """
        Implementation of multi-connection server

        :param port:
        :param backlog:
        :return:

        References used:
            (1) https://steelkiwi.com/blog/working-tcp-sockets/
            (2) https://pymotw.com/2/select/
            (3) https://realpython.com/python-sockets/
        """
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as accept_socket:        
            # unblock, bind, and listen to accept_socket
            accept_socket.setblocking(0) 
            accept_socket.bind(('',port)) 
            accept_socket.listen(backlog)

            # Initialize open_connections to the accept_socket
            self.open_connections.append(accept_socket)

            while self.open_connections:
                read_list, write_list, exception_list = select.select(self.open_connections, self.writable_connections, self.open_connections)
                   
                for s in read_list:
                    if s is accept_socket:                        
                        self.tcp_handshake(s)
                    else:
                        self.read_socket(s)

                for s in write_list:
                    self.write_socket(s)

                # Terminate sockets that have exception.
                for s in exception_list:
                    self.terminate_socket(s)
        pass



if __name__ == '__main__':
    main()

