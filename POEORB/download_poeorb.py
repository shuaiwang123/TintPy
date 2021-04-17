#!/usr/bin/env python3
# -*- coding:utf-8 -*-
####################################################
# Download Sentinel-1 A/B precise orbits from ASF  #
# Copyright (c) 2021, Lei Yuan                     #
####################################################
import argparse
import datetime
import os
import re
import sys
import urllib.request
import subprocess
import time


def date_operation(date, num=-1, flag='-'):
    """
    :param date: date of Sentinel-1
    :return: date of orbit (before Sentinel-1)
    """
    image_date = datetime.datetime.strptime(date, '%Y%m%d')
    delta = datetime.timedelta(days=num)
    orbit_date = image_date + delta
    return orbit_date.strftime(f'%Y{flag}%m{flag}%d')


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


def get_all_poeorbs(url, username, password):
    """
    :param url: 
    :param username: 
    :param password: 
    :return: poeorbs
    """
    print('Getting all poeorb urls')
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, username, password)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)
    response = opener.open(url)
    content = response.read().decode("UTF-8")
    poeorb_urls = re.findall(r"S1.*EOF", content)
    poeorb_urls = [url + i for i in poeorb_urls]
    print('Done\n')
    return poeorb_urls


def get_needed_poeorbs(date_and_mission, all_poeorb_urls):
    """
    :param url: 
    :param username: 
    :param password: 
    :return: poeorbs
    """
    needed_poeorb_urls = []
    for dm in date_and_mission:
        date = 'V' + date_operation(dm[0:8], num=-1, flag='')
        mission = dm[-3:]
        for url in all_poeorb_urls:
            if date in url and mission in url:
                needed_poeorb_urls.append(url)
    num = len(needed_poeorb_urls)
    if num:
        print('Need to download {} poeorbs\n'.format(num))
    return needed_poeorb_urls


def download_poeorb(poeorb_url, username, password):
    """
    :param poeorb_url: 
    :param username: 
    :param password: 
    """
    cmd_str = "wget --http-user={} --http-password={} -c {}".format(
        username, password, poeorb_url)
    # os.system(cmd_str)
    print('Downloading')
    time_start = time.time()
    p = subprocess.run(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time_delta = time.time() - time_start
    if p.returncode == 0:
        print('Finished in {} seconds'.format(int(time_delta)))
    else:
        print('Error')


EXAMPLE = '''Note for Windows user: 
You must install [wget] tool and add wget path to System variable.
'''


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description='Download Sentinel-1 A/B precise orbit urls from ASF.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument(
        'input_path',
        type=str,
        help='path of text or directory for getting images names')
    parser.add_argument('--out_dir',
                        type=str,
                        default='.',
                        help='directory path for saving poeorbs')
    parser.add_argument(
        '--username',
        type=str,
        default='leiyuan',
        help='username for login https://urs.earthdata.nasa.gov/')
    parser.add_argument(
        '--password',
        type=str,
        default='PVmg2NeCSLatf3v',
        help='password for login https://urs.earthdata.nasa.gov/')
    return parser


def main():
    # argument parser
    parser = cmdline_parser()
    args = parser.parse_args()
    input_path = args.input_path
    out_dir = os.path.abspath(args.out_dir)
    username = args.username
    password = args.password
    # check path
    if not os.path.exists(input_path):
        print('cannot find {}'.format(input_path))
        sys.exit()
    if not os.path.isdir(out_dir):
        print('cannot find {}'.format(out_dir))
        sys.exit()
    # get date_and_mission
    date_and_mission = get_sentinel1_date_and_mission(input_path)
    if date_and_mission:
        num = 0
        url = "https://s1qc.asf.alaska.edu/aux_poeorb/"
        all_poeorb_urls = get_all_poeorbs(url, username, password)
        needed_poeorb_urls = get_needed_poeorbs(date_and_mission,
                                                all_poeorb_urls)
        for url in needed_poeorb_urls:
            num += 1
            print(f"{num}. {url}")
            os.chdir(out_dir)
            download_poeorb(url, username, password)
    else:
        print("Nothing found, please check path!")


if __name__ == '__main__':
    main()
