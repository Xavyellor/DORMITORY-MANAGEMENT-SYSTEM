// Dashboard JavaScript for managing Add, Edit, and Delete actions on the user's listings

document.addEventListener("DOMContentLoaded", function () {
    // Open the Edit Modal and populate it with property data
    window.openEditModal = function (id, title, description, price, location, numBeds, amenities, status) {
        console.log(`Opening modal for ID: ${id}`);
        console.log(`Title: ${title}, Description: ${description}, Price: ${price}, Location: ${location}, Beds: ${numBeds}, Amenities: ${amenities}, Status: ${status}`);
    
        // Populate modal fields
        document.getElementById('editTitle').value = title;
        document.getElementById('editDescription').value = description;
        document.getElementById('editPrice').value = price;
        document.getElementById('editLocation').value = location;
        document.getElementById('editNumBeds').value = numBeds;
        document.getElementById('editAmenities').value = amenities;
        document.getElementById('editStatus').value = status;
    
        // Dynamically set the form's action URL to include the property ID
        document.getElementById('editPropertyForm').action = `/edit_property/${id}`;
    
        // Display the modal
        document.getElementById('editModal').style.display = 'block';
    };

    // Close the Edit Modal
    window.closeEditModal = function () {
        document.getElementById('editModal').style.display = 'none';
    };

    // Attach confirmation to Delete buttons
    const deleteForms = document.querySelectorAll('form[action*="/delete_property"]');

    deleteForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!confirm("Are you sure you want to delete this property?")) {
                e.preventDefault(); // Prevent form submission if not confirmed
            }
        });
    });

    // Handle Add Listing Form Submission
    const addListingForm = document.getElementById('propertyForm');
    if (addListingForm) {
        addListingForm.addEventListener('submit', function (e) {
            console.log('Add Listing form submitted');
        });
    }

    // Close modal when clicking outside the modal content
    const modal = document.getElementById('editModal');
    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            closeEditModal();
        }
    });

    // Debug: Ensure JavaScript file is loaded
    console.log('Dashboard.js loaded successfully');
});




