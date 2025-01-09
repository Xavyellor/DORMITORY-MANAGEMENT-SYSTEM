// Haversine formula to calculate distances
function haversine(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of Earth in kilometers
    const toRad = (deg) => (deg * Math.PI) / 180;

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in kilometers
}

// Other functions like fetching user location or calculating distances for properties
function calculateDistances(userLat, userLon) {
    const properties = document.querySelectorAll(".property");

    properties.forEach((property) => {
        const propertyLat = parseFloat(property.getAttribute("data-lat"));
        const propertyLon = parseFloat(property.getAttribute("data-lon"));

        const distance = haversine(userLat, userLon, propertyLat, propertyLon);

        const distanceElement = property.querySelector(".distance");
        if (distanceElement) {
            distanceElement.textContent = `${distance.toFixed(2)} km`;
        }
    });
}

// Example: Call the function after fetching user location
document.addEventListener("DOMContentLoaded", function () {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const userLat = position.coords.latitude;
            const userLon = position.coords.longitude;

            calculateDistances(userLat, userLon);
        });
    } else {
        console.error("Geolocation is not supported by this browser.");
    }
});


