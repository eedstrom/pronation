#!/usr/bin/env python3
from __main__ import *
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import pinv

H=np.array([[0,1.]])
angle_p=np.array([])
angle_a=np.array([])
"""for i in range(0,len(df0['gx'].values)-1):
    angle_a=np.append(angle_a,df0['gx'].values[i+1]-df0['gx'].values[i])"""
for i in range(0,len(df0['gx'].values)-1):
    if i==0:
        angle_p=np.append(angle_p,0)
        continue
    pos=angle_p[i-1]+df0['gx'].values[i]*df0['dtime'].values[i]/(10e3)
    angle_p=np.append(angle_p,pos)
gyro=np.delete(df0['gx'].values,len(df0['gx'].values)-1)
angle_v=np.delete(df0['gx'].values,len(df0['gx'].values)-1)
x=np.vstack((angle_v,angle_p))
#print(x[0])
#x=angle_p #print(angle_p)
#print(len(df0['gx'].values))
#print(len(angle_a))
R=np.array([np.var(angle_v)])
#print(R)
P=np.diag([R[0],np.var(angle_p)])
#print(max(angle_v), np.var(angle_v))
z0=angle_v[0]
#print(z0)
#print(z0)
x0=np.dot(pinv(H),z0)
#print(x0)
#print(x)
dt=np.mean(df0['dtime'].values)/(10e3)
#dt=df0['dtime'].values

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

def run(x0=x0, P=P, R=R, Q=0, dt=dt, track=None, zs=x[0], count=0, do_plot=True, **kwargs):
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
#Ms, Pss = run()
zs=df0['gx'].values
f=gyro_filter_helper(x0, R=R, P=P, Q=0, dt=dt)
#Xs, Ps, Xs_prior, Ps_prior = f.batch_filter(zs)
#print(Xs)
