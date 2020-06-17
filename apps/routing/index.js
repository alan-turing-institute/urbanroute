"use strict";
mapboxgl.accessToken = 'pk.eyJ1IjoiamFtZXNjcmFzdGVyIiwiYSI6ImNrYmo0NWlxcTBsaDYycnB2YmU5aTgzN3EifQ.Or9ka8Q8WOKvNEXTznnVFw';
let map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11?optimize=true', // stylesheet location
    center: [-0.118092, 51.509865], // starting position [lng, lat]
    //restrict panning/zooming to the british isles
    maxBounds: [[-10.8544921875,
        49.82380908513249], [2.021484375,
        59.478568831926395]],
    zoom: 10 // starting zoom
});

map.on('load', () => {
    //show dynamic map instead of static background
    document.getElementById("map").style.visibility = "visible";
    //add routing layer and an empty source (as no route currently)
    map.addSource('route', {
        'type': 'geojson',
        'data': {
            'type': 'FeatureCollection',
            'features': []
        }
    });
    map.addLayer({
        'id': 'route',
        'type': 'line',
        'source': 'route',
        'layout': {
            'line-join': 'round',
            'line-cap': 'round'
        },
        'paint': {
            'line-color': '#888',
            'line-width': 8
        }
    });
    map.setLayoutProperty('route', 'visibility', 'none')
});
//add fullscreen control to the map
map.addControl(new mapboxgl.FullscreenControl());
//zooming and rotating
map.addControl(new mapboxgl.NavigationControl());

//add direction controls
let directionsControl = new MapboxDirections({
    accessToken: mapboxgl.accessToken,
    controls: { inputs: true, instructions: false, profileSwitcher: true }
});

let origin = undefined;
let destination = undefined;
//when destination/origin updated on input UI, check to see if route can be formed
directionsControl.on('origin', (location) => { origin = location; processRoute() })
directionsControl.on('destination', (location) => { destination = location; processRoute() })
//when destination/origin cleared on input UI, clear route and remove marker
directionsControl.on('clear', (event) => { event.type == "origin" ? origin = undefined : destination = undefined; map.setLayoutProperty('route', 'visibility', 'none') });
//if both origin and destination present, draw a route
function processRoute() {
    if (origin && destination) {
        map.getSource('route').setData({
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'LineString',
                'coordinates': [origin.feature.geometry.coordinates, destination.feature.geometry.coordinates]
            }
        })
        map.setLayoutProperty('route', 'visibility', 'visible');
    }
}
//add direction controls
map.addControl(directionsControl, 'top-left');
