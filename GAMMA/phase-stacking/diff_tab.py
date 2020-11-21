#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#####################################################
# write diff_tab for stacking using GAMMA           #
# Author: Yuan Lei, 2020                            #
#####################################################
import os
import glob
import datetime
import re


def get_baseline(unw):
    name = os.path.basename(unw)
    dates = re.findall('\d{8}', name)
    date1 = datetime.datetime.strptime(dates[0], '%Y%m%d')
    date2 = datetime.datetime.strptime(dates[1], '%Y%m%d')
    baseline = (date2 - date1).days
    return baseline


def write_diff_tab(ifg_dir, diff_tab_path):
    unws = glob.glob(os.path.join(ifg_dir, '*/*.unw'))
    with open(diff_tab_path, 'w+') as f:
        for unw in unws:
            baseline = get_baseline(unw)
            f.write(f"{unw} {baseline}\n")


ifg_dir = '/media/ly/文件/gamma_stack/gamma_stack/interferograms'
diff_tab_path = '/media/ly/文件/gamma_stack/diff_tab'
write_diff_tab(ifg_dir, diff_tab_path)
