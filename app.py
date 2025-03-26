from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
from datetime import datetime
import re
from db import save_user

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_static_file('templates/form.html', 'text/html')
        elif self.path == '/static/styles.css':
            self.serve_static_file('static/styles.css', 'text/css')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)
            
            errors = self.validate_form_data(data)
            
            if errors:
                self.send_json_response(400, {'errors': errors})
            else:
                try:
                    user_data = self.prepare_user_data(data)
                    user_id = save_user(user_data)
                    self.send_json_response(200, {
                        'success': True,
                        'message': 'Данные успешно сохранены',
                        'user_id': user_id
                    })
                except Exception as e:
                    self.send_json_response(500, {'error': str(e)})

    def serve_static_file(self, filepath, content_type):
        try:
            with open(filepath, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

   

    def prepare_user_data(self, data):
        fullname_parts = data['fullname'][0].strip().split()
        return {
            'first_name': fullname_parts[0] if len(fullname_parts) > 0 else '',
            'last_name': fullname_parts[1] if len(fullname_parts) > 1 else '',
            'middle_name': fullname_parts[2] if len(fullname_parts) > 2 else None,
            'phone': data['phone'][0].strip(),
            'email': data['email'][0].strip(),
            'birthdate': data['birthdate'][0],
            'gender': data['gender'][0],
            'biography': data['bio'][0].strip(),
            'languages': data['language']
        }

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Сервер запущен на порту 8000...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
