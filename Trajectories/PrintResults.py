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
    
    

        