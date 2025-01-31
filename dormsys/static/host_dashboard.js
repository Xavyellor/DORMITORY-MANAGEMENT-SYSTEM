async function suggestLocations() {
    const query = document.getElementById("location").value;

    if (!query) {
        document.getElementById("suggestions").style.display = "none";
        return;
    }

    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&addressdetails=1&limit=5`,
            {
                headers: { "User-Agent": "YourAppName/1.0 (your-email@example.com)" },
            }
        );

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        const data = await response.json();
        const suggestionsList = document.getElementById("suggestions");
        suggestionsList.innerHTML = "";
        suggestionsList.style.display = "block";

        if (data.length > 0) {
            data.forEach((item) => {
                const suggestionItem = document.createElement("li");
                suggestionItem.textContent = item.display_name;
                suggestionItem.className = "list-group-item list-group-item-action";
                suggestionItem.onclick = () => selectLocation(item);
                suggestionsList.appendChild(suggestionItem);
            });
        } else {
            suggestionsList.style.display = "none";
        }
    } catch (error) {
        console.error("Error fetching location suggestions:", error);
    }
}

function selectLocation(location) {
    document.getElementById("location").value = location.display_name;
    document.getElementById("latitude").value = location.lat;
    document.getElementById("longitude").value = location.lon;

    console.log(`Selected Location: ${location.display_name}`);
    console.log(`Latitude: ${location.lat}, Longitude: ${location.lon}`);

    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("suggestions").style.display = "none";
}

// Attach event listener to trigger suggestions
document.addEventListener("DOMContentLoaded", function () {
    const locationInput = document.getElementById("location");
    if (locationInput) {
        locationInput.addEventListener("input", suggestLocations);
    }
});











