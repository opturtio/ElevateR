// heatmap.js

// Initialize an empty array to store heatmap data
const heatmapData = [];

// Create the heatmap layer with initial empty data
let heatLayer = L.heatLayer([], {
    radius: 25,
    blur: 15,
    maxZoom: 17,
    gradient: {
        0.1: 'green',
        0.5: 'orange',
        1.0: 'red'
    }
});

// Function to add the heatmap layer to the map
function initializeHeatmap(map) {
    heatLayer.addTo(map);
}

// Function to refresh the heatmap with new data
function refreshHeatmap() {
    heatLayer.setLatLngs(heatmapData);
}

// Function to fetch travel time data and populate heatmap data
function fetchTravelTimeData(originLat, originLon) {
    const query = `
    {
      plan(
        from: {lat: ${originLat}, lon: ${originLon}}
        to: {lat: 60.2055, lon: 24.6559}  // Replace with desired destination coordinates
        numItineraries: 1
      ) {
        itineraries {
          duration
        }
      }
    }`;

    fetch('https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
    })
    .then(response => response.json())
    .then(data => {
        const duration = data.data.plan.itineraries[0].duration / 60; // Convert duration to minutes

        // Determine intensity based on travel duration (for heatmap color)
        let intensity;
        if (duration <= 30) intensity = 0.1;  // Green for travel time under 30 minutes
        else if (duration <= 60) intensity = 0.5;  // Orange for travel time under 1 hour
        else intensity = 1.0;  // Red for travel time over an hour

        // Add the location and intensity to the heatmap data
        heatmapData.push([originLat, originLon, intensity]);

        // Refresh the heatmap layer with new data
        refreshHeatmap();
    })
    .catch(error => console.error('Error fetching travel time data:', error));
}

// Export functions that need to be used in other scripts
export { initializeHeatmap, fetchTravelTimeData };
