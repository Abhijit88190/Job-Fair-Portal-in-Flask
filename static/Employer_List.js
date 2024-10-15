// Function to clear all checkboxes
function clearCheckboxes() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = false;
    });
}

// Event listener for the clear button
document.getElementById('clearBtn').addEventListener('click', function() {
    clearCheckboxes();
});