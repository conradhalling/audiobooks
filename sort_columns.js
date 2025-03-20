// Revised from source: https://github.com/VFDouglas/HTML-Order-Table-By-Column/blob/main/index.html
window.onload = function () {
    document.querySelectorAll('th').forEach((element) => { // Table headers
        element.addEventListener('click', function () {
            let table = this.closest('table');

            // If the column is sortable
            if (this.querySelector('span')) {
                let order_icon = this.querySelector('span');
                let order = encodeURI(order_icon.innerHTML).includes('%E2%86%91') ? 'desc' : 'asc';
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

                if (order === 'desc') {
                    obj_key.reverse();
                    order_icon.innerHTML = '&darr;';  // down arrow indicates descending sort
                }
                else {
                    order_icon.innerHTML = '&uarr;';  // up arrow indicates ascending sort
                }

                let html = '';
                obj_key.forEach(function (chave) {
                    html += value_list[chave];
                });
                table.getElementsByTagName('tbody')[0].innerHTML = html;
            }
        });
    });
};
