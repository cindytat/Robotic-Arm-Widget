# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import os
import math
import sys
import time

os.environ["DISPLAY"] = ":0.0"

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
from dpeaDPi.DPiComputer import *
from dpeaDPi.DPiStepper import *

# ////////////////////////////////////////////////////////////////
# //                     HARDWARE SETUP                         //
# ////////////////////////////////////////////////////////////////
"""Stepper goes into MOTOR 0
   Limit Sensor for Stepper Motor goes into HOME 0
   Talon Motor Controller for Magnet goes into SERVO 1
   Talon Motor Controller for Air Piston goes into SERVO 0
   Tall Tower Limit Sensor goes in IN 2
   Short Tower Limit Sensor goes in IN 1
   """

# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
UP = False
DOWN = True
ON = True
OFF = False
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (.1, .1, .1, 1)  # (WHITE)

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()

#Servo motor
dpiComputer = DPiComputer()
dpiComputer.initialize()

#Stepper
dpiStepper = DPiStepper()
dpiStepper.setBoardNumber(0)
stepper_num = 0
if not dpiStepper.initialize():
    print("Communication with the DPiStepper board failed")

speed_steps_per_second = 1500
accel_steps_per_second_per_second = speed_steps_per_second

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

class MainScreen(Screen):
    armPosition = 0
    #lastClick = time.clock()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.time()
        if ((currentTime - self.lastClick) > DEBOUNCE):
            processInput = True
        self.lastClick = currentTime
        return processInput

    def toggleArm(self):
        servo_num = 1
        dpiStepper.enableMotors(True)
        dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(0, accel_steps_per_second_per_second)

        dpiStepper.moveToRelativePositionInSteps(0, -1900, True)
        print("move to ball")
        dpiStepper.enableMotors(False)

        self.toggleMagnet()
        if self.isBallOnShortTower():
            dpiStepper.enableMotors(True)
            dpiComputer.writeServo(servo_num, 90)
            sleep(2)
            dpiComputer.writeServo(servo_num, 180)

            sleep(2)

            dpiStepper.moveToRelativePositionInSteps(stepper_num, -550, True)
            dpiComputer.writeServo(servo_num, 90)
            sleep(2)
            self.toggleMagnet()
            dpiComputer.writeServo(servo_num, 180)
            dpiStepper.enableMotors(False)

        print("Process arm movement here")

    magnet = False
    def toggleMagnet(self):
        servo_num = 0
        if not self.magnet:
            dpiComputer.writeServo(servo_num, 180)
            print("magnet on")
            self.magnet = True
        else:
            dpiComputer.writeServo(servo_num, 90)
            print("magnet off")
            self.magnet = False
        print("Process magnet here")

    def auto(self):
        self.homeArm()
        print("home")
        self.toggleArm()
        self.homeArm()
        sleep(3)
        print("Run the arm automatically here")

    def setArmPosition(self, position):
        servo_num = 1
        dpiComputer.writeServo(servo_num, 180)
        print("Move arm here")

    def homeArm(self):
        dpiStepper.enableMotors(True)
        dpiStepper.moveToHomeInSteps(stepper_num, -1, 800, 3000)
        dpiStepper.enableMotors(False)
        #arm.home(self.homeDirection))

    def isBallOnTallTower(self):
        return dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1) == 0
        #print("Determine if ball is on the top tower")

    def isBallOnShortTower(self):
        if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1) == 0:
            return True
        return False
        #print("Determine if ball is on the bottom tower")

    def initialize(self):
        print("Home arm and turn off magnet")

    def resetColors(self):
        self.ids.armControl.color = YELLOW
        self.ids.magnetControl.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////
if __name__ == "__main__":
    # Window.fullscreen = True
    # Window.maximize()
    MyApp().run()