/**
 * Escape a HTML string for display as a raw string.
 * @param unsafe
 * @returns {string}
 */
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/**
 * Apply a URL search query to the requirements table.
 * @param get_query
 */
function process_url_query(get_query) {
    // Apply search if we have one.
    if (typeof (get_query.q) !== "undefined") {
        /**
         * Pad a Number string with 0 prefix (max length is 2).
         * Examples: 2 -> 02, '' -> 00, 12 -> 12, 123 -> 23
         * @param num
         * @returns {string}
         */
        function pad(num) {
            let s = "00" + num;
            return s.substr(s.length - 2);
        }

        // Clear filters.
        $('#status-filter-input').val('');
        $('#tag-filter-input').val('');
        $('#type-filter-input').val('');

        // Create the search string.
        let s = get_query.q;
        if (typeof (get_query.col) !== "undefined") {
            s = ':COL_INDEX_' + pad(get_query.col).toString() + ':' + s;
        }
        // Apply the search string
        $('#search_bar').val(s);
    }
}

module.exports.escapeHtml = escapeHtml;
module.exports.process_url_query = process_url_query;