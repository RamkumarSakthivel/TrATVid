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


#Interpolation methods to get node coordinates for intermediate/outside positions from actual nodes

__metaclass__=type

'BSpline interpolation tools'
import numpy
import scipy.interpolate as si
from math import sqrt
from .Node import NodeType, coord
from .Exceptions import TrajectoryException

class Interpolator:
    'Interpolator used to compute coordinates at intermediate positions'
    
    'Default value for the interpolation method.'
    defaultInterpolator='GC'
    

    def __init__(self, interpolatorType):
        '''Constructor: type refers to the type of interpolation to use
        Values:
        - 'NI': No interpolation
        - 'LI': Linear interpolation 2D
        - 'GI': Interpolation using Geometric 3D reconstruction
        - 'CS': Planar Cubic BSpline interpolation
        - 'GC': Combined Cubic BSpline interpolation with Geometric 3D reconstruction 
        - 'LM': LabelMe interpolation method (see [Yuen 2009])
        '''
        'If no interpolator is given, set it to the default interpolator, defined above.'
        if interpolatorType is None:
            interpolatorType=self.defaultInterpolator
        'check if the interpolation method is defined'
        if not interpolatorType in self.interpolatorMethod:
            raise TrajectoryException('Interpolation method '+interpolatorType+' not implemented')
        self.interpolatorType=interpolatorType

    def getUpdatable(self):
        'Return if the interpolator need to be updated each time the trajectory changes'
        return self.interpolatorMethod[self.interpolatorType]['U']
    updatable=property(getUpdatable)
    
    def updateInterpolator(self, data):
        'Build the interpolator structure. The data supplied must have the following structure:'
        'It is a list with all the node coordinates, in time order. Each node consists on:'
        '[0]: time'
        '[1]: dict{pos:pos, size:size} when a rectangle'
        '[1]: dict{pos:pos} when a point'
        
        'Change interpolation interType, if a new interType is given. Otherwise, not change it.'
        if not self.getUpdatable():
            'In this case, remove previous auxilar data, if any'
            try: del self.tckp
            except AttributeError: pass
            return
        
        'If the trajectory has only one node, the interpolator is not needed.'
        if len(data)==1: 
            'In this case, remove previous auxilar data, if any'
            try: del self.tckp
            except AttributeError: pass
            return
        'With only two actual nodes, only linear interpolation is possible'
        if len(data)<=2: kl=1
        else: kl=2

        'If needed, transform coordinates. If not needed, this function does not modify the data'
        try: self.interpolatorMethod[self.interpolatorType]['I'](self, data)
        #TODO: Remove this exception
        except KeyError: pass

        'Create list with all the data in scipy format compatible'         
        t=[d[0] for d in data]
        x=[d[1]['pos'].x for d in data]
        y=[d[1]['pos'].y for d in data]
        try:
            'Rectangle nodes. Build a 4-D interpolator'
            w=[d[1]['size'].x for d in data]
            h=[d[1]['size'].y for d in data]
            self.tckp, u=si.splprep([x,y,w, h], u=t, k=kl, s=0)
        except KeyError:
            'Point nodes. Build a 2-D interpolator'
            self.tckp, u=si.splprep([x,y],u=t, k=kl, s=0)
        del u
        
###################################################################################################
###################################################################################################
###################################################################################################
    'General interpolation functions:'
    
    def interpolatePoint(self, node1, node2, frame):
        'Generic method for point-point interpolation. The actual interpolation method is based on interpolationType value'
        if node1.time==node2.time:
            'If we are given the same node, return the same coordinates, and compute the type of node'
            'NOTE: This will happen when we need to interpolate when only one sample is available'
            return node1.pos, self.interpolationType(frame, node1.time, node2.time)
        'Check if the frame is the one for node1 or node2'
        if frame==node1.time:
            return node1.pos, NodeType.real
        if frame==node2.time:
            return node2.pos, NodeType.real
        try:
            'Compute the coordinates using the corresponding function'
            pos=self.interpolatorMethod[self.interpolatorType]['P'](self, node1, node2, frame)
        except ValueError:
            'An error can raise if the node is not a point. In this case, we'
            'need to interpolate with the rectangle function'
            pos, size=self.interpolatorMethod[self.interpolatorType]['R'](self, node1, node2, frame)
            del size
        return pos, self.interpolationType(frame, node1.time, node2.time)

    def interpolateRectangle(self, node1, node2, frame):
        'Same as interpolatePoint, for rectangles'
        if node1.time==node2.time:
            'If we are given the same node, return the same coordinates, and compute the type of node'
            'NOTE: This will happen when we need to interpolate when only one sample is available'
            return node1.pos, node1.size, self.interpolationType(frame, node1.time, node2.time)
        'Check if the frame is the one for node1 or node2'
        if frame==node1.time:
            return node1.pos, node1.size, NodeType.real
        if frame==node2.time:
            return node2.pos, node2.size, NodeType.real
        'Compute the coordinates using the corresponding function'
        pos, size=self.interpolatorMethod[self.interpolatorType]['R'](self, node1, node2, frame)
        return pos, size, self.interpolationType(frame, node1.time, node2.time)
        
###################################################################################################
###################################################################################################
###################################################################################################
    'Private interpolation functions:'
    
    'Generic interpolation (point and rectangles)'
    def interpolateNoInterpolate(self, node1, node2, frame):
        'No interpolation method. Return the same coordinates than the previous node'
        try:
            'Convert to float value, as is the type for the rest of the interpolation methods'
            return node1.pos.valueFloat, node1.size.valueFloat
        except AttributeError:
            return node1.pos.valueFloat
    
###################################################################################################
###################################################################################################
###################################################################################################
    'Private functions: Point interpolation'
    
    def interpolatePointLinear(self, node1, node2, frame):
        'Point to point linear interpolation'
        dif=node2.pos-node1.pos
        return node1.pos+dif*self.interpolatorFactor(frame, node1.time, node2.time)
 
    def interpolatePointBSpline(self, node1, node2, frame):
        'Point to point b-spline interpolation'
        x,y = si.splev(frame, self.tckp)
        'Build a coord with the interpolated elements'
        'NOTE: splev returns a ndarray of 0 dimension. Although it can be used as a normal'
        'number, to prevent further errors, extract the scalar using item() method'
        return coord(x.item(), y.item())
    
###################################################################################################
###################################################################################################
###################################################################################################
    'Private functions: Rectangle interpolation'
       
    def interpolateRectangleLinear(self, node1, node2, frame):
        'Rectangle to rectangle linear interpolation'
        pos, NodeType=self.interpolatePoint(node1, node2, frame)
        del NodeType
        dif=node2.size-node1.size
        size=node1.size+dif*self.interpolatorFactor(frame, node1.time, node2.time)
        return pos, size

    def interpolateRectangleBSpline(self, node1, node2, frame):
        'Rectangle to rectangle b-spline interpolation'
        x, y, w, h=si.splev(frame,self.tckp)
        'Build a coord with the interpolated elements'
        'NOTE: splev returns a ndarray of 0 dimension. Although it can be used as a normal'
        'number, to prevent further errors, extract the scalar using item() method'
        pos=coord(x.item(), y.item())
        size=coord(w.item(), h.item())
        return pos, size
    
    def interpolateRectangle3D(self, node1, node2, frame):
        'Rectangle to rectangle linear interpolation using 3D reconstruction (see paper)'
        XY, DXY, Z, DZ, WH, r=self.rectangle3DReconstruction(node1.pos, node1.size, node2.pos, node2.size)
        'Variables:'
        'XY: Coordinates, on the plane XY, of the rectangle center at frame1'
        'DXY: Shift on the plane XY of the rectangle center from frame1 to frame2'
        'Z: Reconstructed depth of the rectangle at frame1'
        'DZ: Reconstructed shift on depth from frame1 to frame2'
        'WH: Width and height of the reconstructed 3D rectangle'
        'r: Change in rectangle aspect ratio from frame1 to frame2'
        
        'Computation of the projection of the 3D rectangle for the frame given'
        'Interpolation factor'
        factor=self.interpolatorFactor(frame, node1.time, node2.time)
        'Change in XY coordinates. Computed from the initial coordinates at node 1'
        'plus the change proportional to frame'
        XY+=DXY*factor
        'Same for depth'
        Z+=DZ*factor
        'The aspect ratio variation change in a similar way. In this case, for node 1'
        'r=1 (aspect ratio is the aspect ratio of node 1), and for node 2, r=r (aspect'
        'ratio is the aspect ratio of node 2)'
        r=1+(r-1)*factor
        'Camera projection of the 3D rectangle. Take the canonical form for the projective camera'
        'XY coordinates'
        '  |1 0 0 0|'
        'M=|0 1 0 0|'
        '  |0 0 1 0|'
        xy=XY/Z
        'Z coordinate'
        'For the computation of the rectangle size, we have to take into account the change in'
        'the aspect ratio r'
        wh=coord(WH.x*r/Z, WH.y/r/Z)
        return xy, wh
    
    def interpolateRectangleBSpline3D(self, node1, node2, frame):
        'Rectangle to rectangle b-spline interpolation using 3D reconstruction (see paper)'
        
        'The first step is compute the size of the 3D rectangle, since this parameter is not'
        'kept by the interpolator. To this end, compute the projected size at frame of node 1'
        'and then compute the relation between the projected rectangle, and the actual one'
        'which is just node1.size'
        'So, compute parameters for frame of node 1'
        X, Y, Z, R=si.splev(node1.time, self.tckp)
        'NOTE: splev returns a ndarray of 0 dimension. Although it can be used as a normal'
        'number, to prevent further errors, extract the scalar using item() method'
        R0=R.item()
        Z0=Z.item()
        del X, Y #Remove the warning

        'Then, compute parameters for the frame required'
        X, Y, Z, R=si.splev(frame, self.tckp)
        'The relation between the projected frame, and the actual one, is just Z1/Z0 (and'
        'R1/R0 for the variation in aspect ratio)'
        R1=R.item()/R0
        Z1=Z.item()/Z0
        'With all this, compute the projected size of the node'
        size=coord(node1.size.x*R1/Z1, node1.size.y/R1/Z1)
        'And finally, compute the position of the rectangle. This is directly obtained'
        'from the interpolator, plus camera projection (1/Z)'
        pos=coord(X.item()/Z.item(), Y.item()/Z.item())
        return pos, size
    
    def rectangle3DReconstruction(self, pos1, size1, pos2, size2):
        '3D reconstruction using node1 and node 2 rectangle coordinates (see paper)'

        'Computation of the geometric mean of node sizes'
        bm1=sqrt(size1.x*size1.y)
        bm2=sqrt(size2.x*size2.y)
        'Null space computation'
        'Depth for 3D rectangle at frame=node1'
        Z=bm2
        'Change in depth from node1 to node2'
        DZ=bm1-bm2
        '3D coordinates on XY plane of the center of the rectangle at frame=node1'
        XY=pos1*Z
        '3D rectangle size of the rectangle at frame=node1'
        WH=size1*Z
        'Change in the upper-left corner coordinates from node1 to node2'
        DXY=pos2*(Z+DZ)-XY
        'Change in rectangle aspect ratio from node1 to node2'
        r=sqrt(float(size2.x*size1.y)/float(size2.y*size1.x))
        return XY, DXY, Z, DZ, WH, r

    def interpolateRectangleLabelMe(self, node1, node2, frame):
        'Interpolation using the method defined in LabelMe (see [Yuen 2009])'
        
        'Get corner in homogeneous coordinates'
        p1_0=numpy.matrix([node1.points[0].x, node1.points[0].y, 1], numpy.float32) 
        p1_1=numpy.matrix([node1.points[1].x, node1.points[1].y, 1], numpy.float32)
        p2_0=numpy.matrix([node2.points[0].x, node2.points[0].y, 1], numpy.float32)
        p2_1=numpy.matrix([node2.points[1].x, node2.points[1].y, 1], numpy.float32)
        'Get line parameter in homogeneous coordinates'
        l0=numpy.cross(p1_0, p2_0)
        l1=numpy.cross(p1_1, p2_1)
        'Get cross point for l0 and l1'
        pC=numpy.cross(l0, l1)
        'Dehomogenize point'
        if numpy.abs(pC[0,2])<=0.0001*numpy.abs(pC[0,0]) or numpy.abs(pC[0,2])<=0.0001*numpy.abs(pC[0,1]):
            'If the point reaches infinite, means parallel lines. Parallel lines happen'
            'when the object moves parallel to the image plane, and so, there is no change'
            'in depth. In this case, the interpolation can be done with a simple linear'
            'interpolation.'
            return self.interpolateRectangleLinear(node1, node2, frame)
        'Otherwise, dehomogenize the poiint'
        pv=(pC[0,0]/pC[0,2], pC[0,1]/pC[0,2])
        
        
        if ((pv[0]<=p1_0[0,0] and pv[0]>=p2_0[0,0]) or (pv[0]>=p1_0[0,0] and pv[0]<=p2_0[0,0])):
            return self.interpolateRectangleLinear(node1, node2, frame)
        if ((pv[1]<=p1_0[0,1] and pv[1]>=p2_0[0,1]) or (pv[1]>=p1_0[0,1] and pv[1]<=p2_0[0,1])):
            return self.interpolateRectangleLinear(node1, node2, frame)
        if ((pv[0]<=p1_1[0,0] and pv[0]>=p2_1[0,0]) or (pv[0]>=p1_1[0,0] and pv[0]<=p2_1[0,0])):
            return self.interpolateRectangleLinear(node1, node2, frame)
        if ((pv[1]<=p1_1[0,1] and pv[1]>=p2_1[0,1]) or (pv[1]>=p1_1[0,1] and pv[1]<=p2_1[0,1])):
            return self.interpolateRectangleLinear(node1, node2, frame)

        'Check zero division. In case it happens, change LM interpolation to Linear'
        if numpy.abs(p2_0[0,0]-pv[0])<0.01:
            return self.interpolateRectangleLinear(node1, node2, frame)
        if numpy.abs(p2_0[0,1]-pv[1])<0.01:
            return self.interpolateRectangleLinear(node1, node2, frame)
        if numpy.abs(p2_1[0,0]-pv[0])<0.01:
            return self.interpolateRectangleLinear(node1, node2, frame)
        if numpy.abs(p2_1[0,1]-pv[1])<0.01:
            return self.interpolateRectangleLinear(node1, node2, frame)

        'Compute velocity as described in [Yuen 2009]'
        v0=( \
                (p2_0[0,0]-p1_0[0,0]) / (pv[0]-p2_0[0,0]), \
                (p2_0[0,1]-p1_0[0,1]) / (pv[1]-p2_0[0,1]))
        v1=( \
                (p2_1[0,0]-p1_1[0,0]) / (pv[0]-p2_1[0,0]), \
                (p2_1[0,1]-p1_1[0,1]) / (pv[1]-p2_1[0,1]))
        
        f=self.interpolatorFactor(frame, node1.time, node2.time)
        'Project point as described in [Yuen 2009]'
        if numpy.abs(1+v0[0]*f)<1e-5:
            return self.interpolateRectangleLinear(node1, node2, frame)
        if numpy.abs(1+v0[1]*f)<1e-5:
            return self.interpolateRectangleLinear(node1, node2, frame)
        if numpy.abs(1+v1[0]*f)<1e-5:
            return self.interpolateRectangleLinear(node1, node2, frame)
        if numpy.abs(1+v1[1]*f)<1e-5:
            return self.interpolateRectangleLinear(node1, node2, frame)

        p0=( \
                (p1_0[0,0]+pv[0]*v0[0]*f) / (1+v0[0]*f), \
                (p1_0[0,1]+pv[1]*v0[1]*f) / (1+v0[1]*f))
        p1=( \
                (p1_1[0,0]+pv[0]*v1[0]*f) / (1+v1[0]*f), \
                (p1_1[0,1]+pv[1]*v1[1]*f) / (1+v1[1]*f))
        pos= coord(0.5*(p0[0]+p1[0]), 0.5*(p0[1]+p1[1]))
        size=coord((p0[0]-p1[0]), (p0[1]-p1[1]))
        return pos, size
        
    def interpolatorFactor(self, frame, time1, time2):
        'Computes the interpolation factor for the frame given.'
        return float(frame-time1)/float(time2-time1)
    
    def interpolationType(self, frame, time1, time2):
        if frame<time1 and frame<time2:
            return NodeType.anterior
        if frame>time1 and frame>time2:
            return NodeType.posterior
        if frame==time1 or frame==time2:
            return NodeType.real
        return NodeType.interpolated
        
    def transformData3D(self, data):
        'For algorithms based on 3D reconstruction, the data for interpolation must be transformed'
        'from 2d to 3D.'
        'Depth for the rectangle at the beginning of the trajectory. Set it arbitrary to 1'
        Z1=1
        'The variable r refers to the change in aspect ratio between rectangles. For the'
        'first step, this value is 1, since it refers to the same rectangle'
        r1=1
        for i in range(1, len(data)):
            'Take two consecutive nodes of the trajectory'
            d1=data[i-1][1]
            d2=data[i][1]
            'Compute the 3D reconstruction'
            XY, DXY, Z, DZ, WH, r=self.rectangle3DReconstruction(d1['pos'], d1['size'], d2['pos'], d2['size'])
            'Fix the scale data to make the sections continuous (change the focal length of the camera)'
            scale=Z1/Z
            'Scale all the variables (adjust the camera focal length)'
            XY*=scale
            DXY*=scale
            Z*=scale
            DZ*=scale
            'Update data values'
            d1['pos']=XY
            'NOTE: With this algorithm, the parameter size is reused to store the depth and r values'
            'This change must also be taken into account in the interpolation algorithm'
            d1['size']=coord(Z, r1)
            r1*=r
            Z1=Z+DZ
        del WH
        'Update the last element'
        data[-1][1]['pos']=XY+DXY
        data[-1][1]['size']=coord(Z1, r1)
            
    interpolatorMethod={
        #Relation between interpolation ID and methods used for computations
        #U: Uptadable
        #P: Method for point interpolation
        #R: Method for rectangle interpolation
        #I: Data transformation
        'NI':{'U':False, 'P': interpolateNoInterpolate, 'R':interpolateNoInterpolate},
        'LI':{'U':False, 'P': interpolatePointLinear,   'R':interpolateRectangleLinear},
        'GI':{'U':False, 'P': interpolatePointLinear,   'R':interpolateRectangle3D},
        'CS':{'U':True,  'P': interpolatePointBSpline,  'R':interpolateRectangleBSpline},
        'GC':{'U':True,  'P': interpolatePointBSpline,  'R':interpolateRectangleBSpline3D, 'I':transformData3D},
        'LM':{'U':False, 'P': interpolatePointLinear,   'R':interpolateRectangleLabelMe}
        }
