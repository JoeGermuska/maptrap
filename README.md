Map that Trap
=============
A system for helping Chicagoans report problem buildings in their neighborhoods.

The Chicago Police created a REST API (http://api1.chicagopolice.org/clearpath/documentation) which, among other things, supports reporting community concerns. We considered the problem of making it easy for people to report on vacant buildings and other problem buildings in their neighborhood.

What's here now is code to: 
* load in the city's shapefile of building footprints
* find building footprints within a certain circle around a point
* create an Excel spreadsheet for a list of building footprints
* load in an updated version of that spreadsheet which contains indications of problem buildings and create "concerns" using the police API.

What needs to be done (broadly):
* any and all web interface (including below)
* something to support drawing boundaries on a map and getting the footprints in that shape, instead of a circle
* integration with http://localdata.com/ to make data collection easier than using a spreadsheet
* integration with other data sources about problem buildings