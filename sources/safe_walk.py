from calendar import month
from naoqi import ALProxy
from nao_conf import *
from rai_say import say


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

def move(proxy):
    vX = 0.0
    vY = 0.25
    Theta = 0.0
    Frequency = 0.0 # low speed
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

    # 30 second window
    for _ in range(10): move(motionProxy)









if __name__ == "__main__":
    # run the main function
    main(IP)