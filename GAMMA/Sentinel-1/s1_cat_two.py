#!/usr/bin/env python3
#######################################################
# Concatenate adjacent Sentinel-1 TOPS SLC images     #
# Copyright (c) 2020, Lei Yuan                        #
#######################################################

import os
import glob
import argparse
import re


EXAMPLE = """
[Note:This script only concatenates adjacent SLC processed by zip2slc_all.py]
./s1_cat_two.py slc 1 slc
./s1_cat_two.py slc 1 slc --rlks 8 --alks 2
"""



def cmdline_parse():
    parser = argparse.ArgumentParser(
        description='Concatenate adjacent Sentinel-1 TOPS SLC images', formatter_class=argparse.RawTextHelpFormatter, epilog=EXAMPLE)
    parser.add_argument('slc_dir', help='slc need to concatenate')
    parser.add_argument('iw_num', help='number of IW (1 or 2 or 3)', type=int)
    parser.add_argument(
        'save_dir', help='directory of saving concatenated slc')
    parser.add_argument(
        '--rlks',
        help='range looks for generating amplitude image (default: 20)',
        type=int,
        default=20)
    parser.add_argument(
        '--alks',
        help='azimuth looks for generating amplitude image (default: 5)',
        type=int,
        default=5)
    inps = parser.parse_args()
    return inps


def get_state_vector(file_path):
    '''
    get all state_vectors from .par file
    '''
    state_vector = []
    temp = []
    with open(file_path) as f:
        for line in f:
            if line.startswith('state_vector_position_') or \
                    line.startswith('state_vector_velocity_'):
                temp.append(line)
    for s in temp:
        line = re.split(r'\s+', s)
        state_vector.append(line[1:4])
    return state_vector


def get_nonrepeated_state_vector(state_vector_1, state_vector_2):
    '''
    compare two state_vectors, get nonrepeated state_vectors
    '''
    nonrepeated_state_vector = []
    index = 1
    for sv in state_vector_2:
        if sv not in state_vector_1:
            nonrepeated_state_vector.append(sv)
    for i in range(len(state_vector_2)):
        if state_vector_2[i] == nonrepeated_state_vector[0]:
            index = i
    return nonrepeated_state_vector, index


def get_time_of_first_state_vector(file_path):
    '''
    get time_of_first_state_vector from .par file
    '''
    time_of_first_state_vector = ''
    with open(file_path) as f:
        for line in f:
            if line.startswith('time_of_first_state_vector'):
                time_of_first_state_vector = re.split(r'\s+', line)[1]
    return time_of_first_state_vector


def get_content(file_path):
    '''
    get content before the line of 'number_of_state_vectors'
    '''
    content = ''
    with open(file_path) as f:
        for line in f:
            if not line.startswith('number_of_state_vectors'):
                content += line
            else:
                break
    return content


def gen_new_par(par1, par2, new_par):
    state_vector_1 = get_state_vector(par1)
    state_vector_2 = get_state_vector(par2)
    nonrepeated_state_vector, index = get_nonrepeated_state_vector(
        state_vector_1, state_vector_2)
    number_of_state_vectors = int(len(nonrepeated_state_vector)/2)

    # calculate the new time_of_first_state_vector
    time_of_first_state_vector = get_time_of_first_state_vector(par2)
    time_of_first_state_vector = float(
        time_of_first_state_vector) + index/2*10
    time_of_first_state_vector = str(time_of_first_state_vector)+'00000'

    # get content before 'number_of_state_vectors'
    content = get_content(par2)

    # write .par file
    with open(new_par, 'w+') as f:
        f.write(content)
        f.write('number_of_state_vectors:' +
                str(int(len(nonrepeated_state_vector)/2)).rjust(21, ' ')+'\n')
        f.write('time_of_first_state_vector:' +
                time_of_first_state_vector.rjust(18, ' ')+'   s'+'\n')
        f.write('state_vector_interval:              10.000000   s'+'\n')
        nr = nonrepeated_state_vector
        for i in range(number_of_state_vectors):
            f.write('state_vector_position_'+str(i+1)+':'+nr[i*2][0].rjust(
                15, ' ')+nr[i*2][1].rjust(16, ' ')+nr[i * 2][2].rjust(16, ' ')+'   m   m   m'+'\n')
            f.write('state_vector_velocity_'+str(i+1)+':'+nr[i*2+1][0].rjust(
                15, ' ')+nr[i*2+1][1].rjust(16, ' ')+nr[i*2+1][2].rjust(16, ' ')+'   m/s m/s m/s'+'\n')


def read_gamma_par(par_file, keyword):
    value = ''
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if l.count(keyword) == 1:
                tmp = l.split(':')
                value = tmp[1].strip()
    return value


def get_time_and_direction(par_file):
    with open(par_file, 'r') as f:
        for l in f.readlines():
            if 'start_time' in l:
                start_time = l.strip().split()[1]
            if 'heading' in l:
                heading = l.strip().split()[1]
    heading = float(heading)
    start_time = float(start_time)
    if heading > -180 and heading < -90:
        direction = 'DES'
    else:
        direction = 'ASC'

    return start_time, direction


def get_date_for_cat(slc_dir):
    dates = []
    for i in os.listdir(slc_dir):
        if re.search(r'^\d{8}-\d{1}$', i):
            dates.append(i[0:8])
    dates = set(j for j in dates if dates.count(j) == 2)
    return sorted(list(dates))


def cat_slc(slc_dir, save_dir, iw_num, rlks, alks):
    iw = str(iw_num)
    dates = get_date_for_cat(slc_dir)
    for date in dates:
        cat_dir = os.path.join(save_dir, date)
        if not os.path.isdir(cat_dir):
            os.mkdir(cat_dir)

        slc1 = os.path.join(slc_dir, date + '-1', date + '.iw' + iw + '.slc')
        slc_par1 = os.path.join(slc_dir, date + '-1',
                                date + '.iw' + iw + '.slc.par')
        tops_par1 = os.path.join(slc_dir, date + '-1',
                                 date + '.iw' + iw + '.slc.tops_par')
        slc2 = os.path.join(slc_dir, date + '-2', date + '.iw' + iw + '.slc')
        slc_par2 = os.path.join(slc_dir, date + '-2',
                                date + '.iw' + iw + '.slc.par')
        tops_par2 = os.path.join(slc_dir, date + '-2',
                                 date + '.iw' + iw + '.slc.tops_par')
        slc = os.path.join(cat_dir, date + '.iw' + iw + '.slc')
        slc_par = os.path.join(cat_dir, date + '.iw' + iw + '.slc.par')
        tops_par = os.path.join(cat_dir, date + '.iw' + iw + '.slc.tops_par')

        # backup par file
        call_str = f"cp {slc_par1} {slc_par1 + '-copy'}"
        os.system(call_str)
        call_str = f"cp {slc_par2} {slc_par2 + '-copy'}"
        os.system(call_str)

        # get image start_time and direction
        start_time1, direction1 = get_time_and_direction(slc_par1)
        start_time2, direction2 = get_time_and_direction(slc_par2)

        des = (direction1 == 'DES') and (start_time1 > start_time2)
        asc = (direction1 == 'ASC') and (start_time1 > start_time2)
        if asc or des:
            tmp1 = slc1
            slc1 = slc2
            slc2 = tmp1

            tmp2 = slc_par1
            slc_par1 = slc_par2
            slc_par2 = tmp2

            tmp3 = tops_par1
            tops_par1 = tops_par2
            tops_par2 = tmp3

        # delete repeated vectors
        gen_new_par(slc_par1, slc_par2, slc_par2)

        # write catlist
        os.chdir(cat_dir)
        call_str = f"echo {slc1} {slc_par1} {tops_par1} > catlist1"
        os.system(call_str)
        call_str = f"echo {slc2} {slc_par2} {tops_par2} > catlist2"
        os.system(call_str)
        call_str = f"echo {slc} {slc_par} {tops_par} > catlist"
        os.system(call_str)

        # concatenate adjacent Sentinel-1 TOPS SLC images
        call_str = "SLC_cat_S1_TOPS.TOPS catlist1 catlist2 catlist"
        os.system(call_str)

        # generate amplitude image
        width = read_gamma_par(slc_par, 'range_samples:')
        if width:
            bmp = slc + '.bmp'
            call_str = f"rasSLC {slc} {width} 1 0 {rlks} {alks} 1. .35 1 0 0 {bmp}"
            os.system(call_str)

        # delete catlist, catlist1, catlist2
        os.remove('catlist')
        os.remove('catlist1')
        os.remove('catlist2')


def main():
    inps = cmdline_parse()
    slc_dir = inps.slc_dir
    slc_dir = os.path.abspath(slc_dir)
    iw_num = inps.iw_num
    save_dir = inps.save_dir
    save_dir = os.path.abspath(save_dir)
    rlks = inps.rlks
    alks = inps.alks
    cat_slc(slc_dir, save_dir, iw_num, rlks, alks)
    print('\nall done, enjoy it.\n')


if __name__ == "__main__":
    main()
