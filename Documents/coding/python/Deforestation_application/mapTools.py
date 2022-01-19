#importing the various libraries needed
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from constants import *
import sys
import os
import math

#special mixin class with helper methods for deforestation custom maps tools
class CustomMapToolMixin:
    
    #set reference to current layer for use on custom map tools
    def setCurrentLayer(self, currentLayer):
        self.currentLayer = currentLayer
    
    #converts current mouse position and(pixel coordinates) of the screen into the map and layer coordinate system and transforms
    def convertCoordinates(self, screenPoint):
        return (self.toMapCoordinates(screenPoint), self.toLayerCoordinates(self.currentLayer, screenPoint))

    #calculate the tolerance for allowing minor error margin for when the user clicks on the map canvas, 5 screen pixels apart.
    def calcTol(self, position):
        point1 = QPoint(position.x(), position.y())
        point2 = QPoint(position.x() + 5, position.y())
        
        mapPoint1,layerPoint1 = self.convertCoordinates(point1)
        mapPoint2,layerPoint2 = self.convertCoordinates(point2)
        tolerance = layerPoint2.x() - layerPoint1.x()
        
        return tolerance

#find the selected feaeture
    def findFeatureAt(self, position):
        mapPoint,layerPoint = self.convertCoordinates(position)
        tolerance = self.calcTol(position)
        
        #checking in the created tolerance grid
        toleranceRect = QgsRectangle(layerPoint.x() - tolerance,
                                  layerPoint.y() - tolerance,
                                  layerPoint.x() + tolerance,
                                  layerPoint.y() + tolerance)
                                  
        #find first deforestation area feature in rectangle
        request = QgsFeatureRequest()
        request.setFilterRect(toleranceRect)
        request.setFlags(QgsFeatureRequest.ExactIntersect)
            
        for feature in self.currentLayer.getFeatures(request):
            return feature
            
        return None
    
#finds area feature's closest vertex to the click point of the user
    def findVertexAt(self, feature, position):
        
        mapPoint,layerPoint = self.convertCoordinates(position)
        tolerance     = self.calcTol(position)
        
        #calculate the closet feature to the click point using the area features geometry closetvertex
        vertexCoord,vertex,prevVertex,nextVertex,vertexDifference = \
            feature.geometry().closestVertex(layerPoint)

        vertexDifference = math.sqrt(vertexDifference)
        
        #checking area feature within tolerance
        if vertexDifference > tolerance:
            return None
        else:
            return vertex

#The subclasses of maptool

#inherits from QgqMapTool and directly manipulates the map canvas
class PanTool(QgsMapTool):
    
    #initialise the map tool and set tool to use a cross qt hand cursor
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.setCursor(Qt.OpenHandCursor)
        self.dragging = False
    
    #respond to the canvas event
    def canvasMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.canvas().panAction(event)

    #respond when the user releases the mouse
    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.canvas().panActionEnd(event.pos())
            self.dragging = False

#adding of a deforestation area feature
class AddDeforestObject(QgsMapTool, CustomMapToolMixin):
    
    #initisaling the map canvas, current layer, and finish call function
    def __init__(self, canvas, currentLayer, onDeforestObjectAdded):
        
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.onDeforestObjectAdded = onDeforestObjectAdded
        #canvas rubberBand to visualize drawing of area
        self.rubberBand = None
        self.tempRubberBand = None
        
        #array to capture the points
        self.recordedPoints = []
        
        #bool representing capturing mode
        self.recording = False
        
        #set the current vector layer
        self.setCurrentLayer(currentLayer)
        self.setCursor(Qt.CrossCursor)
    
    #check user type of click to respond repectively
    def canvasReleaseEvent(self, event):
        #left click start capturing the points
        if event.button() == Qt.LeftButton:
            #check whether in recording mode
            if not self.recording:
                self.startRecording()
            #add users selected point
            self.addAreaPoint(event.pos())
        #stop caturing and get the captured area points
        elif event.button() == Qt.RightButton:
            #gets recorded users selected points
            points = self.getRecordedPoints()
            #stop recording
            self.stopRecording()
            #check to see if user captured any points
            if points != None:
                self.pointsRecorded(points)

    #responds to whenever user moves mouse, updates the tempRubberband to display the polygon to the moved position
    def canvasMoveEvent(self, event):
        if self.tempRubberBand != None and self.recording:
            mapPoint,layerPt = self.convertCoordinates(event.pos())
            self.tempRubberBand.movePoint(mapPoint)

    #catching key press event
    def keyPressEvent(self, event):
        #pyQGIS by default uses back space and delete key to delete the currently selected feature, event dot ignore
        #checking if user pressed repective button
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
            #delete last vertex of the recorded polygon
            self.deleteAreaPoint()
            event.ignore()

#starting capturing the users selected area points
    def startRecording(self):
        color = QColor("red")
        color.setAlphaF(0.78)
        
        #rubberBand is set up (width and colour to the canvas and the geometry type: polygon)
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubberBand.setWidth(2)
        self.rubberBand.setColor(color)
        self.rubberBand.show()
        
        #tempRubberBand is set up, displays a dotted line when user is setting more than one point
        self.tempRubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
        self.tempRubberBand.setWidth(2)
        self.tempRubberBand.setColor(color)
        self.tempRubberBand.setLineStyle(Qt.DotLine)
        self.tempRubberBand.show()
        
        #current capturing
        self.recording = True

#when user stops drawing the polygon
    def stopRecording(self):
        
        if self.rubberBand != None:
            self.canvas.scene().removeItem(self.rubberBand)
            self.rubberBand = None
        
        if self.tempRubberBand != None:
            self.canvas.scene().removeItem(self.tempRubberBand)
            self.tempRubberBand = None
        
        #reset variables
        self.recording = False
        self.recordedPoints = []
        self.canvas.refresh()

#adds the users clicked point
    def addAreaPoint(self, canvasPoint):
        #retrives map and layer coordinates of the users click
        mapPoint, layerPoint = self.convertCoordinates(canvasPoint)
        #adds the map layer coordinate to the rubberpant, records the currenlt captured geometry layer coordinate
        self.rubberBand.addPoint(mapPoint)
        
        self.recordedPoints.append(layerPoint)
        
        #resets the temp rubber band
        self.tempRubberBand.reset(QGis.Polygon)
        
        #set the start point of the currently recorded geometry
        startPoint = self.rubberBand.getPoint(0, 0)
        
        #update the tempRubberBand
        self.tempRubberBand.addPoint(startPoint)
        self.tempRubberBand.movePoint(mapPoint)
        self.tempRubberBand.addPoint(mapPoint)
   
   #delete the previous add area point
    def deleteAreaPoint(self):
        
        if not self.recording:
            return
        #getting the amount of vertices captured by both rubber boths
        numAreaPoints = self.rubberBand.numberOfVertices()
        tempAreaPoints = self.tempRubberBand.numberOfVertices()
        numberPoints = len(self.recordedPoints)
        
        #return if not enough points are recorded
        if numAreaPoints < 1 or numberPoints < 1:
            return
        #remove point from rubberband
        self.rubberBand.removePoint(-1)
        #moves point of tempRubberBand to the point before the last removed point.
        if numAreaPoints > 1:
            if tempAreaPoints > 1:
                point = self.rubberBand.getPoint(0, numAreaPoints-2)
                self.tempRubberBand.movePoint(tempAreaPoints-2, point)
        else:
            self.tempRubberBand.reset(QGis.Polygon)
        #delete from recorded point from list
        del self.recordedPoints[-1]

#gets the recorded area points, checks whether user added enough
    def getRecordedPoints(self):
        pointsCoordinates = self.recordedPoints
        if len(pointsCoordinates) < 3:
            return None
        else:
            #close polygon
            pointsCoordinates.append(pointsCoordinates[0])
        return pointsCoordinates
            
    #finished recording polygon
    def pointsRecorded(self, newPolygon):
        #data provider for the vector layer to store the polygon
        fields = self.currentLayer.dataProvider().fields()
        #create geomtry type polygon and pass recorded polygon
        geometry = QgsGeometry.fromPolygon([newPolygon])
        #calculate are for polygon
        area = self.calculateArea(newPolygon)
        #create new QgsFeature object
        feature = QgsFeature()
        #set the geomtetry
        feature.setGeometry(geometry)
        feature.setFields(fields)
    
        #set default attributes for the feature
        feature.setAttribute("name", "New Area")
        feature.setAttribute("type", AREA_TYPE_DEFORESTED)
        feature.setAttribute("defType", DEF_TYPE_DEFORESTATION)
        feature.setAttribute("date", "default")
        feature.setAttribute("area", area)
        
        #add new deforestation feature to the area
        self.currentLayer.addFeature(feature)
        self.currentLayer.updateExtents()
        #trigger repaint of the
        self.currentLayer.triggerRepaint()
        #call back function
        self.onDeforestObjectAdded()

#using the PyQGIS geospatial analysis class
    def calculateArea(self, polygon):
        #set up the area calculator class
        calculator = QgsDistanceArea()
        #set the ellipsoid to the coordinate reference of the vector layer
        calculator.setEllipsoid('WGS84')
        calculator.setEllipsoidalMode(True)
            #are in squared kilometers
        calculator.computeAreaInit()
        area = calculator.measurePolygon(polygon)
        round(area, 2)
        return area


#removing selected deforestation area feature by id from vector layer
class RemoveDeforestObject(QgsMapTool, CustomMapToolMixin):
    #set variables for areaFeatureId, call back function, current layer and cursor type
    def __init__(self, canvas, currentLayer, onDeforestObjectRemoved):
        QgsMapTool.__init__(self, canvas)
        self.onDeforestObjectRemoved = onDeforestObjectRemoved
        self.areaFeatureId = None
        self.setCurrentLayer(currentLayer)
        self.setCursor(Qt.CrossCursor)
   
   #getting the users selected feature via findFeatureAt
   
    def canvasPressEvent(self, event):
        areaFeature = self.findFeatureAt(event.pos())
        if areaFeature != None:
            #get id for deletion
            self.areaFeatureId = areaFeature.id()
        else:
            self.areaFeatureId  = None

    #delete on release of mouse
    def canvasReleaseEvent(self, event):
        areaFeature = self.findFeatureAt(event.pos())
        if areaFeature != None and areaFeature.id() == self.areaFeatureId:
            self.currentLayer.deleteFeature(areaFeature.id())
            self.onDeforestObjectRemoved()

#the user edting a currernt deforestation area geometry
class EditDeforestObject(QgsMapTool, CustomMapToolMixin):
    #intialising call back funtion, feature, point and reference to canvas.
    #to keep track of the user dragging the bool variable is used
    def __init__(self, canvas, currentLayer, onDeforestObjectEdited):
        QgsMapTool.__init__(self, canvas)
        self.onDeforestObjectEdited = onDeforestObjectEdited
        self.dragging = False
        self.feature = None
        self.areaVertex = None
        #setting the current layer and cursor type
        self.setCurrentLayer(currentLayer)
        self.setCursor(Qt.CrossCursor)
    
    #check the user moving, pressing and releasing the mouse of the map canvas
    
    #check for when user clicks on map canvas
    def canvasPressEvent(self, event):
        
        #find clicked on derforestation feature and vertex of that feature with the use of the helper methods inherited
        feature = self.findFeatureAt(event.pos())
        if feature == None:
            return
        areaVertex = self.findVertexAt(feature, event.pos())
        if areaVertex == None:
            return
        
        # if the user left click move point of set deforestation area feature, setting dragging to true so dont edit non selected area feature
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.feature = feature
            self.areaVertex = areaVertex
            self.newVertex(event.pos())
            self.canvas().refresh()

    #check if user editing area and set edited geomtry
    def canvasMoveEvent(self, event):
        if self.dragging:
            #replace geomtry
            self.newVertex(event.pos())
            self.canvas().refresh()

    #set new geometry of the deforestation area when user releases
    def canvasReleaseEvent(self, event):
        if self.dragging:
            self.newVertex(event.pos())
            self.currentLayer.updateExtents()
            self.canvas().refresh()
            self.dragging = False
            self.feature = None
            self.areaVertex = None

    #sets new point of users mouse position when click on a feature
    def newVertex(self, position):
        #seet geometry type
        geometry = self.feature.geometry()
        #get layer coordinates of mouse
        layerPoint = self.toLayerCoordinates(self.currentLayer, position)
        #move selected point for editing
        geometry.moveVertex(layerPoint.x(), layerPoint.y(), self.areaVertex)
        #update the deforesation area feature to new position
        self.currentLayer.changeGeometry(self.feature.id(), geometry)
        #call back function
        self.onDeforestObjectEdited()

#selecting the deforestation area feature for viewing of attributes
class GetAreaInfoTool(QgsMapTool, CustomMapToolMixin):
    #set the current vector layer and call back function
    def __init__(self, canvas, currentLayer, onGetAreaInfo):
        QgsMapTool.__init__(self, canvas)
        self.onGetAreaInfo = onGetAreaInfo
        self.setCurrentLayer(currentLayer)
        self.setCursor(Qt.WhatsThisCursor)
    
    #simple using findfeature at to get the users selected deforestation are image
    def canvasReleaseEvent(self, event):
        if event.button() != Qt.LeftButton: return
        feature = self.findFeatureAt(event.pos())
        if feature != None:
            self.onGetAreaInfo(feature)


