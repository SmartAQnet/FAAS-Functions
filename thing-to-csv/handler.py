#!/usr/bin/env python
# coding: utf-8

# # Simple CSV Export SAQN Webseite

# Takes a Thing iot.id as argument e.g. saqn:t:xyz and outputs a CSV datasheet with all observations of the thing
import pandas as pd
import requests
import json
import copy
import sys
import os

url = "https://api.smartaq.net/v1.0"

def getdatastreamIDs(thingid):
    query = url + "/Things('" + thingid + "')/Datastreams?$select=@iot.id"
    return(list(map(lambda x: x["@iot.id"], json.loads(requests.get(query).text)["value"])))

def datafromlink(link):
    return(json.loads(requests.get(link).text))

def grabdata(ds, from_date, to_date):
    top = 2147483646
    link=url + "/Datastreams('" + ds + "')/Observations?$select=phenomenonTime,result&$filter=phenomenonTime gt " + from_date + " and phenomenonTime lt " + to_date + "&$top=" + str(top);

    metadata = json.loads(requests.get(url + "/Datastreams('" + ds + "')?$expand=ObservedProperty,Thing,Sensor").text)

    
    resultframe = pd.DataFrame()
    morenextlinks=True;

    while(morenextlinks):

        try: 
            obs=json.loads(requests.get(link).text)['value']
            if(obs==[]):
                #print('no observations under this link')
                break
                
        except: 
            #print('no observations under this link')
            break


        if(len(obs)>0):
            df = pd.DataFrame.from_dict(obs).set_index("phenomenonTime")
            df.rename(columns={'result': metadata["name"] + " (id: " + metadata["@iot.id"] + ")"},inplace=True)
            resultframe = pd.concat([resultframe, df], sort=True)
            resultframe.index.name = "phenomenonTime"

            try:
                link=json.loads(requests.get(link).text)["@iot.nextLink"]
            except:
                morenextlinks=False;
                break

    return(resultframe)


def createbigdf(listofds, from_date, to_date):

    concatme_with_duplicates=list(map(lambda x: grabdata(x, from_date, to_date),listofds))
    concatme = list(map(lambda x: x[~x.index.duplicated(keep='first')],concatme_with_duplicates))
    bigdf = pd.concat(concatme, axis=1, sort=True)
        
    return(bigdf)

def handle(event, context):

    thingid = event.query['thingid'] if event is not None else "saqn:t:7bd2cd3"
    from_date = event.query['from_date'] if event is not None else "2019-09-01T23:00:00.000Z"
    to_date = event.query['to_date'] if event is not None else "2019-11-17T23:59:00.000Z"
    download = event.query['download'] if event is not None and 'download' in event.query else None


    dslist=getdatastreamIDs(thingid)
    sheet=createbigdf(dslist, from_date, to_date)
    sheet.index = sheet.index.map(lambda s: s.replace("T", " ").replace(".000Z", ""))

    return {
        "statusCode": 200,
        "body": sheet.to_csv(),
        "headers": {
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment;filename=" + download + ".csv" if download is not None else "inline"
        }
    }

if os.environ.get("DEBUG") is "1":
    print(handle(None, None))
