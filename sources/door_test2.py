from naoqi import ALProxy
from nao_conf import *
from rai_say import say
import time
#import pygame
import io
import subprocess
import keyboard
import msvcrt
from matplotlib.figure import figaspect
import almath as m # python's wrapping of almath
import sys
import matplotlib.pyplot as plt
from rai_sonar import read_sonar, savitzky_golay
import csv
import numpy as np
from subprocess import call
from hmmlearn import hmm

def speak(text):
    tts = ALProxy("ALTextToSpeech", IP, 9559)
    tts.say(text)

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


    door = False
    np.set_printoptions(formatter={'float_kind':'{:f}'.format})
    model = hmm.MultinomialHMM(n_components=2,  n_iter=1)
    model.startprob_ = np.array([0.5, 0.5])
    model.n_features = 3
    model.transmat_ = np.array([[0.9940766550522648, 0.005923344947735192],[0.017857142857142856, 0.9821428571428571],
    ])

    vocabulary = ["b", "s", "f"]
    emission_probs = np.array([[0.1137, 0.5937, 0.0434],[0.0023, 0.0277, 0.2183],
                            ])
    model.emissionprob_=emission_probs

    door_count = 0



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
    by_door = False

    a_l = []



    # 30 second window
    while time_now < 250:
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
            a_l.append([0])
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
            a_l.append([2])
            for _ in range(20):
                move(motionProxy, 0.2, 0.0, 0.0)
            time.sleep(0.05)
            move(motionProxy, 0.0, 0.2, 0.0)
            
            time.sleep(0.05)
        else:
            # stay put
            a_array.append('stay')
            a_l.append([1])
            move(motionProxy, 0.0, 0.2, 0.0)
            time.sleep(0.05)



        print(time_now)
        #print(a_l)
        action_arr = np.array(a_l)
        _, prob_arr = (model.score_samples(action_arr))
        current_prob = prob_arr[-1]
        door_prob = current_prob[-1]
        print("Action:",a_array[-1])
        print("door_prob:", door_prob)
        if door_prob > 0.7:
            print("Door")
            door = True
        else:
            if door and door_prob < 0.005:
                door_count +=1
                door = False
                speak("Passed Door"+ str(door_count))

        print("Door count:",door_count)
        endRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))
        robotMove = m.pose2DInverse(initRobotPosition)*endRobotPosition
        x_array.append([robotMove.x, robotMove.y])

        if door_count >=3:
            break

    if door_count >=3:
        speak("I passed three doors")
        
        time_start = time.time()
        time_now = 0 
        x_array = [] # x position of the robot
        z_array = [] # distance to wall
        t_arr = []  # time array
        a_array = []  # actions 
        door_array = []

        while time_now < 2:
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

            # stop the robot
            motionProxy.post.stopMove()

            say("I'm back at the start!")
        else:
            say("I didn't find 3 doors!")
            say(f"I only found {door_count} doors!")

            say("I'm back at the start!")
    


if __name__ == "__main__":
    # run the main function
    main(IP)