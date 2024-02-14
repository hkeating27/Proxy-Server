# Place your imports here
import signal
from optparse import OptionParser
from socket import *
import sys

# Signal handler for pressing ctrl-c
def ctrl_c_pressed(signal, frame):
    sys.exit(0)

# Start of program execution
# Parse out the command line server address and port number to listen to
parser = OptionParser()
parser.add_option('-p', type='int', dest='serverPort')
parser.add_option('-a', type='string', dest='serverAddress')
(options, args) = parser.parse_args()

port = options.serverPort
address = options.serverAddress
if address is None:
    address = 'localhost'
if port is None:
    port = 2100

# Set up signal handling (ctrl-c)
signal.signal(signal.SIGINT, ctrl_c_pressed)

# Set up sockets to receive requests
with socket(AF_INET, SOCK_STREAM) as listen_skt:
    listen_skt.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    listen_skt.bind((address, port))
    listen_skt.listen()
    print("The server is ready to receive")
    
    while True:
        # Accept incoming connection
        skt, client_address = listen_skt.accept()
        print("Accepted connection from:", client_address)
        
        try:
            # Receive request
            request = skt.recv(2048)
            print("Received request:", request)
            
            # Split request into lines
            request_lines = request.split(b'\r\n')
            
            # Check if the first line contains method, URL, and HTTP version
            if len(request_lines) < 1:
                response = b"HTTP/1.0 400 Bad Request\r\n\r\n"
            else:
                first_line_parts = request_lines[0].split(b' ')
                if len(first_line_parts) != 3:
                    response = b"HTTP/1.0 400 Bad Request\r\n\r\n"
                else:
                    method, url, http_version = first_line_parts
                    if (http_version != b"HTTP/1.0"):
                        response = b"HTTP/1.0 400 Bad Request\r\n\r\n"
                    else:
                        # Parse URL to extract host address
                        url_parts = url.split(b'/')
                        host_address = url_parts[2]
                        host_port = host_address.split(b':')
                        if len(host_port) > 1:
                            port = int(host_port[1])
                        else:
                            port = 80  # Default port if not specified
                        # Handle different HTTP methods
                        if method in (b"HEAD", b"POST"):
                            response = b"HTTP/1.0 501 Not Implemented\r\n\r\n"
                        elif method != b"GET":
                            response = b"HTTP/1.0 400 Bad Request\r\n\r\n"
                        else:
                            # Connect to the destination server
                            with socket(AF_INET, SOCK_STREAM) as dest_skt:
                                dest_skt.connect((host_address, port))
                                dest_skt.sendall(request)
                                response = b""
                                while True:
                                    part = dest_skt.recv(2048)
                                    if not part:
                                        break
                                    response += part
        except Exception as e:
            response = b"You got an unexpected error\r\n\r\n"

        # Send response to client
        skt.sendall(response)
        skt.close()
        
'''while True:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024).decode()
    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence.encode())
    connectionSocket.close()'''
