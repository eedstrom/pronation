#!/usr/bin/evn python3
from __main__ import *
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import pinv

H=np.array([[1,0.]])
angle_v=np.array([])
for i in range(0,len(df0['gx'].values)-1):
    angle_a=np.append(angle_v,abs(df0['gx'].values[i+1])-abs(df0['gx'].values[i]))
R=np.array([np.var(df0['gx'].values)])
P=np.diag([R[0],(max(angle_a))**2])
z0=df0['gx'].values[0]
print(z0)
x=np.dot(pinv(H),z0)
print(x)
dt=np.mean(df0['dtime'].values)

def gyro_filter_helper(x, P, R, Q=0., dt=1.0):
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.x = np.array([x[0], x[1]])
    kf.F = np.array([[1., dt], [0., 1.]])
    kf.R *= R
    if np.isscalar(P):
        kf.P *= P
    else:
        kf.P[:] = P
    if np.isscalar(Q):
        kf.Q = Q_discrete_white_noise(dim=2, dt=dt, var=Q)
    else:
        kf.Q[:] = Q
    return kf

def run(x0=x, P=P, R=R, Q=0, dt=dt, track=None, zs=df0['gx'].values, count=0, do_plot=True, **kwargs):
    kf = gyro_filter_helper(x0, R=R, P=P, Q=Q, dt=dt)
    xs, cov = [], []
    for z in zs:
        kf.predict()
        kf.update(z)
        xs.append(kf.x)
        cov.append(kf.P)
    xs, cov = np.array(xs), np.array(cov)
    """if do_plot:
        plot_track(xs[:, 0], track, zs, cov, **kwargs)"""
    return xs, cov
#Ms, Ps = run()