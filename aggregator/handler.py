#!/usr/bin/env python
# coding: utf-8
import json, requests
import pandas as pd
import numpy as np

def getdata(initiallink):
    
    link=initiallink
    data=pd.Series(dtype="float64")
    morenextlinks=True
    
    while(morenextlinks):

        try:
            #get the data
            datarequest=json.loads(requests.get(link).text)
            if(datarequest['value']==[]):
                #print('no observations under this link')
                break

        except: 
            #print('no observations under this link')
            break


        if(len(datarequest['value'])>0):
            #append chunks
            datachunk=pd.Series(list(map(lambda x: x["result"],datarequest["value"])),index=list(map(lambda x: pd.to_datetime(x["resultTime"]),datarequest["value"])))
            data=data.append(datachunk)

            try:
                link=datarequest["@iot.nextLink"]
            except:
                morenextlinks=False;
                break
    return data


def handle(event, context):
    
    t = event.query["$aggregate"]
    realkeys = list(filter(lambda x: x != "$aggregate", event.query.keys()))
    urlquery = "&".join(list(map(lambda x: x + "=" + event.query[x], realkeys)))
    print(t)
    
    url = "https://api.smartaq.net/v1.0"
    frostquery=url + event.path + "?" + urlquery
    
    
    freq=str(t) + "T"
    data=getdata(frostquery)
    
    #check for empty link
    try:
        data[0]
    except: 
        return {
            "statusCode": 404,
            "body": {}, 
            "headers": {
                "Content-Type": "application/json"
            }
        }
    
    #aggregate the data
    agg=data.resample(freq).agg([np.sum, np.mean, np.std])
    agg["count"]=(agg["sum"]/agg["mean"]).apply(int)
    
    #output the result as a dataframe
    result=pd.DataFrame({"result": list(agg["mean"]),"resultTime": list(agg.index.map(lambda x: x.isoformat().split("+")[0] + ".000Z")),"phenomenonTime": list(agg.index.map(lambda x: (x-pd.Timedelta(str(t) + "m")).isoformat().split("+")[0] + ".000Z" + "/" + x.isoformat().split("+")[0] + ".000Z")), "parameters": json.loads(agg[["count","std"]].to_json(orient="records"))})
    
    
    
    return {
        "statusCode": 200,
        "body": result.to_json(orient='records'), 
        "headers": {
            "Content-Type": "application/json"
        }
    }
