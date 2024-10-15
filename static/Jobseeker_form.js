document.querySelector('.logout-btn').addEventListener('click', function(e) {
    e.preventDefault(); // Prevent the default behavior of the anchor tag
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/login'; // Replace '/login' with the actual URL of your login page
    }
});

// Function to handle notification icon click
function showNotifications() {
    // Retrieve the reports from localStorage
    var notificationReports = JSON.parse(localStorage.getItem("reports"));

    // Get the element to display the reports
    var reportsList = document.getElementById("reports-list");
    // Get the element for the notification counter
    var notificationCounter = document.getElementById("notification-counter");

    // Clear any existing content in the list
    reportsList.innerHTML = "";

    // If there are reports, populate the list
    if (notificationReports && notificationReports.length > 0) {
        // Loop through the reports and create list items
        notificationReports.forEach(function(report) {
            var listItem = document.createElement("li");
            listItem.textContent = report;
            // Append list items to the list
            reportsList.appendChild(listItem);
        });

        // Update notification counter with the number of reports
        notificationCounter.innerText = notificationReports.length;
        // Make the counter visible
        notificationCounter.style.display = "block";
    } else {
        // If there are no reports, display a message
        var noReportsMessage = document.createElement("li");
        noReportsMessage.textContent = "No reports available";
        reportsList.appendChild(noReportsMessage);
        // Hide the notification counter
        notificationCounter.style.display = "none";
    }
}