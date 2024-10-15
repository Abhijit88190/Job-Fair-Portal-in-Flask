function editRow(button) {
    var row = button.closest('tr');
    var cells = row.querySelectorAll('td');
    cells.forEach(function(cell, index) {
        if (index !== 1 && index !== 6) { // Skip the email section (index 1) and index 6
            var input = document.createElement('input');
            input.type = 'text';
            input.value = cell.textContent.trim();
            cell.textContent = '';
            cell.appendChild(input);
        } else {
            cell.classList.add('read-only');
        }
    });
    button.disabled = true;
}

function saveChanges() {
    var table = document.getElementById('personal_details');
    var rows = table.rows;
    var data = {};
    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].cells;
        for (var j = 0; j < cells.length - 1; j++) {
            var input = cells[j].querySelector('input');
            if (input) {
                data[input.name] = input.value;
                cells[j].textContent = input.value;
            }
        }
    }
    // Enable all edit buttons after saving changes
    var buttons = document.querySelectorAll('button');
    buttons.forEach(function(button) {
        button.disabled = false;
    });

    // Send the AJAX request to update the database
    fetch('/update_personal_info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // Display a success message or handle the response as needed
    })
    .catch(error => {
        console.error('Error:', error);
        // Display an error message or handle the error as needed
    });
}

function cancelEdit() {
    var table = document.getElementById('personal_details');
    var rows = table.rows;
    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].cells;
        for (var j = 0; j < cells.length - 1; j++) {
            var input = cells[j].querySelector('input');
            if (input) {
                cells[j].textContent = input.value;
            }
        }
    }
    // Enable all edit buttons after canceling edit
    var buttons = document.querySelectorAll('button');
    buttons.forEach(function(button) {
        button.disabled = false;
    });
}
