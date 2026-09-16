from http.server import HTTPServer, BaseHTTPRequestHandler
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path.startswith("/static/"):
            self.serve_static(self.path)
            return

        html = self.render_template("index.html")

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        self.wfile.write(html.encode("utf-8"))

    def render_template(self, filename):
        filepath = os.path.join(BASE_DIR, "templates", filename)

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    def serve_static(self, path):

        filepath = path[1:]

        with open(filepath, "rb") as f:
            content = f.read()

        if path.endswith(".css"):
            content_type = "text/css; charset=utf-8"
        else:
            content_type = "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

        self.wfile.write(content)
def run():
    server_address = ("", 8000)

    httpd = HTTPServer(server_address, MyHandler)
    print("http://localhost:8000")

    httpd.serve_forever()


if __name__ == "__main__":
    run()