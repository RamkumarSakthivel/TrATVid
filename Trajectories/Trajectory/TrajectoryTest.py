'''
Created on Jan 29, 2015

@author: pedro
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


