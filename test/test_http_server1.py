import sys, pytest, os
sys.path.append('../src')
from http_server1 import *
"""
Testing for file `http_server1.py`

From the command line type:
 >> pytest -q test_http_server1.py
"""

# Generate test object
testObj = HttpServer1()

#Last modified time for out testing http file: "rfc2616.html"
last_modified = datetime.fromtimestamp(os.path.getmtime(os.path.join(testObj.html_path,"rfc2616.html")), get_localzone())
last_modified = last_modified.astimezone(pytz.timezone("GMT"))
last_modified = last_modified.strftime('%a, %d %b %Y %H:%M:%S')+" "+last_modified.tzname()

#the length of our testing http file: "rfc2616.html"
content_length = os.path.getsize(os.path.join(testObj.html_path,"rfc2616.html"))

# content type of our testing http file: "rfc2616.html"
content_type =  "text/html; utf-8"

#####  Good: Sample HTTP req to check 
sample_req1_good = paste("GET /rfc2616.html HTTP/1.1","\r\n", "HOST: 192.168.0.104","\r\n","Connection: close","\r\n\r\n")
data_dict = testObj.get_header_body(sample_req1_good)

######   Bad: Sample HTTP req to check
    # File thats not found
sample_req_404error = paste("GET user/rfc2616.html HTTP/1.1","\r\n", "HOST: 192.168.0.104","\r\n","Connection: close","\r\n\r\n")
    # Server only supports 'GET'
sample_req_400error = paste("PUT /rfc2616.html HTTP/1.1","\r\n", "HOST: 192.168.0.104","\r\n","Connection: close","\r\n\r\n")
    # Server only supports HTTP/1.1
sample_req_505error = paste("GET /rfc2616.html HTTP/1.0","\r\n", "HOST: 192.168.0.104","\r\n","Connection: close","\r\n\r\n")


def test_get_header_body():
    #Testing function `get_header_body`
    correct_val = {"req_type": "GET","req_file": '/rfc2616.html', "http_version":'HTTP/1.1',"HOST":"192.168.0.104","Connection": "close" }
    for k,v in data_dict["header"].items():
        assert v.strip() == correct_val[k].strip(), "Failed: "+v.strip()+"!="+correct_val[k].strip()

def test_isgoodrequest():
    date = testObj.format_datetime()
    with open(os.path.join(testObj.html_path,"rfc2616.html"),'r') as test_file:
        good_resp = paste("HTTP/1.1 200 OK","\r\n","Connection: ","close","\r\n", 
                          "Date: ",date,"\r\n","Last-Modified: ",last_modified,"\r\n",
                          "Content-Length: ",content_length,"\r\n","Content-Type: ",content_type,"\r\n\r\n",
                          test_file.read())
        #Testing function `is_goodrequest` and '_get_content_type'
        assert testObj.is_goodrequest(data_dict["header"]["req_file"]) == good_resp, 'there is an error in "is_goodrequest"'+testObj.is_goodrequest(data_dict["header"]["req_file"]).decode()
        assert testObj.is_goodrequest(testObj.get_header_body(sample_req_404error)["header"]["req_file"]) == False , 'there is an error in "is_goodrequest"'
        assert testObj._get_content_type(os.path.join(testObj.html_path,"testfile1.html")) == "text/html", 'error in "_get_content_type" for testfile1'
        assert testObj._get_content_type(os.path.join(testObj.html_path,"htm4_example.html")) == "text/html; charset=iso-8859-1", 'error in "_get_content_type" for HTML4 Test File'

def test_get_HTTP_response():        
    date = testObj.format_datetime()
    with open(os.path.join(testObj.html_path,"rfc2616.html"),'r') as test_file:
        good_resp = paste("HTTP/1.1 200 OK","\r\n","Connection: ","close","\r\n", 
                          "Date: ",date,"\r\n","Last-Modified: ",last_modified,"\r\n",
                          "Content-Length: ",content_length,"\r\n","Content-Type: ",content_type,"\r\n\r\n",
                          test_file.read())
        http_error = lambda error_type : paste(error_type,"\r\n","Connection: ","close","\r\n", 
                                                               "Date: ",date,"\r\n", "Content-Length: ",0,"\r\n\r\n")
        
        assert testObj.get_HTTP_response(data_dict["header"]) ==  good_resp
        assert testObj.get_HTTP_response(testObj.get_header_body(sample_req_404error)["header"]) == http_error("404 Not Found")
        assert testObj.get_HTTP_response(testObj.get_header_body(sample_req_400error)["header"]) == http_error("400 Bad Request")
        assert testObj.get_HTTP_response(testObj.get_header_body(sample_req_505error)["header"]) == http_error("505 Version Not Supported")

