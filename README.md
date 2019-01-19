# EECS340

Write Todos here:


- All request use the HTTP GET method
- Completion and failure
    - The program should return a unix exit code of 0 if eventually get a "200 OK" response **so have to parse response**
    - The program should return a nonzero number if failure. 
    - The program  should return a nonzero number if response

- Parsing the input by the user
    - Watch out for slash on the end of a website 
    - transform the host name of http://example.com/  -> www.example.com. 
    - Program immediately returns a nonzero number if we see "https" 
    - Program immediately returns a nonzero number if we see anything but "http://"
    - Allow  request to include a port number like http://example.com:8080/
        - so parse and check for portnumber, if found adjust port number from default 80 -> 8080
    - Able to handle large pages like http://stevetarzia.com/libc.html
        - this one easy has to do w/ toggling w/ buffer size which should already be good. 

- Parsing input from the server
    - Understand and follow 301 and 301 status redirects, find the redirect URL then rerun the program. 
        - This might need to be recurive to handle a chain of multiple redirects (See Project Page), but give up after 10 redirects and probably if we see the same webpage... so no loops ... like graph search
    - Parse the response code to complete below


**PROBLEM STATEMENT says to print out the HTML but all the rules talk about response codes. Im guessing print out HTML if it exits and always the nonzero numbers that indicate different types of failure (and success = 0) at the bottom. Maybe clarify?** 





