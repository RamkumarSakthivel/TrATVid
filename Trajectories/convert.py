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


from .Trajectory.Trajectory import Trajectory
from .Trajectory.Node import RectangleNode, coord

def createNode(stringNode):
    node=stringNode.split()
    t=node[1]
    x=node[2]
    y=node[3]
    h=node[5]
    w=node[6]
    T=int(t[1:])
    X=int(x[1:])
    Y=int(y[0:])
    H=int(h[1:])
    W=int(w[0:])
    pos=coord(X, Y)
    size=coord(2*H, 2*W)
    n=RectangleNode(T, pos, size)
    return n

def convert(path):
    f=open(path+'annotation')
    f.readline()
    f.readline()
    s=f.readline().split('S')
    del s[0]
    node=createNode(s[0])
    tr=Trajectory(node)
    del s[0]
    for n in s:
        node=createNode(n)
        tr.addNode(node)
    return tr
        
