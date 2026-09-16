from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = "notes.json"


def load_notes():

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
def save_notes(notes):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    
class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path.startswith("/static/"):
            self.serve_static(self.path)
            return

        notes = load_notes()

        notes_html = ""

        notes_html = ""

        for note in notes:

            note_html = self.render_template(
                "note.html",
                content=note
            )

            notes_html += note_html

            html = self.render_template("index.html")

            html = html.replace("{{ notes }}", notes_html)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            self.wfile.write(html.encode("utf-8"))

    def render_template(self, filename, **kwargs):
        filepath = os.path.join(BASE_DIR, "templates", filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        for key, value in kwargs.items():
            content = content.replace(
                f"{{{{ {key} }}}}",
                str(value)
            )

        return content
        
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

    def do_POST(self):

        length = int(self.headers["Content-Length"])

        body = self.rfile.read(length).decode()

        params = urllib.parse.parse_qs(body)

        memo = params.get("memo", [""])[0]

        if memo.strip():

            notes = load_notes()

            notes.append(memo)

            save_notes(notes)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()
    def render_template(self, filename, **kwargs):
        filepath = os.path.join(BASE_DIR, "templates", filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        for key, value in kwargs.items():
            content = content.replace(
                f"{{{{ {key} }}}}",
                str(value)
        )

        return content
        
def run():
    server_address = ("", 8000)

    httpd = HTTPServer(server_address, MyHandler)

    print("🚀 サーバーを起動しました")
    print("http://localhost:8000")

    httpd.serve_forever()
if __name__ == "__main__":
    run()