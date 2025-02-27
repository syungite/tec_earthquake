import ftplib
import os
import gzip
import shutil
import datetime
import subprocess

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
        
        # ファイルがダウンロードできなかった場合、空のファイルを作成
        if not os.path.exists(local_file_path):
            with open(local_file_path, 'wb') as empty_file:
                print(f"Created empty file: {local_file_path}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
      
def download_obs_and_nav(year, day_of_year, ftp, rinex_list, local_o_directory, local_n_directory, timelist):
    """ RINEXリストから.oファイルと.nファイルをダウンロードして解凍する """
    for rinex_id in rinex_list:
        if timelist:
            header = ""
            # 結合するデータを保存するリスト
            all_data_o = []
            all_data_n = []
            
            # timelistの各時刻に対して処理
            for time in timelist:
                # RINEXの観測データ（.oファイル）
                remote_file_o_path = f"/data/G_2.11/{year}/{day_of_year}/{rinex_id}{day_of_year}{time}.{str(year)[-2:]}o.gz"
                local_file_o_path = os.path.join(local_o_directory, 'tmp', f"{rinex_id}{day_of_year}{time}.{str(year)[-2:]}o")
                
                # RINEXのナビゲーションデータ（.nファイル）
                remote_file_n_path = f"/data/G_2.11/{year}/{day_of_year}/{rinex_id}{day_of_year}{time}.{str(year)[-2:]}n.gz"
                local_file_n_path = os.path.join(local_n_directory, 'tmp', f"{rinex_id}{day_of_year}{time}.{str(year)[-2:]}n")

                # 観測ファイルをダウンロードして解凍
                download_and_extract_gz_file(ftp, remote_file_o_path, local_file_o_path)

                # ナビゲーションファイルをダウンロードして解凍
                download_and_extract_gz_file(ftp, remote_file_n_path, local_file_n_path)         

                # 観測データのファイルが存在する場合に処理
                if os.path.exists(local_file_o_path):
                    with open(local_file_o_path, 'r') as file_o:
                        lines = file_o.readlines()
                        # 最初の行をヘッダーとして保存
                        if not header:
                            header = "".join(lines[:26])  # 最初の9行はヘッダー
                        # ヘッダー以降をデータとして追加
                        all_data_o.extend(lines[26:])
                
                # ナビゲーションデータのファイルが存在する場合に処理
                if os.path.exists(local_file_n_path):
                    with open(local_file_n_path, 'r') as file_n:
                        lines = file_n.readlines()
                        # 最初の行をヘッダーとして保存
                        if not header:
                            header = "".join(lines[:4])  # 最初の9行はヘッダー
                        # ヘッダー以降をデータとして追加
                        all_data_n.extend(lines[4:])
            
            # 結合したデータを新しいファイルに書き出す
            with open(os.path.join(local_o_directory, f"{rinex_id}{day_of_year}0.{str(year)[-2:]}o"), 'w') as output_o:
                output_o.write(header)
                output_o.writelines(all_data_o)
            
            with open(os.path.join(local_n_directory, f"{rinex_id}{day_of_year}0.{str(year)[-2:]}n"), 'w') as output_n:
                output_n.write(header)
                output_n.writelines(all_data_n)            

        else:
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

def download_and_process_data(year, month, day, timelist):
    #A. ftpを利用して国土地理院のデータのダウンロードを自動化
    subprocess.run("rm -f /home/blue/heki/data/obs/*", shell=True)
    subprocess.run("rm -f /home/blue/heki/data/obs/tmp/*", shell=True)
    subprocess.run("rm -f /home/blue/heki/data/nav/*", shell=True)
    subprocess.run("rm -f /home/blue/heki/data/nav/tmp/*", shell=True)


    day_of_year = date_to_day_of_year(year, month, day)

    ftp_host = "terras.gsi.go.jp"
    ftp_user = "goldrunner"
    ftp_pass = "Geomaster10"

    id_file_path = "../data/list.txt"  

    local_o_directory = "../data/obs"
    local_n_directory = "../data/nav"

    # RINEX IDと地点IDのリストを取得
    rinex_list = read_rinex_from_file(id_file_path)

    # FTPサーバーに接続
    ftp = test_ftp_connection(ftp_host, ftp_user, ftp_pass)
    if ftp:
        # RINEXファイルをダウンロードして解凍
        download_obs_and_nav(year, day_of_year, ftp, rinex_list, local_o_directory, local_n_directory, timelist)

        # FTPセッションを終了
        ftp.quit()

if __name__ == "__main__":
    year = 2011
    month = 3
    day = 11
    download_and_process_data(year, month, day)







