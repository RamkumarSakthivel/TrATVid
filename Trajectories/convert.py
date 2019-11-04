'''
Created on Oct 8, 2015

@author: pedro
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
        
