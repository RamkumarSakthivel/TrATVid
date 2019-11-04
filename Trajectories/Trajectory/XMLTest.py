'''
Created on Feb 4, 2015

@author: pedro
'''

from .Node import coord, PointNode, RectangleNode

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

r=RectangleNode(10, 3, 4, 5, 6)
e=Element('prueba')
r.XMLData(e, 'rect')
print('fin')
