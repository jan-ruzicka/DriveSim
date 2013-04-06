#!/usr/bin/python
# Script to generate random walk on a network.
# @author Jan Ruzicka
#
from distutils import version
import json
import os
import re
import random
import copy
from StringIO import StringIO
import sys
from time import localtime, sleep, time
from datetime import datetime
from urllib2 import urlopen, Request
from xml.etree import ElementTree

start_time = time()

# id ->  {lat, long}
points = {}
# wayId -> [ pointId ]
way2points = {}
point2ways = {}
debugPrint = False
def main():
    """The main function"""
    readOsm('map.osm');

    writeKmlHead(bouds)
    #print 'point2ways: ', len(point2ways)
    myRandom = random.randrange(len(point2ways))
    #print 'random =', myRandom
    currPoint = point2ways.keys()[myRandom];
    currWayId = point2ways[currPoint][0]
    nextPoints = copy.deepcopy(way2points[currWayId])
    index = way2points[currWayId].index(currPoint)
    if index > 0 and index < len(way2points[currWayId])-1:
         if random.randrange(2) > 1:
              nextPoints = copy.deepcopy(way2points[currWayId][:(index-1)]).reverse()
         else:
              nextPoints = copy.deepcopy(way2points[currWayId][(index+1):])
    else:
        if index == 0:
            nextPoints = copy.deepcopy(way2points[currWayId])
        else:
            nextPoints = copy.deepcopy(way2points[currWayId]).reverse()
    for i in range(47):
       #name = "%3d pt %-10s" % ( i,currPoint)
       name = "%3d" % (i)
       description = "ID%-10s ways: %s" % (currPoint,str(point2ways[currPoint]))
       writeKmlPoint(name,description,points[currPoint])
       currWays = point2ways[currPoint]
       if len(currWays) > 1:
          if len(nextPoints) == 0:
              for wayId in currWays:
                 if wayId != currWayId:
                     newWayId = wayId
          else:
              newWayId = currWays[random.randrange(len(currWays))]
          if not newWayId == currWayId:
                currWayId = newWayId
                index = way2points[currWayId].index(currPoint)
                if debugPrint:
                    print '<!-- way: ',currWayId,' (',len(way2points[currWayId]),') index: ',index,' -->'
                if index > 0 and index < len(way2points[currWayId])-1:
                     if random.randrange(2) > 1:
                          nextPoints = copy.deepcopy(way2points[currWayId][:index])
                          nextPoints.reverse()
                     else:
                          nextPoints = copy.deepcopy(way2points[currWayId][index:])
                else:                    
                    nextPoints = copy.deepcopy(way2points[currWayId])
                    if index != 0:
                        nextPoints.reverse()
                nextPoints=nextPoints[1:]

       if debugPrint:
           print '<!-- nextPoints: ', len(nextPoints) , nextPoints, ' -->'
           print '<!-- way: ', currWayId,' ', len(way2points[currWayId]) , way2points[currWayId], ' -->'
       if len(nextPoints) == 0:
           index = way2points[currWayId].index(currPoint)
           nextPoints = copy.deepcopy(way2points[currWayId])
           if index != 0:
               nextPoints.reverse()
           nextPoints=nextPoints[1:]
           if debugPrint:
               print '<!-- nextPointsup: way', currWayId,' ', len(nextPoints) , nextPoints, ' -->'
       currPoint = nextPoints[0]
       nextPoints=nextPoints[1:]

    duration = int(time() - start_time)
    if debugPrint:
       print('\n<!-- Generated in %d min %d sec -->\n' % (duration/60, duration%60))
    writeKmlEnd()

### Helper methods
def getCoordPoint(lon,lat,alt='0'):
    return "%s,%s,%s"%(lon,lat,alt)
def getCoordPoint4point(point):
    return getCoordPoint(point['lon'],point['lat'])
def writeKmlHead(bouds):
    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<kml xmlns="http://www.opengis.net/kml/2.2">'
    print '<Document>'
    print '  <Placemark><name>Bounding box</name><visibility>0</visibility><Polygon><tessellate>1</tessellate><outerBoundaryIs><LinearRing>',
    print '<coordinates>',
    print getCoordPoint(bouds['minlon'],bouds['minlat']),
    print getCoordPoint(bouds['minlon'],bouds['maxlat']),
    print getCoordPoint(bouds['maxlon'],bouds['maxlat']),
    print getCoordPoint(bouds['maxlon'],bouds['minlat']),
    print getCoordPoint(bouds['minlon'],bouds['minlat']),
    print '</coordinates>',
    print '</LinearRing></outerBoundaryIs></Polygon></Placemark>'

def writeKmlPoint(name,description,point):
    print '  <Placemark><name>%s</name><description>%s</description><Point><coordinates>%s</coordinates></Point></Placemark>' % (name, description, getCoordPoint4point(point))

def writeKmlEnd():
    print '</Document>'
    print '</kml>'

def readOsm(file):
    global points
    global way2points
    global point2ways
    global bouds

    xml=ElementTree.parse(file)
    #<bounds minlat="39.1748000" minlon="-77.2909000" maxlat="39.2177000" maxlon="-77.2262000"/>
    for boundsNode in xml.findall('bounds'):
        bouds = boundsNode.attrib
    for node in xml.findall('node'):
        #print node
        points[node.attrib['id']] = {'lat':node.attrib['lat'],'lon':node.attrib['lon']}
        
    for way in xml.findall('way'):
        #print way
        # tag k="highway"
        isHighway = False
        for tag in way.findall('tag'):
            if 'k' in tag.attrib and tag.attrib['k']=="highway":
                isHighway = True
                break
        if not isHighway:
            continue
        #      <nd ref="49310132"/>
        for node in way.findall('nd'):
            id = node.attrib['ref']
            #print "nd:", id
            if way.attrib['id'] in way2points:
                way2points[way.attrib['id']].append(id)
            else:
                way2points[way.attrib['id']] = [id]
            if id in point2ways:
                point2ways[id].append(way.attrib['id'])
            else:
                point2ways[id] = [way.attrib['id']]

main()
