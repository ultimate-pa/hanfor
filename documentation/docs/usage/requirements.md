# Requirements

## Search in requirements table
Searching in the requirements table is accessible via the `search` tab. 
Typing in the search input supports autocomplete for extended search triggered by `:`. 

### Search Operators
You can concatenate search queries by

* `search_1:OR:search_2` yields the union of search_1 and search_2.
* `search_1:AND:search_2` yields the intersection of search_1 and search_2.
* `:AND:` binds stronger than `:OR:`.

To **invert the result** use `:NOT:` before your search string.

### Exact searches
You can get exact search results by using `"` to indicate the beginning or end of a sequence.

* `"fast` Includes faster but not breakfast.
* `fast"` Includes breakfast but not faster.
* `"fast"` Includes only exact matches of fast.

<h5>Search Target column</h5>
To target a specific column use `:COL_INDEX_02:` to target column 2.
The column indexes are appended in the requirements table header in parentheses.

## Mass edit requirements
You can mass edit requirements. Select requirements by clicking on the requirement checkbox in the table.
Hold shift for multi select and Ctrl to toggle a single selection.
Click on `Edit Selected`, fill out the form. Empty fields will have no effect.
