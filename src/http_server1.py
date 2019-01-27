import socket, argparse, re, sys, functools, os, time, platform, subprocess, pytz
from datetime import timezone, datetime, timedelta

try: 
    from tzlocal import get_localzone
except:
    subprocess.call("pip install tzlocal", shell=True)
    from tzlocal import get_localzone

"""
https://www.thoughtco.com/building-a-simple-web-server-2813571

Python script for a HTTP server that handles one connection at a time
and serves any files in the current directory if their names ends w/ .html or .htm

Written and tested in Python 2.7

Usage: python http_server1.py [port]
    
    port: The default port to "hear" incoming connections for TCP 3-way handshake



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

    #Dictionary of file names and file data to serve up to 
    html_path = "../server_dir"

    #File names in `html_path' that end in html or htm
    fnames = [fn for fn in os.listdir(html_path) if bool(re.search( r"\.htm[l]?$",fn))]

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


def get_content_type(filepath):
    """
    Loop over and check each line for content length in the HTML file

    """
    with open(filepath) as f:
        count = 0
        while True:
            line = f.readline()
            type_match = _parse_line(line)
            if type_match:
                return type_match
            elif not line or (count == 100) :
                return "text/html"
            else:
                pass
            count += 1

def _parse_line(line):
    """
    Parse the line to find the content-type
    """
    if len(line) == 0: return False

    html5parser = re.compile(r"charset=\"(.*)(?=\")")
    html4parser = re.compile(r"content=\"(.*)\"")

    for parser, _type in zip([html5parser,html4parser],["html5","html4"]):
        match = parser.search(line)
        if match:
            match = match.groups()[0]
            if _type == "html5":
                match = "text/html; "+match
            else:
                match = re.sub(";","; ",match)
            break
    return match




def is_goodrequest(req_filename, fnames, html_path = "../server_dir"):

    """
    Returns the response header for the requested file `req_file_name`
    
    Input:
      req_filename (str) : Name of the request file for instance "rfc2616.html"
    """
    #Gets path of request file it it ex

    valid_codes = {"bad":"HTTP/1.1 404 Not Found", "good":"HTTP/1.1 200 OK"}
    connection = "close"
    date = datetime.now(get_localzone())
    date = date.astimezone(pytz.timezone("GMT"))
    date = date.strftime('%a, %d %b %Y %H:%M:%S')+" "+date.tzname()

    if req_filename in fnames:
        last_modified = datetime.fromtimestamp(os.path.getmtime(os.path.join(html_path,req_filename)), get_localzone())
        last_modified = last_modified.astimezone(pytz.timezone("GMT"))
        last_modified = last_modified.strftime('%a, %d %b %Y %H:%M:%S')+" "+last_modified.tzname()

        content_length = os.path.getsize(os.path.join(html_path,req_filename))
        content_type = get_content_type(os.path.join(html_path,req_filename))

        with open(os.path.join("../server_dir",req_filename),'r') as html_file:
            response =  paste(valid_codes["good"],"\r\n","Connection: ","close","\r\n", 
                              "Date: ",date,"\r\n","Last-Modified: ",last_modified,"\r\n",
                              "Content-Length: ",content_length,"\r\n","Content-Type: ",content_type,"\r\n\r\n",
                              html_file.read())
        return response
    else:
        return False 

def get_HTTP_response(header_dict, fnames):
    """
    Checks the HTTP request to see if its valid, and then outputs appropriate http response

    """
    http_error = lambda error_type, connection_type: paste(error_type,"\r\n","Connection: ",connection_type,"\r\n", 
                      "Date: ",date,"\r\n", "Content-Length: ",0,"\r\n\r\n")

    if header_dict["req_type"] != 'GET':
        return http_error("400 Bad Request", "close").encode()
    elif header_dict['http_version'] != 'HTTP/1.1':
        return http_error("505 Version Not Supported", "close").encode()

    good_req = is_goodrequest(header_dict['req_file'],fnames)
    if not good_req:
        http_error("400 Bad Request", "close").encode()
    else:
        return good_req.encode()



#class Http_Server1:
    #def __init__(self, fnames, portnumber):
      #  self.fnames = fnames
       # self.portnumber = portnumber



def get_header_body(resp):
        """
        Splits a `resp' into the http header, and http body. 

        Args: 
           resp (string): Raw response buffer data

        Returns:
           dict: {"header": dict , "body": string}
                  - dict["body"] is text of the HTTP body 
                  - dict["header"] is a dict of HTTP header keys,values pairs. 
                     For example:
                        - dict["header"]["req_type"] the request type of HTTP (e.g GET)
                        - dict["header"]["req_file"] the file requested of HTTP (e.g rfc2616.html)
                        - dict["header"]["http_version"] the version of HTTP protocol (e.g HTTP/1.1)

                        - dict["header"]["Content-Type"] the content type of HTTP (e.g text/html)
                        - dict["header"]["Location"] if the status code is 301 or 302 then this contains the url of the redirect. 
                             .
                             .
                             .
        """
        bufferlst = resp.split(str.encode("\r\n\r\n")) #split data into header and body based on delimiter "\r\n\r\n"
        header = bufferlst[0]

        #Split data into list based on delimeter "\r\n" then split again based on first occurence of ':'
        keyval_pairs = [item.split(str.encode(':'),1) for item in header.split(str.encode("\r\n"))]

        top_line_of_header = keyval_pairs[0][0].decode().split(" ")
        keyval_pairs = keyval_pairs[1:] 
        header_dict = {entry[0].decode():entry[1].decode() for entry in keyval_pairs}
        header_dict["req_type"] = top_line_of_header[0]
        header_dict["req_file"] = re.sub("/","",top_line_of_header[1]) 
        header_dict["http_version"] = top_line_of_header[2]

        return {"header":header_dict,"body":bufferlst[1]}

def server(port = 12000, backlog = 20):
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
                    if not data
                        break

                #Parses the http request. 
                data_dict = get_header_body(data)
                header_dict = data_dict["header"]

                #gets the request to give back to client
                http_request = get_HTTP_response(header_dict, fnames)

                #send the data to client
                conn.sendall(http_request)

if __name__ == '__main__':
    main()

