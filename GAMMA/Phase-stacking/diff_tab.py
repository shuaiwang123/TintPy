#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#####################################################
# write diff_tab for Phase-Stacking using GAMMA     #
# Author: Yuan Lei, 2020                            #
#####################################################
import argparse
import datetime
import glob
import os
import re
import sys

EXAMPLE = """Example:
  ./diff_tab.py /ly/stacking diff.int.sm.unw -o /ly/stacking
"""


def cmdline_parser():
    parser = argparse.ArgumentParser(
        description='write diff_tab for Phase-Stacking using GAMMA.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLE)

    parser.add_argument('ifg_dir', help='path of ifg directory.')
    parser.add_argument('extension',
                        help='filename extension of unwrapping file.')
    parser.add_argument('out_dir', help='path of directory saving diff_tab.')

    inps = parser.parse_args()

    return inps


def get_baseline(unw):
    name = os.path.basename(unw)
    dates = re.findall(r'\d{8}', name)
    date1 = datetime.datetime.strptime(dates[0], '%Y%m%d')
    date2 = datetime.datetime.strptime(dates[1], '%Y%m%d')
    baseline = (date2 - date1).days
    return baseline


def get_unws(ifg_dir, extension):
    unws = glob.glob(os.path.join(ifg_dir, '*/*' + extension))
    return unws


def write_diff_tab(unws, out_dir):
    diff_tab = os.path.join(out_dir, 'diff_tab')
    print('writing data to {}'.format(diff_tab))
    with open(diff_tab, 'w+') as f:
        for unw in unws:
            baseline = get_baseline(unw)
            f.write(f"{unw} {baseline}\n")
    print('all done, enjot it.')


def main():
    # get inputs
    inps = cmdline_parser()
    ifg_dir = os.path.abspath(inps.ifg_dir)
    extension = inps.extension
    out_dir = os.path.abspath(inps.out_dir)
    # get unws
    unws = get_unws(ifg_dir, extension)
    if len(unws) == 0:
        print('no unws in {}'.format(ifg_dir))
        sys.exit()
    # write diff_tab
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    write_diff_tab(unws, out_dir)


if __name__ == "__main__":
    main()
