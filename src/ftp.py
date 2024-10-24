import ftplib
import os
import gzip
import shutil

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

def download_and_extract_gz_file(ftp, remote_file_path, local_file_path):
    """ .gzファイルをダウンロードし、解凍して保存 """
    temp_gz_path = local_file_path + ".gz"
    
    try:
        # .gzファイルとして一時的にダウンロード
        with open(temp_gz_path, 'wb') as local_file:
            ftp.retrbinary(f"RETR {remote_file_path}", local_file.write)
        
        # ダウンロードした .gz ファイルを解凍
        with gzip.open(temp_gz_path, 'rb') as gz_file:
            with open(local_file_path, 'wb') as extracted_file:
                shutil.copyfileobj(gz_file, extracted_file)

        # 解凍成功後、.gzファイルを削除
        os.remove(temp_gz_path)
        print(f"Downloaded and extracted: {local_file_path}")

    except ftplib.error_perm as e:
        print(f"Error downloading {remote_file_path}: {e}")

def download_rinex_files(ftp, rinex_list, local_o_directory, local_n_directory):
    """ RINEXリストからFTPサーバーからファイルをダウンロードして解凍する """
    for rinex_id in rinex_list:
        remote_file_o_path = f"/data/G_2.11/2011/070/{rinex_id}0700.11o.gz"
        local_file_o_path = os.path.join(local_o_directory, f"{rinex_id}0700.11o")
        
        remote_file_n_path = f"/data/G_2.11/2011/070/{rinex_id}0700.11n.gz"
        local_file_n_path = os.path.join(local_n_directory, f"{rinex_id}0700.11n")
        
        # 観測ファイルをダウンロードして解凍
        download_and_extract_gz_file(ftp, remote_file_o_path, local_file_o_path)

        # ナビゲーションファイルをダウンロードして解凍
        download_and_extract_gz_file(ftp, remote_file_n_path, local_file_n_path)

def read_rinex_from_file(file_path):
    """ id.txtからRINEX名を抽出する """
    rinex_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) == 2:
                # RINEX ID 部分を抽出してリストに追加
                rinex_list.append(parts[1].strip())
    return rinex_list

def main():
    # FTPのホスト名、ユーザー名、パスワード
    ftp_host = "terras.gsi.go.jp"
    ftp_user = "goldrunner"
    ftp_pass = "Geomaster10"

    # id.txt のファイルパス
    id_file_path = "../data/list.txt"  # id.txtの実際のパスを指定

    # ダウンロード先のローカルディレクトリ
    local_o_directory = "../data/obs"  
    local_n_directory = "../data/nav"  

    # id.txtからRINEX IDを取得
    rinex_list = read_rinex_from_file(id_file_path)

    # FTPサーバーに接続
    ftp = test_ftp_connection(ftp_host, ftp_user, ftp_pass)
    if ftp:
        # RINEXファイルをダウンロードして解凍
        download_rinex_files(ftp, rinex_list, local_o_directory, local_n_directory)
        # FTPセッションを終了
        ftp.quit()

if __name__ == "__main__":
    main()


