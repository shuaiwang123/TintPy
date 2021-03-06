import os
import glob
import datetime
import zipfile
import re
import shutil


def unzip_orbits(src_dir):
    orbits = glob.glob(os.path.join(src_dir, 'S1*.EOF'))
    for orbit in orbits:
        zip_name = orbit + '.zip'
        name = os.path.split(orbit)[1]
        with zipfile.ZipFile(zip_name, 'w') as f:
            os.chdir(src_dir)
            f.write(name)


def get_info(orbit_name):
    info = []
    info.append(orbit_name[0:3])
    dates = re.findall(r'\d{8}', orbit_name)
    date = datetime.datetime.strptime(dates[1], '%Y%m%d')
    image_date = date + datetime.timedelta(1)
    year = image_date.year
    info.append(str(year))
    month = image_date.month
    if month < 10:
        info.append('0' + str(month))
    else:
        info.append(str(month))
    return info


def mv_zips(src_dir, dst_dir):
    zips = glob.glob(os.path.join(src_dir, 'S1*.EOF.zip'))
    for zip in zips:
        name = os.path.split(zip)[1]
        mission, year, month = get_info(name)
        mission_dir = os.path.join(dst_dir, mission)
        if not os.path.isdir(mission_dir):
            os.mkdir(mission_dir)

        year_dir = os.path.join(mission_dir, year)
        if not os.path.isdir(year_dir):
            os.mkdir(year_dir)

        mv_dir = os.path.join(year_dir, month)
        if not os.path.isdir(mv_dir):
            os.mkdir(mv_dir)

        dst_file = os.path.join(mv_dir, name)
        if not os.path.isfile(dst_file):
            shutil.move(zip, mv_dir)


def run(src_dir, dst_dir):
    unzip_orbits(src_dir)
    mv_zips(src_dir, dst_dir)


src_dir = r'D:\SNAP2STAMPS\test\orbits'
dst_dir = r'D:\SNAP2STAMPS\test\orbits'
run(src_dir, dst_dir)
