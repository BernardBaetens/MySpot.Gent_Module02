from urllib2 import Request, urlopen
import json

from mySpot import *

#############################################################################


class PanTool(QgsMapTool):
    def __init__(self, mapCanvas):
        QgsMapTool.__init__(self, mapCanvas)
        self.setCursor(Qt.OpenHandCursor)
        self.dragging = False

    def canvasMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.canvas().panAction(event)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.canvas().panActionEnd(event.pos())
            self.dragging = False

#############################################################################


class InformationTool(QgsMapToolIdentify):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolIdentify.__init__(self, canvas)
        self.setCursor(Qt.WhatsThisCursor)

    def canvasReleaseEvent(self, event):
        found_features = self.identify(event.x(), event.y(),
                                       self.TopDownStopAtFirst,
                                       self.VectorLayer)
        if len(found_features) > 0:
            layer = found_features[0].mLayer
            feature = found_features[0].mFeature

            # call function depending on layer name
            if layer.name() == 'ParkingAreas':
                self.info_parking_areas(feature, layer)
            elif layer.name() == 'Circulation':
                self.info_circulation(feature, layer)
            elif layer.name() == 'StreetParking':
                self.info_streetparking(feature, layer)
            elif layer.name() == 'ParkingGarage':
                self.info_garages(feature, layer)
            elif layer.name() == 'PR':
                self.info_pr(feature, layer)

    # define the message-box for the information
    def msgbox(self, layername,  info):
        header = "%s Information" % layername
        msgbox = self.canvas
        msgbox.setStyleSheet("""
                .QMessageBox {}
                """)
        QMessageBox.information(msgbox, header, "\n".join(info))

    def msgbox_error(self):
        header = "Real-time data error"
        msg = 'No real-time data available due to internet or server connection.\nFalling back to regular data. '
        msgbox = self.canvas
        msgbox.setStyleSheet("""
                .QMessageBox {}
                """)
        QMessageBox.warning(msgbox, header, msg)

    # functions to create the information to be displayed
    def info_parking_areas(self, feature, layer):
        layername = layer.name()
        info = []

        name = feature.attribute('Zone')
        if name != None:
            info.append('Name: ' + name)
        url = feature.attribute('URL')
        if url != None:
            info.append('URL: ' + url)

        # call the message-box to be displayed
        self.msgbox(layername, info)

    def info_circulation(self, feature, layer):
        layername = layer.name()
        info = []

        name = feature.attribute('Naam')
        if name != None:
            info.append('Name: ' + name)
        zone = feature.attribute('Zone')
        if zone != None:
            info.append('Zone: ' + zone)

        # call the messagebox to be displayed
        self.msgbox(layername, info)

    # info over streetparking (parkeerareaal)
    def info_streetparking(self, feature, layer):
        layername = layer.name()
        info = []

        zone = feature.attribute('Pregime')
        if zone != None:
            if zone == '0':
                zone = 'Blauwe tariezone'
            if zone == '1':
                zone = 'Rode tariefzone'
            if zone == '2':
                zone = 'Oranje tariefzone'
            if zone == '3':
                zone = 'Gele tariefzone'
            if zone == '4':
                zone = 'Groene tariefzone'
            if zone == '5':
                zone = 'Vrij parkeren'
            if zone == '6':
                zone = 'Bewonersparkeren'
            if zone == '7':
                zone = 'Tijdsvenster (Voorbehouden tijdens specifiek deel van de dag (meer dan 1dag per week))'
            if zone == '8':
                zone = 'Voorbehouden (Voorbehouden ifv doelgroep, altijd de hele dag)'
            if zone == '9':
                zone = 'Foutparkeren (plaatsen waar geparkeerd wordt, hoewel er geen wettelijke parkeermogelijkheden zijn)'

            info.append('Parking Specification: ' + zone)

        opmerking = feature.attribute('Opmerkinge')
        if opmerking != None:
            info.append('Remark: ' + opmerking)

        capaciteit = feature.attribute('Capaciteit')
        if capaciteit != None:
            info.append('Capacity: ' + str(capaciteit))

        # call the message-box to be displayed
        self.msgbox(layername, info)

    # info P+R
    def info_pr(self, feature, layer):
        layername = layer.name()
        info = []

        name = feature.attribute('Naam')
        if name != None:
            info.append('Name: ' + name)

        address = feature.attribute('address')
        if address != None:
            info.append('Address: ' + address)

        capacity = feature.attribute('Aantal aut')
        if capacity != None:
            info.append('Capacity: ' + str(capacity))

        bike = feature.attribute('P+R-Fiets')
        if bike != None:
            info.append('P+R-Bike: ' + bike)

        status = feature.attribute('Status')
        if status != None:
            info.append('Status: ' + status)

        url = feature.attribute('URL')
        if url != None:
            info.append('URL: ' + url)

        # call the message-box to be displayed
        self.msgbox(layername, info)

    # info over parking garages
    def info_garages(self, feature, layer):
        layername = layer.name()
        info = []

        name = feature.attribute('naam')
        if name != None:
            info.append('Name: ' + name)

        # list of the garages with real-time data
        lst = ['Sint-Michiels', 'Sint-Pietersplein', 'Vrijdagmarkt', 'Savaanstraat', 'Ramen', 'Reep']

        if name in lst:
            # real-time data garages
            # check if everything goes for the real-time data, if not, fall back to non-real time
            try:
                self.garages_rt(name)
                info.extend(self.info_rt)
            except:
                self.garages_nrt(feature)
                info.extend(self.info_nrt)

        elif name == 'Gent Sint-Pieters':
            # real-time date of nmbs garage
            # check if everything goes for the real-time data, if not, fall back to non-real time
            self.garage_stpieters(feature)
            info.extend(self.info_nmbs)
            if not self.info_nmbs:
                self.garages_nrt(feature)
                info.extend(self.info_nrt)

        else:
            self.garages_nrt(feature)
            info.extend(self.info_nrt)

        url = feature.attribute('URL')
        if url != None:
            info.append('URL: ' + url)

        # call the message-box to be displayed
        self.msgbox(layername, info)

    # non real-time info about garages
    def garages_nrt(self, feature):
        self.info_nrt = []
        address = feature.attribute('address')
        if address != None:
            self.info_nrt.append('Address: ' + address)
        contact = feature.attribute('contact')
        if contact != None:
            self.info_nrt.append(contact)
        capacity = feature.attribute('capaciteit')
        if capacity != None:
            self.info_nrt.append('Capacity: ' + str(capacity))

    # --------------------------------------------------------------------------#

    # Real-time garage info
    def garages_rt(self, input):
        request = Request("https://datatank.stad.gent/4/mobiliteit/bezettingparkingsrealtime.json")

        try:
            response = urlopen(request)
            parking_read = response.read()

            parking_load = json.loads(parking_read)

            garage = {}

            for garages in parking_load:
                if garages['description'] == input:
                    garage = garages

            self.garage_load(garage)
        except:
            self.msgbox_error()

    # real- time info Gent-Sint-Pieters
    def garage_stpieters(self, feature):
        self.info_nmbs = []
        request = Request("https://datatank.stad.gent/4/mobiliteit/bezettingparkeergaragesnmbs.json")

        try:
            response = urlopen(request)
            nmbs_read = response.read()

            nmbs_load = json.loads(nmbs_read)

            for d in nmbs_load:
                parking_nmbs = d

            nmbs = parking_nmbs['parkingStatus']

            address = feature.attribute('address')
            if address != None:
                self.info_nmbs.append('Address: ' + address)
            contact = feature.attribute('contact')
            if contact != None:
                self.info_nmbs.append(contact)
            self.info_nmbs.append('Available Capacity (real-time): ' + str(nmbs['availableCapacity']))
            self.info_nmbs.append("\n")
            self.info_nmbs.append('Time of Data: ' + nmbs['lastModifiedDate'])
            if nmbs['open'] == 0:
                open = 'Yes'
            else:
                open = 'No'
            self.info_nmbs.append('Is open: ' + open)
            self.info_nmbs.append('Total Capacity: ' + str(nmbs['totalCapacity']))

        except :
            self.msgbox_error()

    # Real-time garage output
    def garage_load(self, garage):
        self.info_rt = []
        self.info_rt.append('Address: ' + garage['address'])
        self.info_rt.append(garage['contactInfo'])

        status = garage['parkingStatus']
        self.info_rt.append('Available Capacity (real-time): ' + str(status['availableCapacity']))
        self.info_rt.append("\n")
        self.info_rt.append('Time of Data: ' + status['lastModifiedDate'])
        self.info_rt.append('Is open: ' + str(status['open']))
        self.info_rt.append('Total Capacity: ' + str(status['totalCapacity']))

#############################################################################


class ClickTool(QgsMapToolEmitPoint):

    def __init__(self, canvas, where):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.point = None
        self.where = where

    def canvasPressEvent(self, e,):
        self.point = self.toMapCoordinates(e.pos())
        if self.where == 'from':
            # send a signal back to the 'From'
            self.emit(SIGNAL("Position_from(QgsPoint)"), self.point)
        else:
            # send a signal back to the 'To'
            self.emit(SIGNAL("Position_to(QgsPoint)"), self.point)






