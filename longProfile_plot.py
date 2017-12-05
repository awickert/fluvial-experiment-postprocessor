import numpy as np
from matplotlib import pyplot as plt

plt.ion()

lp = np.genfromtxt('channel_centerline_points_0000000.csv', skip_header=1, delimiter=',')
# Distance downstream: lp[:,2]
x = lp[:,3] # x direction of flume
z = lp[:,5]

fig = plt.figure(figsize=(12,6))
ax = fig.add_subplot(1,1,1)
ax.plot(x, z, 'k-', linewidth=2)
ax.set_xlabel('Down-flume distance [m]', fontsize=24)
ax.set_ylabel('Elevation [m]', fontsize=24)
ax.tick_params(axis='both', which='major', labelsize=16)

plt.tight_layout()
