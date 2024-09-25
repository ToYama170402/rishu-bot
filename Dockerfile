# ベースイメージとしてPythonの公式イメージを使用
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# ファイルの所有者を変更
RUN chown -R nobody:nogroup /app

# 非スーパーユーザーに切り替え
USER nobody

# ボットを起動するコマンドを指定
CMD ["python", "app.py"]
