"use strict";
mapboxgl.accessToken = 'pk.eyJ1IjoiamFtZXNjcmFzdGVyIiwiYSI6ImNrYmo0NWlxcTBsaDYycnB2YmU5aTgzN3EifQ.Or9ka8Q8WOKvNEXTznnVFw';
let map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11', // stylesheet location
    center: [-0.118092, 51.509865], // starting position [lng, lat]
    //restrict panning/zooming to the british isles
    maxBounds: [[-10.8544921875,
        49.82380908513249], [2.021484375,
        59.478568831926395]],
    zoom: 10 // starting zoom
});
//add routing source and layer 
map.on('load', () => {
    map.addSource('route', {
        'type': 'geojson',
        'data': {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [-122.48369693756104, 37.83381888486939],
                    [-122.48348236083984, 37.83317489144141],
                    [-122.48339653015138, 37.83270036637107],
                    [-122.48356819152832, 37.832056363179625],
                    [-122.48404026031496, 37.83114119107971],
                    [-122.48404026031496, 37.83049717427869],
                    [-122.48348236083984, 37.829920943955045],
                    [-122.48356819152832, 37.82954808664175],
                    [-122.48507022857666, 37.82944639795659],
                    [-122.48610019683838, 37.82880236636284],
                    [-122.48695850372314, 37.82931081282506],
                    [-122.48700141906738, 37.83080223556934],
                    [-122.48751640319824, 37.83168351665737],
                    [-122.48803138732912, 37.832158048267786],
                    [-122.48888969421387, 37.83297152392784],
                    [-122.48987674713133, 37.83263257682617],
                    [-122.49043464660643, 37.832937629287755],
                    [-122.49125003814696, 37.832429207817725],
                    [-122.49163627624512, 37.832564787218985],
                    [-122.49223709106445, 37.83337825839438],
                    [-122.49378204345702, 37.83368330777276]
                ]
            }
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
//zooming,rotating
map.addControl(new mapboxgl.NavigationControl());
//add address search
/*map.addControl(
    new MapboxGeocoder({
        countries: 'gb',
        //bounding box to restrict geocoding to london:
        //bbox: [["51.2867602", "0.3340155"], ["51.2867602", "0.3340155"]],
        accessToken: mapboxgl.accessToken,
        mapboxgl: mapboxgl
    })
);*/

let directionsControl = new MapboxDirections({
    //accessToken: mapboxgl.accessToken,
    controls: { inputs: true, instructions: false, profileSwitcher: true }
});

let start = undefined;
let destination = undefined;
//when destination/origin updated on input UI
directionsControl.on('origin', (type) => { console.log(type); start = type; processRoute() })
directionsControl.on('destination', (type) => { console.log(type); destination = type; processRoute() })
//when destination/origin cleared on input UI
directionsControl.on('clear', (type) => { type.type == "origin" ? start = undefined : destination = undefined; console.log(type); map.setLayoutProperty('route', 'visibility', 'none') });
function processRoute() {
    if (start && destination) {
        console.log(start.feature.geometry.coordinates);
        console.log(destination.feature.geometry.coordinates);
        map.getSource('route').setData({
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'LineString',
                'coordinates': [start.feature.geometry.coordinates, destination.feature.geometry.coordinates]
            }
        })
        map.setLayoutProperty('route', 'visibility', 'visible');
    }
}

map.addControl(directionsControl, 'top-left');
