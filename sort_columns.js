// Revised from source: https://github.com/VFDouglas/HTML-Order-Table-By-Column/blob/main/index.html
window.onload = function () {
    const UP_ARROW = "\u2191";
    const DOWN_ARROW = "\u2193";
    const UP_DOWN_ARROW = "\u2195";

    document.querySelectorAll('th').forEach((element) => { // Table headers
        element.addEventListener('click', function () {
            let table = this.closest('table');

            // The column is sortable if the th element contains a span element.
            if (this.querySelector('span')) {
                // Get the order icon from the span element.
                // The order icon is one of:
                //   up arrow "↑" "\u2191"
                //   down arrow "↓" "\u2193"
                //   up down arrow "↕" "\u2195"
                let order_icon = this.querySelector('span');
                // Clicking the th element changes the order of the sort.
                // If the up arrow is present, the user is requesting a descending sort.
                // If the up down arrow or the down arrow is present, the user is
                // requesting an ascending sort.
                let order = order_icon.innerHTML.includes(UP_ARROW) ? 'desc' : 'asc';


                let separator = '-----'; // Separate the value of its index, so data keeps intact
                let value_list = {}; // <tr> Object
                let obj_key = []; // Values of selected column
                let string_count = 0;
                let number_count = 0;

                // <tbody> rows
                table.querySelectorAll('tbody tr').forEach((line, index_line) => {
                    // Set the key for sorting each column.
                    let key = line.children[element.cellIndex].textContent.toUpperCase();

                    // Set the key to data-minutes, data-title, or data-author
                    // as appropriate.
                    if (line.children[element.cellIndex].hasAttribute('data-length')) {
                        key = line.children[element.cellIndex].getAttribute('data-length');
                    }
                    else if (line.children[element.cellIndex].hasAttribute('data-title')) {
                        key = line.children[element.cellIndex].getAttribute('data-title');
                    }
                    else if (line.children[element.cellIndex].hasAttribute('data-author')) {
                        key = line.children[element.cellIndex].getAttribute('data-author');
                    }

                    // Check if the keys are numbers or strings.
                    if (key.replace('-', '').match(/^[0-9,.]*$/g)) {
                        number_count++;
                    }
                    else {
                        string_count++;
                    }

                    // This is an effort to keep the synthetic keys and values in the correct order
                    // by giving the keys unique names that include the index.
                    // This doesn't work quite right.
                    // value_list is an associative array with key and value. This could be sorted directly.
                    // Want to create an array of JavaScript objects with fields "sortKey", "index", and "html".
                    // The sort function compares the "sortKey" values first, then the "index" values.
                    value_list[key + separator + index_line] = line.outerHTML.replace(/(\t)|(\n)/g, ''); // Adding <tr> to object
                    obj_key.push(key + separator + index_line);
                });
                if (string_count === 0) { // If all values are numeric
                    obj_key.sort(function (a, b) {
                        return a.split(separator)[0] - b.split(separator)[0];
                    });
                }
                else {
                    obj_key.sort();
                }

                // Reverse the sort for a descending sort.
                if (order === 'desc') {
                    obj_key.reverse();
                }

                // Build the HTML for the sorted tr elements.
                let html = '';
                obj_key.forEach(function (chave) {
                    html += value_list[chave];
                });
                table.getElementsByTagName('tbody')[0].innerHTML = html;

                // Reset the order icons for all columns to "up down arrow".
                let th_elements = table.getElementsByTagName('th');
                for (const th_element of th_elements) {
                    th_element.querySelector('span').innerHTML = UP_DOWN_ARROW;
                }

                // Set the order icon of the current column.
                if (order === "desc") {
                    order_icon.innerHTML = DOWN_ARROW; // down arrow indicates descending sort
                }
                else {
                    order_icon.innerHTML = UP_ARROW; // up arrow indicates ascending sort
                }
            }
        });
    });
};
