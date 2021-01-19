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


import math
import fileinput
'Directory character separator'
import os
'Access program arguments'
import sys
'XML support'
from xml.etree import ElementTree

from TrATVid.Trajectory.Trajectory import CreateTrajectoryFromXML

def findBin(value):
    'Compute the histogram bin that corresponds to a given value'
    'In this case, implement a logarithmic x scale.'
    'NOTE: To get more samples of the histogram, include a constant'
    'multiplying the log value, and conversely, dividing in the'
    'opposite function'
    #binValue=int(2.0*math.log(value, 2))
    binValue=int(math.log(value, 2))
    return binValue

def valueOfBin(binValue):
    'Inverse function of the previous one'
    #value=int(math.pow(2, binValue/2.0))
    value=int(math.pow(2, binValue))
    return value

def fillHistogram(value, histogram):
    try: binValue=findBin(value)
    except ValueError: return
    
    try: 
        if binValue>histogram['max']:
            histogram['max']=binValue
    except KeyError:
        histogram['max']=binValue
        
    try: histogram[binValue]+=1
    except KeyError:histogram[binValue]=1

'''
Program start
'''
durationHist={}
lengthHist={}
occlusionHist={}

'Open program settings'
try:
    settingsFile=sys.argv[1]
except IndexError:
    settingsFile='settings.xml'
    
settings=ElementTree.parse(settingsFile)
'Read file with the list of annotations to evaluate'
projectPath=settings.find('video').attrib['path']
xmlPath=settings.find('xml').attrib['directory']
'Build the name of the file with all the annotations'
listFile=projectPath+os.sep+xmlPath+os.sep+'xmlList'

timeIndex={0:0}
end=0
start=0

csvFrameRate=open(projectPath+os.sep+xmlPath+os.sep+"frameRate.csv", 'w')

'Read annotation files'
for annFile in fileinput.input(listFile):
    annFile=annFile.strip();
    print("Reading "+annFile)

    'Read data structure from XML file'
    'NOTE: use the strip function to remove the trailing \n code of the line'
    XMLElement=ElementTree.parse(annFile)

    for XMLTrajectories in XMLElement.findall('Trajectory'):
        'Read trajectory ID'
        finish=False
        try:
            ID=int(XMLTrajectories.attrib['ID'])
            finish=True
        except KeyError:
            'Unfinished trajectories'
            pass
        'Read trajectory nodes'
        XMLTrajectory=XMLTrajectories.find('TrajectoryNodes')
        trajectory=CreateTrajectoryFromXML(XMLTrajectory)
        
        'Take the time stamp of the first trajectory that starts in a given'
        'time. Ignore the rest of trajectories that starts in this time.'
        'NOTE: The trajectories are stored ordered by starting time, so it is'
        'enough detecting when the trajectory starting time changes'
        'However, for multiple xml files, unfinished trajectories can be'
        'stored in more than one file. In this case, trajectories with'
        'smaller starting time can appear. It is enough ignoring those'
        'trajectories'
        if trajectory.start>end:
            end=trajectory.start
            time=int(XMLTrajectories.attrib['time'])
            while end-start>=9:
                try: elapsed=time-timeIndex[start]
                except KeyError:
                    pass
                else:
                    fr=(10000*(end-start))/elapsed
                    csvFrameRate.write(str(start)+','+str(fr)+'\n')
                    del timeIndex[start]
                start+=1
            timeIndex[end]=time
            
        'Unfinished trajectories are trajectories that will be opened in the next'
        'file. So, just ignore it in this iteration'
        if not finish: continue
        fillHistogram(trajectory.duration(), durationHist)
        fillHistogram(trajectory.length(), lengthHist)
        fillHistogram(trajectory.occludedLength(), occlusionHist)

cvsDuration=open(projectPath+os.sep+xmlPath+os.sep+"duration.csv", 'w')
for i in xrange(0,durationHist['max']+1):
    cvsDuration.write(str(durationHist.get(i, 0))+',')
cvsDuration.write('\n')
for i in xrange(0,durationHist['max']+1):
    cvsDuration.write(str(valueOfBin(i))+',')
cvsDuration.close()

cvsLength=open(projectPath+os.sep+xmlPath+os.sep+"length.csv", 'w')
for i in xrange(0,lengthHist['max']+1):
    cvsLength.write(str(lengthHist.get(i, 0))+',')
cvsLength.write('\n')
for i in xrange(0,lengthHist['max']+1):
    cvsLength.write(str(valueOfBin(i))+',')
cvsLength.close()

cvsOcclusion=open(projectPath+os.sep+xmlPath+os.sep+"occlusion.csv", 'w')
for i in xrange(0,occlusionHist['max']+1):
    cvsOcclusion.write(str(occlusionHist.get(i, 0))+',')
cvsOcclusion.write('\n')
for i in xrange(0,occlusionHist['max']+1):
    cvsOcclusion.write(str(valueOfBin(i))+',')
cvsOcclusion.close()

print('Results saved at', projectPath+os.sep+xmlPath)
