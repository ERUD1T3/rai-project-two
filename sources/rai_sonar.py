# read measurements from the robot and print them to the console
# -*- encoding: UTF-8 -*-
# Before running this command please check your PYTHONPATH is set correctly to the folder of your pynaoqi sdk.
from naoqi import ALProxy 
from nao_conf import *
import numpy as np
from math import factorial

# Set the IP address of your NAO.
ip = IP

# Connect to ALSonar module.
sonarProxy = ALProxy("ALSonar", ip, 9559)

# Subscribe to sonars, this will launch sonars (at hardware level) and start data acquisition.
sonarProxy.subscribe("myApplication")

#Now you can retrieve sonar data from ALMemory.
memoryProxy = ALProxy("ALMemory", ip, 9559)

def read_sonar(n_samples = 20, n_cleanups=1):
    '''Read sonar values print them to the console.'''

    left_sonar_echos = [
        "Device/SubDeviceList/US/Left/Sensor/Value",
        # "Device/SubDeviceList/US/Left/Sensor/Value1",
        # "Device/SubDeviceList/US/Left/Sensor/Value2",
        # "Device/SubDeviceList/US/Left/Sensor/Value3",
        # "Device/SubDeviceList/US/Left/Sensor/Value4",
        # "Device/SubDeviceList/US/Left/Sensor/Value5",
        # "Device/SubDeviceList/US/Left/Sensor/Value6",
        # "Device/SubDeviceList/US/Left/Sensor/Value7",
        # "Device/SubDeviceList/US/Left/Sensor/Value8",
        # "Device/SubDeviceList/US/Left/Sensor/Value9",
    ]

    right_sonar_echos = [
        "Device/SubDeviceList/US/Right/Sensor/Value",
        # "Device/SubDeviceList/US/Right/Sensor/Value1",
        # "Device/SubDeviceList/US/Right/Sensor/Value2",
        # "Device/SubDeviceList/US/Right/Sensor/Value3",
        # "Device/SubDeviceList/US/Right/Sensor/Value4",
        # "Device/SubDeviceList/US/Right/Sensor/Value5",
        # "Device/SubDeviceList/US/Right/Sensor/Value6",
        # "Device/SubDeviceList/US/Right/Sensor/Value7",
        # "Device/SubDeviceList/US/Right/Sensor/Value8",
        # "Device/SubDeviceList/US/Right/Sensor/Value9",
    ]

    left_sonar_values = []
    right_sonar_values = []

    # read n samples
    for _ in range(n_samples):
        # read raw sonar values
        left_sonar_values.append(memoryProxy.getData(left_sonar_echos[0]))
        right_sonar_values.append(memoryProxy.getData(right_sonar_echos[0]))

    # remove outliers 
    # for _ in range(n_cleanups):
    #     # find mean of all sonar echos for left and right
    #     left_sonar_mean = sum(left_sonar_values) / len(left_sonar_values)
    #     right_sonar_mean = sum(right_sonar_values) / len(right_sonar_values)
    #     # find standard deviation of all sonar echos for left and right
    #     left_sonar_std = (sum([(value - left_sonar_mean) ** 2 for value in left_sonar_values]) / len(left_sonar_values)) ** 0.5
    #     right_sonar_std = (sum([(value - right_sonar_mean) ** 2 for value in right_sonar_values]) / len(right_sonar_values)) ** 0.5
    #     # remove outliers
    #     left_sonar_values = [value for value in left_sonar_values if abs(value - left_sonar_mean) < left_sonar_std]
    #     right_sonar_values = [value for value in right_sonar_values if abs(value - right_sonar_mean) < right_sonar_std]

    # calculate mean of all sonar echos for left and right
    left_sonar_mean = sum(left_sonar_values) / len(left_sonar_values)
    right_sonar_mean = sum(right_sonar_values) / len(right_sonar_values)

    # print sonar values
    # print("Left:", left_sonar_mean)
    # print("Right:", right_sonar_mean, "\n")
    
    return (left_sonar_mean + right_sonar_mean) / 2.0


# def plot_sonar():
#     '''Plot sonar values in a graph.'''

#     fig = plt.figure()
#     ax1 = fig.add_subplot(1,1,1)

#     def animate(i):
#         left_sonar_mean, right_sonar_mean = read_sonar()
#         ax1.clear()
#         ax1.plot([left_sonar_mean, right_sonar_mean])
#         ax1.set_ylim([0, 1.5])

#     ani = animation.FuncAnimation(fig, animate, interval=1000)
#     plt.show()

# def write_csv(data, path):
#     '''Write sonar, imu, data to csv values to a csv file.
#     data: list of tuples (
#         timestep, distance along wall, 
#         left sonar, right sonar, rotation angle, 
#         measured x, measured y, measured theta)
#     path: path to csv file
#     '''

#     with open(path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile, delimiter=',')
#         writer.writerow(['t', 'y', 'x', 'r_x', 'r_y'])
#         for row in data:
#             writer.writerow(row)


# def gather_date():
#     '''Gather sonar, imu, data to csv values to a csv file.'''
#     pass


# while True:
#     # Get sonar left first echo (distance in meters to the first obstacle).
#     sonar_reading = read_sonar(n_samples=20)
#     # print sonar values
#     print("Sonar reading:", sonar_reading, "\n")

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
   
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')
