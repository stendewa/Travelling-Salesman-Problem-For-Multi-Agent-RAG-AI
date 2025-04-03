document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("routeForm");
    const loader = document.getElementById("loader");

    form.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent full page reload
        loader.style.display = "block"; // Show loading spinner

        const formData = new FormData(form);

        fetch("/", {
            method: "POST",
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            document.documentElement.innerHTML = html; // Replace page content with response
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Something went wrong! Please try again.");
        })
        .finally(() => {
            loader.style.display = "none"; // Hide loader
        });
    });
});
