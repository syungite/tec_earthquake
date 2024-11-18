import ftplib
import os
import re
import gzip
import shutil
import datetime
import subprocess
from calculate_distance import process_pos_files

def date_to_day_of_year(year, month, day):
    date = datetime.datetime(year, month=month, day=day)
    day_of_year = date.strftime("%j")
    return day_of_year

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

def find_and_download_files(year,ftp, coordinate_id, local_directory):
    """ 指定された地点IDで末尾4桁が一致するファイルをダウンロード """
    # リモートファイルリストを取得
    remote_dir = f"/data/coordinates_F5/GPS/{year}/"
    try:
        files = ftp.nlst(remote_dir)  # リモートディレクトリ内のファイルリストを取得
    except ftplib.error_perm as e:
        print(f"Error listing directory {remote_dir}: {e}")
        return

    # 末尾4桁が一致するファイルを見つける
    pattern = re.compile(rf".*{coordinate_id}\.{str(year)[-2:]}.pos$")
    for remote_file in files:
        match = pattern.search(remote_file)  # 一致するファイルを探す
        if match:
            local_file_path = os.path.join(local_directory, os.path.basename(remote_file)[-11:])
            download_file(ftp, remote_file, local_file_path)

def download_rinex_files(year, day_of_year, ftp, rinex_list, local_o_directory, local_n_directory):
    """ RINEXリストからFTPサーバーからファイルをダウンロードして解凍する """
    for rinex_id in rinex_list:
        remote_file_o_path = f"/data/G_2.11/{year}/{day_of_year}/{rinex_id}{day_of_year}0.{str(year)[-2:]}o.gz"
        local_file_o_path = os.path.join(local_o_directory, f"{rinex_id}{day_of_year}0.{str(year)[-2:]}o")
        
        remote_file_n_path = f"/data/G_2.11/{year}/{day_of_year}/{rinex_id}{day_of_year}0.{str(year)[-2:]}n.gz"
        local_file_n_path = os.path.join(local_n_directory, f"{rinex_id}{day_of_year}0.{str(year)[-2:]}n")
        
        # 観測ファイルをダウンロードして解凍
        download_and_extract_gz_file(ftp, remote_file_o_path, local_file_o_path)

        # ナビゲーションファイルをダウンロードして解凍
        download_and_extract_gz_file(ftp, remote_file_n_path, local_file_n_path)

def read_rinex_from_file(file_path):
    """ list.txtからRINEX名を抽出する """
    rinex_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) == 2:
                rinex_list.append(parts[1].strip())
    return rinex_list

def read_coordinate_from_file(file_path):
    """ list.txtから地点IDを抽出する """
    coordinate_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) == 2:
                coordinate_list.append(parts[1].strip())
    return coordinate_list

def main():
    subprocess.run(['rm', '-rf', '../data/obs/*'])
    subprocess.run(['rm', '-rf', '../data/nav/*'])
    subprocess.run(['rm', '-rf', '../data/pos/*'])
    year = 2016
    month = 4
    day = 15
    center_coordinate = (3.3730719293E+01,  1.3047677275E+02)
    day_of_year = date_to_day_of_year(year, month, day)
    process_pos_files(year,month, day, center_coordinate)

    ftp_host = "terras.gsi.go.jp"
    ftp_user = "goldrunner"
    ftp_pass = "Geomaster10"

    id_file_path = "../data/list.txt"  

    local_o_directory = "../data/obs"
    local_n_directory = "../data/nav"
    local_pos_directory = "../data/pos"

    # RINEX IDと地点IDのリストを取得
    rinex_list = read_rinex_from_file(id_file_path)
    coordinate_list = read_coordinate_from_file(id_file_path)

    # FTPサーバーに接続
    ftp = test_ftp_connection(ftp_host, ftp_user, ftp_pass)
    if ftp:
        # RINEXファイルをダウンロードして解凍
        download_rinex_files(year, day_of_year, ftp, rinex_list, local_o_directory, local_n_directory)
        
        # 指定された地点IDファイルをダウンロード
        for coordinate_id in coordinate_list:
            find_and_download_files(year, ftp, coordinate_id, local_pos_directory)
        
        # FTPセッションを終了
        ftp.quit()

if __name__ == "__main__":
    main()



