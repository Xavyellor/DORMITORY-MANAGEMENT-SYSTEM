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

        // Populate suggestions
        const suggestionsList = document.getElementById("suggestions");
        suggestionsList.innerHTML = ""; // Clear old suggestions
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
    // Populate the input fields with the selected suggestion
    document.getElementById("location").value = location.display_name;
    document.getElementById("latitude").value = location.lat;
    document.getElementById("longitude").value = location.lon;

    // Clear suggestions
    const suggestionsList = document.getElementById("suggestions");
    suggestionsList.innerHTML = "";
    suggestionsList.style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
    // Open the Edit Modal and populate it with property data
    window.openEditModal = function (id, title, description, price, location, numBeds, amenities, status, images) {
        console.log(`Opening modal for Property ID=${id}`);
    
        // Populate form fields
        document.getElementById("editTitle").value = title;
        document.getElementById("editDescription").value = description;
        document.getElementById("editPrice").value = price;
        document.getElementById("editLocation").value = location;
        document.getElementById("editNumBeds").value = numBeds;
    
        // Handle amenities
        const amenitiesArray = amenities.split(", ").map(item => item.trim());
        document.querySelectorAll("#editAmenities input[type='checkbox']").forEach(checkbox => {
            checkbox.checked = amenitiesArray.includes(checkbox.value);
        });
    
        // Handle status
        document.getElementById("editStatus").value = status;
    
        // Display existing images with delete buttons
        const existingImagesContainer = document.getElementById("existingImages");
        existingImagesContainer.innerHTML = "";
        if (images) {
            images.split(", ").forEach(image => {
                const wrapper = document.createElement("div");
                wrapper.className = "image-wrapper";
    
                const img = document.createElement("img");
                img.src = `/static/uploads/${image}`;
                img.alt = "Property Image";
                img.className = "img-thumbnail";
                img.style.width = "120px";
                img.style.height = "120px";
    
                const deleteButton = document.createElement("button");
                deleteButton.innerHTML = "&times;";
                deleteButton.onclick = function () {
                    wrapper.remove(); // Remove from the DOM
                    const hiddenInput = document.createElement("input");
                    hiddenInput.type = "hidden";
                    hiddenInput.name = "deleted_images[]";
                    hiddenInput.value = image; // Add to the list of deleted images
                    document.getElementById("editPropertyForm").appendChild(hiddenInput);
                };
    
                wrapper.appendChild(img);
                wrapper.appendChild(deleteButton);
                existingImagesContainer.appendChild(wrapper);
            });
        }
    
        // Set form action dynamically
        document.getElementById("editPropertyForm").action = `/edit_property/${id}`;
    
        // Show modal
        const modal = document.getElementById("editModal");
        modal.style.display = "flex"; // Use flex to center the modal
    };
        

    // Close the Edit Modal
    window.closeEditModal = function () {
        const modal = document.getElementById("editModal");
        modal.style.display = "none";
    };

    // Attach confirmation to Delete buttons
    const deleteForms = document.querySelectorAll('form[action*="/delete_property"]');
    deleteForms.forEach((form) => {
        form.addEventListener("submit", function (e) {
            if (!confirm("Are you sure you want to delete this property?")) {
                e.preventDefault(); // Prevent form submission if not confirmed
            }
        });
    });

    // Handle Add Listing Form Submission
    const addListingForm = document.getElementById("propertyForm");
    if (addListingForm) {
        addListingForm.addEventListener("submit", function (e) {
            console.log("Add Listing form submitted");
        });
    }

    // Close modal when clicking outside the modal content
    const modal = document.getElementById("editModal");
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeEditModal();
        }
    });

    // Debug: Ensure JavaScript file is loaded
    console.log("host_dashboard.js loaded successfully");
});







