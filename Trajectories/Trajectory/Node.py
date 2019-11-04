'''
Created on Jan 27, 2015

@author: pedro

Definition of the nodes of a trajectory. Include point and rectangular nodes.
'''

__metaclass__=type

import cv2
from enum import Enum
import copy
'XML support'
from xml.etree.ElementTree import SubElement

def CreateCoordFromXML(XMLCoord):
    'Read coordinate data from XML file.'
    val=XMLCoord.attrib['x']
    'Check if the number is float or int'
    try: x=int(val)
    except ValueError: x=float(val)
    val=XMLCoord.attrib['y']
    try: y=int(val)
    except ValueError: y=float(val)
    return coord(x, y)

def CreateNodeFromXML(XMLNode):
    'Read node data from XML file'
    nodeTime=int(XMLNode.attrib['time'])
    'Read and check node type'
    nodeType=XMLNode.attrib['type']
    if nodeType=='P':
        'Point node'
        XMLCoord=XMLNode.find('pos')
        c=CreateCoordFromXML(XMLCoord)
        return PointNode(nodeTime, c)
    elif nodeType=='R':
        'Rectangle node'
        XMLCoord=XMLNode.find('pos')
        c=CreateCoordFromXML(XMLCoord)
        XMLCoord=XMLNode.find('size')
        s=CreateCoordFromXML(XMLCoord)
        return RectangleNode(nodeTime, c, s)

class coord:
    'A pair of values defining a point in 2D' 
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def XMLData(self, element, tag):
        'Write coordinate data in XML file'
        return SubElement(element, tag, x=str(self.x), y=str(self.y))
        
    def __str__(self):
        return 'X:'+str(self.x)+' Y:'+str(self.y)

    #Overloaded operator =, +, -, * and /
    def __eq__(self, c):
        return self.x==c.x and self.y==c.y
    
    def __add__(self, c):
        return coord(self.x + c.x, self.y + c.y)

    def __sub__(self, c):
        return coord(self.x - c.x, self.y - c.y)
    
    def __mul__(self, c):
        return coord(self.x*c, self.y*c)
    
    def __truediv__(self, c):
        return coord(self.x/c, self.y/c)
    
    def distanceL1(self, c):
        x=self.x-c.x
        y=self.y-c.y
        x=x if x>0 else -x
        y=y if y>0 else -y
        return float(x+y)

    def distanceL2_2(self, c):
        'Squared Euclidean distance between two points'
        x=self.x-c.x
        y=self.y-c.y
        return x*x+y*y
    
    def getAbs(self):
        'Convert coordinates to positive values'
        x=self.x if self.x>0 else -self.x
        y=self.y if self.y>0 else -self.y
        return coord(x, y)
    valueAbs=property(getAbs)
    
    def saturate(self):
        'Saturate values on 0'
        if self.x<0: self.x=0
        if self.y<0: self.y=0

    def getInt(self):
        'Convert coordinates to int type (required by drawing functions)'
        x=int(self.x)
        y=int(self.y)
        return coord(x, y)
    valueInt=property(getInt)
    
    def getFloat(self):
        'Convert coordinates to float type'
        x=float(self.x)
        y=float(self.y)
        return coord(x, y)
    valueFloat=property(getFloat)
        
    
    def roundCoord(self, ndigits):
        'Round float values to 2 decimal place'
        self.x=round(self.x, ndigits)
        self.y=round(self.y, ndigits)
        
    
class NodeType(Enum):
    'Type of node, depending on whether the node exists on the trajectory, or has been inter/extrapolated'
    real=0
    interpolated=1
    anterior=2
    posterior=3
    
'Color of the node, as a function of its type'
typeColor={
   NodeType.real        :(0xFF, 0xFF, 0xFF),
   NodeType.interpolated:(0x00, 0x00, 0xFF),  
   NodeType.anterior    :(0xFF, 0x00, 0x00),
   NodeType.posterior   :(0x00, 0xFF, 0x00)
   }
    
    
###################################################################################################
###################################################################################################
###################################################################################################    
class PointNode:
    'Node for trajectories defined by points'
    def __init__(self, frame, pos=None, nodeType=NodeType.real):
        self.time=frame
        self.nodeType=nodeType
        try: self.pos=coord(pos.x, pos.y)
        except AttributeError: pass
        
    'Rich comparison operators: needed for trajectory node sorting'
    def __eq__(self, node2): return self.time==node2.time
    def __ne__(self, node2): return self.time!=node2.time
    def __gt__(self, node2): return self.time>node2.time
    def __ge__(self, node2): return self.time>=node2.time
    def __lt__(self, node2): return self.time<node2.time
    def __le__(self, node2): return self.time<=node2.time
    
    def __str__(self):
        return str(self.time) + ' P:'+str(self.pos)
    
    def getCoords(self):
        'Get coordinates of the node in a dictionary'
        return {'pos':self.pos}
    coords=property(getCoords)
        
    def getPoints(self):
        'Get coordinates of the node in a list'
        return [self.pos]
    points=property(getPoints)
    
    def roundCoord(self, ndigits=0):
        self.pos.roundCoord(ndigits)
    
    def XMLData(self, element, tag):
        'Write node data to a XML file'
        e=SubElement(element, tag, time=str(self.time), type='P')
        self.pos.XMLData(e, 'pos')
        return e

    def interpolateNode(self, node2, interpolator, frame):
        'Compute the coordinates of an intermediate node between 2 point nodes'
        pos, NodeType=interpolator.interpolatePoint(self, node2, frame)
        return PointNode(frame, pos, NodeType)
        
    def drawNode(self, img):
        'Draw the node in the image'
        p=self.pos.valueInt
        cv2.circle(img, (p.x, p.y), 5, (0x00, 0x00, 0x00), -1)
        cv2.circle(img, (p.x, p.y), 2, typeColor[self.nodeType], -1)
    
    def drawPath(self, img, node2, interpolator, color, thickness):
        'Draw a line joining this node with node2 in the image, using the interpolator given'
        if interpolator.updatable:
            'If the interpolator is updatable, it means that the data for interpolation'
            'must be obtained from it, instead of directly from node data'
            try:
                'If the path is previously computed, draw it, instead of computing it again'
                it=iter(self.path)
                p1=it.next()
                while True:
                    try: p2=it.next()
                    except StopIteration:
                        break
                    cv2.line(img, (p1.x, p1.y), (p2.x, p2.y), color, thickness)
                    p1=p2
            except AttributeError:
                'In case it is not previously computed, we have to compute the path, but'
                'we will store it, so that next time, we use the precomputation instead'
                p1=self.pos.valueInt
                'As we draw the path, store it for future use'
                self.path=[p1]
                'Draw a line for every frame between the nodes'
                'However, instead of drawing a line for each node, compute an interval, so that'
                'the number of drawings is reduced.'
                'To this end, first compute the distance between both nodes'
                'This instruction roughly establishes a separation of about 8 pixels between two'
                'nodes computed with the interpolator. This way, we need not compute interpolations'
                'for all the time intervals between both nodes'
                'Number of steps to interpolate (1 each 8 pixels)'
                steps=int(self.pos.distanceL1(node2.pos)/8.0+1)
                'Time interval to get the n steps for the interpolation'
                interval=float(node2.time-self.time)/steps
                for n in range(1,steps+1):
                    t=self.time+interval*n
                    p2, nodeType=interpolator.interpolatePoint(self, node2, t)
                    del nodeType
                    p2=p2.valueInt
                    cv2.line(img, (p1.x, p1.y), (p2.x, p2.y), color, thickness)
                    self.path.append(p2)
                    p1=p2
        else:
            'Otherwise, we use node coordinates to interpolate (linear interpolation)'
            p1=self.pos.valueInt
            p2=node2.pos.valueInt
            cv2.line(img, (p1.x, p1.y), (p2.x, p2.y), color, thickness)
            
    def extractBlob(self, img):
        'Extract an image blob corresponding to the node'
        points=self.getPoints()
        m=coord(PointNode.interMargin, PointNode.interMargin)
        p1=points[0]-m
        p1.saturate()
        p2=points[0]+m
        blob=img[p1.y:p2.y, p1.x:p2.x]
        return blob
            
    def selectNode(self, x, y):
        'Return if the point (x, y) belongs to the node'
        'Point selection: The node will be selected if clicked in a 8 pixel margin'
        'around the point coordinates'
        return -4<self.pos.x-x<+4 and -4<self.pos.y-y<+4

###################################################################################################
###################################################################################################
###################################################################################################
        
class RectangleNode(PointNode):
    'Node for trajectories defined by rectangles'
    def __init__(self, frame, pos, size, nodeType=NodeType.real):
        super(RectangleNode, self).__init__(frame, pos)
        self.size=coord(
            size.x if size.x>0 else -size.x, 
            size.y if size.y>0 else -size.y)
        self.nodeType=nodeType
   
    def __str__(self):
        '''return str(self.time) + ' R:'+str(self.pos)+' '+str(self.size)'''
        return str(self.time)

    def getCoords(self):
        'Get coordinates of the node in a dictionary'
        points=self.getPoints()
        return {'p1':points[0], 'p2':points[1], 'pos':self.pos, 'size':self.size}
    coords=property(getCoords)
    
    def getPoints(self):
        'Get rectangle coordinates'
        return [self.pos-self.size/2, self.pos+self.size/2]
    points=property(getPoints)

    def roundCoord(self, ndigits=0):
        super(RectangleNode, self).roundCoord(ndigits)
        self.size.roundCoord(ndigits)
    
    def XMLData(self, element, tag):
        'Write node data to a XML file'
        e=SubElement(element, tag, time=str(self.time), type='R')
        self.pos.XMLData(e, 'pos')
        self.size.XMLData(e, 'size')
        return e

    def interpolateNode(self, node2, interpolator, frame):
        'Compute the coordinates of an intermediate node between 2 rectangle nodes'
        pos, size, NodeType=interpolator.interpolateRectangle(self, node2, frame)
        return RectangleNode(frame, pos, size, NodeType)
        
    def drawNode(self, img):
        'Draw the node on image'
        p=self.getPoints()
        p1=p[0].valueInt
        p2=p[1].valueInt
        cv2.rectangle(img, (p1.x,  p1.y), (p2.x, p2.y), typeColor[self.nodeType], 2)
            
    def extractBlob(self, img):
        'Extract an image blob corresponding to the node'
        points=self.getPoints()
        'Get the margin to add to the rectangle'
        m=coord(PointNode.interMargin, PointNode.interMargin)
        p1=points[0]-m
        p2=points[1]+m
        'We only have to change if p1 is negative, since this is not managed by numpy'
        p1.saturate()
        'Convert to integer to prevent opencv warnings'
        p1=p1.valueInt
        p2=p2.valueInt
        blob=img[p1.y:p2.y, p1.x:p2.x]
        return blob
            
    def selectNode(self, x, y):
        'Return if the point (x, y) belongs to the node'
        'Rectangle selection: The node will be selected if clicked inside the rectangle'
        p=self.getPoints()
        return ((p[0].x<=x<=p[1].x) and (p[0].y<=y<=p[1].y))

    def intersection(self, node):
        'Compute the intersection with the node given'
        #Get rectangle coordinates for both nodes
        p1=self.points
        p2=node.points
        #Get width and height of the rectangle defining the intersection of both rectangles.
        minP=coord(max(p1[0].x, p2[0].x), max(p1[0].y, p2[0].y))
        maxP=coord(min(p1[1].x, p2[1].x), min(p1[1].y, p2[1].y))
        w=maxP.x-minP.x
        h=maxP.y-minP.y
        #If at least one of the values are negative, it means that there is no intersection
        #between both rectangles.
        if w<0 or h<0:
            return 0
        #Otherwise, return area of intersection
        return w*h

    def union(self, node):
        'Compute the area of union with the given node'
        return \
            self.size.x*self.size.y+\
            node.size.x*node.size.y-\
            self.intersection(node)
    
    def areaError(self, node):
        'Compute the area error (non-overlapping area) with the given node'
        return \
            self.size.x*self.size.y+\
            node.size.x*node.size.y-\
            2*self.intersection(node)
            
    def drawAreaError(self, node, img):            
        p00=self.points[0].valueInt
        p01=self.points[1].valueInt
        p10=node.points[0].valueInt
        p11=node.points[1].valueInt
        
        img1=copy.copy(img)
        img2=copy.copy(img)

        cv2.rectangle(img1, (p00.x, p00.y), (p01.x, p01.y), 0xFF, -1)
        cv2.rectangle(img2, (p10.x, p10.y), (p11.x, p11.y), 0xFF, -1)
        
        img=cv2.bitwise_xor(img1, img2)
        return img

        
        
    
#POINT        
#    def interpolateNode(self, node2, interpolator, frame):
#        'Generates a new node for an intermediate frame'
#        'Cross-call: intended for scalability. A new node NodeType can be added without needed to \
#         change old node types'
#         node=node2.interpolatePoint(self, interpolator, frame)
#         return node 

#RECTANGLE
#    def interpolatePoint(self, node2, interpolator, frame):
#        '''Compute the coordinates of an intermediate node between a rectangle and a point node
#        This method is called when node2 is a Point Node. To reuse the interpolation method, we
#        construct a copy of node2, but of Rectangle NodeType, with null size'''
#        nodeAux=RectangleNode(node2.time, node2.pos)
#        node=self.interpolateRectangle(nodeAux, interpolator, frame)
#        return node

#    def interpolateNode(self, node2, interpolator, frame):
#        'Compute the coordinates of an intermediate rectangular node'
##       try:
#        'Check whether the second node can interpolate a rectangle'
#        node=node2.interpolateRectangle(self, interpolator, frame)
##       except AttributeError:
#        'If not, compute the interpolation using this object'
##        node=self.interpolatePoint(node2, interpolator, frame)
#        return node

