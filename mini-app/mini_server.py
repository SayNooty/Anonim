from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    os.chdir('mini_app')  # Переходим в папку с мини-приложением
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print('🌐 Мини-приложение доступно по адресу:')
    print('   http://localhost:8080')
    print('   http://ваш_ip:8080')
    print('\nДля тестирования используйте ngrok:')
    print('   ngrok http 8080')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()