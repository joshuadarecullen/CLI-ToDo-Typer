#Access to Qt library
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#importing the images for the buttons
import resources

class Ui_MainWindow(object):
    
    #passed in deforestationWindow
    def setupUi(self, window):
        
        window.setWindowTitle("Deforestation Monitoring Application")

        #creating a central widget to hold map canvas
        self.centralWidget = QWidget(window)
        self.centralWidget.setMinimumSize(900, 500)
        window.setCentralWidget(self.centralWidget)
      
        #setiing combo box for the maps
        self.mapComboBox = QComboBox(window)
        self.mapComboBox.setEnabled(False)
        
        #setting the tool bar object and a child of QMainWindow
        self.toolbar = QToolBar(window)
        
        #adding to the tool bar to the window
        window.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        #add options to the menu bar
        self.menuBar = window.menuBar()
        self.fileMenu = self.menuBar.addMenu("File")
        self.mapMenu = self.menuBar.addMenu("Map")
        
        #creating QAction objects
        
        #buttons set to checkable, setting image of the button to the compiled png image.
        
        self.actionPrint = QAction("Print Map: PDF", window)
        
        buttonIcon = QIcon(":/resources/zoomIn.png")
        self.actionZoomIn = QAction(buttonIcon, "Zoom In", window)
        self.actionZoomIn.setShortcut(QKeySequence.ZoomIn)

        buttonIcon = QIcon(":/resources/zoomOut.png")
        self.actionZoomOut = QAction(buttonIcon, "Zoom Out", window)
        self.actionZoomOut.setShortcut(QKeySequence.ZoomOut)

        buttonIcon = QIcon(":/resources/panMode.png")
        self.actionPanMode = QAction(buttonIcon, "Pan", window)
        self.actionPanMode.setCheckable(True)

        icon = QIcon(":/resources/editMode.png")
        self.actionEditMode = QAction(icon, "Edit", window)
        self.actionEditMode.setCheckable(True)
        
        buttonIcon = QIcon(":/resources/getInfo.png")
        self.actionGetAreaInfo = QAction(buttonIcon, "Get Info", window)
        self.actionGetAreaInfo.setCheckable(True)
        
        buttonIcon = QIcon(":/resources/drawArea.png")
        self.actionAddArea = QAction(buttonIcon, "Draw Area", window)
        self.actionAddArea.setCheckable(True)
        
        buttonIcon = QIcon(":/resources/drawPolygon.png")
        self.actionEditArea = QAction(buttonIcon, "Edit Area", window)
        self.actionEditArea.setCheckable(True)
        
        buttonIcon = QIcon(":/resources/remove.png")
        self.actionRemoveArea = QAction(buttonIcon, "Remove Area", window)
        self.actionRemoveArea.setCheckable(True)
        
        buttonIcon = QIcon(":/resources/addLayer.png")
        self.actionAddLayer = QAction(buttonIcon, "Add Layer", window)
        self.actionAddLayer.setCheckable(True)
        
        buttonIcon = QIcon(":/resources/removeLayer.png")
        self.actionRemoveLayer = QAction(buttonIcon, "Remove Layer", window)
        self.actionRemoveLayer.setCheckable(True)
        
        buttonIcon = QIcon(":/resources/mapInfo.png")
        self.actionMapInfo = QAction(buttonIcon, "Map Info", window)
        self.actionMapInfo.setCheckable(True)
        
        #adding the QAction objects and widgets to the respective bars
        
        self.fileMenu.addAction(self.actionRemoveArea)
        self.fileMenu.addAction(self.actionRemoveLayer)
        
        self.mapMenu.addAction(self.actionPrint)
        self.mapMenu.addAction(self.actionZoomIn)
        self.mapMenu.addAction(self.actionZoomOut)
        self.mapMenu.addAction(self.actionPanMode)
        self.mapMenu.addAction(self.actionEditMode)
        
        #grouping actions with addSeparator
        self.toolbar.addAction(self.actionZoomIn)
        self.toolbar.addAction(self.actionZoomOut)
        self.toolbar.addAction(self.actionPanMode)
        self.toolbar.addAction(self.actionEditMode)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionGetAreaInfo)
        self.toolbar.addAction(self.actionAddArea)
        self.toolbar.addAction(self.actionEditArea)
        self.toolbar.addAction(self.actionRemoveArea)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionAddLayer)
        self.toolbar.addAction(self.actionRemoveLayer)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionMapInfo)
        self.toolbar.addWidget(self.mapComboBox)
        
        #resize to fit new content
        window.resize(window.sizeHint())

