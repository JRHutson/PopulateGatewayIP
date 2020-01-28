# PopulateGatewayIP
Python Script to pull features from an ESRI server, determine the Gateway IP of a computer and update the feature.

Tools:

Python

Pandas

ArcGIS API for Python

Netaddr

The field names in the script are specific to the datasets that were used in a specific effort. Leveraging the code elsewhere will require reformatting to suit your environment.

Script pulls features that were added to an ESRI Portal using Survey 123. 
It then uses an asset tag attribute to query DNS listings and identify the computer IP Address.
The address is used to query network segments and indentfy the gateway IP of the machine.
That data is added to the feature to be pushed back to the server.
