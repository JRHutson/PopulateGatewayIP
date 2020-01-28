import pandas as pd
import os
import config
import requests
import arcgis
from arcgis.features import SpatialDataFrame
from arcgis import GIS
import getpass
from netaddr import *
from copy import deepcopy
##from tkinter import filedialog
##from tkinter import #adding Tkinter to return the file name

sites = {"Area1":"SurveyID1", "Area2":"SurveyID2", "Area3":"SurveyID3", "Area4": "SurveyID4"}


#Pull DNS data into a dataframe with column headers
rawdata = pd.read_csv('**URLofDNSListing**', sep='|', index_col=False, 
                 names=['Type', 'IPAddress', 'MacAddress', 'MachineName'])

#Filter DataFrame for only DHCP data and Machine Names in California South
DNSdf = rawdata.loc[(rawdata['Type'] == 'DHCP') & (rawdata['MachineName'].str.startswith('cs'))]


# Pull Network Segment Ranges into DataFrame
DNSrange = pd.read_csv('**URLofNetworkSegmentation**', sep='|', usecols = [*range(0, 13)])
DNSrange.columns = ['First', 'Last', 'Column 3', 'StreetAddress', 'FacilitiesCode', 'FacilityName', 'C7', 'C8', 'C9', 'C10', 'State', 'Zip', 'C13',]

NUID = getpass.getuser()
Password = getpass.getpass()
gis = GIS("URLofESRIPortal", UserID, Password)
print("Connected")
siteMessages = []
for key, value in sites.items():
    #print(value)
    item = gis.content.get(value)
    #print(item)
    
    flayer = item.layers[0]
    #print(flayer)
    #Query produces a Feature Set, which is needed to call .features
    fSet = flayer.query()
    #Stores all features so that ones needing update can be copied
    all_features = fSet.features
    #Pulls data into Data Frame for manipulation with Pandas
    ESRIdf = SpatialDataFrame.from_layer(flayer)
    #print(ESRIdf.head())


    features_for_update = []
    #Iterate over ESRI Data Frame
    print("Starting Query")
    for index, row in ESRIdf.iterrows():
        # skip rows that already have a gateway IP or don't contain a machine
        if pd.notnull(row['gatewayip']) or row['followup']!='No':
            #print("Skipped Row")
            continue
        # Skip rows without an asset tag
        elif pd.isnull(row['asset']):
            #print("Skipped " + str(row['objectid']))
            continue
        else:
            #print(row)
            # Store asset tag in variable
            asset = row['asset']
            #print(asset.lower())
            # Query DNS Data Frame for an entry contining the asset tag
            computer = DNSdf.loc[DNSdf['MachineName'].str.contains(asset.lower())]
            #print(computer)
            # If no results skip
            if computer.empty:
                #print("Not found in DNS.")
                continue
            else:
                #Get machine IP from computer object
                machineIP = computer.iloc[0]['IPAddress']
                #print("MachineIP =" + machineIP)
                # Define IP Address value in Netaddr
                ip = IPAddress(machineIP)
                #print("IP = " + str(int(ip)))
                # Query DNS Segments for segment containing it
                segment = DNSrange.query("First < " + str(int(ip)) + " < Last")
                #print(segment)
                # Calculate Gateway for segment (First IP in segment + 1)
                gateway = IPAddress(str(segment.iloc[0]['First'] + 1))
                #print("Gateway IP= " + str(gateway))
                # Modify feature from ESRI Portal
                original_feature = [f for f in all_features if f.attributes['asset'] == row['asset']][0]
                feature_to_be_updated = deepcopy(original_feature)
                # Update gateway IP field with value
                feature_to_be_updated.attributes['gatewayip'] = str(gateway)
                # Add feature to list for update
                features_for_update.append(feature_to_be_updated)

    #print(features_for_update)

    if len(features_for_update) != 0:
        flayer.edit_features(updates = features_for_update)
        message = str(len(features_for_update)+1) + " Features Updated In " + key + "."
        print(message)
        siteMessages.append(message)
    else:
        message = "No features to update in " + key + "."
        print(message)
        siteMessages.append(message)

linebreak = "\\n"
finalMessage = linebreak.join(siteMessages)
#setting up url for API
url_root = config.webhook_url
api_call = '{"Title":"Gateway IP Script Run Confirmation", "Text":"' + finalMessage + '"}'
print(api_call)

#header for GET call
call_header = {"Content-Type":"application/json"}


#calling API
post_session = requests.session()
print("DEBUG: POST request in progress...")
post_response = post_session.post(url_root, data= api_call, headers=call_header, verify=False)
print("DEBUG: POST request done.")
print(post_response.text)
#sdf.to_csv("SpatialDataFrameTest.csv", encoding = 'utf-8', index =False)
#https://developers.arcgis.com/python/sample-notebooks/updating-features-in-a-feature-layer/#Perform-updates-to-the-existing-features
