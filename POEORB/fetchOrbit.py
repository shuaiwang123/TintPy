#!/usr/bin/env python3
##########################################################
# Download Sentinel-1 A/B precise orbits                 #
# Modified from https://github.com/isce-framework/isce2  #
##########################################################

import numpy as np
import requests
import re
import os
import argparse
import datetime
from html.parser import HTMLParser

server = 'https://scihub.copernicus.eu/gnss/'

orbitMap = [('precise', 'AUX_POEORB'),
            ('restituted', 'AUX_RESORB')]

datefmt = "%Y%m%dT%H%M%S"
queryfmt = "%Y-%m-%d"
queryfmt2 = "%Y/%m/%d/"

# Generic credentials to query and download orbit files
credentials = ('gnssguest', 'gnssguest')


def cmdLineParse():
    '''
    Command line parser.
    '''

    parser = argparse.ArgumentParser(
        description='Fetch orbits corresponding to given SAFE package')
    parser.add_argument('-i', '--input', dest='input', type=str, required=True,
                        help='Path of text or directory for getting images names')
    parser.add_argument('-o', '--output', dest='outdir', type=str, default='.',
                        help='Path to output directory')

    return parser.parse_args()


def FileToTimeStamp(safename):
    '''
    Return timestamp from SAFE name.
    '''
    safename = os.path.basename(safename)
    fields = safename.split('_')
    sstamp = []  # sstamp for getting SAFE file start time, not needed for orbit file timestamps

    try:
        tstamp = datetime.datetime.strptime(fields[-4], datefmt)
        sstamp = datetime.datetime.strptime(fields[-5], datefmt)
    except:
        p = re.compile(r'(?<=_)\d{8}')
        dt2 = p.search(safename).group()
        tstamp = datetime.datetime.strptime(dt2, '%Y%m%d')

    satName = fields[0]

    return tstamp, satName, sstamp


class MyHTMLParser(HTMLParser):

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.fileList = []
        self._url = url

    def handle_starttag(self, tag, attrs):
        for name, val in attrs:
            if name == 'href':
                if val.startswith("https://scihub.copernicus.eu/gnss/odata") and val.endswith(")/"):
                    pass
                else:
                    downloadLink = val.strip()
                    downloadLink = downloadLink.split("/Products('Quicklook')")
                    downloadLink = downloadLink[0] + downloadLink[-1]
                    self._url = downloadLink

    def handle_data(self, data):
        if data.startswith("S1") and data.endswith(".EOF"):
            self.fileList.append((self._url, data.strip()))


def download_file(url, outdir='.', session=None):
    '''
    Download file to specified directory.
    '''

    if session is None:
        session = requests.session()

    path = outdir
    print('Downloading URL: ', url)
    request = session.get(url, stream=True, verify=True, auth=credentials)

    try:
        val = request.raise_for_status()
        success = True
    except:
        success = False

    if success:
        with open(path, 'wb') as f:
            for chunk in request.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

    return success


def fileToRange(fname):
    '''
    Derive datetime range from orbit file name.
    '''

    fields = os.path.basename(fname).split('_')
    start = datetime.datetime.strptime(fields[-2][1:16], datefmt)
    stop = datetime.datetime.strptime(fields[-1][:15], datefmt)
    mission = fields[0]

    return (start, stop, mission)


def get_sentinel1_from_zip(images_path):
    """
    :param images_path: path of directory including Sentinel-1A/B (.zip)
    :return: sentinel-1 image name (list)
    """
    image_name = []
    date_mission = []
    files = os.listdir(images_path)
    for file in files:
        if re.search(r'S1\w{65}\.zip', file):
            dm = re.findall(r"\d{8}", file)[0] + file[0:3]
            if dm not in date_mission:
                date_mission.append(dm)
                image_name.append(file)
    return image_name


def get_sentinel1_from_text(text_path):
    """
    :param text_path: path of file including Sentinel-1A/B names
    :return: sentinel-1 image name (list)
    """
    image_name = []
    date_mission = []
    with open(text_path, encoding='utf-8') as file:
        content = file.read()
        names = re.findall(r"S1\w{65}", content)
        if names:
            for name in names:
                dm = re.findall(r"\d{8}", name)[0] + name[0:3]
                if dm not in date_mission:
                    date_mission.append(dm)
                    image_name.append(name)
    return image_name


def get_sentinel1(path):
    """
    :param path: path of directory or file
    :return: sentinel-1 image name
    """
    if os.path.isdir(path):
        return get_sentinel1_from_zip(path)
    else:
        return get_sentinel1_from_text(path)


if __name__ == '__main__':
    '''
    Main driver.
    '''

    inps = cmdLineParse()

    sentinel_names = get_sentinel1(inps.input)
    for name in sentinel_names:
        fileTS, satName, fileTSStart = FileToTimeStamp(name)
        print('Task: ' + str(sentinel_names.index(name) + 1) + '/' + str(len(sentinel_names)))
        print('Reference time: ', fileTS)
        print('Satellite name: ', satName)
        match = None
        session = requests.Session()

        for spec in orbitMap:
            oType = spec[0]
            delta = datetime.timedelta(days=1)
            timebef = (fileTS - delta).strftime(queryfmt)
            timeaft = (fileTS + delta).strftime(queryfmt)
            url = server + 'search?q=( beginPosition:[{0}T00:00:00.000Z TO {1}T23:59:59.999Z] AND endPosition:[{0}T00:00:00.000Z TO {1}T23:59:59.999Z] ) AND ( (platformname:Sentinel-1 AND filename:{2}_* AND producttype:{3}))&start=0&rows=100'.format(
                timebef, timeaft, satName, spec[1])

            success = False
            match = None

            try:
                r = session.get(url, verify=True, auth=credentials)
                r.raise_for_status()
                parser = MyHTMLParser(url)
                parser.feed(r.text)
                for resulturl, result in parser.fileList:
                    tbef, taft, mission = fileToRange(os.path.basename(result))
                    if (tbef <= fileTSStart) and (taft >= fileTS):
                        matchFileName = result
                        match = resulturl

                if match is not None:
                    success = True
            except:
                pass

            if success:
                break

        if match is not None:
            output = os.path.join(inps.outdir, matchFileName)
            res = download_file(match, output, session)
            if res is False:
                print('Failed to download URL: ', match)
        else:
            print('Failed to find {1} orbits for tref {0}'.format(
                fileTS, satName))
