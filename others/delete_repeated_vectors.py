#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# --------------------------------------------------
# when concatenating adjacent S1 images using gamma,
# it may fail. Because the .par files have the same
# state vectors.
# --------------------------------------------------
# This script can delete the same state vectors and
# change some parameters.
# --------------------------------------------------
# leiyuan
# 2019-11-17

import re


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


if __name__ == "__main__":
    par1 = '20170315.iw3.slc.par-1'
    par2 = '20170315.iw3.slc.par-3'
    new_par = '20170315.iw3.slc.par-3'
    gen_new_par(par1, par2, new_par)
