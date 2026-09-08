from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ブラウザからのリクエストを処理するクラス
# BaseHTTPRequestHandlerを継承することで、HTTP通信を扱えるようになる
class MyHandler(BaseHTTPRequestHandler):

    # GETリクエスト（ページ表示など）が送られてきたときに自動で呼ばれる
    def do_GET(self):

        # URLを解析して、パス部分だけを取得する
        # 例: http://localhost:8000/about?id=1
        # → path は "/about"
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # ==========================
        # 静的ファイル（CSS・画像など）の処理
        # ==========================
        # URLが /static/ から始まる場合は、
        # HTMLではなくCSSや画像ファイルを返す
        if path.startswith('/static/'):
            self.serve_static(path)
            return

        # ==========================
        # ルーティング処理
        # ==========================
        # URLごとに表示するHTMLを切り替える
        if path == '/':
            self.render_template('index.html')

        elif path == '/about':
            self.render_template('about.html')

        elif path == '/contact':
            self.render_template('contact.html')

        # 定義されていないURLの場合は404エラーを表示する
        else:
            self.send_404()

    def render_template(self, filename, **kwargs):
        """テンプレートファイルを読み込み、プレースホルダーを置換して表示"""

        try:
            # templatesフォルダの中のHTMLファイルを指定する
            # filepath = os.path.join("templates", filename)
            filepath = os.path.join(BASE_DIR, "templates", filename)

            # HTMLファイルを読み込む
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # ==========================
            # テンプレート変数の置換
            # ==========================
            for key, value in kwargs.items():
                content = content.replace(f"{{{{ {key} }}}}", str(value))

            # ==========================
            # HTTPレスポンスを返す
            # ==========================

            # ステータスコード200（成功）
            self.send_response(200)

            # ブラウザへ「HTMLですよ」と伝える
            self.send_header("Content-type", "text/html; charset=utf-8")

            # ヘッダー情報の送信終了
            self.end_headers()

            # HTMLの内容をブラウザへ送信する
            self.wfile.write(content.encode("utf-8"))

        except FileNotFoundError:
            # HTMLファイルが存在しなければ404エラー
            self.send_404()

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

    def send_404(self):
        """404 Not Foundを返す"""

        # HTTPステータス404（ページが見つからない）
        self.send_response(404)

        # HTMLとして返す
        self.send_header('Content-type', 'text/html; charset=utf-8')

        # ヘッダー終了
        self.end_headers()

        # エラーメッセージをブラウザへ送信
        self.wfile.write('<h1>404 Not Found</h1>')


def run():
    print(os.getcwd())
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandler)

    print('🚀 サーバーを起動しました: http://localhost:8000')
    print('📁 テンプレートディレクトリ: templates/')
    print('📁 静的ファイルディレクトリ: static/')

    httpd.serve_forever()

if __name__ == '__main__':
    run()