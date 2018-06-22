// Search query grammar declarations.
const operators = {":AND:": 1, ":OR:": 1};
const leftAssoc = {":AND:": 1, ":OR:": 1};
const rightAssoc = {};
const parantheses = {"(": 1, ")": 1};
const precedenceOf = {":AND:": 3, ":OR:": 2};

/**
 * SearchNode represents one node in a search expression used to filter the requirements table.
 */
class SearchNode {
    constructor(value) {
        this.left = false;
        this.value = value;
        this.right = false;
        this.col_target = -1;
        this.update_target();
    }

    update_target() {
        const col_string_index = this.value.indexOf(':COL_INDEX_');
        if (col_string_index >= 0) {
            const target_index = parseInt(this.value.substring(col_string_index + 11, col_string_index + 13));
            if (target_index >= 0) {
                this.value = this.value.substring(col_string_index + 14);
                this.col_target = target_index;
            }
        }
    }

    evaluate(data, visible_columns) {
        return evaluateSearchExpressionTree(this, data, visible_columns);
    }

    static is_search_string(token) {
        return !(token in parantheses || token in operators);
    }

    static to_string(tree) {
        let repr = '';
        if (tree.left !== false) {
            repr += SearchNode.to_string(tree.left) + ' ';
        }
        repr += tree.value;
        if (tree.right !== false) {
            repr += ' ' + SearchNode.to_string(tree.right);
        }
        return repr;
    }

    static peek(array) {
        return array[array.length - 1];
    }

    /**
     * Parses a search array to a binary search tree using shunting yard algorithm.
     * @param array
     * @returns {*}
     */
    static searchArrayToTree(array) {

        let output_tree_stack = [], op_stack = [];

        for (let i = 0, length = array.length; i < length;  i++) {
            const token = array[i]; // current token

            // If token is a search string, add it to the output_tree_stack as a singleton tree.
            if (SearchNode.is_search_string(token))
                output_tree_stack.push(new SearchNode(token));

            else if (token in operators) {
                // We encountered an operator.
                while (op_stack.length) {
                    // As long as there is an operator (prev_op) at the top of the op_stack
                    const prev_op = SearchNode.peek(op_stack);
                    if (prev_op in operators && (
                            // and token is left associative and precedence <= to that of prev_op,
                            (token in leftAssoc &&
                                (precedenceOf[token] <= precedenceOf[prev_op])) ||
                            // or token is right associative and its precedence < to that of prev_op,
                            (token in rightAssoc &&
                                (precedenceOf[token] < precedenceOf[prev_op]))
                        )) {
                        // Pop last two subtrees and make them children of a new subtree (with prev_op as root).
                        let right = output_tree_stack.pop(), left = output_tree_stack.pop();
                        let sub_tree = new SearchNode(op_stack.pop());
                        sub_tree.left = left;
                        sub_tree.right = right;
                        output_tree_stack.push(sub_tree);
                    } else {
                        break;
                    }
                }
                op_stack.push(token);
            }

            // If token is opening parenthesis, just push to the op_stack.
            else if (token === "(")
                op_stack.push(token);

            // If token is closing parenthesis:
            else if (token === ")") {

                let has_opening_match = false;

                // Search for opening paranthesis in op_stack.
                while (op_stack.length) {
                    const op = op_stack.pop();
                    if (op === "(") {
                        has_opening_match = true;
                        break;
                    } else {
                        // Until match pop operators off the op_stack and create a new subtree with operator as root.
                        let right = output_tree_stack.pop();
                        let left = output_tree_stack.pop();
                        let sub_tree = new SearchNode(op);
                        sub_tree.left = left;
                        sub_tree.right = right;
                        output_tree_stack.push(sub_tree);
                    }
                }
                if (!has_opening_match)
                    throw "Error: parentheses mismatch.";
            }
            else throw "Error: Token unknown: " + token;
        }

        // No more tokens in input but operator tokens in the op_stack:
        while (op_stack.length) {

            const op = op_stack.pop();

            if (op === "(" || op === ")")
                throw "Error: Parentheses mismatch.";

            // Create new subtree with op as root.
            let right = output_tree_stack.pop();
            let left = output_tree_stack.pop();
            let sub_tree = new SearchNode(op);
            sub_tree.left = left;
            sub_tree.right = right;
            output_tree_stack.push(sub_tree);
        }

        // Empty stack => create empty dummy Node.
        if (output_tree_stack.length === 0) {
            output_tree_stack.push(new SearchNode(''));
        }

        // The last remaining node should be the root of our complete search tree.
        return output_tree_stack[0];
    }

    /**
     * Splits a search query into array where each element is one token.
     * @param query
     * @param target_col optional target col to restrict the search on a specific col.
     * @returns {*|string[]}
     */
    static awesomeQuerySplitt0r(query, target_col=undefined) {
        // Split by :AND:
        let result = query.split(/(:OR:|:AND:|\(|\))/g);
        result = result.filter(String); // Remove empty elements.
        // If the resulting tree should be restricted to a col..
        if (target_col !== undefined) {
            for (let i = 0, length = result.length; i < length;  i++) {
                // Add :COL_INDEX_<target_col>: to each search string (not a operator or parenthesis).
                if (!(result[i] in operators || result[i] in parantheses)) {
                    result[i] = ':COL_INDEX_' + ("00" + target_col).slice(-2) + ':' + result[i];
                }
            }
        }
        return result;
    }

    /**
     * Create a Search Tree from search query.
     * @param query
     * @param target_col optional target col to restrict the search on a specific col.
     * @returns {*}
     */
    static fromQuery(query='', target_col=undefined) {
        return SearchNode.searchArrayToTree(SearchNode.awesomeQuerySplitt0r(query, target_col));
    }

}

module.exports = { SearchNode };

/**
 * Check is value is in string. Support `"` for exact and `""` padding for exclusive match.
 * @param value string to be converted to regex and matched agains string.
 * @param string
 * @returns {boolean}
 */
function check_value_in_string(value, string) {
    // We support value to be `
    //  * "<inner>"` for exact match.
    //  * ""<inner>"" for exclusive match.

    if (value.startsWith('""') && value.endsWith('""')) {
        value = '^\\s*' + value.substr(2, (value.length - 4)) + '\\s*$';
    } else {
        // replace " by \b to allow for exact matches.
        // In the input we escaped " by \" so we would like to apply (?<!\\)\"
        // since javascript does not allow negative look behinds we do
        // something like ([^\\])(\") and replace the 2. group by \b but keeping \" intact.
        value = value.replace(/([^\\])?\"/g, "$1\\b");
    }

    const regex = new RegExp(value, "i");
    return regex.test(string);

}

/**
 * Apply a search expression tree on row data.
 * @param tree
 * @param data
 * @param visible_columns
 * @returns {bool}
 */
function evaluateSearchExpressionTree(tree, data, visible_columns) {
    // Root node
    if (tree === undefined) {
        return true;
    }

    // Leaf node.
    if (tree.left === false && tree.right === false) {
        // First build the string to search.
        let string = '';
        // We have a specific target.
        if (tree.col_target !== -1) {
            string = data[tree.col_target];
        } else {
            // We search in all visible columns.
            for (let i = 0; i < visible_columns.length; i++) {
                if (visible_columns[i]) {
                    string += data[i] + ' ';
                }
            }
        }
        const not_index = tree.value.indexOf(':NOT:');
        if (not_index >= 0) { // Invert search on :NOT: keyword.
            return !check_value_in_string(tree.value.substring(not_index + 5), string);
        } else {
            return check_value_in_string(tree.value, string);
        }
    }

    // evaluate left tree
    let left_sub = evaluateSearchExpressionTree(tree.left, data, visible_columns);

    // evaluate right tree
    let right_sub = evaluateSearchExpressionTree(tree.right, data, visible_columns);

    // Apply operations
    if (tree.value === ':AND:') {
        return (left_sub && right_sub);
    }

    if (tree.value === ':OR:') {
        return (left_sub || right_sub);
    }
}
