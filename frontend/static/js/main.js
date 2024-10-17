document.addEventListener('DOMContentLoaded', function() {
    // Your code here will run once the DOM is fully loaded
    let selectedLat = null;
    let selectedLon = null;
    let heatmapLayer = null;  // Declare a global variable for the heatmap layer

    // Initialize the map with a view centered on Helsinki
    const map = L.map('map').setView([60.170677, 24.941514], 12);

    // Add OpenStreetMap tiles to the map (basic map rendering)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copy</link>right">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Create a cluster group to handle marker clustering with specific options
    const markers = L.markerClusterGroup({
        maxClusterRadius: 40, 
        spiderfyOnMaxZoom: false, 
        zoomToBoundsOnClick: true, 
        showCoverageOnHover: true, 
        animate: true,
        removeOutsideVisibleBounds: true,  
        disableClusteringAtZoom: 15, 
        spiderLegPolylineOptions: { 
            weight: 0.5, 
            color: '#222',
            opacity: 0.3
        },
    });

    // Fetch the station data from the backend API
    console.log(stations);

    const vehicleTypes = {
        0: 'Tram',
        1: 'Metro',
        109: 'Train',
        3: 'Bus',
        4: 'Ferry',
    }

    // Arrays to store markers for different types of vehicles
    const busTramMarkers = [];
    const nonBusTramMarkers = [];

    // Function to return marker color based on the vehicle type
    function getMarkerColor(vehicleType) {
        switch (vehicleType) {
            case 0:
                return 'green';  // Tram
            case 1:
                return 'orange'; // Metro
            case 109:
                return 'red';    // Train
            case 3:
                return 'blue';   // Bus
            case 4:
                return 'purple'; // Ferry
            default:
                return 'gray';   // Default color for unknown/other types
        }
    }

    // Loop through all the stations and create markers accordingly
    stations.forEach(station => {
        const markerColor = getMarkerColor(station.vehicleType);
        const vehicleIcons = {
            0: 'fa-subway',     
            1: 'fa-subway',     
            109: 'fa-train',    
            3: 'fa-bus',        
            4: 'fa-ship',       
        };

        // Create a colored marker using the AwesomeMarkers plugin
        const coloredMarker = L.AwesomeMarkers.icon({
            icon: vehicleIcons[station.vehicleType],
            markerColor: markerColor,
            prefix: 'fa'
        });

        // Create the marker with the corresponding popup for station details
        const marker = L.marker([station.lat, station.lon], { icon: coloredMarker })
            .bindPopup(`${station.name} (${vehicleTypes[station.vehicleType]})`)
            .on('click', function() {
                selectedLat = station.lat;
                selectedLon = station.lon;
            });

        // Separate markers into bus/tram and non-bus/tram categories
        if (station.vehicleType === 0 || station.vehicleType === 3) {
            busTramMarkers.push(marker);
        } else {
            nonBusTramMarkers.push(marker);
            marker.addTo(map);
        }
    });

    // Add all non-bus/tram markers to the map at the beginning
    nonBusTramMarkers.forEach(marker => marker.addTo(map));

    // Initially add all bus and tram markers to the cluster group
    map.addLayer(markers);
    busTramMarkers.forEach(marker => {
        markers.addLayer(marker);
    });

    // Event listener for when the zoom starts
    map.on('zoomstart', function() {
        const currentZoom = map.getZoom();
        const zoomThreshold = 14;

        // Remove bus/tram markers from the map if zoom level is below threshold
        if (currentZoom <= zoomThreshold) {
            busTramMarkers.forEach(marker => marker.removeFrom(map));
        }
    });

    // Event listener for when zooming ends
    map.on('zoomend', function() {
        const currentZoom = map.getZoom();
        const zoomThreshold = 14;

        // Add or remove bus/tram markers based on zoom level
        if (currentZoom <= zoomThreshold) {
            busTramMarkers.forEach(marker => markers.addLayer(marker));
        } else {
            busTramMarkers.forEach(marker => {
                markers.removeLayer(marker);
                marker.addTo(map);
            });
        }
    });

    // Event listener for the "Elevate" button
    document.getElementById('elevateButton').addEventListener('click', function() {
        if (selectedLat && selectedLon) {
            // Send a POST request to trigger the elevation process with the selected station's lat/lon
            fetch('/elevate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    lat: selectedLat,
                    lon: selectedLon
                })
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to trigger elevation process');
                }
            })
            .then(data => {
                alert('Elevation process triggered successfully!');

                const maxTravelTime = Math.max(...data.map(station => station.travel_time));
                const minTravelTime = Math.min(...data.map(station => station.travel_time));

                // Remove existing heatmap layer if it exists
                if (heatmapLayer) {
                    map.removeLayer(heatmapLayer);
                }

                // Step 1: Prepare heatmap data using the station data returned from the backend
                const heatmapData = data.map(station => {
                    let travelTimeNormalized = (station.travel_time - minTravelTime) / (maxTravelTime - minTravelTime);
                    travelTimeNormalized = Math.min(Math.max(travelTimeNormalized, 0), 1);
                    return [station.lat, station.lon, travelTimeNormalized];
                });
                console.log("Heatmap Data:", heatmapData);

                // Step 2: Create and add the heatmap layer to the map
                heatmapLayer = L.heatLayer(heatmapData, {
                    radius: 10,
                    blur: 1,         
                    opacity: 1,
                    maxZoom: 0,        
                    gradient: {         
                        0.0: 'lightgreen',    
                        0.25: 'green',
                        0.5: 'yellow', 
                        0.75: 'orange',     
                        1.0: 'red'   
                    }
                }).addTo(map);
            })
            .catch(error => {
                console.error('Error during elevation process:', error);
                alert('Error during elevation process.');
            });
        } else {
            alert('Please select a station on the map.');
            console.warn("No station selected on the map.");
        }
    });
});