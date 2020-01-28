# PopulateGatewayIP
Python Script to pull features from an ESRI server, determine the Gateway IP of a computer and update the feature.

Tools:

Python

Pandas

ArcGIS API for Python

Netaddr

Script pulls features that were added to and ESRI Portal using Survey 123. 
It then uses an asset tag attribute to query DNS listings and identify the computer IP Address.
The address is used to query network segments and indentfy the gateway IP of the machine.
That data is added to the feature to be pushed back to the server.
