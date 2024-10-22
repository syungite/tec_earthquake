import ftplib
import os
import re

def test_ftp_connection(ftp_host, ftp_user, ftp_pass):
    """ FTPサーバーに接続して、接続が成功するか確認する """
    try:
        # FTPサーバーに接続
        ftp = ftplib.FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        print(f"Successfully connected to {ftp_host}")
        print("Current directory:", ftp.pwd())
        return ftp
    except ftplib.all_errors as e:
        print("FTP error:", e)
        return None

def download_file(ftp, remote_file_path, local_file_path):
    """ 指定されたファイルをダウンロード """
    try:
        with open(local_file_path, 'wb') as local_file:
            ftp.retrbinary(f"RETR {remote_file_path}", local_file.write)
        print(f"Downloaded: {local_file_path}")
    except ftplib.error_perm as e:
        print(f"Error downloading {remote_file_path}: {e}")

def find_and_download_files(ftp, coordinate_id, local_directory):
    """ 指定された地点IDで末尾4桁が一致するファイルをダウンロード """
    # リモートファイルリストを取得
    remote_dir = "/data/coordinates_F5/GPS/2011/"
    try:
        files = ftp.nlst(remote_dir)  # リモートディレクトリ内のファイルリストを取得
    except ftplib.error_perm as e:
        print(f"Error listing directory {remote_dir}: {e}")
        return

    # 末尾4桁が一致するファイルを見つける
    pattern = re.compile(rf".*{coordinate_id}(\d{{2}})\.pos$")  # 任意の位置に地点IDが含まれ、末尾が4桁の数字で終わる
    for remote_file in files:
        match = pattern.search(remote_file)  # 一致するファイルを探す
        if match:
            local_file_path = os.path.join(local_directory, os.path.basename(remote_file))
            download_file(ftp, remote_file, local_file_path)

def read_coordinate_from_file(file_path):
    """ list.txtから地点IDを抽出する """
    coordinate_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) == 2:
                # 地点ID部分を抽出してリストに追加
                coordinate_list.append(parts[1].strip())
    return coordinate_list

def main():
    # FTPのホスト名、ユーザー名、パスワード
    ftp_host = "terras.gsi.go.jp"
    ftp_user = "goldrunner"
    ftp_pass = "Geomaster10"

    # list.txt のファイルパス
    id_file_path = "../data/list.txt"  # list.txtの実際のパスを指定

    # ダウンロード先のローカルディレクトリ
    local_directory = "../data/pos"  

    # list.txtから地点IDを取得
    coordinate_list = read_coordinate_from_file(id_file_path)

    # FTPサーバーに接続
    ftp = test_ftp_connection(ftp_host, ftp_user, ftp_pass)
    if ftp:
        # 指定されたファイルをダウンロード
        for coordinate_id in coordinate_list:
            find_and_download_files(ftp, coordinate_id, local_directory)
        # FTPセッションを終了
        ftp.quit()

if __name__ == "__main__":
    main()


