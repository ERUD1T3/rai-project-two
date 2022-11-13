from naoqi import ALProxy
from nao_conf import *
from say import say
from sonar import read_sonar, savitzky_golay
import csv
import numpy as np
import time
import almath as m # python's wrapping of almath
import matplotlib.pyplot as plt
from detect_door import DoorDetector


def main(robotIP):
    '''
        main demo run function
    '''

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


    say("Hello World!")
    say("Look at how pretty I am!")
    
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

    say("It's showtime.")

    x_array = [] # x position of the robot
    z_array = [] # distance to wall
    t_arr = []  # time array
    a_array = []  # actions 
    door_array = []
    detector = DoorDetector() # DBN based door detector
    n_doors_encountered = 0
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
            for _ in range(20):
                move(motionProxy, -0.2, 0.0, 0.0)
            time.sleep(0.05)
            move(motionProxy, 0.0, 0.2, 0.0)
            
        
            time.sleep(0.05)
        elif sonar_readings > .5:
            # move towards the wall
            # motionProxy.post.move(0, -0.1, 0)
            #motionProxy.post.move(.2, 0, wTheta)
            a_array.append('forward')
            for _ in range(20):
                move(motionProxy, 0.2, 0.0, 0.0)
            time.sleep(0.05)
            move(motionProxy, 0.0, 0.2, 0.0)
            
            time.sleep(0.05)
        else:
            # stay put
            a_array.append('stay')
            move(motionProxy, 0.0, 0.2, 0.0)
            time.sleep(0.05)

        # get robot position after move
        print(time_now)
        endRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))
        robotMove = m.pose2DInverse(initRobotPosition)*endRobotPosition
        x_array.append([robotMove.x, robotMove.y])

        # check if we are by a door based on last two actions
        if detector.detect_door(timestep=time_now, evidence=a_array[-2:]):
            n_doors_encountered += 1
            door_array.append(True)
            say("I found a door!")

        else:
            door_array.append(False)
            
        # check if we have passed 3 doors
        if n_doors_encountered >= 3:
            say("I found 3 doors!")

    # walk back to the start if we found 3 doors
    if n_doors_encountered >= 3:
        say("I'm going back to the start!")

        time_start = time.time()
        time_now = 0 
        x_array = [] # x position of the robot
        z_array = [] # distance to wall
        t_arr = []  # time array
        a_array = []  # actions 
        door_array = []

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
                for _ in range(20):
                    move(motionProxy, -0.2, 0.0, 0.0)
                time.sleep(0.05)
                move(motionProxy, 0.0, -0.2, 0.0)
                
            
                time.sleep(0.05)
            elif sonar_readings > .5:
                # move towards the wall
                # motionProxy.post.move(0, -0.1, 0)
                #motionProxy.post.move(.2, 0, wTheta)
                a_array.append('forward')
                for _ in range(20):
                    move(motionProxy, 0.2, 0.0, 0.0)
                time.sleep(0.05)
                move(motionProxy, 0.0, -0.2, 0.0)
                
                time.sleep(0.05)
            else:
                # stay put
                a_array.append('stay')
                move(motionProxy, 0.0, -0.2, 0.0)
                time.sleep(0.05)

            # get robot position after move
            print(time_now)
            endRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))
            robotMove = m.pose2DInverse(initRobotPosition)*endRobotPosition
            x_array.append([robotMove.x, robotMove.y])

            say("I'm back at the start!")
    else:
        say("I didn't find 3 doors!")
        say(f"I only found {n_doors_encountered} doors!")

    # write the data to a csv file
    filtered_y = savitzky_golay(np.array(z_array), window_size=31, order=4)
    write_to_csv(t_arr, x_array, z_array, a_array, door_array)

    # plot the sonar readings, and the robot's position in subplot
    fig, ax1 = plt.subplots()
    ax1.plot(t_arr, filtered_y)
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('sonar readings', color='b')
    ax1.tick_params('y', colors='b')

    fig.tight_layout()
    fig.savefig('../data/plots/plot_{}.png'.format(time.time()))
    # save plot
    fig.savefig('../data/plots/sonar_data_{}.png'.format(time.time()))




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

if __name__ == "__main__":
    # run the main function
    main(IP)