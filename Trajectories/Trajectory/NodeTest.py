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

from .Node import PointNode, RectangleNode
from .Interpolator import Interpolator

# Create a black image
img = numpy.zeros((400,600,3), numpy.uint8)

#Create and draw some point nodes
p1=PointNode(3, 250, 100)
#p1.drawNode(img)
p2=PointNode(8, 70, 30)
#p2.drawNode(img)
p3=PointNode(8, 90, 30)
#p3.drawNode(img)

'''
print(p1==p2)
print(p1>p2)
print(p1<p2)
print(p1!=p2)
print(p3==p2)
print(p3>p2)
print(p3<p2)
print(p3!=p2)
print(p3>=p2)
print(p3<=p2)
'''
#Create and draw some rectangle nodes
r1=RectangleNode(2, 150, 300, 20, 70)
#r1.drawNode(img)
r2=RectangleNode(9, 480, 240, 50, 100)
#r2.drawNode(img)

print(r1==p2)
print(r1>p2)
print(r1<p2)
print(r1!=p2)
print(r1>=p2)
print(r1<=p2)


cv2.imshow('img', img)
cv2.waitKey(0)

#Create an interpolator (L:Linear, D: 3D reconstruction)
#interpolator=Interpolator('L')
interpolator=Interpolator('D')

for t in range(r1.time-2, r2.time+3):
    r=r1.interpolateNode(r2, interpolator, t)
    r.drawNode(img)
    cv2.imshow('img', img)
    cv2.waitKey(0)

for t in range(p1.time,p2.time+1):
    p=p1.interpolateNode(p2, interpolator, t)
    p.drawNode(img)
    cv2.imshow('img', img)
    cv2.waitKey(0)

for t in range(r1.time, p2.time+1):
    r=r1.interpolateNode(p2, interpolator, t)
    r.drawNode(img)
    cv2.imshow('img', img)
    cv2.waitKey(0)

for t in range(p1.time, r2.time+1):
    r=p1.interpolateNode(r2, interpolator, t)
    r.drawNode(img)
    cv2.imshow('img', img)
    cv2.waitKey(0)
