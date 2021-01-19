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


__metaclass__=type

import cv2
from copy import copy
from enum import Enum
from .Trajectory.Node import coord


class VerticalPosition(Enum):
    top=0
    bottom=1
    center=2
class HorizontalPosition(Enum):
    left=0
    right=1
    center=2

class EditNode:
    'Wrapper for nodes to be edited using mouse events'
    def __init__(self, newNode, p1, p2=None):
        'For node edition, take all the coordinates integer, since only integer precision'
        'is available from mouse events'
        self.p1=p1.valueInt
        try:
            'If p2 is given, we have a rectangle node'
            self.p2=p2.valueInt
            'In case coordinates are not sorted, sort them'
            'p1 must be the upper-left point, and p2 the lower-right point'
            'This function ensures that condition'
            self.sortCoordinates()
        except AttributeError: pass
        'Node behaviour is diferent for new and not new nodes. For that reason, client must'
        'indicate if it is new or not'
        self.newNode=newNode
        'Since OpenCV mouse listeners do not handle mouse drag (mouseMove is used for both'
        'mouseOver and mouseDrag, we have to control it inside this module'
        self.drag=False
        
    def getNodeCoords(self):
        'Get coordinates of the node in a dictionary (compatible with Node module)'
        try:
            return {'pos':(self.p1+self.p2)/2, 'size':self.p2-self.p1}
        except AttributeError:
            return {'pos':self.p1}
    def setNodeCoords(self, p1, p2=None):
        self.p1=coord(p1.x, p1.y)
        if not p2 is None:
            self.p2=p2
    nodeCoords=property(getNodeCoords, setNodeCoords)

    def sortCoordinates(self):
        'Set p1 the upper-left point, and p2 the lower-right point'
        if self.p1.x>self.p2.x:
            self.p1.x, self.p2.x=self.p2.x, self.p1.x
        if self.p1.y>self.p2.y:
            self.p1.y, self.p2.y=self.p2.y, self.p1.y
            
    def drawNode(self, img):
        'Edition nodes are drawn with lines running from the whole image, and crossing at node coordinates'
        
        'Check if node is a point or a rectangle node'
        try: 
            points=[self.p1, self.p2]
        except AttributeError:
            points=[self.p1]
        
        'Draw all the lines'
        for p in points:
            'Horizontal line'
            p1h=coord(p.x, 0).valueInt
            p2h=coord(p.x, img.shape[0]).valueInt
            cv2.line(img, (p1h.x, p1h.y), (p2h.x, p2h.y), (0x00, 0x00, 0x00))
            'Vertical line'
            p1v=coord(0, p.y)
            p2v=coord(img.shape[1], p.y)
            cv2.line(img, (p1v.x, p1v.y), (p2v.x, p2v.y), (0x00, 0x00, 0x00))

    def changeNodeCoordinates(self, x, y):
        'Function designed for the mouse move event'
        if self.newNode:
            'When creating a new node, we have to update points p1 and p2'
            if not self.drag:
                'After start dragging, update first point'
                self.p1=coord(x, y)
            else:
                'And when dragging, update the second point'
                self.p2=coord(x, y)
        else:
            'If the point is not new:'
            if not self.drag:
                'After draging, update the dragging point'
                self.c1=coord(x, y)
            else:
                'When dragging, change rectangle coordinates'
                self.changeCoordinates(x, y)
    
    def createNode(self, drag):
        'Function designed for the mouse down and up events'
        if self.newNode:
            if self.drag:
                'If the node is new, this is the event when the user finishes drawing the rectangle'
                'In this case, the node finishes being a new node'
                self.newNode=False
                'and sort the coordinates (if it is a rectangle), in case the user drawn the'
                'rectangle in inverse direction'
                try: self.sortCoordinates()
                except AttributeError: pass
        else:
            if not self.drag:
                'Check location of mouse down coordinates with respect to the rectangle'
                self.vertical, self.horizontal=self.nodePosition(self.c1.x, self.c1.y)
        'Update dragging condition for proper operation of the mouse move events'
        self.drag=drag
        
    def nodePosition(self, x, y):
        'Determine the position, with relation to the rectangle, where the user click.'
        try:
            'If the node is a rectangle, set p1 the upper-left point, and p2 the lower-right point'
            self.sortCoordinates()
        except AttributeError:
            'Otherwise, the node is a point, and only need to store p1'
            self.r1=copy(self.p1)
            'These values are irrelevant, so return center for proper operation of move events'
            return VerticalPosition.center, HorizontalPosition.center
        
        'If the node is a rectangle, determine the click location with respect to the rectangle'
        'Temporal variables, to take account of mouse shifts'
        self.r1=copy(self.p1)
        self.r2=copy(self.p2)
        'Check the position of a given point in relation with the coordinates of the rectangle'
        'Horizontal position'
        if self.p1.x<self.c1.x and self.p2.x<self.c1.x:
            horizontal=HorizontalPosition.left
        elif self.p1.x>self.c1.x and self.p2.x>self.c1.x:
            horizontal=HorizontalPosition.right
        else:
            horizontal=HorizontalPosition.center
        'Vertical position'
        if self.p1.y<self.c1.y and self.p2.y<self.c1.y:
            vertical=VerticalPosition.top
        elif self.p1.y>self.c1.y and self.p2.y>self.c1.y:
            vertical=VerticalPosition.bottom
        else:
            vertical=VerticalPosition.center
        
        return vertical, horizontal
    
    def changeCoordinates(self, x, y):
        'Auxiliar function for mouse move events'
        
        'Compute mouse shift from mouse down to actual position'
        inc=coord(x, y)-self.c1
        'If the user drag from inside the rectangle, move the rectangle'
        if self.vertical==VerticalPosition.center and self.horizontal==HorizontalPosition.center:
            self.p1=self.r1+inc
            try:
                self.p2=self.r2+inc
            except AttributeError: pass
            return
        'Otherwise, modify corresponding edges'
        'Horizontal component'
        if self.horizontal==HorizontalPosition.left:
            'Modify right edge'
            self.p2.x=self.r2.x+inc.x
        elif self.horizontal==HorizontalPosition.right:
            'Modify left edge'
            self.p1.x=self.r1.x+inc.x
        
        'Vertical component'
        if self.vertical==VerticalPosition.top:
            'Modify lower edge'
            self.p2.y=self.r2.y+inc.y
        elif self.vertical==VerticalPosition.bottom:
            'Modify upper edge'
            self.p1.y=self.r1.y+inc.y
        