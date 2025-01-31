// Function to get the user's current location
function getUserLocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const userLat = position.coords.latitude;
                const userLon = position.coords.longitude;

                console.log("User Location:", userLat, userLon); // ✅ Debugging

                // Call function to update property distances
                updatePropertyDistances(userLat, userLon);
            },
            function (error) {
                console.error("Error getting user location:", error.message);
                alert("Failed to get location. Please enable GPS and try again.");
            }
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Function to calculate the distance between two coordinates (Haversine formula)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the Earth in km
    const dLat = toRadians(lat2 - lat1);
    const dLon = toRadians(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Returns distance in km
}

// Convert degrees to radians
function toRadians(degrees) {
    return degrees * (Math.PI / 180);
}

// Function to update property distances dynamically
function updatePropertyDistances(userLat, userLon) {
    document.querySelectorAll(".distance").forEach((distanceElement) => {
        const propertyLat = parseFloat(distanceElement.dataset.lat);
        const propertyLon = parseFloat(distanceElement.dataset.lon);

        if (!propertyLat || !propertyLon) {
            distanceElement.textContent = "Distance unavailable";
            return;
        }

        try {
            const distance = calculateDistance(userLat, userLon, propertyLat, propertyLon);
            distanceElement.textContent = `${distance.toFixed(2)} km away`;
        } catch (error) {
            console.error("Error calculating distance:", error);
            distanceElement.textContent = "Error calculating distance";
        }
    });
}

// Run the location retrieval when the page loads
document.addEventListener("DOMContentLoaded", function () {
    getUserLocation();
});

document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.querySelector(".search-form");
    const propertyCards = document.querySelectorAll(".property-card");

    searchForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent form submission

        const query = document.getElementById("query").value.trim().toLowerCase();
        const budget = parseFloat(document.getElementById("budget").value) || null;
        const capacity = parseInt(document.getElementById("capacity").value) || null;

        propertyCards.forEach(card => {
            const title = card.dataset.title.toLowerCase();
            const location = card.dataset.location.toLowerCase();
            const price = parseFloat(card.dataset.price);
            const beds = parseInt(card.dataset.beds);

            let matchesQuery = query ? (title.includes(query) || location.includes(query)) : true;
            let matchesBudget = budget ? price <= budget : true;
            let matchesCapacity = capacity ? beds === capacity : true;

            if (matchesQuery && matchesBudget && matchesCapacity) {
                card.style.display = "block"; // Show matching properties
            } else {
                card.style.display = "none"; // Hide non-matching properties
            }
        });
    });
});
