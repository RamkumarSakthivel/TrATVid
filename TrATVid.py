'''
Created on Feb 2, 2015

@author: pedro
'''

'OpenCV'
import cv2
'Image copy'
from copy import deepcopy
'For backup'
import time
'Access program arguments'
import sys
'Create an manipulate directories'
import os

'XML support for program settings'
from xml.etree import ElementTree

from Trajectories.PrintResults import printBlobs, saveVideoResult
from Trajectories.Trajectories import Trajectories
from Trajectories.EditNode import EditNode
from Trajectories.Trajectory.Trajectory import Trajectory
from Trajectories.Trajectory.Node import coord, RectangleNode, PointNode
from Trajectories.Trajectory.Interpolator import Interpolator

'''
SYSTEM STATES:
ActiveNode is not None and ActiveTrajectory is None
- Adding a new trajectory. The first node is already created.
  
ActiveNode is None and ActiveTrajectory is not None
- Editing a trajectory.

ActiveNode is not None and ActiveTrajectory is not None
- Editing a node of a trajectory

ActiveNode is None and ActiveTrajectory is None
- View mode (or eventually creating the first node of a new trajectory).
'''

'Mouse handlers'
'When editing a node'
def mouseEditNode(event, x, y, flags, mousePoints):
    if event==cv2.EVENT_LBUTTONDOWN or \
       event==cv2.EVENT_MOUSEMOVE or \
       event==cv2.EVENT_LBUTTONUP:
        mousePoints['x']=x
        mousePoints['y']=y
    else:
        return
    mousePoints['p']=event
'When in view mode (to allow for double click selections'
def mouseSelectNode(event, x, y, flags, mousePoints):
    if event==cv2.EVENT_LBUTTONDBLCLK:
        mousePoints['x']=x
        mousePoints['y']=y
        mousePoints['p']=event
  
###################################################################################################
###################################################################################################
##################MAIN PROGRAM#####################################################################
###################################################################################################
###################################################################################################

print('Trajectories v0.0')
'Open program settings'
try:
    settingsFile=sys.argv[1]
except IndexError:
    settingsFile='settings.xml'
    
settings=ElementTree.parse(settingsFile)

'Read project path'
projectPath=settings.find('video').attrib['path']

'Read video file'
videoName=settings.find('video').attrib['name']
'Open video'
video=cv2.VideoCapture(str(projectPath+videoName))
if not video.isOpened():
    raise Exception('Video '+videoName+' not found')
print('Opening video:'+videoName)
# 'Generate name for video results'
# videoResultName=projectPath+'res_'+videoName

'Read interpolation type and margin'
try:
    interMargin=int(settings.find('interpolation').attrib['margin'])
except (AttributeError, KeyError, ValueError):
    interMargin=0
PointNode.interMargin=interMargin

try:
    interType=settings.find('interpolation').attrib['type']
    'Set the default type of interpolation as a static variable of the'
    'trajectory class. This variable is used in its constructor' 
    Interpolator.defaultInterpolator=interType
    print('Interpolation type: '+interType)
except (AttributeError, KeyError):
    'If the key does not exist, take default interpolator' 
    print('Interpolation type: Default')

'Read annotation file'
annXmlFile=settings.find('file').attrib['name']
annotationFile=projectPath+annXmlFile
print('Opening annotation file:'+annotationFile)
windowTitle='Trajectories - ('+annotationFile+')'
'File to save complete trajectories (if needed)'
annCompleteFile=projectPath+'co_'+annXmlFile
'Create object for the trajectory list (read trajectories from the XML file, if it exists)'
trajectories=Trajectories(annotationFile)

'Reading information for back up'
backupInterval=int(settings.find('backup').attrib['time'])
'Generating mane for back up file'
backupFile=annotationFile+'.bak'

'Variables for editing trajectories and nodes'
activeTrajectory=None
activeNode=None
activeID=0
'Current video frame'
frame=0
'Structure for communications between mouse events and main program'
mousePoints={'x':0, 'y':0, 'p':-1}

'Indicates if current editions has already been saved.'
saved=True

#'TODO: Borrar'
#trajectories.addTrajectory(convert.convert(projectPath), 0)
#saved=False

'Read first frame of the video'
video.set(cv2.CAP_PROP_POS_FRAMES, frame)
ret, imgAux=video.read();
cv2.imshow(windowTitle, imgAux)
'Read number of frames for the video'
'NOTE: function get from OpenCV return the value as a double. Since the frame count is'
'an integer value, convert it to its correct type (int)'
totalFrames=int(video.get(cv2.CAP_PROP_FRAME_COUNT))
'Initialize mouse listener with the default one: trajectory selection'
cv2.setMouseCallback(windowTitle, mouseSelectNode, mousePoints)

'Capture the first time mark for backup intervals'
time1=time.mktime(time.localtime())
time1+=backupInterval
while True:
    'Make a backup when time since last backup reaches the limit'
    time2=time.mktime(time.localtime())
    if (time2>time1):
        try: trajectories.SaveXMLFile(backupFile)
        except IOError:
            backupPath = os.path.dirname(backupFile)
            os.makedirs(backupPath)
            print('Creating backup directory ' + backupPath + '...')
            trajectories.SaveXMLFile(backupFile)
        'And update time checker'
        time1=time2+backupInterval

    'Create a copy of the image where the trajectories will be drawn'
    img=deepcopy(imgAux)
    'Draw the elements on the image. The element(s) drawn depends on which elements are selected'
    try:
        'Draw the node currently in edition'
        activeNode.drawNode(img)
        'In case of editing a node, check edit node mouse events'
        if mousePoints['p']==cv2.EVENT_MOUSEMOVE:
            activeNode.changeNodeCoordinates( \
                mousePoints['x'], mousePoints['y'])
            mousePoints['p']=-1
        elif mousePoints['p']==cv2.EVENT_LBUTTONDOWN:
            activeNode.createNode(True)
            mousePoints['p']=-1
        elif mousePoints['p']==cv2.EVENT_LBUTTONUP:
            activeNode.createNode(False)
            mousePoints['p']=-1

    except AttributeError:
        try:
            'If any node is in edit mode, draw the current selected trajectory'
            activeTrajectory.drawPath(img, (0x00, 0x00, 0x00), (0xFF, 0xFF, 0xFF))
            'and the node for the current frame'
            activeTrajectory.selectNode(frame).drawNode(img)
        except AttributeError:
            'Otherwise, draw all the trajectories'
            trajectories.drawPath(img, frame)
            trajectories.drawNode(img, frame)
            'In this state, we can be drawing the first point of a new node of a new'
            'trajectory, so we have to check it'
            if mousePoints['p']==cv2.EVENT_MOUSEMOVE:
                activeNode=EditNode(True, coord(mousePoints['x'], mousePoints['y']))
                mousePoints['p']=-1

    'Mark the current frame number in the window'
    cv2.putText(img, str(frame), (15, 30),  cv2.FONT_HERSHEY_DUPLEX, 1.0, (0xFF, 0xFF, 0xFF)) 
    cv2.imshow(windowTitle, img)
    c=cv2.waitKey(10) & 0xFF
    
    'Check if the user has double clicking on a trajectory'
    if mousePoints['p']==cv2.EVENT_LBUTTONDBLCLK:
        if activeTrajectory is None:
            activeTrajectory, activeID=trajectories.selectTrajectory(frame, mousePoints['x'], mousePoints['y'])
        mousePoints['p']=-1
    'Check the key pressed (if any).'
###############################################################################
    if c==ord('a'):
        'Set the saved check to false, to indicate that a modification has been done'
        saved=False
        'Add trajectory/node or edit node'
        cv2.setMouseCallback(windowTitle, mouseEditNode, mousePoints)
        try:
            'If we are currently editing a trajectory, add a new node (or modify node for the current frame)'
            node=activeTrajectory.selectNode(frame)
            coords=node.coords
            'Create a new node to edit node coordinates'
            try:
                activeNode=EditNode(False, coords['p1'], coords['p2'])
            except KeyError:
                activeNode=EditNode(False, coords['pos'])
        except AttributeError:
            pass
            'Add a new trajectory. Start creating a new node. It is enough to set the mouse handler.'
###############################################################################
    elif c==ord('d'):
        'Delete selected element'
        'Check the element to delete'
        if not activeNode is None:
            try:
                if activeTrajectory.deleteNodeCheck(frame):
                    print('Delete selected node (y/n)?')
                    if (cv2.waitKey(0) & 0xFF)==ord('y'):
                        'If we have an active node, try to delete it from the trajectory (if it exists)'
                        activeTrajectory.deleteNode(frame)
                        activeNode=None
            except AttributeError: pass
        else:
            try:
                if trajectories.deleteTrajectoryCheck(activeID):
                    print('Delete selected trajectory (y/n)?')
                    if (cv2.waitKey(0) & 0xFF)==ord('y'):
                        trajectories.deleteTrajectory(activeID)
                        activeTrajectory=None
                        activeID=0
                        'Set the saved check to false, to indicate that a modification has been done'
                        saved=False
            except KeyError: pass
###############################################################################
            'Change interpolation type'
    elif c==ord('1'):
        if activeTrajectory is not None:
            activeTrajectory.updateInterpolator('NI')
            saved=False
    elif c==ord('2'):
        if activeTrajectory is not None:
            activeTrajectory.updateInterpolator('LI')
            saved=False
    elif c==ord('3'):
        if activeTrajectory is not None:
            activeTrajectory.updateInterpolator('CS')
            saved=False
    elif c==ord('4'):
        if activeTrajectory is not None:
            activeTrajectory.updateInterpolator('GI')
            saved=False
    elif c==ord('5'):
        if activeTrajectory is not None:
            activeTrajectory.updateInterpolator('GC')  
            saved=False
    elif c==ord('6'):
        if activeTrajectory is not None:
            activeTrajectory.updateInterpolator('LM')  
            saved=False
###############################################################################
    elif c==ord('w'):
        'Write data to XML file'
        if saved:
            print('Nothing to save.')
            continue
        'Check if we have unsaved trajectories'
        if activeNode is None and activeTrajectory is None:
            try: trajectories.SaveXMLFile(annotationFile)
            except IOError:
                annotationPath = os.path.dirname(annotationFile)
                os.makedirs(annotationPath)
                print('Creating directory ' + annotationPath + '...')
                trajectories.SaveXMLFile(annotationFile)
            print('File ' + annotationFile + ' saved')
            saved=True
        else:
            print('Please, save changes (s key) before writing to a file.')
###############################################################################
    elif c==ord('o'):
        'Generate a xml file with all the trajectories complete'
        'Check if we have unsaved trajectories'
        if activeNode is None and activeTrajectory is None:
            trajectories.SaveXMLFile(annCompleteFile, True)
            print('Completed trajectories saved in ' + annCompleteFile)
        else:
            print('Please, save changes before writing to a file.')
###############################################################################
    elif c==ord('p'):
        'Extract blobs corresponding to all the nodes of the trajectories'
        if activeTrajectory is None:
            print('Extract blob for', len(trajectories.trajectories), 'trajectories (y/n)?')
            if (cv2.waitKey(0) & 0xFF)==ord('y'):
                'Extract blob for all the trajectories'
                for ID, trajectory in trajectories.trajectories.items():
                    printBlobs(video, trajectory, projectPath, ID)
                print('Blobs extracted for', len(trajectories.trajectories),'trajectories at', projectPath)
        else:
            'Extract blob only for selected trajectory'
            printBlobs(video, activeTrajectory, projectPath, activeID)
###############################################################################
    elif c==ord('v'):
        if activeNode is None and activeTrajectory is None:
            saveVideoResult(videoName, projectPath, trajectories)
        else:
            print('Please, save changes before savint the video.')
###############################################################################
    elif c==ord('s'):
        'Whenever we save the current edition, we need to set the mouse listener to node selection'
        cv2.setMouseCallback(windowTitle, mouseSelectNode, mousePoints)
        'Save edition of current trajectory (or current node)'
        try:
            'Check if we already have an active node.'
            nodeCoords=activeNode.nodeCoords
            'If so, capture its coordinates and create a new node'
            try:
                node=RectangleNode(frame, nodeCoords['pos'], nodeCoords['size'])
            except KeyError:
                node=PointNode(frame, nodeCoords['pos'])
            try:
                'Check if we are already editing a trajectory'
                activeTrajectory.addNode(node)
            except AttributeError:
                'If not, create a new one'
                activeTrajectory=Trajectory(node)
            activeNode=None
        except AttributeError:
            try:
                'If not, check if the user want to save the whole trajectory'
                trajectories.addTrajectory(activeTrajectory, activeID)
                activeTrajectory=None
                activeID=0
            except AttributeError: pass
            'Otherwise, the user pressed save without anything to save'
###############################################################################
    elif c==27:
        'Cancel edition of current trajectory'
        if activeNode is not None: 
            activeNode=None
        else: 
            activeTrajectory=None
            activeID=0
        cv2.setMouseCallback(windowTitle, mouseSelectNode, mousePoints)
###############################################################################
    elif c==ord('q'):
        'Close application'
        if activeNode is None and activeTrajectory is None:
            'Only close if no edition is in progress'
            if saved:
                'If there is no modification, exit'
                break
            print('Save file before exit (y/n/c)?')
            c=(cv2.waitKey(0) & 0xFF)
            if c==ord('y'):
                trajectories.SaveXMLFile(annotationFile)
                break
            elif c==ord('n'):
                break
        else:
            'Otherwise, warn the user to save changes before exit'
            print('Please, save changes before exit...')
###############################################################################
    elif c==ord('z') or c==ord('x'):
        if activeNode is None:
            'Video shift is only possible when no node is in edition'
            shift=(+1 if c==ord('x') else -1)
            frame+=shift
            'Check if we move outside video sequence'
            if frame<0: 
                frame=0
            if frame>=totalFrames:
                frame=totalFrames-1
            'Move along the video sequence'
            video.set(cv2.CAP_PROP_POS_FRAMES, frame)
            'Get the new required frame from the video'
            ret, imgAux=video.read();
            if not ret:
                print("Error Frame:", frame)
###############################################################################
    elif c==ord('i'):
        print('Trajectory ID: '+str(activeID))
###############################################################################
    elif c==ord('o'):
        print(trajectories.timeIndex)

print('End of program.')

