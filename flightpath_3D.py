import numpy as np
import matplotlib.pyplot as plt
import lib.read_csv as readcsv
from mpl_toolkits.mplot3d import Axes3D

def generate_3D_flightpath(csv_path):
    mocap_data = readcsv.read_csv(csv_path, "FS2mocap")
    x = mocap_data[:, 1]
    y = mocap_data[:, 2]
    z = mocap_data[:, 3]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x[0], y[0], z[0], color='red', s=20, label='Starting Point')
    ax.scatter(x[-1], y[-1], z[-1], color='red', s=20, label='Ending Point')

    # Plot the line
    ax.plot(x, y, z)

    ax.set_xticks([-5,-4,-3,-2,-1,0,1,2,3,4,5])
    ax.set_xticklabels([-5,-4,-3,-2,-1,0,1,2,3,4,5])

    ax.set_yticks([-5,-4,-3,-2,-1,0,1,2,3,4,5])
    ax.set_yticklabels([-5,-4,-3,-2,-1,0,1,2,3,4,5])

    ax.set_zticks([0,1,2,3,4,5,6,7,8,9,10])
    ax.set_zticklabels([0,1,2,3,4,5,6,7,8,9,10])


    # Optional: Customize the plot
    ax.set_xlabel('Length (m)')
    ax.set_ylabel('Width (m)')
    ax.set_zlabel('Height (m)')
    ax.set_title('3D Line Graph')

    # Show the plot
    plt.show()

print(generate_3D_flightpath("/Users/rishithprathi/Downloads/t2radar/data/FS2mocap25.csv"))