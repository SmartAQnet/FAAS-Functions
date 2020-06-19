#!/usr/bin/env python
# coding: utf-8
import json, requests
import pandas as pd
import numpy as np

def querytodict(s): 
    try:
        return dict((x.split("=")[0],x.split("=")[1]) for x in query.split("?")[1].split("&"))
    except: 
        return {}

def dicttoquery(d):
    try:
        return "&".join(list(map(lambda x: x + "=" + d[x],d.keys())))
    except:
        return ""


def setupquery(query,timestamp_from,timestamp_to):

    timequery = "resultTime gt " + timestamp_from + " and resultTime lt " + timestamp_to
    selectquery = "result,resultTime"

    try:
        [queryprefix,querysuffix] = query.split("?")
    except: 
        [queryprefix,querysuffix] = [query,""]

    #if there is actually a query
    if "=" in querysuffix:
        filterparams=querytodict(querysuffix)

        #if "filter" is being used in the query
        if("$filter" in filterparams.keys()): 

            #if already filtering by phenomenonTime -> use that instead of query
            if("phenomenonTime" in filterparams["$filter"]):
                print("phenomenonTime already filtered, using that for aggregation")

            #else add the time query to the filter
            else: 
                filterparams["$filter"] += "," + timequery

        #else just add the filter
        else: 
            filterparams["$filter"]=timequery


        filterparams["$select"] = selectquery

        querysuffix = dicttoquery(filterparams)

    #else just add the query
    else: 
        querysuffix = "$filter=" + timequery + "&" + "$select=" + selectquery

    return([queryprefix, querysuffix])


def getandaggregate(query,timestamp_from,timestamp_to):
    
    url = "https://api.smartaq.net/v1.0"
        
    [queryprefix, querysuffix]=setupquery(query,timestamp_from,timestamp_to)

    #get the data
    datarequest = json.loads(requests.get(url + queryprefix + "?" + querysuffix).text)

    #prepare as dataframe
    data=pd.Series(list(map(lambda x: x["result"],datarequest["value"])),index=list(map(lambda x: pd.to_datetime(x["resultTime"]),datarequest["value"])))

    #aggregate the data
    agg=data.resample("1T").agg([np.sum, np.mean, np.std])[["mean","std"]]

    #output the result as a dataframe
    result=pd.DataFrame(data=agg[["mean"]].values,index=agg.index.map(lambda x: x.isoformat() + ".000Z"),columns=["result"])
    
    return(result)
    

def handle(event, context):
    
    result=getandaggregate("/Datastreams('saqn%3Ads%3A7540858')/Observations","2019-07-02T15:24:12.000Z","2019-07-03T15:24:12.000Z")
    
    
    return {
        "statusCode": 200,
        "body": result.to_json(),
        "headers": {
            "Content-Type": "application/json"
        }
    }
