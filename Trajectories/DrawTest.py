'''
Created on Feb 2, 2015

@author: pedro
'''

import cv2
import numpy

from .Trajectories import Trajectories
from .Trajectory.Trajectory import Trajectory
from .Trajectory.Node import RectangleNode

# Create a black image
img = numpy.zeros((400,600,3), numpy.uint8)

p1=RectangleNode(2, 50, 90, 30, 40)
p2=RectangleNode(9, 200, 250, 50, 60)

p3=RectangleNode(5, 50, 250, 70, 80)
p4=RectangleNode(10, 90, 190, 90, 100)

trajectories=Trajectories()
t1=Trajectory(p1)
t1.addNode(p2)
trajectories.addTrajectory(t1)
t2=Trajectory(p3)
t2.addNode(p4)
trajectories.addTrajectory(t2)

for frame in range(0, 12):
    img[:]=(0, 0, 0)
    trajectories.drawPath(img, frame)
    trajectories.drawNode(img, frame)
    cv2.imshow('img', img)
    cv2.waitKey()

