from naoqi import ALProxy
from nao_conf import *
from rai_say import say
import time
#import pygame
import keyboard
import msvcrt
from matplotlib.figure import figaspect
import almath as m # python's wrapping of almath
import sys
import matplotlib.pyplot as plt
from rai_sonar import read_sonar, savitzky_golay
import csv
import numpy as np

def write_to_csv(time_arr, x_array, z_array, a_array, d_array):
    '''
    Write the data to a csv file
    '''
    filename = '../data/sonar_data_{}.csv'.format(time.time())
    with open(filename, 'w') as csvfile:
        # write the header
        fieldnames = ['t', 'x', 'z', 'a', 'd']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # write the data
        for i in range(len(time_arr)):
            writer.writerow({
                't': time_arr[i],
                'x': x_array[i], 
                'z': z_array[i], 
                'a': a_array[i], 
                'd': d_array[i]
            })
        

def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def fixHead(proxy):
    # fix nao's head in place
    proxy.setStiffnesses("Head", 1.0)

    # Example showing how to set angles, using a fraction of max speed
    names  = ["HeadYaw", "HeadPitch"]
    angles  = [0.0, 0.0]
    fractionMaxSpeed  = 0.2
    proxy.setAngles(names, angles, fractionMaxSpeed)

def move(proxy, vX=0.1, vY=0.0, vTheta=0.0):
    vX = vX
    vY = vY
    Theta = vTheta
    Frequency = 0.4 # low speed
    proxy.setWalkTargetVelocity(vX, vY, Theta, Frequency)

def main(robotIP):

    # Init proxies.
    try:
        motionProxy = ALProxy("ALMotion", robotIP, 9559)
    except Exception as e:
        print("Could not create proxy to ALMotion")
        print("Error was: ", e)

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)
    except Exception as e:
        print("Could not create proxy to ALRobotPosture")
        print("Error was: ", e)


    
    # Set NAO in stiffness On
    StiffnessOn(motionProxy)
    # Send NAO to Pose Init
    postureProxy.goToPosture("Stand", 0.8)
    # enable arms control by move algorithm
    # motionProxy.setWalkArmsEnabled(True, True)
    # foot contact protection
    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])
    # Fix head position
    fixHead(motionProxy)

     # position of the robot before the move
    initRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))

    # vX = 0
    # vY = 0.1
    # wTheta = 0
    x_array = [] # x position of the robot
    z_array = [] # distance to wall
    t_arr = []  # time array
    a_array = []  # actions 
    door_array = []

    time_start = time.time()
    time_now = 0 

    # 30 second window
    while time_now < 100:
        # read sonar data
        sonar_readings = read_sonar(20)
        time_now = time.time() - time_start
        t_arr.append(time_now)
        z_array.append(sonar_readings)

        # filter the data
        filtered_y = savitzky_golay(np.array(z_array), window_size=31, order=4)
        sonar_readings = filtered_y[-1]

        # print sonar_readings
        print(sonar_readings)
        
        if sonar_readings < .30:
            # move away from the wall
            # motionProxy.post.move(0, 0.1, 0)
            #motionProxy.post.move(-.2, 0, wTheta)
            a_array.append('backward')
            for _ in range(10):
                move(motionProxy, -0.2, 0.0, 0.0)
            time.sleep(0.05)
            move(motionProxy, 0.0, 0.2, 0.0)
            
        
            time.sleep(0.05)
        elif sonar_readings > .5:
            # move towards the wall
            # motionProxy.post.move(0, -0.1, 0)
            #motionProxy.post.move(.2, 0, wTheta)
            a_array.append('forward')
            for _ in range(10):
                move(motionProxy, 0.2, 0.0, 0.0)
            time.sleep(0.05)
            move(motionProxy, 0.0, 0.2, 0.0)
            
            time.sleep(0.05)
        else:
            # stay put
            a_array.append('stay')
            move(motionProxy, 0.0, 0.2, 0.0)
            time.sleep(0.05)

        #keys=pygame.key.get_pressed()
        if msvcrt.kbhit():
            door_array.append(True)
            print("Door detected.")
            msvcrt.getch() 
        else:
            print("NO Door")
            door_array.append(False)
        #        get robot position after move
        print(time_now)
        endRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))
        robotMove = m.pose2DInverse(initRobotPosition)*endRobotPosition
        x_array.append([robotMove.x, robotMove.y])


    # stop the robot
    motionProxy.post.stopMove()

    # write the data to a csv file
    filtered_y = savitzky_golay(np.array(z_array), window_size=31, order=4)
    write_to_csv(t_arr, x_array, z_array, a_array, door_array)

    # plot the sonar readings, and the robot's position in subplot
    fig, ax1 = plt.subplots()
    ax1.plot(t_arr, filtered_y)
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('sonar readings', color='b')
    ax1.tick_params('y', colors='b')

    # plot the robot's position y with respect to x in subplot
    # ax2 = ax1.twinx()
    # ax2.plot(r_x_array, r_y_array, 'r-')
    # ax2.set_ylabel('robot position', color='r')
    # ax2.tick_params('y', colors='r')



    
    fig.tight_layout()
    fig.savefig('../data/plots/plot_{}.png'.format(time.time()))

    # save plot
    fig.savefig('../data/plots/sonar_data_{}.png'.format(time.time()))





if __name__ == "__main__":
    # run the main function
    main(IP)