#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import html
import logging
import ssl
import rpyc
from http.server import BaseHTTPRequestHandler, HTTPServer

def get_data():
    output = ''
    try:
        rcon = rpyc.connect('localhost', 18888)
        output = rcon.root.get_data()
    except ConnectionError as e:
        return(b'Error Error Error')
    return bytes(str(output), 'UTF-8')

def load_binary(file):
    with open(file, 'rb') as f:
        return f.read()

class WebHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s", self.client_address[0],
                        self.log_date_time_string(), format%args)

    def do_GET(self):
        logging.warning('do_GET')
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/wood-background.jpg':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(load_binary('wood-background.jpg'))
        elif self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(get_data())
        else:
            self.send_response(404)
            self.send_header(b'Content-type', b'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<html><head>')
            self.wfile.write(b'</head><body>')
            self.wfile.write(b'<font size="7">')
            self.wfile.write(b'Path not found')
            self.wfile.write(b'</body></html>')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename='/var/log/sauna_web.log')
    try:
        httpd = HTTPServer(("", 443), WebHandler)
        httpd.socket = ssl.wrap_socket(httpd.socket,
                certfile='./server.pem', server_side=True)
        logging.info("HTTPS server started")
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info('Stop with a signal, shutting down server')
        httpd.socket.close()
