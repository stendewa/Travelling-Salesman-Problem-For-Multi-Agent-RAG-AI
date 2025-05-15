// script.js

// Wait for page to load
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("routeForm"); // Grab the form element
    const loader = document.getElementById("loader");   // Grab loader

    // Listen for form submit
    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Stop the form from submitting normally
        loader.style.display = "block"; // Show the loader while processing

        // Gather input values from the form
        const formData = new FormData(form);

        // Send the POST request via Fetch API
        fetch("/compare", {
            method: "POST",
            body: formData
        })
        .then(response => response.text()) // Read response HTML
        .then(html => {
            document.open();         // Clear existing page
            document.write(html);    // Replace with new HTML
            document.close();        // Finish render
        })
        .catch(error => {
            alert("An error occurred. Try again.");
            console.error(error);
        })
        .finally(() => {
            loader.style.display = "none"; // Hide loader
        });
    });
});

