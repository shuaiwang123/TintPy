# -*- coding:utf-8 -*-
import tarfile
import glob
import os


def un_tar_gz(tar_gz_dir, out_dir):
    tar_gz_files = glob.glob(os.path.join(tar_gz_dir, '*.tar.gz'))
    for tar_gz in tar_gz_files:
        file = tarfile.open(tar_gz)
        names = file.getnames()
        for name in names:
            path = os.path.join(out_dir, name)
            if not os.path.exists(path):
                file.extract(name, out_dir)
        file.close()


tar_gz_dir = r'/media/ly/文件/sc2/GACOS'
out_dir = r'/media/ly/文件/sc2/GACOS'
un_tar_gz(tar_gz_dir, out_dir)
