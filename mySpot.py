"""
/***************************************************************************
 MySpot.Gent
                                 
 "Standalone application developed for Postgraduate 'Geo-ICT' at HoGent." 
                             -------------------
        name                 : MySpot.Gent
        version              : 0.1
        begin                : 2017-02-24
        copyright            : (c) 2017 by Bernard Baetens
        email                : bernard_baetens@tutanota.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, os.path, sys
import math

from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.networkanalysis import *

from ui_mainWindow import Ui_MainWindow
from PyQt4 import QtCore, QtGui

import MySpotTools
import datetime

##########################################################################


class MySpotWindow(QMainWindow, Ui_MainWindow):
    # create class, inherits from QMainWindow and Window created in qtDesigner

    def __init__(self):
        QMainWindow.__init__(self)

        # call the method from ui_mainWindow to create the user interface
        self.setupUi(self)

        # connect the gui to the appropriate methods
        # Checkboxes
        self.checkBox_PR.toggled.connect(self.show_maplayers)
        self.checkBox_Garage.toggled.connect(self.show_maplayers)
        self.checkBox_Train.toggled.connect(self.show_maplayers)
        self.checkBox_BlueBike.toggled.connect(self.show_maplayers)
        self.checkBox_Cambio.toggled.connect(self.show_maplayers)
        self.checkBox_Taxi.toggled.connect(self.show_maplayers)

        self.checkBox_ParkingAreas.toggled.connect(self.box_parkingareas)
        self.checkBox_Circulation.toggled.connect(self.box_circulation)
        self.checkBox_Inhabitants.toggled.connect(self.box_inhabitants)

        self.checkBox_Info.toggled.connect(self.show_maplayers)
        self.checkBox_Ortho.toggled.connect(self.box_ortho)

        self.checkBox_RoutePR.toggled.connect(self.box_route_pr)
        self.checkBox_RouteGarage.toggled.connect(self.box_route_garage)
        self.checkBox_RouteStreet.toggled.connect(self.box_route_street)

        # buttons
        # menu-bar
        self.zoomInButton.clicked.connect(self.zoom_in)
        self.zoomOutButton.clicked.connect(self.zoom_out)
        self.panButton.clicked.connect(self.pan)
        self.infoButton.clicked.connect(self.info)
        self.extentButton.clicked.connect(self.extent)
        # user input
        self.toButton.clicked.connect(self.to_btn)
        self.fromButton.clicked.connect(self.from_btn)
        self.calcButton.clicked.connect(self.calculate_btn)
        self.resetButton.clicked.connect(self.reset_btn)
        # export
        # the method is called with a lambda function to send a parameter
        self.routeLabel_export_pr.clicked.connect(lambda: self.export_kml('pr'))
        self.routeLabel_export_g.clicked.connect(lambda: self.export_kml('g'))
        self.routeLabel_export_s.clicked.connect(lambda: self.export_kml('s'))

        # connect to the scale-bar and the coordinates
        self.connect(self.mapCanvas, SIGNAL("xyCoordinates(QgsPoint)"),
                     self.showXY)
        self.connect(self.mapCanvas, SIGNAL("scaleChanged(double)"),
                     self.showScale)

        # create an instance of the map tool from MySpotTools
        self.panTool = MySpotTools.PanTool(self.mapCanvas)

        # create an instance of the information tool from MySpotTools
        self.infoTool = MySpotTools.InformationTool(self.mapCanvas)

        # set the datetime in the input to now
        self.setDateTime()

        # create the two QgsVertexMarker for the from/to position
        self.t = QgsVertexMarker(self.mapCanvas)
        self.f = QgsVertexMarker(self.mapCanvas)
        # create the rubberbands for the routing
        self.rt_ps2 = QgsRubberBand(self.mapCanvas)
        self.rt_ps1 = QgsRubberBand(self.mapCanvas)
        self.rt_pg2 = QgsRubberBand(self.mapCanvas)
        self.rt_pg1 = QgsRubberBand(self.mapCanvas)
        self.rt_pr2 = QgsRubberBand(self.mapCanvas)
        self.rt_pr1 = QgsRubberBand(self.mapCanvas)

        # hide the routing labels
        self.route_label('hide')

        # Change the Crs to Lb72, set the map-units to meter, set the background colour, load
        # in the layers, and set the map extent of the mapCanvas
        lb_72 = QgsCoordinateReferenceSystem(31370)
        self.mapCanvas.mapRenderer().setProjectionsEnabled(False)
        self.mapCanvas.mapRenderer().setDestinationCrs(lb_72)
        self.mapCanvas.setMapUnits(QGis.Meters)
        self.mapCanvas.setCanvasColor(QtGui.QColor(255, 248, 240))
        self.mapCanvas.setExtent(QgsRectangle(98000, 186000, 111414, 201400))

    # --------------------------------------------------------------------------#

    # methods linked to the connections
    def box_parkingareas(self):
        if self.checkBox_ParkingAreas.isChecked():
            self.checkBox_Circulation.setChecked(False)
            self.checkBox_Inhabitants.setChecked(False)
        self.show_maplayers()

    def box_circulation(self):
        if self.checkBox_Circulation.isChecked():
            self.checkBox_ParkingAreas.setChecked(False)
            self.checkBox_Inhabitants.setChecked(False)
        self.show_maplayers()

    def box_inhabitants(self):
        if self.checkBox_Inhabitants.isChecked():
            self.checkBox_ParkingAreas.setChecked(False)
            self.checkBox_Circulation.setChecked(False)
        self.show_maplayers()

    def box_ortho(self):
        if self.checkBox_Ortho.isChecked():
            self.checkBox_Info.setChecked(False)
        elif not self.checkBox_Ortho.isChecked():
            self.checkBox_Info.setChecked(True)
        self.show_maplayers()

    # set routing layer on or off on the map canvas
    def box_route_pr(self):
        if self.checkBox_RoutePR.isChecked():
            self.rt_pr1.setColor(QColor(0, 170, 0))
            self.rt_pr1.setWidth(5)
            self.rt_pr1.setLineStyle(Qt.PenStyle(Qt.SolidLine))
            self.rt_pr1.updatePosition()
            self.rt_pr2.setColor(QColor(0, 170, 0))
            self.rt_pr2.setWidth(5)
            self.rt_pr2.setLineStyle(Qt.PenStyle(Qt.DotLine))
            self.rt_pr2.updatePosition()
        elif not self.checkBox_RoutePR.isChecked():
            self.rt_pr1.setLineStyle(Qt.PenStyle(Qt.NoPen))
            self.rt_pr1.updatePosition()
            self.rt_pr2.setLineStyle(Qt.PenStyle(Qt.NoPen))
            self.rt_pr2.updatePosition()

    def box_route_garage(self):
        if self.checkBox_RouteGarage.isChecked():
            self.rt_pg1.setColor(QColor(0, 170, 255))
            self.rt_pg1.setWidth(5)
            self.rt_pg1.setLineStyle(Qt.PenStyle(Qt.SolidLine))
            self.rt_pg1.updatePosition()
            self.rt_pg2.setColor(QColor(0, 170, 255))
            self.rt_pg2.setWidth(5)
            self.rt_pg2.setLineStyle(Qt.PenStyle(Qt.DotLine))
            self.rt_pg2.updatePosition()
        elif not self.checkBox_RouteGarage.isChecked():
            self.rt_pg1.setLineStyle(Qt.PenStyle(Qt.NoPen))
            self.rt_pg1.updatePosition()
            self.rt_pg2.setLineStyle(Qt.PenStyle(Qt.NoPen))
            self.rt_pg2.updatePosition()

    def box_route_street(self):
        if self.checkBox_RouteStreet.isChecked():
            self.rt_ps1.setColor(QColor(255, 0, 0))
            self.rt_ps1.setWidth(5)
            self.rt_ps1.setLineStyle(Qt.PenStyle(Qt.SolidLine))
            self.rt_ps1.updatePosition()
            self.rt_ps2.setColor(QColor(255, 0, 0))
            self.rt_ps2.setWidth(5)
            self.rt_ps2.setLineStyle(Qt.PenStyle(Qt.DotLine))
            self.rt_ps2.updatePosition()
        elif not self.checkBox_RouteStreet.isChecked():
            self.rt_ps1.setLineStyle(Qt.PenStyle(Qt.NoPen))
            self.rt_ps1.updatePosition()
            self.rt_ps2.setLineStyle(Qt.PenStyle(Qt.NoPen))
            self.rt_ps2.updatePosition()

    # show coordinates
    def showXY(self, p):
        self.coordinateLineEdit.setText('Coordinates:    '+ '%.2f' %p.x() + ' , ' + '%.2f'%p.y())

    # show scale-bar
    def showScale(self, scale):
        self.scaleLineEdit.setText('Scale:    1: ' + '%.2f' %scale)

    # set map-extent when clicked
    def extent(self):
        self.mapCanvas.setExtent(QgsRectangle(86385, 175000, 125031, 212640))
        self.mapCanvas.refresh()

    # zoom-in function
    def zoom_in(self):
        self.mapCanvas.zoomIn()

    # zoom-out function
    def zoom_out(self):
        self.mapCanvas.zoomOut()

    # pan mode sub-classed from QgsMapTool in MySpotTools
    def pan(self):
        # uncheck the other tools
        self.infoButton.setChecked(False)
        self.toButton.setChecked(False)
        self.fromButton.setChecked(False)

        # call method from MySpotTools.py
        if self.panButton.isChecked():
            self.mapCanvas.setMapTool(self.panTool)
        elif not self.panButton.isChecked():
            self.mapCanvas.unsetMapTool(self.panTool)

    # InfoTool sub-classed from QgsMapToolIdentify
    def info(self):
        # uncheck the other tools
        self.panButton.setChecked(False)
        self.toButton.setChecked(False)
        self.fromButton.setChecked(False)

        # Call method from tool.py
        if self.infoButton.isChecked():
            self.mapCanvas.setMapTool(self.infoTool)

        elif not self.infoButton.isChecked():
            self.mapCanvas.unsetMapTool(self.infoTool)

    #clicktool 'to'
    def to_btn(self):
        # uncheck the other tools
        self.infoButton.setChecked(False)
        self.fromButton.setChecked(False)
        self.panButton.setChecked(False)

        # Call method to tool.py
        if self.toButton.isChecked():
            # create an instance with a variable showing the origin (to)
            self.clickTool = MySpotTools.ClickTool(self.mapCanvas, 'to')
            self.mapCanvas.setMapTool(self.clickTool)
            # create a connector for the clicktool-emitted signal
            self.clickTool.connect(self.clickTool, SIGNAL("Position_to(QgsPoint)"), self.show_position_to)

        elif not self.toButton.isChecked():
            self.mapCanvas.unsetMapTool(self.clickTool)

    #clicktool 'from'
    def from_btn(self):
        # uncheck the other tools
        self.infoButton.setChecked(False)
        self.toButton.setChecked(False)
        self.panButton.setChecked(False)

        if self.fromButton.isChecked():
            # create an instance with a variable showing the origin (from)
            self.clickTool = MySpotTools.ClickTool(self.mapCanvas, 'from')
            self.mapCanvas.setMapTool(self.clickTool)
            # create a connector for the clicktool-emitted signal
            self.clickTool.connect(self.clickTool, SIGNAL("Position_from(QgsPoint)"), self.show_position_from)

        elif not self.fromButton.isChecked():
            self.mapCanvas.unsetMapTool(self.clickTool)

    # method to show the coordinates in the fromlineEdit and on the map
    def show_position_from(self, Position):
        # get the x and y
        x_pos = '%.2f'% Position.x()
        y_pos = '%.2f' % Position.y()

        # edit the lineEdit with the coordinates
        self.fromLineEdit.setText('%s , %s' %(x_pos, y_pos))

        # place vertexmarker
        self.f.show()  # in case the reset button was pressed
        self.f.setCenter(Position)

        self.f.setColor(QColor(190, 0, 255))
        self.f.setIconSize(14)
        self.f.setIconType(QgsVertexMarker.ICON_CROSS)
        self.f.setPenWidth(5)

    # method to show the coordinates in the tolineEdit and on the map
    def show_position_to(self, Position):
        # get the x and y
        x_pos = '%.2f'% Position.x()
        y_pos = '%.2f' % Position.y()

        # edit the lineEdit with the coordinates
        self.toLineEdit.setText('%s , %s' %(x_pos, y_pos))

        # place vertexmarker
        self.t.show()  # in case the reset button was pressed
        self.t.setCenter(Position)
        self.t.setColor(QColor(190, 0, 255))
        self.t.setIconSize(14)
        self.t.setIconType(QgsVertexMarker.ICON_CIRCLE)
        self.t.setPenWidth(6)

    # Main method that sets the wheels in motion for routing
    def calculate_btn(self):
        # check if the user input is valid
        try:
            # get the values from the input while converting them from unicode to python-usable
            calc_from = str(self.fromLineEdit.text())
            calc_to = str(self.toLineEdit.text())
            date = self.dateTimeEdit.date().toPyDate()
            time = self.dateTimeEdit.time().toPyTime()
            duration = str(self.durationComboBox.currentText())

            # control of the values (departure and duration are always valid)
            # from values
            calc_from_split = calc_from.split(',')
            calc_from_x = float(calc_from_split[0])
            # check x-coordinate
            if not calc_from_x > 86792.00 and calc_from_x < 124899.00:
                raise ValueError('')
            calc_from_y = float(calc_from_split[1])
            # check y-coordinate
            if not calc_from_y > 175136.00 and calc_from_y < 212609.00:
                raise ValueError('')

            # to values
            calc_to_split = calc_to.split(',')
            calc_to_x = float(calc_to_split[0])
            if not calc_to_x > 86792 and calc_to_x < 124899:
                raise ValueError('')
            calc_to_y = float(calc_to_split[1])
            if not calc_to_y > 175136 and calc_to_y < 212609:
                raise ValueError('')

            # create a dictionary with all the inputs
            self.route_calc = {'from_x':calc_from_x, 'from_y':calc_from_y,
                         'to_x':calc_to_x, 'to_y':calc_to_y,
                         'date':date, 'time':time,
                         'duration':duration}

            # reset the possible existing rubberbands
            self.rt_ps1.reset()
            self.rt_ps2.reset()
            self.rt_pg2.reset()
            self.rt_pg1.reset()
            self.rt_pr2.reset()
            self.rt_pr1.reset()

            # call the method that creates the graphs for routing
            self.route_graphs_pr()
            self.route_graphs_garage()
            self.route_graphs_street()

            # call method that calculates the closest pr, garage and street parking
            self.calc_pr()
            self.calc_pg()
            self.calc_ps()
            # call methods that route
            self.route_pr()
            self.route_pg()
            self.route_s()

            # set the checkboxes of the routing rubberbands
            self.checkBox_RoutePR.setEnabled(True)
            self.checkBox_RouteGarage.setEnabled(True)
            self.checkBox_RouteStreet.setEnabled(True)
            self.checkBox_RoutePR.setChecked(True)
            self.checkBox_RouteGarage.setChecked(True)
            self.checkBox_RouteStreet.setChecked(True)

            # search for closest address
            # from
            self.address('from', self.route_calc['from_x'], self.route_calc['from_y'] )
            # to
            self.address('to', self.route_calc['to_x'], self.route_calc['to_y'])
            # street parking
            self.address('street', self.ps_point.x(), self.ps_point.y())

            # set the line-edits from and to to the addresses
            self.fromLineEdit.setText('%s %s, %s %s' % (self.a_from[0], self.a_from[1], self.a_from[3], self.a_from[2]))
            self.toLineEdit.setText('%s %s, %s %s' % (self.a_to[0], self.a_to[1], self.a_to[3], self.a_to[2]))

            # call the method that displays the routing labels
            self.route_label('show')
            # call the method that displays the information
            self.show_route_info()

        except ValueError:
            msg = 'There is a problem with the input for calculation.' \
                  '\nPlease check the data for errors. '
            QMessageBox.warning(self, 'Input Error', msg)

    def reset_btn(self):
        # set the from and to input to an empty string
        self.toLineEdit.setText("")
        self.fromLineEdit.setText("")

        # set the datetime in the input to now
        self.setDateTime()

        # set the combobox to +3h
        self.durationComboBox.setCurrentIndex(0)

        # hide the vertexmarkers
        self.f.hide()
        self.t.hide()

        # hide the rubberbands
        self.rt_ps1.reset()
        self.rt_ps2.reset()
        self.rt_pg2.reset()
        self.rt_pg1.reset()
        self.rt_pr2.reset()
        self.rt_pr1.reset()

        # unset the checkboxes of the routing
        self.checkBox_RoutePR.setEnabled(False)
        self.checkBox_RouteGarage.setEnabled(False)
        self.checkBox_RouteStreet.setEnabled(False)
        self.checkBox_RoutePR.setChecked(False)
        self.checkBox_RouteGarage.setChecked(False)
        self.checkBox_RouteStreet.setChecked(False)

        # call the method that hides the routing information
        self.route_label('hide')

    # --------------------------------------------------------------------------#

    def setDateTime(self):
        # set the datetime in the input to now
        date = datetime.datetime.today()
        year = date.__getattribute__('year')
        month = date.__getattribute__('month')
        day = date.__getattribute__('day')
        hour = date.__getattribute__('hour')
        minute = date.__getattribute__('minute')
        second = date.__getattribute__('second')
        self.dateTimeEdit.setDateTime(
            QtCore.QDateTime(QtCore.QDate(year, month, day), QtCore.QTime(hour, minute, second)))

    # --------------------------------------------------------------------------#

    # building graphs for routing (every time, otherwise python crashes)
    def route_graphs_pr(self):
        # CAR
        # creation of the director (layer, index of street-direction, direct direction,
        # reverse direction, bidirectional, default = 3 bi-directional
        self.director_car_pr = QgsLineVectorLayerDirector(self.osm_car, 16, str(1), str(-1), str(0), 3)
        # calculate edge properties
        self.properter_car_pr = QgsDistanceArcProperter()
        self.director_car_pr.addProperter(self.properter_car_pr)

        crs = QgsCoordinateReferenceSystem(31370)
        self.builder_car_pr = QgsGraphBuilder(crs, False)

        # BIKE
        # creation of the director (layer, index of street-direction, direct direction,
        # reverse direction, bidirectional, default = 3 bi-directional
        self.director_bike_pr = QgsLineVectorLayerDirector(self.osm_bike, 16, str(1), str(-1), str(0), 3)
        # calculate edge properties
        self.properter_bike_pr = QgsDistanceArcProperter()
        self.director_bike_pr.addProperter(self.properter_bike_pr)

        crs = QgsCoordinateReferenceSystem(31370)
        self.builder_bike_pr = QgsGraphBuilder(crs, False)

    def route_graphs_garage(self):
        # CAR
        # creation of the director (layer, index of street-direction, direct direction,
        # reverse direction, bidirectional, default = 3 bi-directional
        self.director_car_g = QgsLineVectorLayerDirector(self.osm_car, 16, str(1), str(-1), str(0), 3)
        # calculate edge properties
        self.properter_car_g = QgsDistanceArcProperter()
        self.director_car_g.addProperter(self.properter_car_g)

        crs = QgsCoordinateReferenceSystem(31370)
        self.builder_car_g = QgsGraphBuilder(crs, False)

        # WALK
        # creation of the director (layer, index of street-direction, direct direction,
        # reverse direction, bidirectional, default = 3 bi-directional
        self.director_walk_g = QgsLineVectorLayerDirector(self.osm_walk, 16, str(1), str(-1), str(0), 3)
        # calculate edge properties
        self.properter_walk_g = QgsDistanceArcProperter()
        self.director_walk_g.addProperter(self.properter_walk_g)

        crs = QgsCoordinateReferenceSystem(31370)
        self.builder_walk_g = QgsGraphBuilder(crs, False)

    def route_graphs_street(self):
        # CAR
        # creation of the director (layer, index of street-direction, direct direction,
        # reverse direction, bidirectional, default = 3 bi-directional
        self.director_car_s = QgsLineVectorLayerDirector(self.osm_car, 16, str(1), str(-1), str(0), 3)
        # calculate edge properties
        self.properter_car_s = QgsDistanceArcProperter()
        self.director_car_s.addProperter(self.properter_car_s)

        crs = QgsCoordinateReferenceSystem(31370)
        self.builder_car_s = QgsGraphBuilder(crs, False)

        # WALK
        # creation of the director (layer, index of street-direction, direct direction,
        # reverse direction, bidirectional, default = 3 bi-directional
        self.director_walk_s = QgsLineVectorLayerDirector(self.osm_walk, 16, str(1), str(-1), str(0), 3)
        # calculate edge properties
        self.properter_walk_s = QgsDistanceArcProperter()
        self.director_walk_s.addProperter(self.properter_walk_s)

        crs = QgsCoordinateReferenceSystem(31370)
        self.builder_walk_s = QgsGraphBuilder(crs, False)

    # --------------------------#
    # error message when one of the routings failed
    def routing_error(self, route):
        msg = 'No path found for %s -routing.' \
              '\nPlease try again. ' % route
        QMessageBox.critical(self, 'Routing Error', msg)

    # --------------------------#

    # calculate the closest P+R from the endpoint
    def calc_pr(self):
        endpoint = QgsGeometry.fromPoint(QgsPoint(self.route_calc['to_x'], self.route_calc['to_y']))

        # info about the P+R
        layer = self.PR
        d = 999999999

        # iterate over the features in the layer
        for feature in layer.getFeatures():
            geom = feature.geometry()

            # calculate distance between P+R and enpoint, find the closest (data is to small for indexing to have effect)
            dist = math.sqrt(endpoint.asPoint().sqrDist(geom.asPoint()))
            if dist < d:
                d = dist
                # attributes of the closest P+R
                self.pr_attr = feature.attributes()
                # geometry of the closest P+R
                self.pr_point = geom.asPoint()

    # calculate the closest Garage from the endpoint
    def calc_pg(self):
        endpoint = QgsGeometry.fromPoint(QgsPoint(self.route_calc['to_x'], self.route_calc['to_y']))

        # info about the garage
        layer = self.ParkingGarage
        d = 999999999

        # iterate over the features in the layer
        for feature in layer.getFeatures():
            geom = feature.geometry()

            # calculate distance between P+R and enpoint, find the closest (data is to small for indexing to have effect)
            dist = math.sqrt(endpoint.asPoint().sqrDist(geom.asPoint()))
            if dist < d:
                d = dist
                # attributes of the closest garage
                self.pg_attr = feature.attributes()
                # geometry of the closest garage
                self.pg_point = geom.asPoint()

    # calculate the closest StreetParking from the endpoint
    def calc_ps(self):
        l_lst = ['15 -30 min', '1 h', '2 h', '3 h']
        endpoint = QgsGeometry.fromPoint(QgsPoint(self.route_calc['to_x'], self.route_calc['to_y']))
        layer = self.ParkeerAreaal

        # filter the layer in two possibilities: if parking is +3h: no parking in red zone (first)
        # additional to that, only visitor parking's are allowed no inhabitants, preserved...
        if self.route_calc['duration'] not in l_lst:
            exp = QgsExpression(
                "Pregime is '0' OR Pregime is '2' OR Pregime is '3' OR Pregime is '4' OR Pregime is '5'")
        else:
            exp = QgsExpression(
                "Pregime is '0' OR Pregime is '1' OR Pregime is '2' OR Pregime is '3' OR Pregime is '4' OR Pregime is '5'")

        exp.prepare(layer.pendingFields())

        # create spatial index object
        sp_index = QgsSpatialIndex()

        for f in layer.getFeatures():
            value = exp.evaluate(f)
            # filter out the features that match the expression
            if bool(value):
                # add the filtered feature to the index
                sp_index.insertFeature(f)

        # QgsSpatialIndex.nearestNeighbor (QgsPoint point, int neighbors)
        nearest_ids = sp_index.nearestNeighbor(endpoint.asPoint(), 1)

        # get the actual QgsFeature object from the list
        feature_id = nearest_ids[0]
        fit2 = layer.getFeatures((QgsFeatureRequest().setFilterFid(feature_id)))
        feature = QgsFeature()
        fit2.nextFeature(feature)

        geom = feature.geometry()
        self.ps_point = geom.centroid().asPoint()
        self.ps_attr = feature.attributes()

    # --------------------------#

    def crab_index(self):
        # indexing to be used by address-function
        # index the crab layer for performance
        layer = self.crab
        provider = layer.dataProvider()

        # create the spatial index object
        self.sp_index_c = QgsSpatialIndex()
        feat = QgsFeature()
        fit_c = provider.getFeatures()

        # insert features to index
        while fit_c.nextFeature(feat):
            self.sp_index_c.insertFeature(feat)

    def address(self, origin, inp_x, inp_y):
        # create x-y point
        point = QgsGeometry.fromPoint(QgsPoint(inp_x, inp_y))

        # QgsSpatialIndex.nearestNeighbor (QgsPoint point, int neighbors)
        nearest_ids = self.sp_index_c.nearestNeighbor(point.asPoint(), 1)

        # get the actual QgsFeature object from the list
        feature_id = nearest_ids[0]
        fit2 = self.crab.getFeatures((QgsFeatureRequest().setFilterFid(feature_id)))
        feature = QgsFeature()
        fit2.nextFeature(feature)

        # forward the attributes of the calculation to the appropriate variable
        if origin == 'from':
            # from address
            self.a_from = feature.attributes()
        elif origin == 'to':
            # to address
            self.a_to = feature.attributes()
        else:
            # street parking address
            self.a_street = feature.attributes()

    # --------------------------#
    # Routing Functions

    # routing with P+R
    def route_pr(self):

        # car routing from to P+R
        pStart = QgsPoint(self.route_calc['from_x'], self.route_calc['from_y'])
        pStop = self.pr_point

        # build the graph and 'tie' points to it
        tiedPoints = self.director_car_pr.makeGraph(self.builder_car_pr, [pStart, pStop])
        # actual graph, ready for analysis
        graph = self.builder_car_pr.graph()

        tStart = tiedPoints[0]
        tStop = tiedPoints[1]

        idStart = graph.findVertex(tStart)
        idStop = graph.findVertex(tStop)

        # network analysis. Parameters: source(graph), startVertexIdx, CriterionNum
        # (number of edge properties to use
        (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)

        # retrieve the total length of the routing
        self.length_km_pr1 = cost[idStop] / 1000

        if tree[idStop] == -1:
            self.routing_error('PR_Car')
            self.reset_btn()

        else:
            self.pr_1 = []
            curPos = idStop
            while curPos != idStart:
                self.pr_1.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
                curPos = graph.arc(tree[curPos]).outVertex()

            self.pr_1.append(tStart)

            # create the rubberband
            # car routing p+r
            self.rt_pr1.reset()
            for pnt in self.pr_1:
                self.rt_pr1.addPoint(pnt)

        # bike routing from P+R to end
        pStart = self.pr_point
        pStop = QgsPoint(self.route_calc['to_x'], self.route_calc['to_y'])

        # build the graph and 'tie' points to it
        tiedPoints = self.director_bike_pr.makeGraph(self.builder_bike_pr, [pStart, pStop])
        # actual graph, ready for analysis
        graph = self.builder_bike_pr.graph()

        tStart = tiedPoints[0]
        tStop = tiedPoints[1]

        idStart = graph.findVertex(tStart)
        idStop = graph.findVertex(tStop)

        # network analysis. Parameters: source(graph), startVertexIdx, CriterionNum
        # (number of edge properties to use
        (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)

        # retrieve the total length of the routing
        self.length_km_pr2 = cost[idStop] / 1000

        if tree[idStop] == -1:
            self.routing_error('PR_Bike')
            self.reset_btn()

        else:
            self.pr_2 = []
            curPos = idStop
            while curPos != idStart:
                self.pr_2.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
                curPos = graph.arc(tree[curPos]).outVertex()

            self.pr_2.append(tStart)

            # create the rubberband
            # bike routing p+r to end
            self.rt_pr2.reset()
            for pnt in self.pr_2:
                self.rt_pr2.addPoint(pnt)

    # routing with garage
    def route_pg(self):

        # car routing from to parking garage
        pStart = QgsPoint(self.route_calc['from_x'], self.route_calc['from_y'])
        pStop = self.pg_point

        # build the graph and 'tie' points to it
        tiedPoints = self.director_car_g.makeGraph(self.builder_car_g, [pStart, pStop])
        # actual graph, ready for analysis
        graph = self.builder_car_g.graph()

        tStart = tiedPoints[0]
        tStop = tiedPoints[1]

        idStart = graph.findVertex(tStart)
        idStop = graph.findVertex(tStop)

        # network analysis. Parameters: source(graph), startVertexIdx, CriterionNum
        # (number of edge properties to use
        (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)

        # retrieve the total length of the routing
        self.length_km_pg1 = cost[idStop] / 1000

        if tree[idStop] == -1:
            self.routing_error('Garage_Car')
            self.reset_btn()

        else:
            self.pg_1 = []
            curPos = idStop
            while curPos != idStart:
                self.pg_1.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
                curPos = graph.arc(tree[curPos]).outVertex()

            self.pg_1.append(tStart)

            # create the rubberband
            # car routing parking garage
            self.rt_pg1.reset()
            for pnt in self.pg_1:
                self.rt_pg1.addPoint(pnt)

        # walk routing from Parking garage to end
        pStart = self.pg_point
        pStop = QgsPoint(self.route_calc['to_x'], self.route_calc['to_y'])

        # build the graph and 'tie' points to it
        tiedPoints = self.director_walk_g.makeGraph(self.builder_walk_g, [pStart, pStop])
        # actual graph, ready for analysis
        graph = self.builder_walk_g.graph()

        tStart = tiedPoints[0]
        tStop = tiedPoints[1]

        idStart = graph.findVertex(tStart)
        idStop = graph.findVertex(tStop)

        # network analysis. Parameters: source(graph), startVertexIdx, CriterionNum
        # (number of edge properties to use
        (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)

        # retrieve the total length of the routing
        self.length_km_pg2 = cost[idStop] / 1000

        if tree[idStop] == -1:
            self.routing_error('Garage_Walk')
            self.reset_btn()

        else:
            self.pg_2 = []
            curPos = idStop
            while curPos != idStart:
                self.pg_2.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
                curPos = graph.arc(tree[curPos]).outVertex()

            self.pg_2.append(tStart)

            # create the rubberband
            # bike routing parking garage to end
            self.rt_pg2.reset()
            for pnt in self.pg_2:
                self.rt_pg2.addPoint(pnt)

    # routing with street
    def route_s(self):

        # car routing from to street parking
        pStart = QgsPoint(self.route_calc['from_x'], self.route_calc['from_y'])
        pStop = self.ps_point

        # build the graph and 'tie' points to it
        tiedPoints = self.director_car_s.makeGraph(self.builder_car_s, [pStart, pStop])
        # actual graph, ready for analysis
        graph = self.builder_car_s.graph()

        tStart = tiedPoints[0]
        tStop = tiedPoints[1]

        idStart = graph.findVertex(tStart)
        idStop = graph.findVertex(tStop)

        # network analysis. Parameters: source(graph), startVertexIdx, CriterionNum
        # (number of edge properties to use
        (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)

        # retrieve the total length of the routing
        self.length_km_ps1 = cost[idStop] / 1000

        if tree[idStop] == -1:
            self.routing_error('Street_Car')
            self.reset_btn()

        else:
            self.ps_1 = []
            curPos = idStop
            while curPos != idStart:
                self.ps_1.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
                curPos = graph.arc(tree[curPos]).outVertex()

            self.ps_1.append(tStart)
            # create the rubberband
            # car routing to street parking
            self.rt_ps1.reset()
            for pnt in self.ps_1:
                self.rt_ps1.addPoint(pnt)

        # walk routing from Parking street to end
        pStart = self.ps_point
        pStop = QgsPoint(self.route_calc['to_x'], self.route_calc['to_y'])

        # build the graph and 'tie' points to it
        tiedPoints = self.director_walk_s.makeGraph(self.builder_walk_s, [pStart, pStop])
        # actual graph, ready for analysis
        graph = self.builder_walk_s.graph()

        tStart = tiedPoints[0]
        tStop = tiedPoints[1]

        idStart = graph.findVertex(tStart)
        idStop = graph.findVertex(tStop)

        # network analysis. Parameters: source(graph), startVertexIdx, CriterionNum
        # (number of edge properties to use
        (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)

        # retrieve the total length of the routing
        self.length_km_ps2 = cost[idStop] / 1000

        if tree[idStop] == -1:
            self.routing_error('Street_Walk')
            self.reset_btn()

        else:
            self.ps_2 = []
            curPos = idStop
            while curPos != idStart:
                self.ps_2.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
                curPos = graph.arc(tree[curPos]).outVertex()

            self.ps_2.append(tStart)

            # create the rubberbands
            # bike routing streetparking to end
            self.rt_ps2.reset()
            for pnt in self.ps_2:
                self.rt_ps2.addPoint(pnt)

    # --------------------------------------------------------------------------#

    # display the routing information
    def show_route_info(self):

        # Set the routing distances of P+R
        self.routeLabel_pr_totallength.setText('Total distance: %.2f km' % (self.length_km_pr1 + self.length_km_pr2))
        self.routeLabel_pr_car.setText('%.2f km' % self.length_km_pr1)
        self.routeLabel_pr_bike.setText('%.2f km' % self.length_km_pr2)
        # Set the routing distances of Garages
        self.routeLabel_g_totallength.setText('Total distance: %.2f km' % (self.length_km_pg1 + self.length_km_pg2))
        self.routeLabel_g_car.setText('%.2f km' % self.length_km_pg1)
        self.routeLabel_g_walk.setText('%.2f km' % self.length_km_pg2)
        # Set the routing distances of Street
        self.routeLabel_s_totallength.setText('Total distance: %.2f km' % (self.length_km_ps1 + self.length_km_ps2))
        self.routeLabel_s_car.setText('%.2f km' % self.length_km_ps1)
        self.routeLabel_s_walk.setText('%.2f km' % self.length_km_ps2)

        # Set the information of P+R
        info_pr = []
        info_pr.append('Name: %s' % self.pr_attr[3])
        info_pr.append('Address: %s' % self.pr_attr[8])
        info_pr.append('Capacity: %s' % self.pr_attr[4])
        info_pr.append('P+R-Bike: %s' % self.pr_attr[5])
        info_pr.append('Status: %s' % self.pr_attr[6])
        info_pr.append('Cost: Free')
        # set the text
        self.routeLabel_pr_info1.setText("\n".join(info_pr))

        # Set the information of ParkingGarage
        info_g = []
        info_g.append('Name: %s' % self.pg_attr[1])
        info_g.append('Address: %s' % self.pg_attr[5])
        info_g.append('Contact: %s' % self.pg_attr[4])
        info_g.append('Capacity: %s' % self.pg_attr[6])
        info_g.append('Use the InfoTool for real-time data.')
        # set the text
        self.routeLabel_g_info1.setText("\n".join(info_g))

        # Set the information of the StreetParking
        info_s = []
        # parking address
        info_s.append('Address: %s %s\n%s %s' % (self.a_street[0], self.a_street[1],
                                                 self.a_street[3], self.a_street[2]))

        # zone info (type parkeren)
        self.zone = self.ps_attr[0]
        if self.zone != None:
            if self.zone == '0':
                self.zone = 'Blauwe tariefzone'
            if self.zone == '1':
                self.zone = 'Rode tariefzone'
            if self.zone == '2':
                self.zone = 'Oranje tariefzone'
            if self.zone == '3':
                self.zone = 'Gele tariefzone'
            if self.zone == '4':
                self.zone = 'Groene tariefzone'
            if self.zone == '5':
                self.zone = 'Vrij parkeren'
            if self.zone == '6':
                self.zone = 'Bewonersparkeren'
            if self.zone == '7':
                self.zone = 'Tijdsvenster\n(Voorbehouden tijdens specifiek deel\nvan de dag (meer dan 1dag per week))'
            if self.zone == '8':
                self.zone = 'Voorbehouden\n(Voorbehouden ifv doelgroep,\naltijd de hele dag)'
            if self.zone == '9':
                self.zone = 'Foutparkeren\n(plaatsen waar geparkeerd wordt,\nhoewel er geen wettelijke\nparkeermogelijkheden zijn)'
            info_s.append('Parking Specification: ' + self.zone)

        self.opmerking = self.ps_attr[1]
        if self.opmerking != None:
            info_s.append('Remark: ' + self.opmerking)

        self.capaciteit = self.ps_attr[2]
        if self.capaciteit != None:
            info_s.append('Capacity: ' + str(self.capaciteit))

        # set the text
        self.routeLabel_s_info1.setText("\n".join(info_s))

    # method that shows or hides the routing labels
    def route_label(self, input):

        lst_labels = [self.routeLabel_pr_totallength, self.routeLabel_pr_car,
                      self.routeLabel_pr_bike, self.routeLabel_g_totallength, self.routeLabel_g_car,
                      self.routeLabel_g_walk, self.routeLabel_s_totallength, self.routeLabel_s_car,
                      self.routeLabel_s_walk, self.routeLabel_pr_info1, self.routeLabel_g_info1,
                      self.routeLabel_s_info1, self.routeLabel_info2_2, self.routeLabel_info2_5,
                      self.routeLabel_info2_8, self.routeLabel_info2_6, self.routeLabel_info2_4,
                      self.routeLabel_info2_7, self.routeLabel_export_pr,self.routeLabel_export_g,
                      self.routeLabel_export_s]
        if input == 'hide':
            for l in lst_labels:
                l.hide()
        else:
            for l in lst_labels:
                l.show()

    # --------------------------------------------------------------------------#
    # error message when one of the exports failed
    def export_error(self, route):
        msg = 'Export Error for %s -routing.' \
              '\nPlease try again. ' % route
        QMessageBox.critical(self, 'Export Error', msg)

    # export to KML
    def export_kml(self, input):
        # for future reference: create a dictionary for each routing method,
        # when creating an attribute, add it to the corresponding dictionary
        # for cleaner code

        # retrieve the save file location and filenname
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save as KML', '.kml')

        if input == 'pr':
            try:
                # get the rubberbands as a geometry
                rb1_geometry = self.rt_pr1.asGeometry()
                rb2_geometry = self.rt_pr2.asGeometry()

                # Coordinate transformation preparation
                rb_crs = QgsCoordinateReferenceSystem(31370)
                kml_crs = QgsCoordinateReferenceSystem(4326)
                crs_transform = QgsCoordinateTransform(rb_crs, kml_crs)

                # transform the rb to parking geometry to wgs84
                rb1_wgs = QgsFeature()
                rb1_geometry.transform(crs_transform)
                rb1_wgs.setGeometry(rb1_geometry)

                # transform the rb to end geometry to wgs84
                rb2_wgs = QgsFeature()
                rb2_geometry.transform(crs_transform)
                rb2_wgs.setGeometry(rb2_geometry)

                # set the attributes
                rb1_wgs.setAttributes(['PR_Car',
                                       '%s %s, %s %s' % (self.a_from[0], self.a_from[1], self.a_from[3], self.a_from[2]),
                                       '%s %s, %s %s' % (self.a_to[0], self.a_to[1], self.a_to[3], self.a_to[2]),
                                       'date: %s , time: %s' % (self.route_calc['date'], self.route_calc['time']),
                                       self.route_calc['duration'], self.pr_attr[3], self.pr_attr[8], self.pr_attr[4],
                                       self.pr_attr[5], self.pr_attr[6], 'Free', '%.2f' % self.length_km_pr1,
                                       '%.2f' % (self.length_km_pr1 + self.length_km_pr2), self.pr_attr[7]])

                rb2_wgs.setAttributes(['PR_Bike',
                                       '%s %s, %s %s' % (self.a_from[0], self.a_from[1], self.a_from[3], self.a_from[2]),
                                       '%s %s, %s %s' % (self.a_to[0], self.a_to[1], self.a_to[3], self.a_to[2]),
                                       'date: %s , time: %s' % (self.route_calc['date'], self.route_calc['time']),
                                       self.route_calc['duration'], self.pr_attr[3], self.pr_attr[8], self.pr_attr[4],
                                       self.pr_attr[5], self.pr_attr[6], 'Free', '%.2f' % self.length_km_pr2,
                                       '%.2f' % (self.length_km_pr1 + self.length_km_pr2), self.pr_attr[7]])

                # set the fields for feature attributes
                fields = QgsFields()
                fields.append(QgsField('Name', QVariant.String))
                fields.append(QgsField('From', QVariant.String))
                fields.append(QgsField('To', QVariant.String))
                fields.append(QgsField('Departure', QVariant.String))
                fields.append(QgsField('Duration', QVariant.String))
                fields.append(QgsField('Parking_PR', QVariant.String))
                fields.append(QgsField('P_Address', QVariant.String))
                fields.append(QgsField('P_Capacity', QVariant.Int))
                fields.append(QgsField('PR-Bike', QVariant.String))
                fields.append(QgsField('Status', QVariant.String))
                fields.append(QgsField('P_Cost', QVariant.String))
                fields.append(QgsField('Distance (km)', QVariant.Double))
                fields.append(QgsField('Distance_Total (km)', QVariant.Double))
                fields.append(QgsField('URL', QVariant.String))

                # create the writer and write the geometry
                writer = QgsVectorFileWriter(filename, 'utf-8', fields, QGis.WKBLineString, kml_crs, "KML")

                if writer.hasError() != QgsVectorFileWriter.NoError:
                    self.export_error('P+R')

                # add the feature
                writer.addFeature(rb1_wgs)
                writer.addFeature(rb2_wgs)

                # delete the writer to flush features to disk
                del writer

            except:
                self.export_error('P+R')

        elif input == 'g':
            try:
                # get the rubberbands as a geometry
                rb1_geometry = self.rt_pg1.asGeometry()
                rb2_geometry = self.rt_pg2.asGeometry()

                # Coordinate transformation preparation
                rb_crs = QgsCoordinateReferenceSystem(31370)
                kml_crs = QgsCoordinateReferenceSystem(4326)
                crs_transform = QgsCoordinateTransform(rb_crs, kml_crs)

                # transform the rb to parking geometry to wgs84
                rb1_wgs = QgsFeature()
                rb1_geometry.transform(crs_transform)
                rb1_wgs.setGeometry(rb1_geometry)

                # transform the rb to end geometry to wgs84
                rb2_wgs = QgsFeature()
                rb2_geometry.transform(crs_transform)
                rb2_wgs.setGeometry(rb2_geometry)

                # set the attributes
                rb1_wgs.setAttributes(['Garage_Car',
                                       '%s %s, %s %s' % (self.a_from[0], self.a_from[1], self.a_from[3], self.a_from[2]),
                                       '%s %s, %s %s' % (self.a_to[0], self.a_to[1], self.a_to[3], self.a_to[2]),
                                       'date: %s , time: %s' % (self.route_calc['date'], self.route_calc['time']),
                                       self.route_calc['duration'], self.pg_attr[1], self.pg_attr[5], self.pg_attr[4],
                                       self.pg_attr[6], 'To be calculated in Module 3', '%.2f' % self.length_km_pg1,
                                       '%.2f' % (self.length_km_pg1 + self.length_km_pg2), self.pg_attr[2]])

                rb2_wgs.setAttributes(['Garage_Walk',
                                       '%s %s, %s %s' % (self.a_from[0], self.a_from[1], self.a_from[3], self.a_from[2]),
                                       '%s %s, %s %s' % (self.a_to[0], self.a_to[1], self.a_to[3], self.a_to[2]),
                                       'date: %s , time: %s' % (self.route_calc['date'], self.route_calc['time']),
                                       self.route_calc['duration'], self.pg_attr[1], self.pg_attr[5], self.pg_attr[4],
                                       self.pg_attr[6], 'To be calculated in Module 3', '%.2f' % self.length_km_pg2,
                                       '%.2f' % (self.length_km_pg1 + self.length_km_pg2), self.pg_attr[2]])

                # set the fields for feature attributes
                fields = QgsFields()
                fields.append(QgsField('Name', QVariant.String))
                fields.append(QgsField('From', QVariant.String))
                fields.append(QgsField('To', QVariant.String))
                fields.append(QgsField('Departure', QVariant.String))
                fields.append(QgsField('Duration', QVariant.String))
                fields.append(QgsField('Parking_Garage', QVariant.String))
                fields.append(QgsField('P_Address', QVariant.String))
                fields.append(QgsField('P_Contact', QVariant.String))
                fields.append(QgsField('P_Capacity', QVariant.Int))
                fields.append(QgsField('P_Cost', QVariant.String))
                fields.append(QgsField('Distance (km)', QVariant.Double))
                fields.append(QgsField('Distance_Total (km)', QVariant.Double))
                fields.append(QgsField('URL', QVariant.String))

                # create the writer and write the geometry
                writer = QgsVectorFileWriter(filename, 'utf-8', fields, QGis.WKBLineString, kml_crs, "KML")

                if writer.hasError() != QgsVectorFileWriter.NoError:
                    self.export_error('Garage')

                # add the feature
                writer.addFeature(rb1_wgs)
                writer.addFeature(rb2_wgs)

                # delete the writer to flush features to disk
                del writer

            except:
                self.export_error('Garage')

        elif input == 's':
            try:
                rb1_geometry = self.rt_ps1.asGeometry()
                rb2_geometry = self.rt_ps2.asGeometry()

                # Coordinate transformation preparation
                rb_crs = QgsCoordinateReferenceSystem(31370)
                kml_crs = QgsCoordinateReferenceSystem(4326)
                crs_transform = QgsCoordinateTransform(rb_crs, kml_crs)

                # transform the rb to parking geometry to wgs84
                rb1_wgs = QgsFeature()
                rb1_geometry.transform(crs_transform)
                rb1_wgs.setGeometry(rb1_geometry)

                # transform the rb to end geometry to wgs84
                rb2_wgs = QgsFeature()
                rb2_geometry.transform(crs_transform)
                rb2_wgs.setGeometry(rb2_geometry)

                # set the attributes
                rb1_wgs.setAttributes(['Street_Car',
                                       '%s %s, %s %s' % (self.a_from[0], self.a_from[1], self.a_from[3], self.a_from[2]),
                                       '%s %s, %s %s' % (self.a_to[0], self.a_to[1], self.a_to[3], self.a_to[2]),
                                       'date: %s , time: %s' % (self.route_calc['date'], self.route_calc['time']),
                                       self.route_calc['duration'], self.zone, '%s %s, %s %s' % (self.a_street[0], self.a_street[1],
                                       self.a_street[3], self.a_street[2]), self.opmerking, self.capaciteit,
                                       'To be calculated in Module 3', '%.2f' % self.length_km_ps1,
                                       '%.2f' % (self.length_km_ps1 + self.length_km_ps2),
                                       'https://stad.gent/mobiliteitsplan/het-parkeerplan/parkeren-op-straat'])

                rb2_wgs.setAttributes(['Street_Walk',
                                       '%s %s, %s %s' % (self.a_from[0], self.a_from[1], self.a_from[3], self.a_from[2]),
                                       '%s %s, %s %s' % (self.a_to[0], self.a_to[1], self.a_to[3], self.a_to[2]),
                                       'date: %s , time: %s' % (self.route_calc['date'], self.route_calc['time']),
                                       self.route_calc['duration'], self.zone, '%s %s, %s %s' % (self.a_street[0], self.a_street[1],
                                       self.a_street[3], self.a_street[2]), self.opmerking, self.capaciteit,
                                       'To be calculated in Module 3', '%.2f' % self.length_km_ps2,
                                       '%.2f' % (self.length_km_ps1 + self.length_km_ps2),
                                       'https://stad.gent/mobiliteitsplan/het-parkeerplan/parkeren-op-straat'])

                # set the fields for feature attributes
                fields = QgsFields()
                fields.append(QgsField('Name', QVariant.String))
                fields.append(QgsField('From', QVariant.String))
                fields.append(QgsField('To', QVariant.String))
                fields.append(QgsField('Departure', QVariant.String))
                fields.append(QgsField('Duration', QVariant.String))
                fields.append(QgsField('Parking_Street', QVariant.String))
                fields.append(QgsField('P_Address', QVariant.String))
                fields.append(QgsField('P_Remark', QVariant.String))
                fields.append(QgsField('P_Capacity', QVariant.Int))
                fields.append(QgsField('P_Cost', QVariant.String))
                fields.append(QgsField('Distance (km)', QVariant.Double))
                fields.append(QgsField('Distance_Total (km)', QVariant.Double))
                fields.append(QgsField('URL', QVariant.String))

                # create the writer and write the geometry
                writer = QgsVectorFileWriter(filename, 'utf-8', fields, QGis.WKBLineString, kml_crs, "KML")

                if writer.hasError() != QgsVectorFileWriter.NoError:
                    self.export_error('Street')

                # add the feature
                writer.addFeature(rb1_wgs)
                writer.addFeature(rb2_wgs)

                # delete the writer to flush features to disk
                del writer

            except:
                self.export_error('Street')

    # --------------------------------------------------------------------------#

    # Load all the layers
    # for future reference: use a list and iterate through it!
    def base_map(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))

        # CRAB Data for addresses
        filename = os.path.join(cur_dir,
                                "Data",
                                "CRAB",
                                "Crab.shp")
        self.crab = QgsVectorLayer(filename, "crab", "ogr")

        # routing layers
        # cars
        filename = os.path.join(cur_dir,
                                "Data",
                                "OSM",
                                "OSM_cars_ways.shp")
        self.osm_car = QgsVectorLayer(filename, "osm_car", "ogr")
        # bike
        filename = os.path.join(cur_dir,
                                "Data",
                                "OSM",
                                "OSM_bike_ways.shp")
        self.osm_bike = QgsVectorLayer(filename, "osm_bike", "ogr")
        # walk
        filename = os.path.join(cur_dir,
                                "Data",
                                "OSM",
                                "OSM_walk_ways.shp")
        self.osm_walk = QgsVectorLayer(filename, "osm_walk", "ogr")

        # POI
        filename = os.path.join(cur_dir,
                                "Data",
                                "POI",
                                "P+R.geojson")
        self.PR = QgsVectorLayer(filename, "PR", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.PR)

        filename = os.path.join(cur_dir,
                                "Data",
                                "POI",
                                "ParkeerGarages.geojson")
        self.ParkingGarage = QgsVectorLayer(filename, "ParkingGarage", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.ParkingGarage)

        filename = os.path.join(cur_dir,
                                "Data",
                                "POI",
                                "Stations.geojson")
        self.Train = QgsVectorLayer(filename, "Train", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Train)

        filename = os.path.join(cur_dir,
                                "Data",
                                "POI",
                                "BlueBike.geojson")
        self.BlueBike = QgsVectorLayer(filename, "BlueBike", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.BlueBike)

        filename = os.path.join(cur_dir,
                                "Data",
                                "POI",
                                "Cambio.geojson")
        self.Cambio = QgsVectorLayer(filename, "Cambio", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Cambio)

        filename = os.path.join(cur_dir,
                                "Data",
                                "POI",
                                "Taxi.geojson")
        self.Taxi = QgsVectorLayer(filename, "Taxi", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Taxi)

        # Zones
        filename = os.path.join(cur_dir,
                                "Data",
                                "Zones",
                                "ParkeerTariefZones.geojson")
        self.ParkingAreas = QgsVectorLayer(filename, "ParkingAreas", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.ParkingAreas)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Zones",
                                "SectorenCirculatiePlan.geojson")
        self.Circulation = QgsVectorLayer(filename, "Circulation", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Circulation)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Zones",
                                "BewonersZones.geojson")
        self.Inhabitants = QgsVectorLayer(filename, "Inhabitants", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Inhabitants)

        # Info layer
        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "Wvb.shp")
        self.Wvb = QgsVectorLayer(filename, "Wvb", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wvb)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "Knippen.geojson")
        self.Knippen = QgsVectorLayer(filename, "Knippen", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Knippen)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "ParkeerAutomaten.geojson")
        self.ParkeerAutomaten = QgsVectorLayer(filename, "ParkeerAutomaten", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.ParkeerAutomaten)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "ParkeerPlaatsMensenMetBeperking.geojson")
        self.Handicap = QgsVectorLayer(filename, "Handicap", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Handicap)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "Rijrichtingen.geojson")
        self.Rijrichting = QgsVectorLayer(filename, "Rijrichting", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Rijrichting)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "ParkeerAreaal.geojson")
        self.ParkeerAreaal = QgsVectorLayer(filename, "StreetParking", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.ParkeerAreaal)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "Centrum.geojson")
        self.Centrum = QgsVectorLayer(filename, "Centrum", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Centrum)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "Parken.geojson")
        self.Parken = QgsVectorLayer(filename, "Parken", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Parken)

        filename = os.path.join(cur_dir,
                                "Data",
                                "Info",
                                "Gemeenten.geojson")
        self.Gemeenten = QgsVectorLayer(filename, "Gemeenten", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Gemeenten)

        # GRB
        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Wcz.shp")
        self.Wcz = QgsVectorLayer(filename, "Wcz", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wcz)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Wrb.shp")
        self.Wrb = QgsVectorLayer(filename, "Wrb", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wrb)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Wli.shp")
        self.Wli = QgsVectorLayer(filename, "Wli", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wli)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Wrl.shp")
        self.Wrl = QgsVectorLayer(filename, "Wrl", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wrl)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Wti.shp")
        self.Wti = QgsVectorLayer(filename, "Wti", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wti)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Wga.shp")
        self.Wga = QgsVectorLayer(filename, "Wga", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wga)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Knw.shp")
        self.Knw = QgsVectorLayer(filename, "Knw", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Knw)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Sbn.shp")
        self.Sbn = QgsVectorLayer(filename, "Sbn", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Sbn)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Wtz.shp")
        self.Wtz = QgsVectorLayer(filename, "Wtz", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wtz)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Trn.shp")
        self.Trn = QgsVectorLayer(filename, "Trn", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Trn)

        filename = os.path.join(cur_dir,
                                "Data",
                                "GRB",
                                "Wbn.shp")
        self.Wbn = QgsVectorLayer(filename, "Wbn", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.Wbn)

        # Ortho
        url = "url=http://geoservices.informatievlaanderen.be/raadpleegdiensten/omwrgbmrvl/wms?&format=image/png&layers=Ortho&styles=&crs=EPSG:31370"
        self.Ortho = QgsRasterLayer(url, 'Ortho', 'wms')
        if self.Ortho.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(self.Ortho)
        else:
            pass

        # call the method that loads the layers onto the map
        self.show_maplayers()

    def show_maplayers(self):
        # show the layers in the mapCanvas
        layers = []

        # POI
        if self.checkBox_PR.isChecked():
            layers.append(QgsMapCanvasLayer(self.PR))
        if self.checkBox_Garage.isChecked():
            layers.append(QgsMapCanvasLayer(self.ParkingGarage))
        if self.checkBox_Train.isChecked():
            layers.append(QgsMapCanvasLayer(self.Train))
        if self.checkBox_BlueBike.isChecked():
            layers.append(QgsMapCanvasLayer(self.BlueBike))
        if self.checkBox_Cambio.isChecked():
            layers.append(QgsMapCanvasLayer(self.Cambio))
        if self.checkBox_Taxi.isChecked():
            layers.append(QgsMapCanvasLayer(self.Taxi))

        # Zones
        if self.checkBox_ParkingAreas.isChecked():
            layers.append(QgsMapCanvasLayer(self.ParkingAreas))
        if self.checkBox_Circulation.isChecked():
            layers.append(QgsMapCanvasLayer(self.Circulation))
        if self.checkBox_Inhabitants.isChecked():
            layers.append(QgsMapCanvasLayer(self.Inhabitants))

        # Info
        if self.checkBox_Info.isChecked():
            layers.append(QgsMapCanvasLayer(self.Wvb))
            layers.append(QgsMapCanvasLayer(self.ParkeerAutomaten))
            layers.append(QgsMapCanvasLayer(self.Handicap))
            layers.append(QgsMapCanvasLayer(self.Rijrichting))
            layers.append(QgsMapCanvasLayer(self.ParkeerAreaal))
            layers.append(QgsMapCanvasLayer(self.Knippen))
            layers.append(QgsMapCanvasLayer(self.Gemeenten))
            layers.append(QgsMapCanvasLayer(self.Parken))
            layers.append(QgsMapCanvasLayer(self.Centrum))

        # GRB - Ortho
        if self.checkBox_Ortho.isChecked():
            layers.append(QgsMapCanvasLayer(self.Ortho))

        elif not self.checkBox_Ortho.isChecked():
            layers.append(QgsMapCanvasLayer(self.Wcz))
            layers.append(QgsMapCanvasLayer(self.Wrb))
            layers.append(QgsMapCanvasLayer(self.Wli))
            layers.append(QgsMapCanvasLayer(self.Wrl))
            layers.append(QgsMapCanvasLayer(self.Wti))
            layers.append(QgsMapCanvasLayer(self.Wga))
            layers.append(QgsMapCanvasLayer(self.Knw))
            layers.append(QgsMapCanvasLayer(self.Sbn))
            layers.append(QgsMapCanvasLayer(self.Wtz))
            layers.append(QgsMapCanvasLayer(self.Trn))
            layers.append(QgsMapCanvasLayer(self.Wbn))

        self.mapCanvas.setLayerSet(layers)


##########################################################################

def main():

    # create a Qt application
    app = QtGui.QApplication(sys.argv)

    # initialize qgis libraries
    QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
    QgsApplication.initQgis()

    # create main window
    window = MySpotWindow()
    window.base_map()

    # show and raise the UI to foreground
    window.show()
    window.raise_()

    # index the crab layer
    window.crab_index()

    # run the application (event loop until the main window is closed)
    app.exec_()

    # exit the application and tidy up
    app.deleteLater()
    QgsApplication.exitQgis()

    # ultimate answer for crash-on-exit of pyqt.
    sip.setdestroyonexit(False)

if __name__ == "__main__":
    main()


