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
from .Node import RectangleNode
from .Trajectory import Trajectory

# Create a black image
img = numpy.zeros((400,600,3), numpy.uint8)

#Create some point nodes
p1=RectangleNode(3, 60, 100, 60, 80)
p2=RectangleNode(9, 200, 250, 70, 50)
p3=RectangleNode(6, 150, 300, 90, 100)
p4=RectangleNode(9, 250, 240, 60, 40)
p5=RectangleNode(2, 50, 50, 30, 50)
p6=RectangleNode(2, 50, 90, 30, 50)

t1=Trajectory(p1)
print(t1)
'Insert at the end of the list'
t1.addNode(p2)
print(t1)
'Insert in the middle of the list'
t1.addNode(p3)
print(t1)
'Replace the last element'
t1.addNode(p4)
print(t1)
'Insert at the beginning of the list'
t1.addNode(p5)
print(t1)
'Replace at the beginning og the list'
t1.addNode(p6)
print(t1)
img[:]=(0, 0, 0)
t1.drawNode(img)
t1.drawPath(img)
for i in range(-2,12):
    print(i)
    t1.selectNode(i)
    t1.drawNode(img)
    cv2.imshow('img', img)
cv2.waitKey(0)
    
t1.selectNode(5)
t1.deleteNode()
print(t1)

t1.deleteNode()
t1.deleteNode()

t1.selectNode(10)
t1.deleteNode()
print(t1)
t1.selectNode(1)
t1.deleteNode()
print(t1)
t1.selectNode(3)
t1.deleteNode()
print(t1)
t1.selectNode(9)
t1.deleteNode()
print(t1)
t1.selectNode(2)
t1.deleteNode()
print(t1)
t1.selectNode(5)
t1.deleteNode()
print(t1)
t1.selectNode(6)
t1.deleteNode()
print(t1)


