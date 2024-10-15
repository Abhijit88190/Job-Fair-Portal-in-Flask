function addQualification() {
    var newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><input type="text" name="course[]" placeholder="Course" required></td>
        <td><input type="text" name="board[]" placeholder="Board/University" required></td>
        <td><input type="number" name="year[]" placeholder="Year of Passing" required></td>
        <td><input type="text" name="totalMarks[]" placeholder="Total Marks" required oninput="calculatePercentage(this)"></td>
        <td><input type="text" name="securedMarks[]" placeholder="Secured Marks" required oninput="calculatePercentage(this)"></td>
        <td><input type="number" name="percentage[]" placeholder="Percentage" readonly></td>
        <td><button type="button" onclick="removeQualification(this)" class="btn btn-danger">Remove</button></td>
    `;

    document.getElementById('qualificationsContainer').appendChild(newRow);
}

function removeQualification(button) {
    var row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function calculatePercentage(input) {
    var row = input.parentNode.parentNode;
    var totalMarks = parseFloat(row.querySelector('input[name="totalMarks[]"]').value);
    var securedMarks = parseFloat(row.querySelector('input[name="securedMarks[]"]').value);
    var percentageInput = row.querySelector('input[name="percentage[]"]');
    if (!isNaN(totalMarks) && !isNaN(securedMarks) && totalMarks > 0) {
        var percentage = (securedMarks / totalMarks) * 100;
        percentageInput.value = percentage.toFixed(2);
    } else {
        percentageInput.value = '';
    }
}