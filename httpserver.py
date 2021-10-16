"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 0NN
- Fall 202N
- Lab N
- Names:
  - 
  - 

An HTTP server

Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)





"""

import socket
import re
import threading
import os
import mimetypes
import datetime


def main():
    """ Start the server """
    http_server_setup(8080)  # listening startup port-not the port to actually send data through-will estalish this port through thread


def http_server_setup(port):
    """
    Start the HTTP server
    - Open the listening socket
    - Accept connections and spawn processes to handle requests

    :param port: listening port number
    """

    num_connections = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_address = ('', port)
    server_socket.bind(listen_address)
    server_socket.listen(num_connections)
    try:
        while True:
            request_socket, request_address = server_socket.accept()
            ##########################################################
            # delete later: This is the the server sock(listen) acc the request from client
            # it assigns values so the server knows where to send packets
            ################################################################3
            print('connection from {0} {1}'.format(request_address[0], request_address[1]))
            # Create a new thread, and set up the handle_request method and its argument (in a tuple)
            request_handler = threading.Thread(target=handle_request, args=(request_socket,))
            # Start the request handler thread.
            request_handler.start()
            # Just for information, display the running threads (including this main one)
            print('threads: ', threading.enumerate())
    # Set up so a Ctrl-C should terminate the server; this may have some problems on Windows
    except KeyboardInterrupt:
        print("HTTP server exiting . . .")
        print('threads: ', threading.enumerate())
        server_socket.close()


def handle_request(request_socket):  # complete this method to parse a request and respond by returning the designated resource
    # will need to add other helpers
    """
    Handle a single HTTP request, running on a newly started thread.

    Closes request socket after sending response.

    Should include a response header indicating NO persistent connection

    :param request_socket: socket representing TCP connection from the HTTP client_socket
    :return: None
    """

    execute_request(parse_request(request_socket))  # if I need to add more param to execute_request then add after (request_socket)*here*)
    #testing parse response (above line should be called once execute_request is ready):
    print(parse_request(request_socket))

def http_get_word(request_socket):
    """
    Gets the next string of characters surrounded by space or ending in \r\n
    Returns the string, and also whether it's the end of the line.
    This could be used instead of next_byte or socket.recv

    :param socket.pyi http_client_socket: client data socket
    :return: (word, endOfLine)
    :rtype: Any
    :author: Eden Basso
    """

    last_byte = b''
    word = b''
    while (last_byte := request_socket.recv(1)) != b' ':
        if last_byte == b'\r':
            if (last_byte := request_socket.recv(1)) == b'\n':
                return word, True
            else:
                word += b'\r' + last_byte
        else:
            word += last_byte
    return word, False

def parse_request(request_socket):
    """
    ...

    :return: verb, resource, fields, body
    :author: Lucas Gral
    """

    (verb, resource) = get_request_line(request_socket)
    fields = get_header_fields(request_socket)
    body = http_get_body(request_socket)

    return verb, resource, fields, body

def get_request_line(request_socket):
    """
    ...

    :return:
    :author: Lucas Gral
    """
    verb = http_get_word(request_socket)[0]
    resource = http_get_word(request_socket)[0]

    #go to end of request line (so fields can be read after)
    while http_get_word(request_socket)[1] == False:
        pass

    return verb, resource

def get_header_fields(request_socket):
    """
    ...

    :return:
    :author: Lucas Gal
    """
    fields = dict()

    lastWord = None
    while (lastWord := http_get_word(request_socket))[0] != b'':
        key = lastWord[0]
        value = b''

        while (lastWord := http_get_word(request_socket))[1] == False:
            value += lastWord[0] + b' '
        value += lastWord[0]

        fields[key] = value

    return fields

def http_get_body(request_socket):  # method should be fixed
    """
    Gets the body of the client's request for good measure

    :param socket.pyi request_socket: socket representing TCP connection from the HTTP client_socket
    :return: the body of the resource as a bytes object
    :rtype: bytes
    :author: Eden Basso
    """
    request_body = b''
    # uses req header dict() and finds cont len to concatenate body bytes obj
    request_body_length = \
        (get_header_fields(request_socket).get(b'Content-Length:'.decode('ASCII'), key = "KEY NOT FOUND"))
    request_body_length = int.from_bytes(request_body_length, "big")
    for i in range(0, request_body_length):
        request_body += next_byte(request_socket)
    return request_body


def next_byte(request_socket):
    """
    Read the next byte from the socket data_socket.

    :param socket.pyi request_socket: 'TCP data socket' in this case from client used to parse through body of request
    :return: each single byte of the http request
    :rtype: bytes
    """
    return request_socket.recv(1)


def execute_request(request_socket, verb, resource):  # this method should be fixed
    """
    Concatenates the http response and sends it or just sends the status line if client sends an unacceptable request

    :param socket.pyi request_socket: socket representing TCP connection from the HTTP client_socket
    :param bytes verb: HTTP version of the request that will be compared with the server's to ensure correct protocol usage
    :param bytes resource: the URL sent by the client that will be used to retrieve the correct file from the server
    :author: Eden Basso
    """
    http_response = b''
    status_line = get_status_code(resource, request_headers, verb)
    if (status_line := status_line[1])[0]:  # assigns the tuple to just the status ln(bytes) if 200(True)
        # calls helper methods to concatenate res
        http_response = status_line + write_response_headers(resource) + get_response_body(resource)
        # sends res
        send_response(request_socket, http_response)
    else:
        # -> 404 or 400 send only status line
        print("Unacceptable request from client")
        send_response(request_socket, status_line[0])
        # needs to return header lines too



def get_status_code(resource, verb, request_socket):
    """
    Checks the resource, headers, and http version from the client's request and returns the appropriate status code

    :param bytes resource: the URL from the client's request
    :param socket.pyi request_socket: socket representing TCP connection from the HTTP client_socket
    :param verb: HTTP version that will be compared with the server's version to ensure correct protocol usage
    :return: status such as 200 ok, 404 not found, 400 bad connection
    :rtype: bytes
    :author: Eden Basso
    """
    # parses through resource(req) to find './abc.html' (ASCII) : GET sp URL sp ver may need to test what the resource returns
    # needs the file path from server to compare
    # req headers: cont len, and host
    headers = get_header_fields(request_socket)
    if ((b'Content-Length:'.encode('ASCII') not in headers) or (b'Host:'.encode('ASCII') not in headers)) \
        or (verb.decode('ASCII') != b'1.1'):
        print('404 not found: resource na or headers na')
        return b'404 Not Found'.to_bytes(15, 'big')
    elif not os.path.isfile(resource.decode('ASCII')):
        print('404 not found: resource na')
        return b'404 Not Found'.to_bytes(13, 'big')
    return b'200 OK'.to_bytes(6, 'big')

    # for testing purposes
    """if os.path.isfile(resource.decode('ASCII')):
        print('resource exists in path, so far 200')
    else:
        print('404 not found: resource na')
        return b'404 Not Found'.to_bytes(13, 'big')
    if verb.decode('ASCII') == b'1.1':
        print('ver matches')
    else:
        print('400 Bad Request: ver doesnt match')
        return b'400 Bad Request'.to_bytes(15, 'big')
    if (b'Content-Length:'.encode('ASCII') in headers) and (b'Host:'.encode('ASCII') in headers):
        ok = True
        print('all req headers')
    else:
        print('400 Bad Request: req header na')
        return b'400 Bad Request'.to_bytes(15, 'big')
    return b'200 OK'.to_bytes(6, 'big')"""


def get_response_body(resource):  # will need body in parsed bytes
    """
    Gets the body from the resource and returns it to be sent to the client in an http response

    :param resource: URL from the client's request that will be used to return the correct file
    :return: parsed through file that matches the client's request
    :rtype: bytes
    :author: Lucas Gral
    """


def write_response_headers(resource):  # needs mime type, cont len, func for time stamp, and some inc of nonpersitant conn
    """
    Writes the headers of the response that contains the time, non-persist connection, mime type, and cont. length

    :param bytes resource: URL from the client's request
    :return: all of the headers needed for the http server's response
    :rtype: bytes
    :author: Eden Basso
    """
    # must wite headers for 400 and 404






def send_response(request_socket, response):
    """
    Sends the entire response containing the appropriate resource to the client

    :param socket.pyi request_socket: socket with the domain/IPV of the client and port number to send packets to
    :param response: the entire response that will be sent to the client
    :author: Lucas Gral
    """


# ** Do not modify code below this line.  You should add additional helper methods above this line.

# Utility functions
# You may use these functions to simplify your code.


def get_mime_type(file_path):  # this method will be used to identify file type in the response sent to the client
    """
    Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If successful in guessing the MIME type, a string representing the content type, such as 'text/html'
             Otherwise, None
    :rtype: int or None
    """

    mime_type_and_encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type_and_encoding[0]
    return mime_type


def get_file_size(file_path):  # this method will be used to get thee size of the file which will be sent to the client this will be sent in the header
    """
    Try to get the size of a file (resource) as number of bytes, given its path

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If file_path designates a normal file, an integer value representing the the file size in bytes
             Otherwise (no such file, or path is not a file), None
    :rtype: int or None
    """

    # Initially, assume file does not exist
    file_size = None
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    return file_size


main()

# Replace this line with your comments on the lab

#temporary
"""
def execute_request(http_socket, request_data):
    request_verb = request_data[0]
    request_resource = request_data[1]
    request_fields = request_data[2]
    request_body = request_data[3]

    if(request_verb == 'GET'):
        execute_request_get(http_socket, request_resource)
    elif(request_verb == etc):
        ...
    else:
        print("Unknown request:", request_verb)
"""
