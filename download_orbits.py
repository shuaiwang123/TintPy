# -*- coding:utf-8 -*-
import argparse
import datetime
import os
import re
import sys
import urllib
from subprocess import call

import requests
from bs4 import BeautifulSoup

URL_PREFIX = 'https://qc.sentinel1.eo.esa.int/aux_poeorb/'
HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36\
                    (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}


def date_operation(date, num=-1, flag='-'):
    """
    :param date: date of Sentinel-1
    :return: date of orbit (before Sentinel-1)
    """
    image_date = datetime.datetime.strptime(date, '%Y%m%d')
    delta = datetime.timedelta(days=num)
    orbit_date = image_date + delta
    return orbit_date.strftime(f'%Y{flag}%m{flag}%d')


def check_date_and_mission(date_and_mission):
    """
    check orbit date, delete date of no orbit data
    :param date_and_mission: sentinel-1 date and mission
    :return: no_orbit_date
    """
    d_m = date_and_mission
    no_orbit_date_and_mission = []
    now = datetime.datetime.now()
    for d in d_m[::-1]:
        orbit_date = datetime.datetime.strptime(date_operation(d[0:8]),
                                                '%Y-%m-%d')
        if (now - orbit_date).days <= 21:
            no_orbit_date_and_mission.append(d)
            date_and_mission.remove(d)
    return no_orbit_date_and_mission[::-1]


def get_sentinel1_date_and_mission_from_zip(images_path):
    """
    :param images_path: path of directory including Sentinel-1A/B (.zip)
    :return: date and mission (list)
    """
    images_date_and_mission = []
    files = os.listdir(images_path)
    for file in files:
        if re.search(r'S1\w{65}\.zip', file):
            date_and_mission = re.findall(r"\d{8}", file)[0] + file[0:3]
            if date_and_mission not in images_date_and_mission:
                images_date_and_mission.append(date_and_mission)
    return sorted(images_date_and_mission)


def get_sentinel1_date_and_mission_from_text(text_path):
    """
    :param text_path: path of file including Sentinel-1A/B names
    :return: date and mission (list)
    """
    images_date_and_mission = []
    with open(text_path, encoding='utf-8') as file:
        content = file.read()
        names = re.findall(r"S1\w{65}", content)
        if names:
            for name in names:
                date_and_mission = re.findall(r"\d{8}", name)[0] + name[0:3]
                if date_and_mission not in images_date_and_mission:
                    images_date_and_mission.append(date_and_mission)
    return sorted(images_date_and_mission)


def get_sentinel1_date_and_mission(path):
    """
    :param path: path of directory or file
    :return: date and mission
    """
    if os.path.isdir(path):
        return get_sentinel1_date_and_mission_from_zip(path)
    else:
        return get_sentinel1_date_and_mission_from_text(path)


def get_url(date_and_mission):
    """
    :param date_and_mission: date_mission (str)
    :return:
    """
    url = ''
    url_param = {}
    url_param['sentinel1__mission'] = date_and_mission[-3:]
    url_param['validity_start'] = date_operation(date_and_mission[0:8])
    url_param = urllib.parse.urlencode(url_param)
    url = URL_PREFIX + "?" + url_param
    html = requests.get(url, headers=HEADERS)
    if html.status_code == 200:  # 请求成功
        dom = BeautifulSoup(html.text, "html.parser")  # 解析请求到的数据
        eofs = re.findall(r"http.*EOF", str(dom))  # 查找下载链接
        if eofs:
            url = eofs[0]
        else:
            print('    cannot find http.*EOF from html.text')
    else:
        print('    error to get html')
    return url


def download_progress(blocknum, blocksize, totalsize):
    """
    :param blocknum: downloaded block number
    :param blocksize: block size
    :param totalsize: file size
    """
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
        print("\r    Downloaded: " + "#" * int(percent) + " %.2f%%" % percent,
              end=" ",
              flush=True)
    else:
        print("\r    Downloading: " + "#" * int(percent) + " %.2f%%" % percent,
              end=" ",
              flush=True)


def download_orbit(url, save_path):
    try:
        urllib.request.urlretrieve(url,
                                   os.path.join(save_path,
                                                url.split('/')[-1]),
                                   download_progress)
    except Exception as e :
        print(f'    {e}')


def add_to_idm(url, idm_path, save_path):
    try:
        call([
            idm_path, '/d', url, '/p', save_path, '/f',
            url.split('/')[-1], '/n', '/p'
        ])
        print("    Added to IDM")
    except Exception as e:
        print(f'    {e}')


def check_exist_orbits(save_path, all_date_and_mission):
    exist_date_and_mission = []
    orbits = [i for i in os.listdir(save_path) if i.endswith('.EOF')]
    orbits_path = [os.path.join(save_path, o) for o in orbits]
    path_date_and_mission = [
        date_operation(o[-19:-11], flag="") + o[:3] for o in orbits
    ]
    for e, p in zip(path_date_and_mission, orbits_path):
        file_size = os.path.getsize(p)
        if e in all_date_and_mission and file_size <= 4400000:
            all_date_and_mission.remove(e)
            exist_date_and_mission.append(e)
    return all_date_and_mission, exist_date_and_mission


def print_oneline_five(print_list, num=5):
    for dm in print_list:
        if (print_list.index(dm) + 1) % num == 0:
            print(dm)
        elif print_list.index(dm) == len(print_list) - 1:
            print(dm)
        else:
            print(dm, end=" ")


def usage():
    u = '''
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #
#                   Download Sentinel-1 A/B precise orbits                    #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# author : leiyuan                                                            #
# date   : 2020-04-01                                                         #
# version: 2.2.2                                                              #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Examples:                                                                   #
#   python download_orbits.py -i D:\\slc_zip -s D:\\orbits                      #
#   python download_orbits.py -i D:\\slc.txt -s D:\\orbits                      #
#   python download_orbits.py -i D:\\slc_zip -s D:\\orbits -d D:\\IDM\\IDMan.exe  #
#   python download_orbits.py -i D:\\slc.txt -s D:\\orbits -d D:\\IDM\\IDMan.exe  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    '''
    print(u)


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description='Download Sentinel-1 A/B precise orbits')
    parser.add_argument(
        '-i',
        dest='input_path',
        required=True,
        type=str,
        help='path of text or directory for getting images names')
    parser.add_argument('-s',
                        dest='save_path',
                        required=True,
                        type=str,
                        help='path of directory for saving orbits')
    parser.add_argument('-d',
                        dest='idm_path',
                        type=str,
                        help='path of IDMan.exe')
    return parser


def main():
    usage()
    # argument parser
    parser = cmdline_parser()
    args = parser.parse_args()
    # check path
    if args.idm_path and not os.path.exists(args.idm_path):
        print("Wrong path of IDMan.exe, please reset it!\n")
        sys.exit()
    if os.path.exists(args.input_path) and os.path.exists(args.save_path):
        date_and_mission = get_sentinel1_date_and_mission(args.input_path)
        print("Sentinel-1 A/B date_mission found: {}\n".format(
            len(date_and_mission)))
        print_oneline_five(date_and_mission)
        # check date_missions (now - date <= 21)
        no_orbit_date_and_mission = check_date_and_mission(date_and_mission)
        if len(no_orbit_date_and_mission) > 0:
            print(
                "\nSentinel-1 A/B date_missions are excluded (now - date <= 21): {}\n"
                .format(len(no_orbit_date_and_mission)))
            print_oneline_five(no_orbit_date_and_mission)
        else:
            print(
                "\nNo Sentinel-1 A/B date_missions is excluded (now - date <= 21)"
            )
        # check orbit files in saveing directory
        date_and_mission, exist_date_and_mission = check_exist_orbits(
            args.save_path, date_and_mission)
        if exist_date_and_mission:
            print("\nSentinel-1 A/B date_and_mission exist in save_path: {}\n".
                  format(len(exist_date_and_mission)))
            print_oneline_five(exist_date_and_mission)
        else:
            print(
                "\nNo Sentinel-1 A/B date_missions(orbits) exist in save_path"
            )
        if date_and_mission:
            print("\nSentinel-1 A/B orbit url need to crawl: {}\n".format(
                len(date_and_mission)))
            print_oneline_five(date_and_mission)
        else:
            print("\nAll orbits exist, nothing to download")
        num = 0
        if args.idm_path:
            if os.path.exists(args.idm_path):
                if date_and_mission:
                    for d_m in date_and_mission:
                        num += 1
                        print(f"\n{str(num).ljust(4)}Crawling: {d_m}")
                        url = get_url(d_m)
                        if url:
                            print(f"    Crawled: {url}")
                            add_to_idm(url, args.idm_path, args.save_path)
            else:
                print("\nWrong path of IDMan.exe, please reset it!\n")
                sys.exit()
        else:
            if date_and_mission:
                for d_m in date_and_mission:
                    num += 1
                    print(f"\n{str(num).ljust(4)}Crawling: {d_m}")
                    url = get_url(d_m)
                    if url:
                        print(f"    Crawled: {url}")
                        download_orbit(url, args.save_path)
    elif os.path.exists(
            args.input_path) and not os.path.exists(args.save_path):
        print("Wrong path of saving orbits, please reset it!")
    elif not os.path.exists(args.input_path) and os.path.exists(
            args.save_path):
        print(
            "Wrong path of text or directory for getting images names, please reset it!"
        )
    else:
        print("Both path are wrong(exclude IDMan path), please reset them!")
    print("")
    sys.exit()


if __name__ == '__main__':
    main()
