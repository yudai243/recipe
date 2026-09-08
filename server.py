import json
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8000
DATA_FILE = "notes.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_notes():
    """JSONファイルからメモを読み込む"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_notes(notes):
    """メモをJSONファイルに保存"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # 静的ファイルの処理
        if path.startswith('/static/'):
            self.serve_static(path)
            return

        # メモ削除処理
        if path.startswith('/delete?id='):
            query = parsed_url.query
            params = urllib.parse.parse_qs(query)
            try:
                idx = int(params["id"][0])
                notes = load_notes()
                if 0 <= idx < len(notes):
                    notes.pop(idx)
                    save_notes(notes)
            except (KeyError, ValueError, IndexError):
                pass
            self.redirect("/")
            return

        # メインページの表示
        if path == '/':
            self.serve_index()
        else:
            self.send_404()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == '/':
            # メモ追加処理
            length = int(self.headers["Content-Length"])
            body = self.rfile.read(length).decode()
            params = urllib.parse.parse_qs(body)
            memo = params.get("memo", [""])[0]

            if memo.strip():
                notes = load_notes()
                notes.append(memo)
                save_notes(notes)

            self.redirect("/")
        else:
            self.send_404()

    def serve_index(self):
        notes = load_notes()

        notes_html = ""

        for i, note in enumerate(notes):

            note_html = self.render_template(
                "note.html",
                id=i,
                content=note.replace("\n", "")
            )

            notes_html += note_html

        html = self.render_template(
            "index.html",
            notes=notes_html,
            title="メモ帳アプリ"
        )

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        self.wfile.write(html.encode("utf-8"))

    def render_template(self, filename, **kwargs):
        filepath = os.path.join(BASE_DIR, "templates", filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        for key, value in kwargs.items():
            content = content.replace(f"{{{{ {key} }}}}", str(value))

        return content
    def serve_static(self, path):
        """静的ファイル（CSS、画像など）を配信"""

        try:
            # URLの先頭の「/」を削除してファイルパスにする
            #
            # /static/style.css
            # ↓
            # static/style.css
            filepath = os.path.join(BASE_DIR, path.lstrip("/"))

            # CSSや画像はバイナリモード(rb)で読み込む
            with open(filepath, 'rb') as f:
                content = f.read()

            # ==========================
            # ファイルの種類を判定する
            # ==========================
            # ブラウザへ「これはCSSです」「画像です」と伝える
            if path.endswith('.css'):
                content_type = 'text/css; charset=utf-8'

            elif path.endswith('.js'):
                content_type = 'application/javascript; charset=utf-8'

            elif path.endswith('.png'):
                content_type = 'image/png'

            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                content_type = 'image/jpeg'

            else:
                # その他のファイル
                content_type = 'application/octet-stream'

            # HTTPレスポンスを返す
            self.send_response(200)

            # ファイルの種類(Content-Type)を送信
            self.send_header('Content-type', content_type)

            # ヘッダー終了
            self.end_headers()

            # CSSや画像データをブラウザへ送信
            self.wfile.write(content)

        except FileNotFoundError:
            # ファイルが存在しなければ404
            self.send_404()
def run():
    # 必要なディレクトリを作成
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    server = HTTPServer(("localhost", PORT), MyHandler)
    print(f"🚀 メモ帳アプリを起動しました")
    print(f"📡 アドレス: http://localhost:{PORT}")
    print(f"📁 テンプレート: templates/")
    print(f"📁 静的ファイル: static/")
    print(f"📝 データファイル: {DATA_FILE}")
    print("🔄 終了するには Ctrl+C を押してください")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 サーバーを停止しました")
        server.server_close()

if __name__ == "__main__":
    run()