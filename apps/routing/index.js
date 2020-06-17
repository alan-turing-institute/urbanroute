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
map.addControl(
    new MapboxDirections({
        accessToken: mapboxgl.accessToken
    }),
    'top-left'
);
