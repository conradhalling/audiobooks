// Click on a table column header to sort a table by the values in the column.
//
// When using this script, sortable columns in an HTML table must have a th
// element with class "sortable" and a child span element. It is helpful but not
// required to put a "⭥" ("\u2B65" or "&#x2B65;") character (up down
// triangle-headed arrow) in the span element as a visual cue that the table can
// be sorted using that column.
// 
// For example:
//
// <table>
//   <thead>
//     <tr>
//       <th class="sortable">Title <span>⭥</span></th>
//       <th class="sortable">Authors <span>⭥</span></th>
//       <th class="sortable">Length <span>⭥</span></th>
//       <th class="sortable">Acquired Date <span>⭥</span></th>
//       <th class="sortable">Finished Date <span>⭥</span></th>
//       <th class="sortable">Rating <span>⭥</span></th>
//     </tr>
//   </thead>
//
// By default, sorting uses the text content of the td element converted to
// uppercase for case-independent sorting. If all values in the column can be
// converted to numbers, sorting is numeric; otherwise, sorting is
// lexicographical.
//
// Create custom sort keys by transforming the content of the td element into a
// form useful for sorting. Store the custom sort key in the data-sortkey
// attribute of the td element.
// 
// For example:
//
// <tr>
//   <td data-sortkey="OUR MUTUAL FRIEND"><a href="?book_id=1">Our Mutual Friend</a></td>
//   <td data-sortkey="DICKENS CHARLES"><a href="?author_id=1">Charles Dickens</a></td>
//   <td data-sortkey="1875">31:15</td>
//   <td>2008-05-17</td>
//   <td>2008-06-17</td>
//   <td>5 excellent</td>
// </tr>
// 
// Examples of custom sort keys:
// 
// To sort book titles, remove "A", "An", or "The" from the beginning of the
// title and convert the title to all uppercase.
// 
// To sort names, create a sort key with the surname first.
// 
// To sort audiobook lengths, originally expressed in hours:minutes format
// (e.g., 31:15), create the sort keys by converting the lengths to minutes
// (here, 60 * 31 + 15 = 1875).
//
// ISO 8601-format datetime values can be sorted as strings and do not need to
// be transformed. Dates in other formats (e.g., American-style 3/23/2025) need
// to be transformed to a sort key in ISO 8601 format (here, 2025-03-23).
//
// Use CSS styles to change the cursor to a pointer and change the background
// color of the th element when the cursor hovers over the th element.
//
// For example:
//
// th.sortable:hover {
//     cursor: pointer;
//     background-color: #bfbfbf;
// }
//
// As an additional prompt, add a title attribute to the th element.
//
// For example:
//   <th
//     class="sortable" 
//     title="Click this header to sort the table by the values in this column."
//   >Authors <span>⭥</span></th>
//
// This code is revised from these sources:
// - https://stackoverflow.com/questions/10683712/html-table-sort
// - https://github.com/VFDouglas/HTML-Order-Table-By-Column/blob/main/index.html


function sortTableRows(event) {
    const UP_ARROW = "⭡";
    const DOWN_ARROW = "⭣";
    const UP_DOWN_ARROW = "⭥";

    // Get the table that is the parent of this th element.
    const th_element = event.target;
    const table = th_element.closest('table');

    // The column is sortable if the th element has class 'sortable' and the th
    // element has a child span element.
    if (th_element.classList.contains('sortable') && th_element.querySelector('span')) {
        const th_span = th_element.querySelector('span');
        // Clicking the th element changes the order of the sort.
        // If the up arrow is present, the user is requesting a descending sort.
        // If the up down arrow or the down arrow is present, the user is
        // requesting an ascending sort.
        const order = th_span.innerHTML.includes(UP_ARROW) ? 'desc' : 'asc';

        // Initialize the object array and the counter.
        const tr_objects = [];
        let string_count = 0;

        // Iterate through the tr elements to obtain the sort key and index.
        const tr_elements = table.querySelectorAll('tbody tr');
        for (let i = 0; i < tr_elements.length; i++) {
            const tr_element = tr_elements[i];
            // Get the special sort key for this element if it exists. Otherwise, use
            // the uppercase text content of the element as the sort key.
            let sort_key;
            if (tr_element.children[th_element.cellIndex].hasAttribute("data-sortkey")) {
                sort_key = tr_element.children[th_element.cellIndex].getAttribute("data-sortkey");
            }
            else {
                sort_key = tr_element.children[th_element.cellIndex].textContent.toUpperCase();
            }

            // Count the sort keys that are strings.
            // When finished, if string_count is 0, all keys are numbers.
            if (isNaN(sort_key)) {
                string_count++;
            }

            // Convert the key, index, and element into an object for sorting
            // and push it onto the array.
            const tr_object = {
                sort_key: sort_key,
                index: i,
                html: tr_element.outerHTML,
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

        // Reverse the array for a descending sort.
        if (order === "desc") {
            tr_objects.reverse();
        }

        // Rebuild the tbody's HTML with the sorted tr elements.
        let html = '';
        for (let i = 0; i < tr_objects.length; i++) {
            html += tr_objects[i].html;
        }
        table.getElementsByTagName('tbody')[0].innerHTML = html;

        // Reset the arrows for all th span elements of this table to "up down
        // arrow".
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
    event.stopPropagation();
}

export { sortTableRows };
