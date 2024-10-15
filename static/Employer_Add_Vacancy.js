function addVacancy() {
    var newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><input type="text" name="post_name[]" placeholder="Post Name" required></td>
        <td><input type="number" name="number_of_posts[]" placeholder="Number of Posts" required></td>
        <td><textarea name="eligibility[]" placeholder="Eligibility" required></textarea></td>
        <td><textarea name="job_description[]" placeholder="Job Description" required></textarea></td>
        <td>
            <select name="experience[]" required>
                <option value="">Select Experience</option>
                <option value="0-2 yrs/Fresher">0-2 yrs/Fresher</option>
                <option value="2-5 yrs">2-5 yrs</option>
                <option value="More than 5 years">More than 5 years</option>
            </select>
        </td>
        <td><button type="button" onclick="removeVacancy(this)" class="btn btn-danger">Remove</button></td>
    `;
    document.getElementById('vacancycontainer_form').appendChild(newRow);
}

function removeVacancy(button) {
    var row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function toggleForm() {
    var form = document.getElementById('vacancy');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}