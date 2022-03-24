# TransCAD-Data-Sheet
Read, parse, and write to the data sheet of TransCAD if you already got geodata.
## Descriptions
It's a text only document for the moment. These day I'm doing my homework via TransCAD and I have already downloaded geodata from OpenStreetMap, so I figured out the data format used by TransCAD
## OSM Data Parsing
OSM data is of XML format, you can parse it via lxml.etree.XML class by Python.
### "node"
"node" is the point on the map, it can be a independent point or a point consists a line or region with other points(nodes)
### "way"
"way" is the line on the map, it can also consists a region with other lines. A "way" can be a road, a river bank, a administrative boundary, or any other kind of lines exist on the map. If you just want roads, you can find a subelement with a tag "tag", and attributes 'k' = 'highway', 'v' = {'trunk', 'primary', 'secondary', ...}. Some roads may have the attributes of "maxspeed", "lanes", "name:en", "name:zh", "name:ja", ..., but not all of them do.
### "relation"
"relation" is the region on the map, it can comprise "relation", "way", or even "node". 
### Redundant Data
For most cases, you do not need to analyze all kinds of data in the osm map, you need to delete the ones you do not use for the convenience of data processing. If you do not delete them, the processing time may take too long, and the data set is very large. I'll upload one example in Python later.
## Data Format
If you create a layer, the data table is saved as ".dcb" file, like below:
  53
  "ID",I,1,4,0,4,0,,,"",,Blank,
  "Layer",C,5,13,0,13,0,,,"",,Blank,
  "Handle",I,18,4,0,10,0,,,"",,Blank,
  "Name",C,22,32,0,32,0,,,"","NoNameA",Blank,
The first line indicates the size of a single element (a point, line, or area).
The following lines indicate the properties (fields) of a element.
  "Layer" is the name of a filed; 
  C is the data type of the filed, I for int, and C for character;
  5 is the 1-based beginning index of this field;
  13 is the length of this field;
  The rest data is not discovered yet :).
