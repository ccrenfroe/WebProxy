# Caleb Renfroe
# Milestone 3
# Client

#imports
import socket
import sys
import re
import threading

#Global Variables
HOST = 'localhost'

BAD_REQUEST = "400 -- Bad Request\nThe request could not be understood by the server due to malformed syntax. The client SHOULD NOT repeat the request without modifications." # Bad user input
NOT_FOUND = "404 -- Not Found\nThe server has not found anything matching the Request-URI." #Invalid domain & Invalid URL
METHOD_NOT_ALLOWED = "405 -- Method Not Allowed.\nThe method specified in the Request-Line is not allowed for the resource identified by the Request-URI.\n " # Contains Invalid Headers
INTERNAL_SERVER_ERROR = "500 -- Internal Server Error\nThe server encountered an unexpected condition which prevented it from fulfilling the request." # Invalid port
NOT_IMPLEMENTED = "501 -- Not Implemented\nThe server does not support the functionality required to fulfill the request." # Any request type but GET
HTTP_VERSION_NOT_SUPPORTED = "505 -- HTTP Version Not Supported\n The server does not support, or refuses to support, the HTTP protocol version that was used in the request message." # Any HTTP Version but 1.0

# Input: Takes in the first line and the client connection
# Output: Returns the parsed variables. Method from commandline, host and resource from  cleaning and parsing the url, and HTTP Version from commandling, and default port of 80
# Purpose: Work through the commandline input and make necessary changes to return all the variables needed for the HTTP header format.
def inputReader(input,conn):
    input = input.split(" ")
    if (len(input) != 3):
        conn.sendall(BAD_REQUEST.encode()) # Bad syntax
        conn.close()
        sys.exit()
    method = input[0].upper()
    if (method != "GET"):
        conn.sendall(NOT_IMPLEMENTED.encode()) # Must be GET
        conn.close()
        sys.exit()
    # Process to clean & parse url for variables
    host,resource,port = cleanURL(input[1],conn) #Parse the parts of the URL apart
    HTTPVersion = input[2].strip('\n')
    # Error check HTTP Version
    if (HTTPVersion == "HTTP/1.0\r"):
        HTTPVersion += "\n"
    else:
        conn.sendall(HTTP_VERSION_NOT_SUPPORTED.encode()) # Invalid HTTP Version check
        conn.close()
        sys.exit()
    return method, resource, HTTPVersion, host, port

# Input: Takes in the URL to clean
# Output: Parses URL and outputs host, resource, and port
# Purpose: Strip the URL of http:// and parse it to get the host and resource. Also checks for port.

def cleanURL(URLIn,conn):
    #Clean off beginning of URL
    if ("http://" in URLIn  or "https://" in URLIn):
        URLIn = re.sub(r"^http://|^https://", '', URLIn) # Clean off url to format the host and resource
        split = re.split('/',URLIn,1) # split at the first '/'
        host = split[0]
    else:
        conn.sendall(NOT_FOUND.encode()) # Bad URL input
        conn.close()
        sys.exit()
    if ":" in host:
        host_port = host.split(":")
        host = host_port[0]
        port = host_port[1]
        if(port.isdigit() is False):
            conn.sendall(INTERNAL_SERVER_ERROR.encode()) # Port not an integer
            conn.close()
            sys.exit()
    else:
        port = 80 #Default port if not given one
    if (len(split) != 2):
        conn.sendall(NOT_FOUND.encode()) #Requires a resource, i.e. a / or /something
        conn.close()
        sys.exit()
    else:
        temp = split[1] # Temp because need to add / to the beginning
        resource = "/" + temp # Format resource variable correctly
    return host,resource, port

# Input: Take in the headers string and the client connection
# Output: Outputs the headers in a list
# Purpose: Parse through and error check the headers. Returns a  list of headers.
def headerGatherer(headers,conn):
    headersOut = []
    headers = headers.split('\n')
    for header in headers:
        if ("host" in header.lower()) or ("connection" in header.lower()): # Skip host and connection headers
            continue
        elif (header == ''):# Get rid of last blank. I don't know why this is in the list but this skips it in the iterations
            continue
        elif (header == '\r'):
            headersOut.append(header + '\n')
        elif ":" not in header and header != "":
            headersOut.append(header)
            conn.sendall(METHOD_NOT_ALLOWED.encode()) # Invalid header. Needs ':'
            conn.close()
            sys.exit()
        headersOut.append(header + '\n')
    return headersOut

def client_thread(conn,i):
    # Taking in the first line
    firstLine = conn.recv(1)
    while b'\r\n' not in firstLine:
        firstLine += conn.recv(1)
    firstLine = firstLine.decode('utf-8')
    method, resource, HTTPVersion, host, port = inputReader(firstLine,conn)
    # Receiving data for the headers
    headerIn = conn.recv(1024)
    headers = headerIn.decode('utf-8')
    while (b'\r\n\r\n' not in headerIn):  # Keeps looping until empty line
        headerIn = conn.recv(1024)
        headers = headers + headerIn.decode('utf-8')
    headers = headerGatherer(headers,conn)  # Error check, gets rid of any repeat host or connections

    HTTPRequest = method + " " + resource + " " + HTTPVersion + "Host: " + host + "\r\nConnection: close\r\n"  # Format request
    for header in headers:
        HTTPRequest = HTTPRequest + header  # Tack on headers

    # Handshake with server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(5)  # Timesout early instead of waiting a long time for a connection
    try:
        server.connect((host, int(port)))
        server.sendall(HTTPRequest.encode())  # Send request
    except socket.error:  # Handles errors. Added to handle the case where no connection is established after a timeout.
        conn.sendall("Connection could not be established.\n".encode())
        conn.close()
        exit()
    # Keep receiving input until connection is closed
    Server_response = ""
    while True:
        data = server.recv(1024).decode('utf-8')
        if data:
            Server_response += data
        else:
            break

    # Finish and close connections.
    server.close()
    conn.sendall(Server_response.encode())
    conn.close()

    exit()

#Where the magic happens
def main():
    # Check for port argument first
    if (len(sys.argv) != 2):
        print("ERROR -- Need as argument a port to connect to.")
        sys.exit()
    # Try and open port, else trigger an error and exit
    try:
        port_to_connect = int(sys.argv[1])
    except:
        print(INTERNAL_SERVER_ERROR)
        sys.exit()

    thread_list = []
    # Wait and listen for a connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,port_to_connect))
    s.listen(1)

    # Keeps listening and accepting more connections.
    while True:
        #print("Proxy active")
        #print("Listening for connections . . .")
        #Server side of handshake
        i = 1
        while(len(thread_list) < 100):
            conn, addr = s.accept() # Blocking call, returns new socket & address of whos connecting.
            thread = threading.Thread(target=client_thread,args=(conn, i)).start()
            #print("Connection accepted.")
            thread_list.append(thread)
            i + i + 1
    s.close()
    return

#:)
if __name__ == '__main__':
   main()