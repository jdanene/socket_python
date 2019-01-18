# EECS340

Write Todos here:


- All request use the HTTP GET method
- Watch out for slash on the end of a website and transform to www.example.com. 


import sys
HOST = "www.airbedandbreakfast.com"
PORT = 80
s = socket.socket()

# When the connect completes, the socket s can be used
# to send in a request for the text of the page.
s.connect((HOST,PORT))

#Formatted as a byte string as indicated by `r`
test_text = r"GET\sindex.hmtl\sHTTP/1.1\r\n\r\n"
s.send(test_text)
s.recv


