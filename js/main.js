import { filterTableRows } from "./modules/filterTableRows";
import { sortTableRows } from "./modules/sortTableRows";


window.addEventListener('load', function (event) {
  // Add event listeners for filtering table rows and for sorting table rows.
  initFilterTableRows();
  initSortTableRows();
});


function initFilterTableRows() {
  // Add an event listener to the inputs of type checkbox with ID
  // 'new, 'started', or 'finished'.
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  for (const checkbox of checkboxes) {
    if (checkbox.id === 'new' || checkbox.id === 'started' || checkbox.id === 'finished') {
      checkbox.addEventListener('click', filterTableRows);
    }
  }
}


function initSortTableRows() {
  // A table's rows can be sorted if it has a th element with class 'sortable'
  // and a child span element. Add an event listener to each qualifying th
  // element.
  const tables = document.querySelectorAll('table');
  for (const table of tables) {
    const th_elements = table.querySelectorAll('th');
    for (const th_element of th_elements) {
      if (th_element.classList.contains('sortable') && th_element.querySelector('span')) {
        th_element.addEventListener('click', sortTableRows);
      }
    }
  }
}
