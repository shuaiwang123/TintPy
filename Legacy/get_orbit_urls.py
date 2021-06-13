#!/usr/bin/env python3
# -*- coding:utf-8 -*-
####################################################
# Get Sentinel-1 A/B precise orbit urls from ASF.  #
# Copyright (c) 2021, Lei Yuan                     #
####################################################
import argparse
import datetime
import os
import re
import sys


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


def get_urls_from_html(html):
    all_urls = []
    with open(html, 'r', encoding='utf-8') as f:
        content = f.readlines()
        for line in content:
            url = re.findall(r'https://s1qc.asf.alaska.edu/aux_poeorb.*EOF',
                             line)
            if url:
                all_urls.append(url[0])
    return all_urls


def get_needed_urls(date_and_mission, all_urls):
    urls = []
    for dm in date_and_mission:
        date = 'V' + date_operation(dm[0:8], num=-1, flag='')
        mission = dm[-3:]
        for url in all_urls:
            if date in url and mission in url:
                urls.append(url)
    return urls


EXAMPLE = '''Steps for getting orbit urls:
  1. open link [https://s1qc.asf.alaska.edu/aux_poeorb/]
  2. save as html file (eg: index.html)
  3. python get_orbit_urls.py /ly/zips index.html
'''


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description='Get Sentinel-1 A/B precise orbit urls from ASF.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)
    parser.add_argument(
        'input_path',
        type=str,
        help='path of text or directory for getting images names')
    parser.add_argument('html',
                        type=str,
                        help='html file including all orbit urls')
    return parser


def main():
    # argument parser
    parser = cmdline_parser()
    args = parser.parse_args()
    input_path = args.input_path
    html = args.html
    # check path
    if not os.path.exists(input_path):
        print('cannot find {}'.format(input_path))
        sys.exit()
    if not os.path.isfile(html):
        print('cannot find {}'.format(html))
        sys.exit()
    # get date_and_mission
    date_and_mission = get_sentinel1_date_and_mission(input_path)
    if date_and_mission:
        num = 0
        all_urls = get_urls_from_html(html)
        needed_urls = get_needed_urls(date_and_mission, all_urls)
        for url in needed_urls:
            num += 1
            print(f"{num}. {url}")
    else:
        print("Nothing found, please check path!")


if __name__ == '__main__':
    main()
