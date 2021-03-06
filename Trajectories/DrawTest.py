'''
MIT License

Copyright (c) [2018] Pedro Gil-Jiménez (pedro.gil@uah.es). Universidad de Alcalá. Spain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This file is part of the TrATVid Software
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

