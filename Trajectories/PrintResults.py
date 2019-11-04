'''
Created on Feb 12, 2015
function to print or get results from the application
@author: pedro
'''

'Create new directories'
import os
'Opencv'
import cv2

def printBlobs(video, trajectory, path, ID):
    'Create directory for all the images'
    blobPath='%s%03i' % (path, ID)
    try:os.makedirs(blobPath)
    except OSError: pass
    'Set the video at the beginning of the trajectory'
    for fr in range(trajectory.start, trajectory.end+1):
        video.set(cv2.CAP_PROP_POS_FRAMES, fr)
        ret, imgFr=video.read()
        del ret
        node=trajectory.selectNode(fr)
        blob=node.extractBlob(imgFr)
        imgName='%s%s%04i.png' % (blobPath, os.sep, fr)
        cv2.imwrite(imgName, blob)


def saveVideoResult(videoInName, path, trajectories):
    'Save an augmented video as a sequence of images'
    videoIn=cv2.VideoCapture(str(path+videoInName))
    'Create directory for the images'
    imagePath=path+'video'
    try:os.makedirs(imagePath)
    except OSError: pass
    
    print('Generating video. Please, wait...')
    frame=0
    ret, img=videoIn.read()
    while (ret):
        'Draw trajectories in the image'
        trajectories.drawPath(img, frame)
        trajectories.drawNode(img, frame)
        'Generate image name'
        imageName=imagePath+'%simg%05i.jpg' % (os.sep, frame)
        cv2.imwrite(imageName, img)
        ret, img=videoIn.read()
        frame+=1
        if frame%100==0: print('Frame '+str(frame))
    
    videoIn.release();
    print('Enhanced video saved on '+path)
    
    

        