import socket
from urllib.request import Request, urlopen, HTTPError
import argparse


def main():
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 12300

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))

# 5 here means that 5 connections are kept waiting if the server is busy
# and if a 6th socket tries to connect then the connection is refused.
    server_socket.listen(5)

    while True:
        client_connection, client_address = server_socket.accept()

        request_packet = client_connection.recv(1024).decode()
        print(request_packet)

        req_pack_headers = request_packet.split('\n')

        req_pack_top_header = req_pack_headers[0].split()

        response = ''
        if not req_pack_top_header:
            response = ('HTTP/1.0 404 NOT FOUND\n\n File Not Found').encode()
        else:
            method = req_pack_top_header[0]
            filename = req_pack_top_header[1]

            if filename.startswith('http://'):
                filename = filename[6:]

            print(len(filename), filename)

# Get the file
            content = get_file(filename)

# If we have the file, return it, otherwise 404
            response = ""
            if content:
                response = ('HTTP/1.0 200 OK\n\n').encode()
                response += content
            else:
                response = (
                    'HTTP/1.0 404 NOT FOUND\n\n File Not Found').encode()

        client_connection.sendall(response)
        client_connection.close()

    server_socket.close()


# This is basically the heart of the proxy server. It gets a URL,
# checks if it's cached and up to date. If OK, it returns the cached byte file.
# If not, it fetches the file, and then returns the byte file.
def get_file(req_url):
    file_from_cache, cached_date = fetch_from_cache(req_url)

    if file_from_cache:
        print('Fetched successfully from cache.')

        file_from_server, last_modified_date, cache_up_to_date = fetch_conditional(
            req_url, cached_date, file_from_cache)

        if cache_up_to_date:
            print("File found. Loading from cache.")
        else:
            print("File expired. Displaying new file.")
            save_in_cache(req_url, last_modified_date, file_from_server)

        if file_from_server:
            return file_from_server
        else:
            return None
    else:
        print("New URL. Fetching and caching.")
        file_from_server, last_modified_date = fetch_from_server(req_url)

        if file_from_server:
            save_in_cache(req_url, last_modified_date, file_from_server)
            return file_from_server
        else:
            return None


def fetch_conditional(req_url, cached_date, cached_content):
    print('Checking if file has expired')
    url = 'http:/' + req_url
    q = Request(url)
    q.add_header("IF-MODIFIED-SINCE", cached_date)

    try:
        response = urlopen(q)
        # Grab the header and content from the server req
        response_headers = response.info()
        modification_date = response_headers['Last-Modified'] or response_headers['Date'] or "Sun, 12 Jul 1970 08:10:08 GMT"
        content = response.read()
        return content, modification_date, True
    except HTTPError as e:
        status_code = e.code
        if status_code == 304:
            return cached_content, cached_date, False
        else:
            return None, None, None


# Is the file cached and accessible? (Ignoring the last modified stuff)
def fetch_from_cache(req_url):
    try:
        filename = '/' + req_url.replace('/', '^')

        # Check if we have this file locally
        fin = open('cache' + filename, 'rb')
        content = fin.read()
        fin.close()

        fin = open('date' + filename)
        date = fin.read()
        fin.close()

        return content, date
    except IOError:
        return None, None


def save_in_cache(url, last_modified_date, file_content):
    filename = '/' + url.replace('/', '^')
    print('Saving a copy of {} in the cache'.format(filename))
    cached_file = open('cache' + filename, 'wb')
    cached_file.write(file_content)
    cached_file.close()

    date_file = open('date' + filename, 'w')
    date_file.write(last_modified_date)
    date_file.close()


def fetch_from_server(req_url):
    url = 'http:/' + req_url
    q = Request(url)

    try:
        response = urlopen(q)
        # Grab the header and content from the server req
        response_headers = response.info()
        modification_date = response_headers['Last-Modified'] or response_headers['Date'] or "Sun, 12 Jul 1970 08:10:08 GMT"
        content = response.read()
        return content, modification_date
    except Exception:
        return None, None


if __name__ == '__main__':
    main()
