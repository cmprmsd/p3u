#!/usr/bin/env python3

import base64
import os
import re
import shutil
import sys
import urllib
import getopt
import cgi
import http.server
import ssl
import string
from datetime import datetime

__all__ = ["P3U"]
__author__ = "H8.to // 0x483d"
__home_page__ = "http://h8.to/"

auth_log_file = None

# This script makes all arguments optional and uses C style arguments
# Original script: https://github.com/4d4c/http.server_upload/blob/master/https_upload.py
# This version also includes path traversal fix, host argument and certificate generate argument -g

class P3UWebServer(http.server.BaseHTTPRequestHandler):
    server_version = "Apache"  # replaces BaseHTTP/0.6
    sys_version = ""  # replaces Python/3.6.7

    # Check if user is authenticated
    def is_authenticated(self):
        if use_auth:
            authorization_header = self.headers["Authorization"]
            if authorization_header == self.basic_authentication_key:
                # Allow access if password is correct
                return True
            
            # If password is wrong, log failed authentication to stdout
            if authorization_header is not None:
                time = datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")
                source_ip = self.client_address[0]
                
                try:
                    b64 = authorization_header.replace("Basic ", "")
                    provided_data = base64.b64decode(b64).decode('utf-8')
                except:
                    provided_data = str(authorization_header)

                # Log failed authentication
                auth_log_file = open(AUTH_LOG_FILE_PATH, "a")
                auth_log_file.write(time + " -- " + source_ip + " -- " + provided_data + "\n")
                auth_log_file.close()

            self.do_AUTHHEAD()
            self.close_connection = True
            return False
        # If no authentication enabled, allow access
        return True

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic realm=\"Test\"")
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_HEAD(self):
        return self.do_GETANDHEAD()

    def do_GET(self):
        return self.do_GETANDHEAD()

    def do_POST(self):
        if not self.is_authenticated():
            return self.do_GET()

        post_form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers['Content-Type']
            }
        )
        # Save File after uploading it.
        dir_path = os.getcwd()
        file_name = urllib.parse.unquote(post_form["file"].filename)
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        file_name = ''.join(c for c in file_name if c in valid_chars)
        with open(dir_path + self.path + file_name, 'wb') as file_object:
            shutil.copyfileobj(post_form["file"].file, file_object)
        return self.do_GET()

    def do_GETANDHEAD(self):
        if not self.is_authenticated():
            return

        request_path = os.getcwd() + re.split(r'\?|#', self.path)[0]
        if os.path.isdir(request_path):
            directory_contents_html = self.get_directory_contents_html(request_path)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(directory_contents_html)))
            self.end_headers()
            self.wfile.write(directory_contents_html)
            return

        try:
            request_path = urllib.parse.unquote(request_path)

            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.send_header("Content-Length", str(os.stat(request_path).st_size))
            self.send_header("Last-Modified", self.date_time_string(os.stat(request_path).st_mtime))
            self.end_headers()

            if self.command == "GET":
                request_file = open(request_path, 'rb')

                shutil.copyfileobj(request_file, self.wfile)

                request_file.close()
        except IOError:
            self.send_error(404, "File not found")
            return

        return

    def get_directory_contents_html(self, request_path):
        try:
            file_list = os.listdir(request_path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return ""

        file_list_html = ""
        for file_name in file_list:
            file_href = file_display_name = file_name

            if os.path.isdir(file_name):
                file_display_name = file_name + "/"
                file_href = file_href + "/"
            if os.path.islink(file_name):
                file_display_name = file_name + "@"

            file_list_html = file_list_html + "<li><a href=\"{}\">{}</a></li>\n".format(
                urllib.parse.quote(file_href), file_display_name
            )

        return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>P3U</title>
            </head>
            <body>
                <h2>Directory listing for {}</h2>
                <hr>
                <form ENCTYPE="multipart/form-data" method="post">
                    <input name="file" type="file"/>
                    <input type="submit" value="upload"/>
                </form>
                <hr>
                <ul>
                    {}
                </ul>
                <hr>
            </body>
            </html>
        """.format(request_path, file_list_html).encode()

# Setup Server (CustomBaseHTTPR)
def start_https_server(listening_port, basic_authentication_key, certificate_file):
    if use_auth:
        P3UWebServer.basic_authentication_key = "Basic " + basic_authentication_key.decode("utf-8")

    https_server = http.server.HTTPServer((host, listening_port), P3UWebServer)
    if certificate_file:
        https_server.socket = ssl.wrap_socket(https_server.socket, certfile=certificate_file, server_side=True)

    try:
        https_server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Keyboard interrupt received, exiting...")
        https_server.server_close()
        sys.exit(0)

# Print usage data
def usage():
    print('\np3u.py -l ip -p port -a user:password -c server.pem -o auth.log')

# Main function
if __name__ == '__main__':
    # Try to parse arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ghl:p:a:c:o:")

    # Error Handling
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    # Default options
    certificate_file = False
    use_auth = False
    basic_authentication_key = ""
    host = "127.0.0.1"
    listening_port = 8080
    AUTH_LOG_FILE_PATH="failed_auth.txt"

    # Parse arguments
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            # Print Help
            usage()
            sys.exit(0)
        elif opt == '-l':
            # Set listening IP
            host = arg
        elif opt == '-p':
            # Set listening port
            listening_port = int(arg)
        elif opt == '-a':
            # Enable basic authentication
            basicAuthString = arg
            basic_authentication_key = base64.b64encode(basicAuthString.encode("utf-8"))
            use_auth = True
        elif opt == '-c':
            # Set Certificate file
            certificate_file = arg
        elif opt == '-g':
            # Generate certificate
            os.system('openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.pem -out server.pem -subj "/C=YY"')
        elif opt == '-o':
            AUTH_LOG_FILE_PATH = arg

    protocol = "https://" if certificate_file else "http://"
    print("[+] Staring server... " + protocol + host + ":" + str(listening_port))

    start_https_server(listening_port, basic_authentication_key, certificate_file)
