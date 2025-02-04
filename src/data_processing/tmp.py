import ftplib
import os
import gzip
import shutil
import datetime
import concurrent.futures

def date_to_day_of_year(year, month, day):
    date = datetime.datetime(year, month, day)
    return date.strftime("%j")

def test_ftp_connection(ftp_host, ftp_user, ftp_pass):
    """FTPサーバーに接続し、接続確認を行う"""
    try:
        ftp = ftplib.FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        print(f"Successfully connected to {ftp_host}")
        return ftp
    except ftplib.all_errors as e:
        print("FTP error:", e)
        return None

def download_and_extract_gz_file(ftp, remote_file_path, local_file_path):
    """ .gzファイルをダウンロードして解凍する """
    temp_gz_path = local_file_path + ".gz"
    try:
        with open(temp_gz_path, 'wb') as local_file:
            ftp.retrbinary(f"RETR {remote_file_path}", local_file.write)
        with gzip.open(temp_gz_path, 'rb') as gz_file:
            with open(local_file_path, 'wb') as extracted_file:
                shutil.copyfileobj(gz_file, extracted_file)
        os.remove(temp_gz_path)
        print(f"Downloaded and extracted: {local_file_path}")
    except ftplib.error_perm:
        print(f"Error downloading {remote_file_path}. Creating an empty file.")
        with open(local_file_path, 'wb') as empty_file:
            pass
    except Exception as e:
        print(f"Unexpected error: {e}")

def download_and_extract_gz_file_parallel(ftp, remote_paths, local_paths):
    """ 並列で .gz ファイルをダウンロードし、解凍する """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(download_and_extract_gz_file, ftp, r, l): (r, l) for r, l in zip(remote_paths, local_paths)}
        for future in concurrent.futures.as_completed(futures):
            remote_path, _ = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error in {remote_path}: {e}")

def download_obs_and_nav_parallel(year, day_of_year, ftp, rinex_list, local_o_directory, local_n_directory, timelist):
    """ RINEXファイルを並列ダウンロードし、解凍する """
    for rinex_id in rinex_list:
        remote_paths_o, local_paths_o, remote_paths_n, local_paths_n = [], [], [], []

        # timelistが空かどうかで処理を分ける
        if timelist:
            for time in timelist:
                remote_paths_o.append(f"/data/G_2.11/{year}/{day_of_year}/{rinex_id}{day_of_year}{time}.{str(year)[-2:]}o.gz")
                local_paths_o.append(os.path.join(local_o_directory, 'tmp', f"{rinex_id}{day_of_year}{time}.{str(year)[-2:]}o"))
                remote_paths_n.append(f"/data/G_2.11/{year}/{day_of_year}/{rinex_id}{day_of_year}{time}.{str(year)[-2:]}n.gz")
                local_paths_n.append(os.path.join(local_n_directory, 'tmp', f"{rinex_id}{day_of_year}{time}.{str(year)[-2:]}n"))
        else:
            remote_paths_o.append(f"/data/G_2.11/{year}/{day_of_year}/{rinex_id}{day_of_year}0.{str(year)[-2:]}o.gz")
            local_paths_o.append(os.path.join(local_o_directory, f"{rinex_id}{day_of_year}0.{str(year)[-2:]}o"))
            remote_paths_n.append(f"/data/G_2.11/{year}/{day_of_year}/{rinex_id}{day_of_year}0.{str(year)[-2:]}n.gz")
            local_paths_n.append(os.path.join(local_n_directory, f"{rinex_id}{day_of_year}0.{str(year)[-2:]}n"))

        # ダウンロードと解凍を並列で実行
        download_and_extract_gz_file_parallel(ftp, remote_paths_o, local_paths_o)
        download_and_extract_gz_file_parallel(ftp, remote_paths_n, local_paths_n)


def read_rinex_from_file(file_path):
    """ list.txtからRINEX名を抽出 """
    rinex_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) == 2:
                rinex_list.append(parts[1].strip())
    return rinex_list

def download_and_process_data(year, month, day, timelist):
    os.system("rm -f ../data/obs/* ../data/obs/tmp/* ../data/nav/* ../data/nav/tmp/*")
    day_of_year = date_to_day_of_year(year, month, day)
    ftp_host, ftp_user, ftp_pass = "terras.gsi.go.jp", "goldrunner", "Geomaster10"
    rinex_list = read_rinex_from_file("../data/list.txt")
    ftp = test_ftp_connection(ftp_host, ftp_user, ftp_pass)
    if ftp:
        download_obs_and_nav_parallel(year, day_of_year, ftp, rinex_list, "../data/obs", "../data/nav", timelist)
        ftp.quit()

if __name__ == "__main__":
    year, month, day = 2011, 3, 11
    timelist = ["00", "06", "12", "18"]  # 例: ダウンロードする時刻リスト
    download_and_process_data(year, month, day, timelist)
