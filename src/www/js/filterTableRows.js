// The input[type="checkbox"] elements have IDs 'new', 'started', and
// 'finished'. The table with ID 'audiobooks' has rows with classes 'new',
// 'started', or 'finished'. Toggle the display of the table rows where the
// class matches the ID of the checkbox that received the click event.

function filterTableRows(event) {
    // Use the checked attribute to determine whether to hide or display
    // the matching table rows.
    let display;
    if (event.target.checked) {
        display = "table-row";
    }
    else {
        display = "none";
    }

    // Iterate through the table rows to toggle their display.
    const table = document.getElementById('audiobooks');
    const tr_elements = table.querySelectorAll("tbody tr");
    for (const tr_element of tr_elements) {
        if (tr_element.classList.contains(event.target.id)) {
            tr_element.style.display = display;
        }
    }
    event.stopPropagation();
}

export { filterTableRows };
