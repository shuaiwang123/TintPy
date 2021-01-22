#!/usr/bin/env python3
#############################################################
# decompress all gacos tar.gz files to provided direcroty   #
# Copyright (c) 2021, Lei Yuan                              #
#############################################################
import argparse
import glob
import os
import sys
import tarfile

USAGE = """Example:
  ./prep_gacos.py /ly/gacos /ly/gacos
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description='decompress all gacos tar.gz files to provided direcroty.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=USAGE)

    parser.add_argument('gacos_dir', help='directory path of gacos tar.gz ')
    parser.add_argument('out_dir', help='directory path of decompressed gacos')

    inps = parser.parse_args()
    return inps


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


if __name__ == "__main__":
    inps = cmdline_parser()
    gacos_dir = os.path.abspath(inps.gacos_dir)
    out_dir = os.path.abspath(inps.out_dir)
    if not os.path.isdir(gacos_dir):
        print('cannot find directory {}'.format(gacos_dir))
        sys.exit()
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    un_tar_gz(gacos_dir, out_dir)
    print('all done, enjoy it.')
