#!/usr/bin/env python3
###############################################
# read results processed by StaMPS SBAS or PS #
# Copyright (c) 2020, Lei Yuan                #
###############################################
import scipy.io as scio
import numpy as np
import datetime
import os


def get_dates(days):
    dates = []
    for day in days:
        date = datetime.datetime.fromordinal(int(day)) + datetime.timedelta(
            days=int(day) % 1) - datetime.timedelta(days=366)
        date_str = date.strftime('%Y%m%d')
        dates.append(int(date_str))
    return dates


def save_vel_ts(ts_mat, vel_mat, out_ts_file, out_vel_file):
    # load mat
    data_ts = scio.loadmat(ts_mat)
    data_vel = scio.loadmat(vel_mat)
    # get ts vel date lon lat
    vel = data_vel['ph_disp']
    lonlat = data_ts['lonlat']
    ts = data_ts['ph_mm']
    days = data_ts['day']
    # day --> date
    dates = get_dates(days)
    master_day = data_ts['master_day']
    master_date = get_dates(master_day)
    all_dates = sorted(dates + master_date)
    # get master index
    master_index = all_dates.index(master_date[0])
    master_disp = np.zeros((ts.shape[0], 1))
    # add master_disp to ts
    ts_before = ts[:, 0:master_index].reshape((-1, master_index))
    ts_after = ts[:, master_index:].reshape((ts.shape[0], -1))
    ts = np.hstack((ts_before, master_disp, ts_after))

    ts = ts - ts[:, 0].reshape((-1, 1))
    # save vel file
    num = np.arange(0, vel.shape[0]).reshape((-1, 1))
    vel_out = np.hstack((num, lonlat, vel))
    np.savetxt(out_vel_file, vel_out, fmt='%4f')
    # save ts file
    all_dates = np.asarray(all_dates, dtype='int64').reshape((1, -1))
    dates_out = np.hstack((np.array([-1, -1, -1, -1]).reshape(
        (1, -1)), all_dates))
    tmp = np.hstack((vel_out, ts))
    ts_out = np.vstack((dates_out, tmp))
    np.savetxt(out_ts_file, ts_out, fmt='%4f')


os.chdir('/media/ly/file/StaMPS/HY/stamps_oneyear_ps/INSAR_20170619')
save_vel_ts('ps_plot_ts_v-do', 'ps_plot_v-do', './../ts1.txt', './../vel1.txt')
