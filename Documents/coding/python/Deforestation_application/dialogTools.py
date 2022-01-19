from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import os
from constants import *

#Dialog for displaying the map information
class MapDialog(QDialog):
    #Class initializer
    def __init__(self, parent, currentMapVectorLayer):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Deforestation Analysis")
        
        #setting the passed vector layer
        self.currentMap = currentMapVectorLayer
        self.request = QgsFeatureRequest()
        self.mapNames = []
        self.amountOfAreas = 0
        
        #getting list of the current features names for combobox
        for feature in self.currentMap.getFeatures():
            self.mapNames.append(str(feature.attribute("name")))
            self.amountOfAreas = self.amountOfAreas +1
       
       #setting data for combobox
        self.forestTypes = [AREA_TYPE_DEFORESTED, AREA_TYPE_VUN, AREA_TYPE_REFORESTED]

        self.defTypes = [DEF_TYPE_DEFORESTATION, DEF_TYPE_FORESTDEGRADATION , DEF_TYPE_FORESTFRAGMENTATION ]

        #ComboBox by Features
        self.nameField = QComboBox(self)
        if len(self.mapNames) > 0:
            self.nameField.addItems(self.mapNames)
        #ComboBox by forest type
        self.forestTypeField = QComboBox(self)
        self.forestTypeField.addItems(self.forestTypes)
        
        #ComboBox by deforestation type
        self.defTypeField = QComboBox(self)
        self.defTypeField.addItems(self.defTypes)
        
        #connect methods to combo changed index method
        self.nameField.currentIndexChanged.connect(self.onNameChange)
        self.forestTypeField.currentIndexChanged.connect(self.onForestTypeChange)
        self.defTypeField.currentIndexChanged.connect(self.onDefTypeChange)
        
        #setting labels for area totals
        self.amountAreasField = QLabel(self)
        self.areaTotalField = QLabel(self)
        self.areaTypeTotalField = QLabel(self)
        self.areaDefTypeTotalField = QLabel(self)
        self.form = QFormLayout()
        
        #setting vertical layout
        self.form.addRow("Name", self.nameField, )
        self.form.addRow("Area", self.areaTotalField)
        self.form.addRow("Type", self.forestTypeField)
        self.form.addRow("Total area covered:", self.areaTypeTotalField)
        self.form.addRow("Deforestion Type", self.defTypeField)
        self.form.addRow("Total area covered:", self.areaDefTypeTotalField)
        self.form.addRow("Total amount of features: ", self.amountAreasField)
        
        self.cancelButton = QPushButton("Close", self)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.reject)
        
        #setting layour of buttons
        self.button = QHBoxLayout()
        self.button.addStretch(1)
        self.button.addWidget(self.cancelButton)
        
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.form)
        self.layout.addSpacing(5)
        self.layout.addLayout(self.button)
        
        self.setLayout(self.layout)
        self.resize(self.sizeHint())

        #setting the label to display the amount of features in the layer
        self.amountAreasField.setText(str(self.amountOfAreas))
        
        self.onNameChange()
        self.onForestTypeChange()
        self.onDefTypeChange()
    
    #calculating area for single area
    def onNameChange(self):
        area = 0
        index = self.nameField.currentIndex()
        for feature in self.currentMap.getFeatures():
            if index == feature.id():
                area = feature.attribute("area")
                self.areaTotalField.setText(str(area))

    # Calculating total area for features of that forest type
    def onForestTypeChange(self):
        curText = str(self.forestTypeField.currentText())
        #expression to filter get features by type
        expr = QgsExpression(" \"type\" = '{}'".format(curText))
        areaTotal = 0
        for feature in self.currentMap.getFeatures(QgsFeatureRequest(expr)):
            areaTotal += float(feature.attribute("area"))
        self.areaTypeTotalField.setText(str(areaTotal))

    #setting total area to for features of that deforestation type
    def onDefTypeChange(self):
        curText = str(self.defTypeField.currentText())
        expr = QgsExpression(" \"defType\" = '{}'".format(curText))
        areaTotal = 0
        for feature in self.currentMap.getFeatures(QgsFeatureRequest(expr)):
            areaTotal += float(feature.attribute("area"))
        self.areaDefTypeTotalField.setText(str(areaTotal))

#selected features, from getAreaInfo map tool

class getAreaInfoDialog(QDialog):
    def __init__(self, parent, feature):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Area Info")
        
        #setting the combo box by forest type
        self.types = [AREA_TYPE_DEFORESTED, AREA_TYPE_VUN, AREA_TYPE_REFORESTED]
        
        #setting the combo box by def type
        self.defTypes = [DEF_TYPE_DEFORESTATION, DEF_TYPE_FORESTDEGRADATION , DEF_TYPE_FORESTFRAGMENTATION ]
      
        #setting editable QLineEdit boxs for the name and date attributes
        self.nameField = QLineEdit(self)
        self.dateField = QLineEdit(self)
        
        #set comboboxes
        self.forestTypeField = QComboBox(self)
        self.forestTypeField.addItems(self.types)
        
        self.defTypeField = QComboBox(self)
        self.defTypeField.addItems(self.defTypes)
       
        self.areaField = QLabel(self)
        
        #adding widgets to the form dialot layout
        self.form = QFormLayout()
        self.form.addRow("Name", self.nameField)
        self.form.addRow("Type",      self.forestTypeField)
        self.form.addRow("Deforestion Type",      self.defTypeField)
        self.form.addRow("Date",      self.dateField)
        self.form.addRow("Area",      self.areaField)
        
        #setting up the buttons
        self.okButton = QPushButton("OK", self)
        self.connect(self.okButton, SIGNAL("clicked()"), self.accept)
        
        self.cancelButton = QPushButton("Cancel", self)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.reject)
        
        #setting layout for the buttons
        self.buttons = QHBoxLayout()
        self.buttons.addStretch(1)
        self.buttons.addWidget(self.okButton)
        self.buttons.addWidget(self.cancelButton)
        
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.form)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.buttons)
        
        self.setLayout(self.layout)
        self.resize(self.sizeHint())

    #load the selected area features attributes into and set the current display of the dialog box to reflect features attributes
    def loadAttributes(self, feature):
        nameAttr = feature.attribute("name")
        forestTypeAttr = feature.attribute("type")
        defTypeAttr = feature.attribute("defType")
        dateAttr = feature.attribute("date")
        areaAttr = feature.attribute("area")
    
    #set combo box to features current forest and deforestation types
        if   forestTypeAttr == AREA_TYPE_DEFORESTED : index = 0
        elif forestTypeAttr == AREA_TYPE_VUN : index = 1
        elif forestTypeAttr == AREA_TYPE_REFORESTED : index = 2
        else : index = 0
        
        self.forestTypeField.setCurrentIndex(index)
        
        if   defTypeAttr == DEF_TYPE_DEFORESTATION : index = 0
        elif defTypeAttr == DEF_TYPE_FORESTDEGRADATION : index = 1
        elif defTypeAttr == DEF_TYPE_FORESTFRAGMENTATION : index = 2
        else : index = 0
        
        self.defTypeField.setCurrentIndex(index)
        
        self.areaField.setText(str(areaAttr))
        
        #validation statements
        if dateAttr != None:
            self.dateField.setText(dateAttr)
        else:
            self.dateField.setText("")
        if nameAttr != None:
            self.nameField.setText(nameAttr)
        else:
            self.nameField.setText("")
    
    #save the current set of attributes in the fields and comboboxes to the area feature
    def saveAttributes(self, feature):
        
        index = self.forestTypeField.currentIndex()
        if   index == 0: forestTypeAttr = AREA_TYPE_DEFORESTED
        elif index == 1: forestTypeAttr = AREA_TYPE_VUN
        elif index == 2: forestTypeAttr = AREA_TYPE_REFORESTED
        
        dateAttr = str(self.dateField.text())
        nameAttr = str(self.nameField.text())
        
        index = self.defTypeField.currentIndex()
        if   index == 0: defTypeAttr = DEF_TYPE_DEFORESTATION
        elif index == 1: defTypeAttr = DEF_TYPE_FORESTDEGRADATION
        elif index == 2: defTypeAttr = DEF_TYPE_FORESTFRAGMENTATION
       
        feature.setAttribute("name", nameAttr)
        feature.setAttribute("type", forestTypeAttr)
        feature.setAttribute("defType", defTypeAttr)
        feature.setAttribute("date", dateAttr)
