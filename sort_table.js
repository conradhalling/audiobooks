// Click on a table column header to sort a table by the values in the column.
//
// This code is revised from the source:
// https://github.com/VFDouglas/HTML-Order-Table-By-Column/blob/main/index.html
//
// When using this script, sortable columns in an HTML table must contain a
// span element in the th element. It is helpful but not required to put a
// "\u2195" character (up down arrow) in the span element.
// 
// For example:
//
// <table>
//   <thead>
//     <tr>
//       <th>Title <span>\u2195</span></th>
//       <th>Authors <span>\u2195</span></th>
//       <th>Length <span>\u2195</span></th>
//       <th>Acquired Date <span>\u2195</span></th>
//       <th>Finished Date <span>\u2195</span></th>
//       <th>Rating <span>\u2195</span></th>
//     </tr>
//   </thead>
//
// Include sort keys in data attributes of the td elements. For
// case-independent sort keys, convert the value to all uppercase or all
// lowercase. In the example below, book titles have been converted to all
// uppercase after removing "A", "An", or "The" as the first word of the title.
// Author's names have the surname first. Audiobook lengths expressed in
// hours::minutes (31:15) are converted to minutes (1875) for the sort key
// value.
// 
// For example:
//
// <tr class="adaptive">
//     <td data-title="OUR MUTUAL FRIEND" class="adaptive"><a class="adaptive" href="?book_id=1">Our Mutual Friend</a></td>
//     <td data-author="DICKENS CHARLES" class="adaptive"><a class="adaptive" href="?author_id=1">Charles Dickens</a></td>
//     <td data-length="1875" class="adaptive right">31:15</td>
//     <td class="adaptive">2008-05-17</td>
//     <td class="adaptive">2008-06-17</td>
//     <td class="adaptive">5 excellent</td>
// </tr>
//
// Use CSS styles to change the cursor to a pointer and change the background
// color of the th element when the cursor hovers over the th element.
//
// For example:
//
// th:hover {
//     cursor: pointer;
//     background-color: #bfbfbf;
// }
//
// Modify the function below to use the included sort keys for sorting. The
// default sort keys are the text content of the td elements.
//
// The code sorts the rows numerically where possible.
// Note that ISO dates can be sorted as strings.


"use strict";
const UP_ARROW = "\u2191";
const DOWN_ARROW = "\u2193";
const UP_DOWN_ARROW = "\u2195";

window.onload = function () {
    document.querySelectorAll('th').forEach((th_element) => {
        th_element.addEventListener('click', function () {
            const table = this.closest('table');

            // The column is sortable if the th element contains a span element.
            if (this.querySelector('span')) {
                const th_span = this.querySelector('span');
                // Clicking the th element changes the order of the sort.
                // If the up arrow is present, the user is requesting a descending sort.
                // If the up down arrow or the down arrow is present, the user is
                // requesting an ascending sort.
                const order = th_span.innerHTML.includes(UP_ARROW) ? 'desc' : 'asc';

                // Initialize the object array and the counters.
                const tr_objects = [];
                let string_count = 0;

                // Iterate through the tr elements to obtain the sort key and index.
                const tr_elements = table.querySelectorAll('tbody tr');
                for (let i = 0; i < tr_elements.length; i++) {
                    // Get the standard key for the element.
                    const tr_element = tr_elements[i];
                    let sort_key = tr_element.children[th_element.cellIndex].textContent.toUpperCase();

                    // Get the special key for this element if it exists.
                    if (tr_element.children[th_element.cellIndex].hasAttribute('data-length')) {
                        sort_key = tr_element.children[th_element.cellIndex].getAttribute('data-length');
                    }
                    else if (tr_element.children[th_element.cellIndex].hasAttribute('data-title')) {
                        sort_key = tr_element.children[th_element.cellIndex].getAttribute('data-title');
                    }
                    else if (tr_element.children[th_element.cellIndex].hasAttribute('data-author')) {
                        sort_key = tr_element.children[th_element.cellIndex].getAttribute('data-author');
                    }

                    // Count the sort keys that are strings.
                    // When finished, if string_count is 0, all keys were numbers.
                    if (isNaN(sort_key)) {
                        string_count++;
                    }

                    // Convert the key, index, and element into an object for sorting
                    // and push it onto the array.
                    const tr_object = {
                        sort_key: sort_key,
                        index: i,
                        html: tr_element.outerHTML
                    };
                    tr_objects.push(tr_object);
                }

                // Sort the objects by sort_key first and then by index to keep
                // the sort stable.
                if (string_count === 0) {
                    // Compare the sort_key values as numbers.
                    tr_objects.sort(function (a, b) {
                        if (a.sort_key - b.sort_key < 0) {
                            return -1;
                        }
                        else if (a.sort_key - b.sort_key > 0) {
                            return 1;
                        }
                        else {
                            return a.index - b.index;
                        }
                    });
                }
                else {
                    // Compare the sort_key values as strings.
                    tr_objects.sort(function (a, b) {
                        const result = a.sort_key.localeCompare(b.sort_key);
                        if (result !== 0) {
                            return result;
                        }
                        else {
                            return a.index - b.index;
                        }
                    });
                }

                // Reverse the sort for a descending sort.
                if (order === "desc") {
                    tr_objects.reverse();
                }

                // Rebuild the tbody's HTML for the sorted tr elements.
                let html = '';
                for (let i = 0; i < tr_objects.length; i++) {
                    html += tr_objects[i].html;
                }
                table.getElementsByTagName('tbody')[0].innerHTML = html;

                // Reset the arrows for all th span elements of this table to "up down arrow".
                const table_th_elements = table.getElementsByTagName('th');
                for (const table_th_element of table_th_elements) {
                    table_th_element.querySelector('span').innerHTML = UP_DOWN_ARROW;
                }

                // Set the arrow in the th span element of the current column.
                // A down arrow indicates the column is sorted in descending order.
                // An up arrow indicates the column is sorted in ascending order.
                if (order === "desc") {
                    th_span.innerHTML = DOWN_ARROW;
                }
                else {
                    th_span.innerHTML = UP_ARROW;
                }
            }
        });
    });
};
