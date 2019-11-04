'''
Created on Jan 29, 2015

@author: pedro

List of nodes composing a trajectory
'''

__metaclass__=type

'Module to work with sorted lists'
import bisect
import math
'XML support'
from xml.etree.ElementTree import SubElement

from .Interpolator import Interpolator
from .Exceptions import TrajectoryException
from .Node import PointNode, NodeType, CreateNodeFromXML

def CreateTrajectoryFromXML(XMLTrajectory, interType=None):
    'Read trajectory data from XML file'
    
    'Find all nodes of the trajectory'
    XMLNodes=XMLTrajectory.findall('Node')
    'Create first node of the trajectory'
    node=CreateNodeFromXML(XMLNodes[0])
    'Create the trajectory'
    trajectory=Trajectory(node, interType)
    total=len(XMLNodes)
    'and add the rest of nodes'
    duplicates=0
    for i in range(1, total):
        'Read node data'
        node=CreateNodeFromXML(XMLNodes[i])
        'Check if time is already in the trajectory'
        if trajectory.nodes.count(node)!=0:
            'If node time is already in the list of nodes, do not include this'
            'new node in the trajectory'
            duplicates+=1
            continue
        'For the intermediate nodes, we need not update trajectory data, so it is'
        'enough to append the nodes to the trajectory'
        trajectory.nodes.append(node)
    
    if duplicates>0: print("Warning: Found "+str(duplicates)+ " duplicated nodes in trajectory. Check annotation file.")
    'Check trajectory consistency.'
    trajectory.checkConsistency()
    'If the trajectory has only one node, not doing the two loops will five the correct structure'
    'for the trajectory'
    return trajectory

class Trajectory:
    'List of node positions for an object'

    'List of nodes defining the nodes of the trajectory'
    def __init__(self, node, interType=None):
        'Constructor: We can use the constructor to check whether the node type is correct'
        self.start=node.time
        self.end=node.time
        'Add the first node to the nodes of the trajectory'
        self.nodes=[node]
        'Construct the interpolator without data'
        self.interpolator=Interpolator(interType)
        
    def __str__(self):
        s=''
        for n in self.nodes:
            s+=' N:'+str(n)
        return s
    
    'Rich comparison operators: needed for trajectories sorting using'
    'trajectory start. In this case, sort by trajectory starting time'
    def __eq__(self, tr2): return self.nodes[0].time==tr2.nodes[0].time
    def __ne__(self, tr2): return self.nodes[0].time!=tr2.nodes[0].time
    def __gt__(self, tr2): return self.nodes[0].time> tr2.nodes[0].time
    def __ge__(self, tr2): return self.nodes[0].time>=tr2.nodes[0].time
    def __lt__(self, tr2): return self.nodes[0].time< tr2.nodes[0].time
    def __le__(self, tr2): return self.nodes[0].time<=tr2.nodes[0].time
    
    def keyCompare(self): return self.nodes[0].time
   
    def InterpolationType(self):
        return self.interpolator.interpolatorType
    
    def XMLData(self, element, tag, complete=False):
        'Write trajectory data to XML file'
        e=SubElement(element, tag)
        if complete:
            for i in range(self.start, self.end+1):
                'Get the node for time i'
                n=self.selectNode(i)
                n.roundCoord(1)
                n.XMLData(e, 'Node')
        else:
            for n in self.nodes:
                n.XMLData(e, 'Node')
        return e

    def checkConsistency(self):
        'Check if trajectory data is correct. Specially, if the node time order is not'
        'correct, nodes are ordered.'
        self.nodes.sort()
        'Checking for duplicates is not done.'
        
        'Update trajectory start and end'
        self.start=self.nodes[0].time
        self.end=self.nodes[-1].time
        'Update trajectory interpolator (if required)'
        self.updateInterpolator()
        
    def registerTrajectory(self, timeIndex, computeIndex, ID):
        'This function must be called when the trajectory is added into a trajectory list'
        'Store dictionary and function'
        self.timeIndex=timeIndex
        self.computeIndex=computeIndex
        'Update dictionary'
        self.updateTimeIndex(ID)
    
    def unregisterTrajectory(self, ID):
        'This function must be called when the trajectory is removed from a trajectory list'
        'Remove trajectory from dictionary'
        l=self.computeIndex(self.start, self.end)
        for n in l:
            self.timeIndex[n].remove(ID)
            if self.timeIndex[n]==[]: self.timeIndex.pop(n)
        del self.timeIndex
        del self.computeIndex
        
    def updateTimeIndex(self, ID):
        'Compute the frame intervals where the trajectory exists, and update the frame index dictionary'
        'adding/deleting its ID into the dictionary timeIndex'
        'The computations of the frame intervals is performed using the provided function computeIndex'
        l=self.computeIndex(self.start, self.end)
        'l is the list with the frame intervals where the trajectory exists. Now, we have to ensure that'
        'the trajectory is registered only on proper intervals'
        'First, check if it is already registered in the first interval'
        firstInterval=self.timeIndex.setdefault(l[0], [])
        if ID in firstInterval:
            'In this case, check if it is also registered on previous intervals'
            'If so, remove then. This happens when the first node has been removed from the trajectory'
            'so that the trajectory no longer exists on the lowest frame interval(s)'
            n=l[0]-1
            while True:
                'Keep deleting until the trajectory is no longer registered'
                try: 
                    self.timeIndex[n].remove(ID)
                    'Check if a given index is empty. If so, remove it from the dictionary'
                    if self.timeIndex[n]==[]: self.timeIndex.pop(n)
                    n-=1
                except (ValueError, KeyError): break 
                'ValueError happens when trying to delete a trajectory that is not present in the'
                'given entry of the dictionary'
                'KeyError happens when dictionary does not have the required entry'
                'In both cases, do nothing'
                
        'Same as before, for the last interval'
        lastInterval=self.timeIndex.setdefault(l[-1], [])
        if ID in lastInterval:
            'In this case, check if it is also registered on following intervals'
            'If so, remove then. This happens when a node has been removed from the trajectory, so that'
            'the trajectory does not exists in the lowest frame interval(s)'
            n=l[-1]+1
            while True:
                'Keep deleting until the trajectory is no longer registered'
                try: 
                    self.timeIndex[n].remove(ID)
                    'Check if a given index is empty. If so, remove it from the dictionary'
                    if self.timeIndex[n]==[]: self.timeIndex.pop(n)
                    n+=1
                except (ValueError, KeyError): break 

        'Ensure that the trajectory is registered in the intermediate intervals'
        for n in range(l[0], l[-1]+1):
            if not ID in self.timeIndex.get(n, []):
                try: self.timeIndex[n].append(ID)
                except KeyError: self.timeIndex[n]=[ID]
        
    def addNode(self, node):
        'Add a node to the trajectory. If a node for the same frame already exists, the new node'
        'replace the old one'
        'Set the type of node to real, regardless the actual type of the node'
        node.nodeType=NodeType.real
        'Find the insertion point in the ordered nodes list. Ordered list means that node times are'
        'in ascending order'
        i=bisect.bisect_left(self.nodes, node)
        'Check whether the node exists for the same frame as node'
        '(otherwise index will point to the end of the list)'
        try:
            if self.nodes[i]==node:
                'The node already exists. Substutite the old node with the new one'
                self.nodes[i]=node
            else:
                'The node does not exists. Insert it at position i'
                self.nodes.insert(i, node)
        except IndexError:
            pass
            'This exception occurs when node frame is posterior to the end of the current trajectory'
            'In this case, we need to update trajectory end'
            self.end=node.time
            self.nodes.insert(i, node)
        if node.time<self.start: 
            self.start=node.time
        self.updateInterpolator()

    def deleteNodeCheck(self, frame):
        'Check if the required node can be deleted from the trajectory. This is intended to help the'
        'GUI raise an user message before deleting the node'
        
        'To be able to use bisect functions, a temporal node, with the correct frame, must be created'
        node=PointNode(frame)
        if len(self.nodes)>1:
            'Find the node in the sorted list'
            i=bisect.bisect_left(self.nodes, node)
            try:
                if self.nodes[i]==node:
                    return True
            except IndexError: pass
        return False
                
    def deleteNode(self, frame):
        'Delete the node at frame given'
        'To be able to use bisect functions, a temporal node, with the correct frame, must be created'
        node=PointNode(frame)
        'Check if the trajectory only has one node'
        if len(self.nodes)==1:
            raise TrajectoryException('Can not delete last node of a trajectory. Delete the trajectory instead')
        else:
            'Find the node in the sorted list'
            i=bisect.bisect_left(self.nodes, node)
            try:
                if self.nodes[i]==node:
                    'Check that the required node exists'
                    self.nodes.pop(i)
                else: raise IndexError
            except IndexError:
                'An exception is raised when selected node is posterior to the trajectory end.' 
                raise TrajectoryException('Required node does not exists')
            
            'Update start and end values, if necessary'
            if i==0:
                self.start=self.nodes[0].time
            if i==len(self.nodes):
                self.end=self.nodes[-1].time
            'Update interpolator data, if required'
            self.updateInterpolator()

    def updateInterpolator(self, interType=None):
        'Update data associated with the interpolator.'
        'NOTE: This is only necessary for BSpline-based interpolator. Linear interpolator'
        'do not need any update, since the data need for interpolation is obtained directly'
        'from node coordinates'
        if not interType is None:
            'Change interpolation type if a new type is given. Otherwise, keep previous interType'
            self.interpolator.interpolatorType=interType
            
        if self.interpolator.updatable:
            positions=[]
            'Obtain a list with all the coordinates of the nodes'
            for node in self.nodes:
                'Delete pre-computed node paths, if needed'
                try: del node.path
                except AttributeError: pass
                positions.append((node.time, node.coords))
                'and update the interpolator'
            self.interpolator.updateInterpolator(positions)
             
    def selectNode(self, frame):
        'Select the node for the given frame, and return a copy of it. If the node does not exists, an'
        'interpolated/extrapolated node is created.'
        
        'To be able to use bisect functions, a temporal node, with the correct frame, must be created'
        node=PointNode(frame)
        'Check if the trajectory only has one node'
        if len(self.nodes)==1:
            return self.nodes[0].interpolateNode(self.nodes[0], self.interpolator, frame)
        else:
            'Find the node in the sorted list'
            i=bisect.bisect_left(self.nodes, node)
            
            if i==len(self.nodes):
                'This case happens when requiring a frame posterior to the trajectory end'
                i=-2
            elif i>0:
                'This case happens for times within the trajectory start and end'
                i-=1
                'else: this case is for times anterior to the trajectory start'
            return self.nodes[i].interpolateNode(self.nodes[i+1], self.interpolator, frame)
        
    def exists(self, frame):
        'Check whether this trajectory exists for the given frame'
        return self.start<=frame<=self.end
    
    def duration(self):
        'Return the duration of the trajectory, in frames'
        return self.end-self.start+1
    
    def length(self):
        'Return the length traversed by the tracked point'
        it=iter(self.nodes)
        n1=it.next()
        dist=0
        while True:
            try: n2=it.next()
            except StopIteration: break
            'Compute the euclidean distance to the next point'
            dAux=n1.pos.distanceL2_2(n2.pos)
            if dAux>8:
                'Only update with the new distance if this is'
                'greater than sqrt(8) pixels. This prevent static but'
                'erratic points from yield a large distance when'
                'in fact, the point has not moved'
                dist+=math.sqrt(dAux)
                n1=n2
        return dist
    
    def occludedLength(self):
        'Return the length traversed by the tracked point when the point is occluded'
        it=iter(self.nodes)
        n1=it.next()
        dist=0
        while True:
            try: n2=it.next()
            except StopIteration: break
            'Check if there is an occlusion between both points'
            if n2.time-n1.time==1:
                'If there is not occlusion, advance to the next node'
                n1=n2
            else:
                'Compute the euclidean distance to the next point'
                dAux=n1.pos.distanceL2_2(n2.pos)
                if dAux>8:
                    'Only update with the new distance if this is'
                    'greater than sqrt(8) pixels. With filter real'
                    'occlusions from lack of nodes because the node'
                    'is static. Remember that if the node is static'
                    'only the first and the last node are stored'
                    dist+=math.sqrt(dAux)
                    n1=n2
        return dist
        
          
    def drawPath(self, img, innerColor=(0xFF, 0xFF, 0xFF), outerColor=(0x00, 0x00, 0x00)):
        'Draw a line joining the center of all the nodes of the trajectory'
        it=iter(self.nodes)
        n1=next(it)
        while True:
            try: n2=next(it)
            except StopIteration: break
            n1.drawPath(img, n2, self.interpolator, outerColor, 2)
            n1=n2
        it=iter(self.nodes)
        n1=next(it)
        while True:
            try: n2=next(it)
            except StopIteration: break
            n1.drawPath(img, n2, self.interpolator, innerColor, 1)
            n1=n2
