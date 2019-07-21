import re

from reqtransformer import Requirement
from ressources import Ressource
from static_utils import get_filenames_from_dir
from flask import current_app


class SearchNode:
    operators = {":AND:": 1, ":OR:": 1}
    leftAssoc = {":AND:": 1, ":OR:": 1}
    rightAssoc = {}
    parantheses = {"(": 1, ")": 1}
    precedenceOf = {":AND:": 3, ":OR:": 2}

    def __init__(self, value: str):
        self.left = False
        self.value = value
        self.right = False
        self.data_target = None
        self.update_target()

    def update_target(self):
        col_string_index = self.value.find(':COL_INDEX_')
        if col_string_index >= 0:
            part = self.value[col_string_index + 11:col_string_index + 13]
            target_index = int(part)
            if target_index >= 0:
                self.value = self.value[col_string_index + 14:]
                self.data_target = target_index

    def evaluate(self, data, visible_columns):
        raise NotImplementedError
        # return evaluateSearchExpressionTree(self, data, visible_columns)

    @staticmethod
    def is_search_string(token):
        return not (token in SearchNode.parantheses or token in SearchNode.operators)

    @staticmethod
    def to_string(tree):
        string = ''
        if tree.left is not False:
            string += SearchNode.to_string(tree.left) + ' '
        string += tree.value
        if tree.right is not False:
            string += ' ' + SearchNode.to_string(tree.right)
        return string

    @staticmethod
    def peek(array):
        return array[len(array) - 1]

    @staticmethod
    def search_array_to_tree(array):
        output_tree_stack = []
        op_stack = []
        for token in array:
            # If token is a search string, add it to the output_tree_stack as a singleton tree.
            if SearchNode.is_search_string(token):
                output_tree_stack.append(SearchNode(token))
            elif token in SearchNode.operators:
                while len(op_stack):
                    prev_op = SearchNode.peek(op_stack)
                    if (
                        # As long as there is an operator (prev_op) at the top of the op_stack.
                        prev_op in SearchNode.operators and
                            (
                                # and token is left associative and precedence <= to that of prev_op,
                                (token in SearchNode.leftAssoc
                                and (SearchNode.precedenceOf[token] <= SearchNode.precedenceOf[prev_op]) )
                            or
                                # or token is right associative and its precedence < to that of prev_op,
                                (token in SearchNode.rightAssoc
                                and (SearchNode.precedenceOf[token] < SearchNode.precedenceOf[prev_op]) )
                            )
                    ):
                        # Pop last two subtrees and make them children of a new subtree (with prev_op as root).
                        right = output_tree_stack.pop()
                        left = output_tree_stack.pop()
                        sub_tree = SearchNode(op_stack.pop())
                        sub_tree.left = left
                        sub_tree.right = right
                        output_tree_stack.append(sub_tree)
                    else:
                        break
                op_stack.append(token)

            # If token is opening parenthesis, just push to the op_stack.
            elif token == "(":
                op_stack.append(token)

            # If token is closing parenthesis:
            elif token == ")":
                has_opening_match = False

                # Search for opening paranthesis in op_stack.
                while len(op_stack):
                    op = op_stack.pop()
                    if op == "(":
                        has_opening_match = True
                        break
                    else:
                        # Until match pop operators off the op_stack and create a new subtree with operator as root.
                        right = output_tree_stack.pop()
                        left = output_tree_stack.pop()
                        sub_tree = SearchNode(op)
                        sub_tree.left = left
                        sub_tree.right = right
                        output_tree_stack.append(sub_tree)

                if not has_opening_match:
                    raise SyntaxError('Search query parentheses mismatch.')

            else:
                raise SyntaxError('Search query Token unknown: {}'.format(token))

        # No more tokens in input but operator tokens in the op_stack:
        while len(op_stack):
            op = op_stack.pop()
            if op == "(" or op == ")":
                raise SyntaxError('Search query parentheses mismatch.')

            # Create new subtree with op as root.
            right = output_tree_stack.pop()
            left = output_tree_stack.pop()
            sub_tree = SearchNode(op)
            sub_tree.left = left
            sub_tree.right = right
            output_tree_stack.append(sub_tree)

        # Empty stack => create empty dummy Node.
        if len(output_tree_stack) == 0:
            output_tree_stack.append(SearchNode(''))

        # The last remaining node should be the root of our complete search tree.
        return output_tree_stack[0]

    @staticmethod
    def query_splitter(query):
        # Split by :AND:, :OR:, (, )
        result = re.split(r"(:OR:|:AND:|\(|\))", query)
        # Remove empty elements.
        result = [s for s in result if len(s) > 0]
        return result

    @staticmethod
    def from_query(query=''):
        return SearchNode.search_array_to_tree(SearchNode.query_splitter(query))

    @staticmethod
    def check_value_in_string(value: str, string: str):
        # We support value to be `
        #  * "<inner>"` for exact match.
        #  * ""<inner>"" for exclusive match.

        if value.startswith('""') and value.endswith('""'):
            value = r'^\s*' + re.escape(value[2:(len(value) - 2)]) + r'\s*$'
        else:
            value = re.escape(value)
            value = value.replace(r'\"', r'\b')

        return bool(re.search(value, string))

    @staticmethod
    def evaluate_tree(tree, data: dict):
        # Root node
        if not tree:
            return True

        # Leaf node.
        if tree.left is False and tree.right is False:
            # First build the string to search.
            string = ''
            if tree.data_target is not None:
                # We have a specific target.
                string = data[tree.data_target]
            else:
                # We search in all data.
                for s in data.values():
                    string += s

            invert_index = tree.value.find(':NOT:')
            if invert_index >= 0:
                # Invert search on :NOT: keyword.
                return not SearchNode.check_value_in_string(tree.value[invert_index + 5:], string)
            else:
                return SearchNode.check_value_in_string(tree.value, string)

        # evaluate left tree
        left_sub = SearchNode.evaluate_tree(tree.left, data)

        # evaluate right tree
        right_sub = SearchNode.evaluate_tree(tree.right, data)

        # Apply operations
        if tree.value == ':AND:':
            return left_sub and right_sub

        if tree.value == ':OR:':
            return left_sub or right_sub


class Query(dict):
    def __init__(self, name, query='', result=None):
        super().__init__()
        self['name'] = name
        self['query'] = query
        if result is None:
            self['result'] = dict()

    @property
    def name(self):
        return self['name']

    @name.setter
    def name(self, value):
        self['name'] = value

    @property
    def query(self):
        return self['query']

    @query.setter
    def query(self, value):
        self['query'] = value

    @property
    def result(self):
        return self['result']

    @result.setter
    def result(self, value):
        self['result'] = value


class QueryAPI(Ressource):
    def __init__(self, app, request):
        super().__init__(app, request)
        if 'queries' not in self.meta_settings:
            self.turncate_query_storage()

    @property
    def queries(self):
        return self.meta_settings['queries']

    def get_query(self, name):
        """ Get a single query. Returns None is not found.

        :param name: str
        :return: Query
        """
        result = None
        if name in self.queries:
            result = self.queries[name]
        return result

    def add_query(self, query: Query):
        self.queries[query.name] = query
        self.meta_settings.update_storage()

    def update_query(self, name):
        """ Update a existing query.
        """
        raise NotImplementedError

    def set_response_to_enforce_json(self):
        self.response.errormsg = "Only json data supported."
        self.response.success = False

    def get_requirement_data(self):
        filenames = get_filenames_from_dir(current_app.config['REVISION_FOLDER'])
        result = dict()
        for filename in filenames:
            try:
                req = Requirement.load(filename)
                result[req.rid] = req.to_dict()
            except:
                continue
        return result

    def turncate_query_storage(self):
        self.meta_settings['queries'] = dict()
        self.meta_settings.update_storage()

    def eval_query(self, name):
        query = self.get_query(name)
        if query is not None:
            tree = SearchNode.from_query(query.query)
            req_data = self.get_requirement_data()
            for rid, data in req_data.items():
                if SearchNode.evaluate_tree(tree, data['csv_data']):
                    query.result[rid] = data
            self.meta_settings.update_storage()

    def GET(self):
        """ Returns the `name` associated query. Or all stored queries if no name is given.
        """
        name = self.request.args.get('name', '').strip()
        if name:
            self.eval_query(name)
            self.response.data = self.get_query(name)
        else:
            self.response.data = self.queries

    def POST(self):
        """ Add a new query. Expects json encoded data like
        {
            "name": "query name, can be blank.",
            "query": "the search query"
        }
        """
        if not self.request.is_json:
            self.set_response_to_enforce_json()
        else:
            name = self.request.json.get('name', '').__str__().strip()
            query = self.request.json.get('query', '').__str__().strip()
            if not name:
                name = str(id(query))
            self.add_query(Query(name, query))
            self.response.data = self.get_query(name)

    def DELETE(self):
        """ Delete one or multiple queries by name
        Expects a json data like
        a list of query names
        {
            "names": ["foo", "bar"]
        }
        a single query name
        {
            "name": "foo"
        }
        """
        if not self.request.is_json:
            self.set_response_to_enforce_json()
        else:
            name = self.request.json.get('name', '').__str__().strip()
            names = self.request.json.get('names', [])
            if name in self.queries:
                self.queries.pop(name)
            if isinstance(names, list):
                for name in names:
                    if name in self.queries:
                        self.queries.pop(name)
            self.meta_settings.update_storage()
