#!/usr/bin/env python3
import scipy.io as scio
import numpy as np
import datetime
import os


def get_dates(days):
    dates = []
    for day in days:
        date = datetime.datetime.fromordinal(int(day)) + datetime.timedelta(days=int(day)%1) - datetime.timedelta(days = 366)
        date_str = date.strftime('%Y%m%d')
        dates.append(int(date_str))
    return np.asarray(dates, dtype='int64').reshape((1, -1))


os.chdir('/media/ly/file/StaMPS/YG/INSAR_20171229/SMALL_BASELINES')

data_ts = scio.loadmat('ps_plot_ts_v-do')
data_vel = scio.loadmat('ps_plot_v-do')

vel = data_vel['ph_disp']
lonlat = data_ts['lonlat']
ts = data_ts['ph_mm']
ts = ts - ts[:,0].reshape((-1, 1))
days = data_ts['day']
dates = get_dates(days)

num = np.arange(0, vel.shape[0]).reshape((-1, 1))
vel_out = np.hstack((num, lonlat, vel))
np.savetxt('vel.txt', vel_out, fmt='%4f')

dates_out = np.hstack((np.array([-1,-1,-1,-1]).reshape((1, -1)), dates))
tmp = np.hstack((vel_out, ts))
ts_out = np.vstack((dates_out, tmp))
np.savetxt('ts.txt', ts_out, fmt='%4f')