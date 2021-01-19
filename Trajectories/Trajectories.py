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


#List of trajectories.


from copy import deepcopy
'XML support'
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import time

from .Trajectory.Trajectory import CreateTrajectoryFromXML
from .Trajectory.Exceptions import TrajectoryException

__metaclass__=type

class Trajectories:
    '''
    List of trajectories.
    '''
    def __init__(self, XMLFile=None):

        'List of trajectories'
        self.trajectories={}
        'Dictionary for fast access to trajectories, according to the trajectory starting and ending frame'
        'This dictionary store the time intervals where a trajectory exists. Thus, if we need to access all'
        'the trajectories that exist on a given time, we only have to check those included in the dictionary'
        'for the time interval given'
        self.timeIndex={}
        'Time interval length. For instance, a time interval of 3, means that the first key in the timeIndex'
        'dictionary includes time=0, 1 and 2. The second key will include time=3, 4 and 5, and so no'
        self.timeInterval=11
        'Auxiliary variable to assign a unique ID to each trajectory'
        self.ID=0
        try:
            'Read data structure from XML file'
            XMLElement=ElementTree.parse(XMLFile)
        except (TypeError, IOError):
            'If the file does not exist, finish the routine' 
            pass
        except ElementTree.ParseError:
            raise TrajectoryException('XML file '+XMLFile+' is incorrect')
        else:
            try:
                'If the XML file is correct, read the trajectories'
                for XMLTrajectories in XMLElement.findall('Trajectory'):
                    'Read each trajectory on the XML file'
                    'Read trajectory ID'
                    try: 
                        ID=int(XMLTrajectories.attrib['ID'])
                    except KeyError:
                        'If the trajectory does not have ID tag, ignore this trajectory' 
                        continue
                    try:
                        'Read interpolation type for the trajectory'
                        interType=XMLTrajectories.attrib['Interpolation']
                    except KeyError:
                        'If the trajectory does not have interpolation type, give'
                        'the default interpolation type (old files)'
                        interType=None
                    'Read trajectory nodes'
                    XMLTrajectory=XMLTrajectories.find('TrajectoryNodes')
                    trajectory=CreateTrajectoryFromXML(XMLTrajectory, interType)                    
                    'Add the trajectory (updating timeIndex)'
                    self.addTrajectory(trajectory, ID)
                    'Get the last ID used in the file, to have a unique ID for new trajectories'
                    if ID>self.ID: self.ID=ID
            except AttributeError:
                raise TrajectoryException('XML file '+XMLFile+' is incorrect')
            except UnboundLocalError:
                pass
        XMLElement=None
        
    def __str__(self):
        s=''
        for ID, tr in self.trajectories.items():
            s+='T: '+str(ID)+str(tr)+'\n'
        return s

    def SaveXMLFile(self, XMLFile, complete=False):
        'Write data to a XML file'
        'Create the XML element'
        XMLElement=Element('VideoAnnotation', date=repr(time.asctime()))
        'Include data for all the trajectories'
        'Sort trajectories before save it'
        'NOTE: sorting criteria is defined in the rich comparison method of trajectory class'
        #for ID, tr in sorted(self.trajectories.items(), key=lambda k,v: (v,k)):
        for ID, tr in sorted(self.trajectories.items(), key=lambda tr: (tr[1],tr[0])):
            intertype=tr.InterpolationType()
            e=SubElement(XMLElement, 'Trajectory', ID=str(ID), Interpolation=intertype)
            tr.XMLData(e, 'TrajectoryNodes', complete)
        'Write data to file'
        XMLFile = open(XMLFile, 'wb')
        XMLFile.write(b'<?xml version="1.0"?>')
        XMLFile.write(ElementTree.tostring(XMLElement))
        XMLFile.close()       
        
    def computeIndex(self, start, end=None):
        'Return the list of indexes for the trajectory dictionary, according to the start and end frame'
        'This function is intended to be passed to the trajectory for self computation of their'
        'trajectory dictionary indexes'
        'If end is not provided, return the index for start'
        lowerIndex=int(start/self.timeInterval)
        if end is None:
            return lowerIndex
        'Otherwise, return a list with all the indexes between start and end'
        upperIndex=int((end/self.timeInterval)+1)
        l=[n for n in range(lowerIndex,upperIndex)]
        return l
        
    def addTrajectory(self, trajectory, ID):
        'Add the trajectory to the list of trajectories'
        'Also, update timeIndex, for fast access to trajectories as a function of frame number'
        
        'Check if it is a new trajectory'
        if ID==0:
            'Assign an unique ID to the new trajectory'
            self.ID+=1
            ID=self.ID
        else:
            try:
                'Find if the trajectory is already in the dictionary'
                self.trajectories[ID].unregisterTrajectory(ID)
            except KeyError: pass
        'And add the new trajectory'
        trajectory.registerTrajectory(self.timeIndex, self.computeIndex, ID)
        self.trajectories[ID]=trajectory 
            
    def deleteTrajectoryCheck(self, ID):
        'Check if the trajectory can be deleted (for GUI message purposes)'
        return (ID in self.trajectories)
        
    def deleteTrajectory(self, ID):
        'Delete trajectory from the list'
        'If the trajectory does not exists, a KeyError exception is raised'
        t=self.trajectories.pop(ID)
        t.unregisterTrajectory(ID)
        
    def selectTrajectory(self, frame, x, y):
        'Check if the point belongs to a node for the current frame'
        try:
            'Check only the trajectories registered for the given frame (that is, trajectories that exist'
            'in the given frame)'
            index=self.computeIndex(frame)
            for ID in self.timeIndex[index]:
                tr=self.trajectories[ID]
                if tr.exists(frame):
                    node=tr.selectNode(frame)
                    if node.selectNode(x, y):
                        'Make a complete copy of the trajectory'
                        return deepcopy(tr), ID
        except KeyError: pass 
        'Exception happens when there is no one trajectory for the given frame'
        return None, 0
    
    def drawNode(self, img, frame):
        'Draw the node for the given frame for all the trajectories'
        try:
            'We take only the trajectories that exist for the given frame (trajectories registered in the given frame)'
            index=self.computeIndex(frame)
            for ID in self.timeIndex[index]:
                tr=self.trajectories[ID]
                if tr.exists(frame):
                    node=tr.selectNode(frame)
                    node.drawNode(img)
        except KeyError: return
        'Exception happens when there is no one trajectory for the given frame'
        
    def drawPath(self, img, frame):
        'Draw the paths for all the trajectories that exists for the given frame'
        try:
            'Same as drawNode'
            index=self.computeIndex(frame)
            for ID in self.timeIndex[index]:
                tr=self.trajectories[ID]
                if tr.exists(frame):
                    tr.drawPath(img)
        except KeyError: return
        