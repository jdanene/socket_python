import socket, argparse, re, sys, functools, os, platform, pytz
from datetime import timezone, datetime, timedelta
try:
    from tzlocal import get_localzone
except:
    sys.exit('The package "tzlocal" is needed to proceed')
"""
https://www.thoughtco.com/building-a-simple-web-server-2813571

Python script for a HTTP server that handles one connection at a time
and serves any files in the current directory if their names ends w/ .html or .htm

Written and tested in Python 3.6

Usage: python http_server1.py [port]

    port: The default port to "hear" incoming connections for TCP 3-way handshake

Testing example:
    Step 1: from shell set directory to ./src

    Step 2: from shell run the unit test
        >> pytest ../test/test_http_server1.py

    Step 3: from the shell run
        >> python http_server1.py 3000

    Step 3: from the webrowser type the following
        >> http://localhost:3000/rfc2616.html
        >> http://localhost:3000/htm4_example.html

ToDo: Make server support 'HEAD' request instead of just 'GET'
ToDo: For invalid responses automatically output a HTML invalid page.

"""

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("port")

    if re.match('http_server1', sys.argv[0]):
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(sys.argv)

    # Assert condition that port number >= 1024.
    args.port = int(args.port)
    assert args.port >= 1024, "Port Number must be >= 1024"

    # Run HTTP server
    server = HttpServer1()
    server.server(args.port)

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

class HttpServer1:
    def __init__(self, html_path = "../server_dir"):
        self.html_path = html_path
        self.fnames = [fn for fn in os.listdir(html_path) if bool(re.search( r"\.htm[l]?$",fn))]
        pass

    def format_datetime(self, _datetime = ""):
        """
        Returns a properly GMT formatted date time given a datetime object.
        The default is to return the properly GMT formatted current datetime
        """
        if _datetime == "":
            date = datetime.now(get_localzone())
            date = date.astimezone(pytz.timezone("GMT"))
            date = date.strftime('%a, %d %b %Y %H:%M:%S')+" "+date.tzname()
        else:
            date = datetime.fromtimestamp(_datetime, get_localzone())
            date = date.astimezone(pytz.timezone("GMT"))
            date = date.strftime('%a, %d %b %Y %H:%M:%S')+" "+date.tzname()
        return date

    def _get_content_type(self, filepath):
        """
        Loop over and check each line for content length in the HTML file

        """
        with open(filepath) as f:
            count = 0
            while True:
                line = f.readline()
                type_match = self._parse_line(line)
                if type_match:
                    return type_match
                elif not line or (count == 100) :
                    return "text/html"
                else:
                    pass
                count += 1

    def _parse_line(self, line):
        """
        Parse line of html file to find the content-type
        """
        if len(line) == 0: return False
        # See -> https://www.w3schools.com/html/html_charset.asp
        html5parser = re.compile(r'meta charset=\"(.*)\"')
        html4parser = re.compile(r'meta http-equiv=\"Content-Type\" content=\"(.*)(?=\")')

        for parser, _type in zip([html5parser,html4parser],["html5","html4"]):
            match = parser.search(line)
            if match:
                match = match.groups()[0]
                if _type == "html5":
                    match = "text/html; "+match
                break
        return match

    def is_goodrequest(self, req_filename):

        """
        Returns the response header for the requested file `req_filename` if `req_filename`
        is in our HTML directory, otherwise returns False.

        Input:
          req_filename (str) : Name of the request file for instance "rfc2616.html"
        """
        connection = "close"
        date = self.format_datetime()

        req_filename = re.sub("/","",req_filename)
        if req_filename in self.fnames:
            extension = req_filename.split('.')[1]
            if extension != "htm" and extension != "html":
                return "403"
            last_modified = self.format_datetime(os.path.getmtime(os.path.join(self.html_path,req_filename)))
            content_length = os.path.getsize(os.path.join(self.html_path,req_filename))
            content_type = self._get_content_type(os.path.join(self.html_path,req_filename))

            with open(os.path.join(self.html_path,req_filename),'r') as html_file:
                response =  paste("HTTP/1.1 200 OK","\r\n","Connection: ","close","\r\n",
                                  "Date: ",date,"\r\n","Last-Modified: ",last_modified,"\r\n",
                                  "Content-Length: ",content_length,"\r\n","Content-Type: ",content_type,"\r\n\r\n",
                                  html_file.read())
            return response
        else:
            return False

    def get_HTTP_response(self,header_dict):
        """
        Checks the HTTP request to see if its valid, and then outputs appropriate http response

        """
        error_400 = "400 Bad Request"
        error_505 = "505 Version Not Supported"
        error_404 = "404 Not Found"
        error_403 = "403 Forbidden"
        date = self.format_datetime()

        # function to output HTTP headers for different type of errors.
        http_error = lambda error_type, connection_type: paste(error_type,"\r\n","Connection: ",connection_type,"\r\n",
                                                               "Date: ",date,"\r\n", "Content-Length: ",0,"\r\n\r\n")

        if header_dict["req_type"] != 'GET':
            return http_error(error_400, "close")
        elif header_dict['http_version'] != 'HTTP/1.1':
            return http_error(error_505, "close")
        good_req = self.is_goodrequest(header_dict['req_file'])
        if not good_req:
            return http_error(error_404, "close")
        elif good_req == "403":
            return http_error(error_403, "close")
        else:
            return good_req

    def get_header_body(self,request):
            """
            Splits a `request' into the http header, and http body.

            Args:
               request (string): Raw request buffer data

            Returns:
               dict: {"header": dict , "body": string}
                      - dict["body"] is text of the HTTP body
                      - dict["header"] is a dict of HTTP header keys,values pairs.
                         For example:
                            - dict["header"]["req_type"] the request type of HTTP (e.g GET)
                            - dict["header"]["req_file"] the file requested of HTTP (e.g rfc2616.html)
                            - dict["header"]["http_version"] the version of HTTP protocol (e.g HTTP/1.1)

                            - dict["header"]["Content-Type"] the content type of HTTP (e.g text/html)
                                 .
                                 .
                                 .
            """
            bufferlst = request.split(str.encode("\r\n\r\n")) #split data into header and body based on delimiter "\r\n\r\n"
            header = bufferlst[0]

            #Split data into list based on delimeter "\r\n" then split again based on first occurence of ':'
            keyval_pairs = [item.split(str.encode(':'),1) for item in header.split(str.encode("\r\n"))]
            top_line_of_header = keyval_pairs[0][0].decode().split(" ")
            keyval_pairs = keyval_pairs[1:]
            header_dict = {entry[0].decode():entry[1].decode() for entry in keyval_pairs}

            # label and put headers from first line header into header dictionary
            header_dict["req_type"] = top_line_of_header[0]
            header_dict["req_file"] = top_line_of_header[1]
            header_dict["http_version"] = top_line_of_header[2]

            return {"header":header_dict,"body":bufferlst[1]}

    def server(self, port = 12000, backlog = 20):
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
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            #indicates the end of the connection
                            break

                        #Parses the http request.
                        data_dict = self.get_header_body(data)
                        header_dict = data_dict["header"]

                        #gets the request to give back to client
                        http_request = self.get_HTTP_response(header_dict)


                        #send the data to client
                        conn.sendall(http_request)

                    #closes the special socket created for client
                    conn.close()

if __name__ == '__main__':
    main()
