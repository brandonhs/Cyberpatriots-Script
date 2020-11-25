import http.server, socketserver, webbrowser


class Server(http.server.BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content_Type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.path = '/modules/page.html'

    def do_POST(self):
        self._set_headers()

def serve(addr="localhost", port=8080):
    server_address = (addr, port)
    server = http.server.HTTPServer(server_address, Server)

    webbrowser.open_new_tab('http://localhost:8080/'.format(addr,port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server
