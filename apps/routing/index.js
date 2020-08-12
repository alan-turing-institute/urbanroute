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
    map.addSource("myImageSource", {
        "type": "image",
        "url": "pollution.png",
        "coordinates": [
            [-0.550992140362932, 51.71276304828286],
            [0.3764553855290124, 51.71276304828286],
            [0.3764553855290124, 51.26638747107266],
            [-0.550992140362932, 51.26638747107266]
        ]
    });

    map.addLayer({
        "id": "overlay",
        "source": "myImageSource",
        "type": "raster",
        "paint": {
            "raster-opacity": 0.3
        }
    });
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
//add geolocation
map.addControl(
    new mapboxgl.GeolocateControl({
        positionOptions: {
            enableHighAccuracy: true
        },
        trackUserLocation: true
    })
);

//add direction controls
let directionsControl = new MapboxDirections({
    accessToken: mapboxgl.accessToken,
    controls: { inputs: true, instructions: false, profileSwitcher: true },
    flyTo: false
});

let origin = undefined;
let destination = undefined;
//when called from the mapbox plugin, if both origin and destination are present, draw a route
window.getRoute = function processRoute() {
    if (origin && destination) {
        console.log(origin.feature.geometry.coordinates);
        fetch(`http://127.0.0.1:8000/route/?source_lat=${origin.feature.geometry.coordinates[1]}&source_long=${origin.feature.geometry.coordinates[0]}&target_lat=${destination.feature.geometry.coordinates[1]}&target_long=${destination.feature.geometry.coordinates[0]}`)
            .then(response => response.json()).then(data => {
                map.setLayoutProperty('route', 'visibility', 'visible');
                map.getSource('route').setData({
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': data.map(point => [point.x, point.y])
                        //[origin.feature.geometry.coordinates, destination.feature.geometry.coordinates]
                    }
                })
            });

    };
}
//when destination/origin updated on input UI, check to see if route can be formed
directionsControl.on('origin', (location) => { origin = location; })
directionsControl.on('destination', (location) => { destination = location; })
//when destination/origin cleared on input UI, clear route and remove marker
directionsControl.on('clear', (event) => { event.type == "origin" ? origin = undefined : destination = undefined; map.setLayoutProperty('route', 'visibility', 'none') });

directionsControl.on('route', (route) => { console.log(route) });

//add direction controls
map.addControl(directionsControl, 'top-left');
