"use strict"
const fetch = require('node-fetch');
const queryString = require('query-string');
const jsonpath = require('jsonpath');
const moment = require('moment');

const aggregators = {
    "location": {
        "mean": meanLocation,
        "none": null
    },
    "result": {
        "mean": meanResult,
        "none": null
    },
    "time": {
        "mean": meanTime,
        "none": null
    }
};

module.exports = async (event, context) => {
    const result = await aggregateFromQuery(event);
    const cacheControl = event.headers["cache-control"] || "no-cache";
    context
        .status(200)
        .headers({
            "Content-Type":"application/json",
            "Cache-Control": cacheControl
        })
        .succeed(result);
}

async function aggregateFromQuery(event){

    //e.g. $top=100&$expand=FeatureOfInterest
    const queryStringRaw = queryString.stringify(event.query) || "$expand=HistoricalLocations/Locations,Datastreams($filter=ObservedProperty/@iot.id eq 'saqn:op:mcpm2p5' and not (phenomenonTime lt 2019-10-15T13:57:40.302Z or phenomenonTime gt 2019-10-15T14:57:40.302Z);$expand=ObservedProperty,Observations($filter=not (phenomenonTime lt 2019-10-15T13:57:40.302Z or phenomenonTime gt 2019-10-15T14:57:40.302Z);$top=999999;$expand=FeatureOfInterest))&$filter=Datastreams/ObservedProperty/@iot.id eq 'saqn:op:mcpm2p5' and st_within(HistoricalLocations/Location/location, geography'POLYGON((10.825996398925781 48.409605110127586,10.996215816121548 48.409605110127586,10.996215816121548 48.33206077323891,10.825996398925781 48.33206077323891,10.825996398925781 48.409605110127586))')";
    const queryPath = event.path || "/mean-none-mean-PT20M/";
    const pathSplit = queryPath.split("/");
    pathSplit.shift();
    const aggregateParamString = pathSplit.shift();
    const aggregateParam = aggregateParamString.split("-");
    const apiQueryURL = "http://api.smartaq.net/v1.0/" + pathSplit.join("/") + "?" + queryStringRaw;
    const queryResult = await getQuery(apiQueryURL);

    const aggregateResult = aggregators.result[aggregateParam[0]];
    const aggregateLocation = aggregators.location[aggregateParam[1]];
    const aggregateTime = aggregators.time[aggregateParam[2]];
    const duration = aggregateParam[3];

    if(Array.isArray(queryResult.value) && typeof queryResult.value[0] !== "undefined" && typeof queryResult.value[0].result !== "undefined"){
        queryResult.value = aggregate(aggregateResult, aggregateLocation, aggregateTime, duration, queryResult.value);
    }
    jsonpath.apply(queryResult, '$..Observations', function(value) { return aggregate(aggregateResult, aggregateLocation, aggregateTime, duration, value) });
    return queryResult;
}

/**
 * Returns the parsed JSON of the given URL
 * 
 * @param {string} apiQueryURL Path and QueryString (e.g. https://api.smartaq.net/v1.0/Observations?$top=20) which will be requested.
 */
async function getQuery(apiQueryURL){
    const apiResult = await fetch(apiQueryURL);
    return await apiResult.json();
}

function aggregate(resultAggregation, locationAggregation, timeAggregation, duration, observationData){
    if(!Array.isArray(observationData) || observationData.length == 0){
        return;
    }

    //data is reversed if needed depending on sort order by phenomenonTime.
    const needsReversal = observationData.length > 2 &&
        moment(observationData[1].phenomenonTime).isBefore(moment(observationData[0].phenomenonTime));
    observationData = observationData.sort(function (a, b) {
        return moment(a.phenomenonTime).isBefore(moment(b.phenomenonTime)) ? -1 : 1;
    });
    const aggregated = [[observationData[0]]];
    for(let i = 1; i < observationData.length; i++){
        const currentChunk = aggregated[aggregated.length - 1];
        const firstOfChunk = currentChunk[0];
        //difference between current data point and first point of current chunk
        const difference = moment(observationData[i].phenomenonTime).diff(moment(firstOfChunk.phenomenonTime));
        if(difference < Math.abs(moment.duration(duration).asMilliseconds())){
            //push to current chunk if time difference is not high enough
            currentChunk.push(observationData[i]);
        }
        else{
            //push to a new chunk when enough time has passed
            aggregated.push([observationData[i]]);
        }
    }
    let aggregatedData = aggregated.map(chunk => {
        let newObservation = chunk[0];
        if(resultAggregation){
            newObservation.result = resultAggregation(chunk.map(obs => {
                if(typeof obs.result === "undefined"){
                    throw "each Observation needs a result";
                }
                return obs.result;
            }));
        }
        if(locationAggregation){
            newObservation.FeatureOfInterest = locationAggregation(chunk.map(obs => {
                if(typeof obs.FeatureOfInterest === "undefined"){
                    throw "each Observation needs a FeatureOfInterest";
                }
                return obs.FeatureOfInterest;
            }));
        }
        if(timeAggregation){
            newObservation.phenomenonTime = timeAggregation(chunk.map(obs => {
                if(typeof obs.phenomenonTime === "undefined"){
                    throw "each Observation needs a phenomenonTime";
                }
                return obs.phenomenonTime;
            }));
        }
        return newObservation;
    });
    if(needsReversal){
        aggregatedData.reverse();
    }
    return aggregatedData;
}

function meanResult(results){
    return results.reduce((agg, curr) => agg + Number.parseFloat(curr), 0) / results.length;
}

function meanLocation(locations){
    const coordinates = locations.map(loc => loc.feature.coordinates);
    const lat = coordinates.reduce((agg, curr) => 
        agg + curr[0], 0
    ) / locations.length;
    const long = coordinates.reduce((agg, curr) => agg + curr[1], 0) / locations.length;
    const foi = locations[0];
    foi.feature.coordinates = [lat, long];
    foi.feature.type = "Point";
    return foi;
}

function meanTime(times){
    const timestamps = times.map(time => moment(time).valueOf());
    const meanTime = timestamps.reduce((agg, curr) => agg + curr, 0) / times.length;
    return moment(meanTime).toISOString();
}

/*module.exports(null, (n, result) => {
    console.log(JSON.stringify(result.result));
});*/
