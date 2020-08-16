#!/usr/bin/env python3
#-*- coding:utf-8 -*-
######################################################################
# Copy necessary files processed by stackSentinel.py for MintPy      #
# Lei Yuan, 2020                                                     #
######################################################################
import os
import shutil
import sys


def copy_files(stack_dir, save_dir):
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    # copy baselines
    baselines_src = os.path.join(stack_dir, 'baselines')
    baselines_dst = os.path.join(save_dir, 'baselines')
    if os.path.isdir(baselines_src):
        print('copy baselines...')
        shutil.copytree(baselines_src, baselines_dst)
        print('done.')

    # copy reference
    master_src = os.path.join(stack_dir, 'master')
    master_dst = os.path.join(save_dir, 'master')
    if os.path.isdir(master_src):
        print('copy reference...')
        shutil.copytree(master_src, master_dst)
        print('done.')

    # copy merged/geom_reference
    merged_dst = os.path.join(save_dir, 'merged')
    os.mkdir(merged_dst)
    geom_master_src = os.path.join(stack_dir, 'merged', 'geom_master')
    geom_master_dst = os.path.join(merged_dst, 'geom_master')
    if os.path.isdir(geom_master_src):
        print('copy merged/geom_reference...')
        shutil.copytree(geom_master_src, geom_master_dst)
        print('done.')

    # copy merged/interferograms
    files = [
        'filt_fine.cor', 'filt_fine.cor.vrt', 'filt_fine.cor.xml',
        'filt_fine.unw', 'filt_fine.unw.vrt', 'filt_fine.unw.xml',
        'filt_fine.unw.conncomp', 'filt_fine.unw.conncomp.vrt',
        'filt_fine.unw.conncomp.xml'
    ]
    interferograms_dst = os.path.join(merged_dst, 'interferograms')
    os.mkdir(interferograms_dst)
    interferograms_src = os.path.join(stack_dir, 'merged', 'interferograms')
    ifgs = os.listdir(interferograms_src)
    if ifgs:
        for ifg in ifgs:
            sys.stdout.write(
                f"\rcopy merged/interferograms {ifgs.index(ifg) + 1}/{len(ifgs)}",
            )
            sys.stdout.flush()
            ifg_src = os.path.join(interferograms_src, ifg)
            ifg_dst = os.path.join(interferograms_dst, ifg)
            os.mkdir(ifg_dst)
            for f in files:
                file_src = os.path.join(ifg_src, f)
                file_dst = os.path.join(ifg_dst, f)
                if os.path.isfile(file_src):
                    shutil.copy(file_src, file_dst)
                else:
                    print(f"{file_src} doesn't exist.")
        print('\ndone.')


if __name__ == "__main__":
    stack_dir = r'D:\sc1\isce_stack'
    save_dir = r'D:\sc1\isce_stack_test'
    copy_files(stack_dir, save_dir)
