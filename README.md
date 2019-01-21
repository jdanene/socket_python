# EECS340

## Need to make code work for large pages. !!
- Able to handle large pages like http://stevetarzia.com/libc.html
    - Not easy!!! [Must google](https://www.google.com/search?q=get+all+data+recv+socket&oq=get+all+data+recv+socket&aqs=chrome..69i57.5425j0j4&sourceid=chrome&ie=UTF-8) 
- Need to make sure what the code returns is exactly whats asked
    - HTTP response >= 400 returns a nonzero exit... AND PRINT RESPONSE BODY IF ANY!
    - On Piazza instructor says to use sys.exit() for exit codes! 
    - The above are the only things missed... but need to double check it exactly as instructed

## Everything below i think is done
- All request use the HTTP GET method
- Completion and failure
    - The program should return a unix exit code of 0 if eventually get a "200 OK" response 
        - **so have to parse response**
    - The program should return a nonzero number if failure. (>0)
        - Diff numbers for diff types of failure. 

- Parsing the input by the user
    - Watch out for slash on the end of a website 
        - transform the host name of http://example.com/  -> www.example.com. 
    - Program immediately returns a nonzero number if we see anything but "http://" (aka "https://"  fails) 
    - Allow  request to include a port number like http://example.com:8080/
        - so parse and check for portnumber, if found adjust port number from default 80 -> 8080
    - Able to handle large pages like http://stevetarzia.com/libc.html
        - this one easy has to do w/ toggling w/ buffer size which should already be good. 

- Parsing input from the server
    - Understand and follow 301 and 301 status redirects, find the redirect URL then rerun the program. 
        - This might need to be recurive to handle a chain of multiple redirects (See Project Page), but give up after 10 redirects and probably if we see the same webpage... so no loops ... like graph search
        - Diff numbers for diff types of failure. 


**PROBLEM STATEMENT says to print out the HTML but all the rules talk about response codes. Im guessing print out HTML if it exits and always the nonzero numbers that indicate different types of failure (and success = 0) at the bottom. Maybe clarify?** 





