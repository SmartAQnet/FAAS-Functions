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
            if("$top=" in link):
                morenextlinks=False;
    return data


def replaceTimes(thequery,startquery,endquery):

    starttrue=startquery
    endtrue=endquery
    
    for el in thequery.split("$"): 
        if("filter=resultTime" in el):
            for time in el.split("=")[1].split("and"):
                if("%20le%20" in time):
                    endstamp=time.split("resultTime%20le%20")[1].split("Z")[0] + "Z"
                    if(pd.to_datetime(endstamp) > pd.to_datetime(endquery)):
                        endtrue=endquery
                    else:
                        endtrue=endstamp
                elif("%20gt%20" in time):
                    startstamp=time.split("resultTime%20gt%20")[1].split("Z")[0] + "Z"
                    if(pd.to_datetime(startstamp) < pd.to_datetime(startquery)):
                        starttrue=startquery
                    else:
                        starttrue=startstamp
    return "$".join([("filter=resultTime%20gt%20" + starttrue +  "%20and%20" + "resultTime%20le%20" + endtrue + "&$count=true") if ("filter=resultTime" in x) else x for x in thequery.split("$")])

def handle(event, context):
    
    t = event.query["$aggregate"]
    realkeys = list(filter(lambda x: x != "$aggregate", event.query.keys()))
    urlquery = "&".join(list(map(lambda x: x + "=" + event.query[x], realkeys)))
    
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
    agg=data.resample(freq, label='right', closed='right').agg([np.sum, np.mean, np.std])
    agg["count"]=agg["sum"]/agg["mean"]
    
    #output the result as a dataframe
    result=pd.DataFrame({"result": list(round(agg["mean"],2)),"resultTime": [x.isoformat().split("+")[0] + ".000Z" for x in agg.index],"phenomenonTime": [(x-pd.Timedelta(str(t) + "m")).isoformat().split("+")[0] + ".000Z" + "/" + x.isoformat().split("+")[0] + ".000Z" for x in agg.index], "parameters": json.loads(agg[["count","std"]].apply(lambda x: round(x,3)).to_json(orient="records")),"Observations@iot.navigationLink": [replaceTimes(frostquery,(x-pd.Timedelta(str(t) + "m")).isoformat().split("+")[0] + ".000Z",x.isoformat().split("+")[0] + ".000Z") for x in agg.index]})
    
    return {
        "statusCode": 200,
        "body": '{"value":' + result.to_json(orient='records') + '}', 
        "headers": {
            "access-control-allow-origin": "*",
            "content-type": "application/json;charset=UTF-8"
        }
    }