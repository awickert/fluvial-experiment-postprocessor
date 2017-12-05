import numpy as np
from matplotlib import pyplot as plt
import glob

plt.ion()

#lp = np.genfromtxt('channel_centerline_points_0000000.csv', skip_header=1, delimiter=',')
# Distance downstream: lp[:,2]

LPfiles = sorted(glob.glob('channel_centerline_points_*.csv'))

fig = plt.figure(figsize=(12,6))
ax = fig.add_subplot(1,1,1)
for i in range (len(LPfiles)):

  LPfile = LPfiles[i]
  if i > 0:
      LPfile_prev = LPfiles[i-1]
  else:
      LPfile_prev = None

  ax.cla()

  lp = np.genfromtxt(LPfile, delimiter=',', skip_header=1)

  x = lp[:,3] # x direction of flume
  z = lp[:,5]
  z[1:][x[1:]<x[:-1]] = np.nan
  x[1:][x[1:]<x[:-1]] = np.nan

  ax.plot(x, z, 'k-', linewidth=2)
  ax.set_xlabel('Down-flume distance [m]', fontsize=24)
  ax.set_ylabel('Elevation [m]', fontsize=24)
  ax.tick_params(axis='both', which='major', labelsize=16)
  ax.set_xlim(0,4)
  ax.set_ylim(0,0.5)

  plt.tight_layout()
  
  plt.pause(0.1)
