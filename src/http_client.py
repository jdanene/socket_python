import socket, argparse, re, sys, functools, time
"""
Python script for a simple command-line HTTP client implemented using the BSD socket interface.

Written and tested in Python 2.7

Usage: python http_client.py [url]
    
    url: The http web address to fetch. 

Returns: The body of the response (if successful) printed to stdout, 
         otherwise an error message + error code

Original Authors: Jide Anene and Sam Detjen
"""
#url_dict = {'host': 'www.airbedandbreakfast.com', 'path': '/', 'port': 80}

#body = get_header_body(client_request(url_dict))

#python http_client.py maps.google.com


RESPONSE_ERROR_CODE = "2\n"
CONTENT_ERROR_CODE = "3\n"
URL_ERROR_CODE = "4\n"
REDIRECT_ERROR_CODE= "5\n"

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("url")

    if re.match('http_client', sys.argv[0]):
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(sys.argv)

    # check if user indicated HTTP protocol in request
    if is_urlerror(args.url):
        return URL_ERROR_CODE
    # get http response and print output
    else:
        url_dict = get_clean_url(args.url)
        resp = client_request(url_dict)
        print_request(resp)


def print_request(resp, num_redirects = 0):
    """
    Prints the html body of the final request if no error code, otherwise prints the error code. For
    301 or 302 redirects, keeps hopping through links  until failure or success. 
    
    Args: 
       resp (string): Raw response buffer data
       num_redirects (int): number of redirects on current chain. valid for codes 301 or 302 
    """

    header_body_dict = get_header_body(resp)
    header_dict = header_body_dict['header']
    header_error = is_headererror(header_dict)
    if header_error:
        sys.stdout.write(header_error)
    elif num_redirects >=10:
        sys.stdout.write(REDIRECT_ERROR_CODE)
    elif ((header_dict['Status-Code']== 301) or (header_dict['Status-Code']== 302)):
        raw_url = header_dict['Location'].strip()
        print(paste("Redirected to: ",raw_url).decode(), file=sys.stderr)
        print_request(client_request(get_clean_url(raw_url)), num_redirects+1)
    else:
        sys.stdout.write((header_body_dict['body']+b"\n0\n").decode())

def is_headererror(header_dict):
        """
    Checks the header for one of the errors specified in project
    
    Args: 
       header_dict (dictionary):  is a dict of HTTP header keys:values pairs. 
                 For example:
                    - header_dict["Status-Code"] the status code of HTTP (e.g 200)
                    - header_dict["Content-Type"] the content type of HTTP (e.g text/html)
                         .
                         .
                         .
    Returns:
        (boolean): An False if no errors, otherwise returns the specific header error. 
    """

    if is_respcode_error(header_dict): 
        return RESPONSE_ERROR_CODE
    elif is_contenterror(header_dict):
        return CONTENT_ERROR_CODE
    elif ((header_dict['Status-Code']== 301) or (header_dict['Status-Code']== 302)): #condition for redirect
        if is_urlerror(header_dict['Location']):
            return URL_ERROR_CODE
        else:
            return False
    else:
        return False

def get_header_body(resp):
    """
    Splits a `resp' into the http header, and http body. 

    Args: 
       buffer (string): Raw response buffer data

    Returns:
       dict: {"header": string, "body": string}
              - dict["header"] is a dict of HTTP header keys:values pairs. 
                 For example:
                    - dict["header"]["Status-Code"] the status code of HTTP (e.g 200)
                    - dict["header"]["Content-Type"] the content type of HTTP (e.g text/html)
                         .
                         .
                         .
              - dict["body"] is text of the HTTP body 
    """
    bufferlst = resp.split(str.encode("\r\n\r\n")) #split data into header and body based on delimiter "\r\n\r\n"
    header = bufferlst[0]

    #Split data into list based on delimeter "\r\n" then split again based on first occurence of ':'
    keyval_pairs = [item.split(str.encode(':'),1) for item in header.split(str.encode("\r\n"))]

    status_code = int(re.findall(r'\s[0-9][^\.]+[0-9]',keyval_pairs[0][0].decode())[0].strip()) #get HTTP status code
    keyval_pairs = keyval_pairs[1:] 
    header_dict = {entry[0].decode():entry[1].decode() for entry in keyval_pairs}
    header_dict["Status-Code"]=status_code
    return {"header":header_dict,"body":bufferlst[1]}

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

def get_clean_url(raw_url):
    """
    Splits a `raw_url` into its host, path, and port number (if it exists). 
    
    Args: 
       raw_url (string): A raw internet url string

    Returns:
       dict: {"host": string, "path": string,"port": boolean}
        - dict["host"] is the url host name
        - dict["path"] is the url path name 
        - dict["port"]  is either the port associated with the url if it is specified, 
          or 80 if it is not specified. 

    Examples:
    >> get_clean_url("http://stevetarzia.com")
    ("host": "www.stevetarzia.com","path" : "/", "port": 80)

    >> get_clean_url("http://stevetarzia.com/")
    ("host": "www.stevetarzia.com","path" : "/", "port": 80)

    >> get_clean_url("http://stevetarzia.com/pizzagate")
    ("host": "www.stevetarzia.com","path" : "/pizzagate", "port": 80)

    >> get_clean_url("http://stevetarzia.com/pizzagate/")
    ("host": "www.stevetarzia.com","path" : "/pizzagate", "port": 80)

    >> get_clean_url("http://portquiz.net:8080/")
    ("host": "www.portquiz.net","path" : "/", "port": 8080)

    >> get_clean_url("http://portquiz.net:8080")
    ("host": "www.portquiz.net","path" : "/", "port": 8080)

    >> get_clean_url("http://www.google.com:443/maps")
    ("host": "http://www.google.com","path" : "/maps", "port": 443)
    
    """
    raw_url = raw_url.strip()
    clean_url = dict()

    # remove http:// or http://www. from the string
    raw_url = re.sub(r"^http:\/\/((?!www\.)|www\.)", "", raw_url, 1)
    
    #Check if url has a port number
    portnumber = re.search(r":[0-9]+",raw_url)
    if not portnumber:
        host_path = re.compile(r"\/").split(raw_url, 1)
        clean_url["port"] = 80
    else:
        host_path = re.compile(r":[0-9]+").split(raw_url, 1)
        clean_url["port"] = int(portnumber[0][1:])
    
    path = "" if len(host_path)<2 else host_path[1] #initialize path if none is found in the string split
    path = re.sub(r"\/$","",path) #remove trailing backslash
    path = path if re.search(r"^\/",path) else "/"+path #add backslash to the front if it is missing
    clean_url["path"] = path.strip() 

    clean_url["host"] = host_path[0]
    return clean_url

def client_request(url_dict):
    """
    Performs a 'GET' request using the info in `url_dict' and returns the data recieved.  

    Args:
        url_dict (dict): {"host": string, "path": string,"port": boolean}
                - dict["host"] is the url host name
                - dict["path"] is the url path name 
                - dict["port"] is either the port associated with the url if it is specified, 
                               or 80 if it is not specified. 
    Returns: 
        string: The raw output string in byte format.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = url_dict["host"]
        path = url_dict["path"]
        port = url_dict["port"]
        protocol = "HTTP/1.1"
        buffersize = 4096
        request = paste("GET"," ",path," ", protocol, "\r\n","Host:"," ", host,"\r\n\r\n")

        s.connect((host,port)) # Open a connection
        s.send(request) #Send the request. The function `paste` byte encodes the string.  

        #Recieve and Buffer the data. 
        data = b''
        while True:
            results = s.recv(buffersize)
            data += results
            if (len(results)<= buffersize):
                break
    return results

def is_urlerror(raw_url):
    """
    Checks if the HTTP url starts w/ http:

    Args:
        http_header (dict): Http header dict

    Returns: 
        (>0) code if HTTP url does not starts w/ 'http://''

    """
    return not bool(re.match(r"^http:\/\/",raw_url.strip()))


def is_respcode_error(header_dict):
    """
    Checks if the HTTP response code >= 400  

    Args:
        http_header (string): Http header

    Returns: 
        (>0) code if HTTP response header >= 400"

    """
    return header_dict["Status-Code"] >= 400

def is_contenterror(header_dict):
    """
    Checks if content-type: in a HTTP header begins with "text/html"

    Args:
        http_header (string): Http header

    Returns: 
        (>0) code if content-type: does not begin with "text/html"
    """
    return not bool(re.match(r"^\s*text\/html",header_dict["Content-Type"]))


if __name__ == "__main__":
    main()

