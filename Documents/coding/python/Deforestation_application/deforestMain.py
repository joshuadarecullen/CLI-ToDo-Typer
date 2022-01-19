#importing system modules to access the command line and operating system
import sys
import os
import os.path, shutil
import glob

#importing PyQgis and PyQt libraries
from qgis.gui import *
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from osgeo import gdal

#the GUI template
from ui_mainWindow import Ui_MainWindow

#importing the resources module
import resources
from constants import *
from mapTools import *
from dialogTools import *

#pyqt based application use multiply inheritance to include the ui template as a parent of the Deforestation application
#set up class for the main window. Inherits the object from PyQT Main Window and ui_mainWindow class

class DeforestationMapWindow(QMainWindow, Ui_MainWindow):
    #initialising, (basically a constructer) Whenever this class is called this method will.
    def __init__(self):
        QMainWindow.__init__(self) #initialising the inherited object, no need to inherit from the super class as importing the whole module
        self.setupUi(self) #initialising the setUPUI method from ui_mainWindow, and passing parent class to have access to window
   
        #connecting the action buttons to to the respective reference method when clicked
        self.connect(self.actionZoomIn, SIGNAL("triggered()"), self.zoomIn)
        self.connect(self.actionZoomOut, SIGNAL("triggered()"), self.zoomOut)
        self.connect(self.actionPanMode, SIGNAL("triggered()"), self.panMode)
        self.connect(self.actionEditMode, SIGNAL("triggered()"), self.setEditMode)
        self.connect(self.actionAddArea, SIGNAL("triggered()"), self.addArea)
        self.connect(self.actionEditArea, SIGNAL("triggered()"), self.editArea)
        self.connect(self.actionRemoveArea, SIGNAL("triggered()"), self.removeArea)
        self.connect(self.actionGetAreaInfo, SIGNAL("triggered()"), self.getAreaInfo)
        self.connect(self.actionAddLayer, SIGNAL("triggered()"), self.addLayer)
        self.connect(self.actionRemoveLayer, SIGNAL("triggered()"), self.removeLayer)
        self.connect(self.actionMapInfo, SIGNAL("triggered()"), self.getMapInfo)
        self.connect(self.actionPrint, SIGNAL("triggered()"), self.onPrint)
        
        #connecting a specfic method of the combo box, calling onSelectionChange method when the index of the mapCombo box has changed
        self.mapComboBox.currentIndexChanged.connect(self.onSelectionChange)
        
        #setting current directory
        self.cur_dir = os.path.dirname(os.path.realpath(__file__))
        
        #setting path of geoData directory in the cur_dir
        self.map_layers = os.path.join(self.cur_dir, "geoData")
        
        #creating list to store the current maps for use the the onPrint method
        self.layer_set = []
        
        #creating an instance of Qgs Map canvas and bringing to front
        self.mapCanvas = QgsMapCanvas()
        self.mapCanvas.useImageToRender(False)
        self.mapCanvas.setCanvasColor(Qt.white)
        self.mapCanvas.show()
        
        #setting the layout and adding the canvas
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mapCanvas)
        self.centralWidget.setLayout(layout)
    
        #bool variables for editing mode and vector data is modified
        self.editing  = False
        self.modified = False
    
#adjust the button's states
    def setButtonsStatus(self):
        if len(self.maps) > 0:
            self.actionEditMode.setEnabled(True)
            self.actionAddLayer.setChecked(False)
            self.actionRemoveLayer.setChecked(False)
            self.actionMapInfo.setChecked(False)
            self.actionPanMode.setEnabled(True)
            if self.editing:
                self.actionAddArea.setEnabled(True)
                self.actionRemoveArea.setEnabled(True)
                self.actionEditArea.setEnabled(True)
                self.actionGetAreaInfo.setEnabled(True)
                self.actionRemoveLayer.setEnabled(False)
                self.actionAddLayer.setEnabled(False)
                self.mapComboBox.setEnabled(False)
                self.actionMapInfo.setEnabled(False)
            else:
                self.actionAddArea.setEnabled(False)
                self.actionRemoveArea.setEnabled(False)
                self.actionEditArea.setEnabled(False)
                self.actionGetAreaInfo.setEnabled(False)
                self.actionZoomIn.setEnabled(True)
                self.actionZoomOut.setEnabled(True)
                self.actionRemoveLayer.setEnabled(True)
                self.actionAddLayer.setEnabled(True)
                self.actionMapInfo.setEnabled(True)
                self.mapComboBox.setEnabled(True)
        else:
            self.actionAddArea.setEnabled(False)
            self.actionRemoveArea.setEnabled(False)
            self.actionGetAreaInfo.setEnabled(False)
            self.actionEditMode.setEnabled(False)
            self.actionZoomIn.setEnabled(False)
            self.actionZoomOut.setEnabled(False)
            self.actionPanMode.setEnabled(False)
            self.actionRemoveLayer.setEnabled(False)
            self.actionMapInfo.setEnabled(False)
            self.mapComboBox.setEnabled(False)
    
#button event handlers
    #setting to the default map canvas zoom in/out method
    def zoomIn(self):
        self.mapCanvas.zoomIn()

    def zoomOut(self):
        self.mapCanvas.zoomOut()
    
    #setting to panTool instanstiated in set up map
    def panMode(self):
        self.mapCanvas.setMapTool(self.panTool)
    
    #edit mode button method for saving changes to the vector layer database
    def setEditMode(self):
        #if user in editing mode check if data been modified and prompt to save
        if self.editing:
            if self.modified:
                reply = QMessageBox.question(self, "Confirm", "Save Changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    #save changes
                     self.deforestObjectLayer.commitChanges()
                else:
                    #discard changes
                     self.deforestObjectLayer.rollBack()
            else:
                self.deforestObjectLayer.commitChanges()
            
            #forces update on of the map canvas
            self.deforestObjectLayer.triggerRepaint()
            self.editing = False
            self.panMode()
        else:
            
            #vector layer set to editing, force a update of the vector layer.
            self.deforestObjectLayer.startEditing()
            self.deforestObjectLayer.triggerRepaint()
            self.editing  = True
            self.modified = False
                                                                     
        self.setButtonsStatus()

#set the mapCanvas map tool to the custom map tools when user clicks on the repective button: add, edit, remove, getAreaInfo. making sure the respespective connected button is checked
    def addArea(self):
        if self.actionAddArea.isChecked():
            self.mapCanvas.setMapTool(self.addDeforestObject)
        else:
            self.panMode()
        self.setButtonsStatus()

    def editArea(self):
        if self.actionEditArea.isChecked():
            self.mapCanvas.setMapTool(self.editDeforestObject)
        else:
            self.panMode()
        self.setButtonsStatus()
    
    def removeArea(self):
        if self.actionRemoveArea.isChecked():
            self.mapCanvas.setMapTool(self.removeDeforestObject)
        else:
            self.panMode()
        self.setButtonsStatus()
            
    def getAreaInfo(self):
        if self.actionGetAreaInfo.isChecked():
            self.mapCanvas.setMapTool(self.getAreaInfoTool)
        else:
            self.panMode()

    def getMapInfo(self):
        mapDialog = MapDialog(self, self.deforestObjectLayer)
        if mapDialog.exec_():
            self.mapCanvas.refresh()
            self.setButtonsStatus()

#Adding .tif file
    def addLayer(self):
        if self.actionAddLayer.isChecked():
            #use of the the QFileDialog object to retrieve map
            filePath = QFileDialog.getOpenFileName(self, "." , "Image Files (*.tif)")
            
            #QFileInfo object to get the name of the file without the type
            fileInfo = QFileInfo(filePath)
            
            #check whether user collection is a tif file
            if ".tif" in filePath:
                currentMapName = fileInfo.baseName()
                
                #storing path .tif files to validate if they exits
                mapPathVal = os.path.join(self.cur_dir, "geoData", currentMapName + ".tif")
                
                mapPathVal1 = os.path.join(self.cur_dir, "geoData", currentMapName + "WGS84" + ".tif")
                
                #check if user added file exits
                if not os.path.exists(mapPathVal) | os.path.exists(mapPathVal1):
                    currentMapName = fileInfo.baseName()
                    ReprojectGeospatialFile().reprojectTifFile(mapPathVal1, filePath, self.onAddedLayer)
            
                else:
                    QMessageBox.about(self, "Map Already Exists", "Fix: %s" % "Rename" )
        
            #Stating to user what file type is need.
            elif len(filePath) < 3 | len(filePath) > 3:
                QMessageBox.about(self, "Error", "Fix: %s" % "Geo referenced .tif "  )

#remove layers from the application when the actionRemoveLayer is selected
    def removeLayer(self):
        #Throw message box to confirm the users selection of removing the map
        reply = QMessageBox.question(self, "Confirm", "Delete Layer?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        #clear map registry and remove the respective map form the geoData library
        if reply == QMessageBox.Yes:
            
            QgsMapLayerRegistry.instance().removeAllMapLayers()
            
            mapLayerPath = self.maps[self.mapComboBox.currentIndex()]
            mapName = os.path.splitext(os.path.basename(mapLayerPath))[0]
            
            #remove map layers from the current lay_set
            del self.layer_set[:]
            
            os.remove(mapLayerPath)
            os.remove(self.map_layers + "/" + mapName + ".sqlite")
            
            #up date the map comboBox and canvas of change
            self.setUpMapsComboBox()
            self.mapCanvas.refresh()
        
        self.setButtonsStatus()

#Change map to selected from the combo box
    def onSelectionChange(self):
        if len(self.maps) > 0:
            #retrieve the new map
            mapLayerPath = self.maps[self.mapComboBox.currentIndex()]
            mapName = os.path.splitext(os.path.basename(mapLayerPath))[0]
            
            #remove old layers from the map registry
            QgsMapLayerRegistry.instance().removeAllMapLayers()
            del self.layer_set[:]
            
            #set up and diasplay the layers
            self.setMapLayers(mapLayerPath, mapName)
            self.setVectorRenderer()
            self.setMapTools()
            self.mapCanvas.refresh()
    
###########completion of the map tools functions############

    def onGetAreaInfo(self, feature):
        #instatiating getAreaInforDialog to display feature
        dialog = getAreaInfoDialog(self, feature)
        dialog.loadAttributes(feature)
        if dialog.exec_():
            dialog.saveAttributes(feature)
            self.deforestObjectLayer.updateFeature(feature)
            self.modified = True
            self.mapCanvas.refresh()

    #call back funtion from AddedDeforestation MapTool.
    def onDeforestObjectAdded(self):
        self.modified = True
        self.mapCanvas.refresh()
        self.actionAddArea.setChecked(False)
        self.panMode()

    #call back function from RemoveDeforestOject MapTool
    def onDeforestObjectRemoved(self):
        self.modified = True
        self.mapCanvas.refresh()
        self.actionRemoveArea.setChecked(False)
        self.panMode()

    #call back function from the EditDeforestObject MapTool
    def onDeforestObjectEdited(self):
        self.modified = True
        self.mapCanvas.refresh()
    
    #call back function from the convertToTiff function
    def onAddedLayer(self, rasterLayer):
        #checking if reprojection failed
        vectorLayer = os.path.splitext(os.path.basename(rasterLayer))[0]
        if rasterLayer is not None:
            #set up new layer
            self.maps.append(rasterLayer)
            self.setUpDatabase(vectorLayer)
            self.setUpMapsComboBox()
            self.setButtonsStatus()
        else:
            QMessageBox.about(self, "Error", "Type: %s" % "No GeoReferencing Information" )

        self.actionAddLayer.setChecked(False)

#############################End###########################

#printing the layers combined to a pdf
    def onPrint(self):
        filePath = QFileDialog.getSaveFileName(self, "Save File", "", "PDF (*.pdf)")
        fileInfo = QFileInfo(filePath)
        imagePath = fileInfo.absolutePath()
        PrintMapCanvas(self.mapCanvas, self.layer_set, filePath)
    
    def setUpMapsComboBox(self):
        #setting a list of current maps and vector layers in the current directory
        self.maps = glob.glob(self.map_layers + "/*.tif")

        #clear combo box (when map is added//deleted)
        self.mapComboBox.clear()
        
        #checking for current maps and filling mapCombobox with map names
        if len(self.maps) > 0:
            for mapLayer in self.maps:
                #splitting the path name
                mapName = os.path.splitext(os.path.basename(mapLayer))[0]
                self.mapComboBox.addItem(mapName)
                self.mapComboBox.setEnabled(True)
  
    def setMapLayers(self, currentMapLayer, currentVectorDB):
        #layers array for storing rastermap and vector layer
        layers = []
        # Setup the area vector layer.
        uri = QgsDataSourceURI()
        uri.setDatabase(os.path.join(self.cur_dir, "geoData", currentVectorDB + ".sqlite"))
        uri.setDataSource("", currentVectorDB, "GEOMETRY")
        
        #using the QgsRasterLayer QgsVectorLayer class from the pyqgis core package, add to map registry
        self.deforestObjectLayer = QgsVectorLayer(uri.uri(), currentVectorDB, "spatialite")
        QgsMapLayerRegistry.instance().addMapLayer(self.deforestObjectLayer)
        
        self.rasterLayer = QgsRasterLayer(currentMapLayer, currentVectorDB)
        QgsMapLayerRegistry.instance().addMapLayer(self.rasterLayer)
 
        #Append layers list in correct positioning to process for display
        layers.append(QgsMapCanvasLayer(self.deforestObjectLayer))
        layers.append(QgsMapCanvasLayer(self.rasterLayer))
        
        #setting the layerset array to the current id's of the raster and vector layer
        self.layer_set.append(self.deforestObjectLayer.id())
        self.layer_set.append(self.rasterLayer.id())
        
        #Add all the layers to the map canvas.
        self.mapCanvas.setLayerSet(layers)
        self.mapCanvas.setExtent(self.rasterLayer.extent())


    #setting up the data base for the vector layer source
    def setUpDatabase(self, vectorName):
        #getting data base
        db_name = os.path.join(self.cur_dir, "geoData", vectorName + ".sqlite")
        
        #set up data base if one doesnt exist, making use of the class QgsFields create fields for the database
        if not os.path.exists(db_name):
            fields = QgsFields()
            fields.append(QgsField("name", QVariant.String))
            fields.append(QgsField("type", QVariant.String))
            fields.append(QgsField("defType", QVariant.String))
            fields.append(QgsField("date", QVariant.String))
            fields.append(QgsField("area", QVariant.Double))
            
            #the crs used is the same in which the raster layer is reprojected too
            crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
            
            # specific vector layer type WKBPolygon. Vector layer has to given a spefific type of geometry will be utiliased via the data base
            writer = QgsVectorFileWriter(db_name, "utf-8", fields, QGis.WKBPolygon, crs, "SQLite", ["SPATIALITE=YES"])
            
            if writer.hasError() != QgsVectorFileWriter.NoError:
                print "Error creating tracks database!"
            del writer

    # Setup the renderer for the vector layer.
    def setVectorRenderer(self):
        #for type of forest area
        areaColour = ""
        #for cause of deforestation
        areaFill = ""
        #clearing rule in the rule based renderer
        root_rule = QgsRuleBasedRendererV2.Rule(None)
        #looping through to get all the combinations of forest and deforesttaion types
        for area_type in (AREA_TYPE_DEFORESTED, AREA_TYPE_VUN, AREA_TYPE_REFORESTED):
            #setting repective colours depending on forest types
            if area_type == AREA_TYPE_DEFORESTED:
                areaColour = DEF_COLOUR
            elif area_type == AREA_TYPE_VUN:
                areaColour = VUN_COLOUR
            elif area_type == AREA_TYPE_REFORESTED:
                areaColour = REF_COLOUR
                #setting colours for the pattern fill for the types of deforestation
            for def_type in (DEF_TYPE_DEFORESTATION, DEF_TYPE_FORESTFRAGMENTATION, DEF_TYPE_FORESTDEGRADATION):
                if def_type == DEF_TYPE_DEFORESTATION:
                    areaFill = DEFF_COLOUR
                if def_type == DEF_TYPE_FORESTFRAGMENTATION:
                    areaFill = FRAG_COLOUR
                if def_type == DEF_TYPE_FORESTDEGRADATION:
                    areaFill = DEG_COLOUR
                #create symbol
                areaFeatureSymbol = self.createAreaSymbol(areaColour, areaFill)
                #set filter for the rule based renderer
                areaExpression = ("(type='%s') and " + "(defType='%s')") % (area_type, def_type)
                areaDisplayRule = QgsRuleBasedRendererV2.Rule(areaFeatureSymbol, filterExp=areaExpression)
                #adding set symbol design to the renderer root renderer
                root_rule.appendChild(areaDisplayRule)
                    
        #creating the QgsRuleBasedRendererV2 object and setting the rule
        renderer = QgsRuleBasedRendererV2(root_rule)
        #setting the vector layer renderer
        self.deforestObjectLayer.setRendererV2(renderer)

#creating and setting the smybol colours
    def createAreaSymbol(self, areaColour, areaFill):
    
        #creating fill symbol object
        areaFeatureSymbol = QgsFillSymbolV2()
        areaFeatureSymbol.deleteSymbolLayer(0)
    
        #the outline for the type of forest
        areaOutlineSymbol = QgsSimpleFillSymbolLayerV2()
        areaOutlineSymbol .setFillColor(QColor(0, 0, 0, 0))
        areaOutlineSymbol .setBorderColor(QColor(areaColour))
        areaOutlineSymbol .setBorderWidth(0.9)
        areaFeatureSymbol.appendSymbolLayer(areaOutlineSymbol )
        
        #line pattern fill for deforestation type
        areaPatternSymbol = QgsLinePatternFillSymbolLayer()
        areaPatternSymbol.setColor(QColor(areaFill))
        areaPatternSymbol.setLineWidth(2)
        areaPatternSymbol.setDistance(6)
        areaPatternSymbol.setLineAngle(40)
        areaFeatureSymbol.appendSymbolLayer(areaPatternSymbol)
        
        return areaFeatureSymbol

    #initialing and linking the map tool objects: PanTool, AddDeforestObject, RemoveDeforestObject, EditDeforestObject, GetAreaInfoTool classes from mapTools.py to the GUI button actions
    def setMapTools(self):
        
        self.panTool = PanTool(self.mapCanvas)
        self.panTool.setAction(self.actionPanMode)
        
        self.addDeforestObject = AddDeforestObject(self.mapCanvas, self.deforestObjectLayer, self.onDeforestObjectAdded)
        self.addDeforestObject.setAction(self.actionAddArea)
        
        self.removeDeforestObject = RemoveDeforestObject(self.mapCanvas, self.deforestObjectLayer, self.onDeforestObjectRemoved)
        self.removeDeforestObject.setAction(self.actionRemoveArea)
        
        self.editDeforestObject = EditDeforestObject(self.mapCanvas, self.deforestObjectLayer, self.onDeforestObjectEdited)
        self.editDeforestObject.setAction(self.actionEditArea)
        
        self.getAreaInfoTool = GetAreaInfoTool(self.mapCanvas, self.deforestObjectLayer, self.onGetAreaInfo)
        self.getAreaInfoTool.setAction(self.actionGetAreaInfo)


class ReprojectGeospatialFile(QObject):
    
    #Reprojection on the added image
    def reprojectTifFile(self, projectedMap, fileName, onAddedLayer):
        
        #Open .tif - gdal will automatically assign correct driver: raster format
        src_ds = gdal.Open(fileName)
        
        #if geoReferencing information is not contained projection will fail
        try:
            #Create the final warped image
            gdal.Warp(projectedMap ,src_ds, dstSRS='EPSG:4326')
        except:
            onAddedLayer("","")
        #on success of the warp send path and name of for the raster layer
        else:
            onAddedLayer(projectedMap)

class PrintMapCanvas(QObject):
    
    def __init__(self, mapCanvas, layer_set, imageName):
    
        comp, mapSettings = self.create_composition(layer_set, mapCanvas.extent())
        
        #set sytle for printering map
        comp.setPlotStyle(QgsComposition.Print)
        
        #using pyqgis map composer class
        composerMap = QgsComposerMap(comp, 5,5,200,200)
        
        #Uses mapsettings value
        composerMap.setNewExtent(mapSettings.extent())
        
        comp.addItem(composerMap)
        #use QPrinter to print the file for map to be printed on
        printer = QPrinter()
        #set format
        printer.setOutputFormat(QPrinter.PdfFormat)
        #set location of output
        printer.setOutputFileName(imageName)
        #setting size, colour and print seolution of the image
        printer.setPaperSize(QSizeF(comp.paperWidth(), comp.paperHeight()),    QPrinter.Millimeter)
        printer.setFullPage(True)
        printer.setColorMode(QPrinter.Color)
        printer.setResolution(comp.printResolution())
        
        #set object painter with the set out size
        pdfPainter = QPainter(printer)
        
        paperRectMM = printer.pageRect(QPrinter.Millimeter)
        paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
        comp.render(pdfPainter, paperRectPixel, paperRectMM)
        pdfPainter.end()
    
    def create_composition(self, layer_list, extent):
        
        #set the compition extent to that of the current extent of the map canvas
        mapSettings = QgsMapSettings()
        mapSettings.setLayers(layer_list)
        mapSettings.setExtent(extent)
        comp = QgsComposition(mapSettings)
        #return map settings and composition for printing
        return comp, mapSettings


def main():
    
    #instance of qt application
    app = QApplication(sys.argv)
    # supply path to qgis install location where the resources are stored
    # setting the second argument to True enables the GUI
    QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX'], True) #initialising the pyQgis environment
    # This line is providing a path to Qt telling it to look here for plugins
    # load providers
    QgsApplication.initQgis()
    
    #creating instance of the class, this sets up the main window, contains the map canvas and contains the event handlers.
    
    deforestMapWindow = DeforestationMapWindow()
    deforestMapWindow.show()
    deforestMapWindow.raise_()
    
    #filling the current map combo box
    deforestMapWindow.setUpMapsComboBox()
    deforestMapWindow.setButtonsStatus()
    #executing Qt application until user quites
    app.exec_()
    
    deforestMapWindow.close()
    #removes the provider and layer registries from memory
    QgsApplication.exitQgis()
    #issues when deleting an object
    app.deleteLater()

if __name__ == "__main__":
    main()

