#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import argparse
import datetime
import os
import re
import sys
import urllib

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


def get_urls(date_and_mission):
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
            print('Cannot find http.*EOF from html.text')
    else:
        print('Error to get html')
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
        print("\rDownloaded: " + "#" * int(percent / 2) + " %.2f%%" % percent,
              end=" ",
              flush=True)
    else:
        print("\rDownloading: " + "#" * int(percent / 2) + " %.2f%%" % percent,
              end=" ",
              flush=True)


def download_orbits(url, save_path):
    abs_path = os.path.join(save_path, url.split('/')[-1])
    try:
        urllib.request.urlretrieve(url, abs_path, download_progress)
    except Exception as e:
        print(f'{e}')


def check_exist_orbits(save_path, all_date_and_mission):
    exist_date_and_mission = []
    tmp = all_date_and_mission
    orbits = [i for i in os.listdir(save_path) if i.endswith('.EOF')]
    orbits_path = [os.path.join(save_path, o) for o in orbits]
    date_and_mission = [
        date_operation(o[-19:-11], flag="") + o[:3] for o in orbits
    ]
    for e, p in zip(date_and_mission, orbits_path):
        file_size = os.path.getsize(p)
        if e in tmp and file_size > 4400000:
            all_date_and_mission.remove(e)
            exist_date_and_mission.append(e)
    return all_date_and_mission, exist_date_and_mission


def print_oneline_five(print_list, num=5):
    """
    :param print_list: list for print
    :param num: num of each line
    """
    for dm in print_list:
        if (print_list.index(dm) + 1) % num == 0:
            print(dm)
        elif print_list.index(dm) == len(print_list) - 1:
            print(dm)
        else:
            print(dm, end=" ")


INTRODUCTION = '''
########################################################################
    Copy Right(c): 2019-2020, Yuan Lei
   
    Download Sentinel-1 A/B precise orbits.

'''

EXAMPLE = '''
    Examples:
        python download_orbits.py -i . -s .
        python download_orbits.py -i D:\\test -s D:\\test
        python download_orbits.py -i D:\\test\\test.txt -s D:\\test
########################################################################
'''


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description='Download Sentinel-1 A/B precise orbits',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=INTRODUCTION + '\n' + EXAMPLE)
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
    return parser


def main():
    # argument parser
    parser = cmdline_parser()
    args = parser.parse_args()
    # check path
    exist_i = os.path.exists(args.input_path)
    exist_s = os.path.exists(args.save_path)
    if exist_i and exist_s:
        date_and_mission = get_sentinel1_date_and_mission(args.input_path)
        if len(date_and_mission):
            print("Sentinel-1 A/B date_mission found: {}\n".format(
                len(date_and_mission)))
            print_oneline_five(date_and_mission)
            # check date_missions (now - date <= 21)
            no_orbit_date_and_mission = check_date_and_mission(
                date_and_mission)
            if len(no_orbit_date_and_mission) > 0:
                print(
                    "\nSentinel-1 A/B date_missions are excluded (now - date <= 21): {}\n"
                    .format(len(no_orbit_date_and_mission)))
                print_oneline_five(no_orbit_date_and_mission)
            else:
                print(
                    "\nNo Sentinel-1 A/B date_missions is excluded (now - date <= 21)"
                )
            # check orbit files if exist in saving directory
            date_and_mission, exist_date_and_mission = check_exist_orbits(
                args.save_path, date_and_mission)
            if exist_date_and_mission:
                print(
                    "\nSentinel-1 A/B date_and_mission exist in save_path: {}\n"
                    .format(len(exist_date_and_mission)))
                print_oneline_five(exist_date_and_mission)
            else:
                print(
                    "\nNo Sentinel-1 A/B date_missions(orbits) exist in save_path"
                )
            if date_and_mission:
                print("\nSentinel-1 A/B orbit urls need to crawl: {}\n".format(
                    len(date_and_mission)))
                print_oneline_five(date_and_mission)
            else:
                print("\nAll orbits exist, nothing to download")
            num = 0
            if date_and_mission:
                for d_m in date_and_mission:
                    num += 1
                    tmp = str(num) + '.'
                    print(f"\n{tmp}Crawling: {d_m}")
                    url = get_urls(d_m)
                    if url:
                        print(f"Crawled: {url}")
                        download_orbits(url, args.save_path)
        else:
            print("Nothing found, please check path!")
    elif exist_i and not exist_s:
        print("Wrong path of saving orbits, please reset it!")
    elif not exist_i and exist_s:
        print(
            "Wrong path of text or directory for getting images names, please reset it!"
        )
    else:
        print("Wrong path of all, please reset them!")
    print("")
    sys.exit()


if __name__ == '__main__':
    main()
