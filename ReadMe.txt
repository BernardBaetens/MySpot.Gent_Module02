Name:           MySpot.Gent
Version:        0.1
Begin:          2017-02-24
Copyright:      (c) 2017 by Bernard Baetens
Email:          bernard_baetens@tutanota.com

# ------ #

The application makes use of the QGIS libraries.
For use of the application:
    - install QGIS (OSGeo4W64 installation)
    - copy and paste the .svg -files from 'MySpot.Gent_Application\Resources\Icons_extra'
      to '%OSGEO4W_ROOT%\apps\qgis\svg'
    - Install 'text me one' font ('%\MySpot.Gent_Application\Resources\Font')
	- (Adjust directories in .cmd-file if needed)
	
	- For a shotcut on the desktop:
		- create shortcut from the.cmd file
		- change the icon to 'Rafa_Head_Big.ico' from the 
		  'MySpot.Gent_Application\Resources' directory
		- change name to 'MySpot.Gent'
    
# ------ #

This program is free software; you can redistribute it and/or modify  
it under the terms of the GNU General Public License as published by  
the Free Software Foundation; either version 2 of the License, or     
(at your option) any later version.

# ------ #

The MySpot.Gent application is built for 'module 2 - Geodata ontwerpen en verwerken'
of the Postgraduate Geo-ICT at HoGent 2016-2017

Purpose:
Provide the user insights into the 'Circulation - Parking and Mobility Plan 
of the City of Ghent to be launched on 2017-04-03.
Provide a routing for three parking possibilities (P+R, Parking Garage and 
Street Parking) with additional data about the parking abilities.
Possibility to export the routing to KML.

# ------ #

The data used within the application consists exclusively of 'open data'.

# ------ #
    
For the routing functions the 'QGIS network analysis library' was used.
This provides 'a' routing. For now this does not provide a routing that 
is applicable to the coming Mobility Plan. In a later fase a more in depth 
routing will be provided through the use of POSTGIS and pgRouting.

# ------ #

- The application window is (for now) non-responsive. So a Full-HD resolution
 (1920x1080) is strongly advised.
- If your graphics card is not up to standard, the colors could come off to strong.