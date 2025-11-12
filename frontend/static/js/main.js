document.addEventListener('DOMContentLoaded', function() {
    // Your code here will run once the DOM is fully loaded
    let selectedLat = null;
    let selectedLon = null;
    let selectedMarker = null;  // Track the currently selected marker
    let lastElevatedMarker = null;  // Track the last elevated marker
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

    // Function to update selected bus stop
    function updateSelectedBusStop(busStopName) {
        document.getElementById('selectedBusStop').value = busStopName || 'Select a bus stop';
    }

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

    // Function to reset marker color to its original state
    function resetMarkerColor(marker, vehicleType) {
        const vehicleIcons = {
            0: 'fa-subway',     
            1: 'fa-subway',     
            109: 'fa-train',    
            3: 'fa-bus',        
            4: 'fa-ship',       
        };

        marker.setIcon(L.AwesomeMarkers.icon({
            icon: vehicleIcons[vehicleType],
            markerColor: getMarkerColor(vehicleType),
            prefix: 'fa'
        }));
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
                // Reset the color of the previously selected marker to its original color (except for the elevated marker)
                if (selectedMarker && selectedMarker !== marker && selectedMarker !== lastElevatedMarker) {
                    resetMarkerColor(selectedMarker, selectedMarker.vehicleType);
                }

                // Set the new selected marker's color to cadet blue
                selectedLat = station.lat;
                selectedLon = station.lon;
                selectedMarker = marker;
                    selectedMarker.vehicleType = station.vehicleType;  // Store vehicle type for resetting
    
                    // Change the color of the selected marker to cadet blue
                    marker.setIcon(L.AwesomeMarkers.icon({
                        icon: vehicleIcons[station.vehicleType],
                        markerColor: 'cadetblue',
                        prefix: 'fa'
                    }));
                updateSelectedBusStop(station.name); // Update the selected bus stop
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
    document.getElementById('elevateButton').addEventListener('click', async function() {
        if (selectedLat == null || selectedLon == null) {
            alert('Please select a station on the map.');
            return;
        }

        const btn = this;
        btn.disabled = true;
        const oldText = btn.textContent;
        btn.textContent = 'Elevating...';

        try {
            const res = await fetch('/elevate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat: Number(selectedLat), lon: Number(selectedLon) })
            });

            if (!res.ok) {
                let msg = `HTTP ${res.status}`;
                try {
                    const err = await res.json();
                    if (err && err.error) msg += `: ${err.error}`;
                } catch {}
                throw new Error(msg);
            }

            const data = await res.json();

            const times = data.map(s => s.travel_time).filter(t => t != null);
            if (!times.length) return;

            const maxTravelTime = Math.max(...times);
            const minTravelTime = Math.min(...times);

            if (heatmapLayer) map.removeLayer(heatmapLayer);

            const heatmapData = data
                .filter(s => s.travel_time != null)
                .map(s => {
                    let t = (s.travel_time - minTravelTime) / Math.max(1, (maxTravelTime - minTravelTime));
                    t = Math.min(Math.max(t, 0), 1);
                    return [s.lat, s.lon, t];
                });

            heatmapLayer = L.heatLayer(heatmapData, {
                radius: 15,
                blur: 2,
                opacity: 1,
                maxZoom: 0,
                gradient: { 0.0: 'lightgreen', 0.25: 'green', 0.5: 'yellow', 0.75: 'orange', 1.0: 'red' }
            }).addTo(map);
        } catch (err) {
            console.error('Error during elevation process:', err);
            alert(`Elevation failed: ${err.message}`);
        } finally {
            btn.disabled = false;
            btn.textContent = oldText;
        }
    });
});