import re
from lib_core.data import Requirement
from ressources import Ressource
from dataclasses import dataclass, field
from json_db_connector.json_db import DatabaseTable, TableType, DatabaseID, DatabaseField
from immutabledict import immutabledict
from uuid import uuid4
from hanfor_flask import current_app, HanforFlask
from static_utils import SessionValue


class SearchNode:
    operators = {":AND:": 1, ":OR:": 1}
    leftAssoc = {":AND:": 1, ":OR:": 1}
    rightAssoc = {}
    parentheses = {"(": 1, ")": 1}
    precedenceOf = {":AND:": 3, ":OR:": 2}

    def __init__(self, value: str):
        self.left = False
        self.value = value
        self.right = False
        self.data_target = None
        self.update_target()

    def update_target(self):
        """Updates the data target if it is set in the string:
        :DATA_TARGET:`the target name`

        """
        target_index = self.value.find(":DATA_TARGET:")
        if target_index >= 0:
            sub_string = self.value[target_index + 13 :]
            match = re.match(r"`(.+)`", sub_string)
            if match:
                self.data_target = sub_string[match.span()[0] + 1 : match.span()[1] - 1]
                self.value = sub_string[match.span()[1] :]

    def evaluate(self, data):
        return SearchNode.evaluate_tree(self, data)

    @staticmethod
    def is_search_string(token):
        return not (token in SearchNode.parentheses or token in SearchNode.operators)

    @staticmethod
    def to_string(tree):
        string = ""
        if tree.left is not False:
            string += SearchNode.to_string(tree.left) + " "
        string += tree.value
        if tree.right is not False:
            string += " " + SearchNode.to_string(tree.right)
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
                        prev_op in SearchNode.operators
                        and (
                            # and token is left associative and precedence <= to that of prev_op,
                            (
                                token in SearchNode.leftAssoc
                                and (SearchNode.precedenceOf[token] <= SearchNode.precedenceOf[prev_op])
                            )
                            or
                            # or token is right associative and its precedence < to that of prev_op,
                            (
                                token in SearchNode.rightAssoc
                                and (SearchNode.precedenceOf[token] < SearchNode.precedenceOf[prev_op])
                            )
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

                # Search for opening parenthesis in op_stack.
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
                    raise SyntaxError("Search query parentheses mismatch.")

            else:
                raise SyntaxError("Search query Token unknown: {}".format(token))

        # No more tokens in input but operator tokens in the op_stack:
        while len(op_stack):
            op = op_stack.pop()
            if op == "(" or op == ")":
                raise SyntaxError("Search query parentheses mismatch.")

            # Create new subtree with op as root.
            right = output_tree_stack.pop()
            left = output_tree_stack.pop()
            sub_tree = SearchNode(op)
            sub_tree.left = left
            sub_tree.right = right
            output_tree_stack.append(sub_tree)

        # Empty stack => create empty dummy Node.
        if len(output_tree_stack) == 0:
            output_tree_stack.append(SearchNode(""))

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
    def from_query(query=""):
        return SearchNode.search_array_to_tree(SearchNode.query_splitter(query))

    @staticmethod
    def check_value_in_string(value: str, string: str):
        # We support value to be `
        #  * "<inner>"` for exact match.
        #  * ""<inner>"" for exclusive match.

        if value.startswith('""') and value.endswith('""'):
            value = r"^\s*" + re.escape(value[2 : (len(value) - 2)]) + r"\s*$"
        else:
            value = re.escape(value)
            value = value.replace(r"\"", r"\b")

        return bool(re.search(value, string))

    @staticmethod
    def evaluate_tree(tree, data: dict):
        # Root node
        if not tree:
            return True

        # Leaf node.
        if tree.left is False and tree.right is False:
            # First build the string to search.
            string = ""
            if tree.data_target is not None:
                # We have a specific target.
                string = data[tree.data_target]
            else:
                # We search in all data.
                for s in data.values():
                    string += s

            invert_index = tree.value.find(":NOT:")
            if invert_index >= 0:
                # Invert search on :NOT: keyword.
                return not SearchNode.check_value_in_string(tree.value[invert_index + 5 :], string)
            else:
                return SearchNode.check_value_in_string(tree.value, string)

        # evaluate left tree
        left_sub = SearchNode.evaluate_tree(tree.left, data)

        # evaluate right tree
        right_sub = SearchNode.evaluate_tree(tree.right, data)

        # Apply operations
        if tree.value == ":AND:":
            return left_sub and right_sub

        if tree.value == ":OR:":
            return left_sub or right_sub


@DatabaseTable(TableType.Folder)
@DatabaseID("name", str)
@DatabaseField("query", str)
@DatabaseField("results", list[str])
@dataclass()
class Query:
    name: str
    query: str = ""
    results: list[str] = field(default_factory=list)

    @property
    def hits(self):
        return len(self.results)

    def get_dict(self) -> dict[str, str]:
        return {"name": self.name, "query": self.query, "result": self.results, "hits": self.hits}


class QueryAPI(Ressource):
    def __init__(self, app, request):
        super().__init__(app, request)
        self._requirement_data = None

    @property
    def requirement_data(self):
        if self._requirement_data is None:
            self._requirement_data = dict()
            for req in self.app.db.get_objects(Requirement).values():
                self._requirement_data[req.rid] = QueryAPI.req_dict_to_search_dict(req.to_dict())
        return self._requirement_data

    @property
    def queries(self) -> immutabledict[str, Query]:
        return self.app.db.get_objects(Query)

    def get_query(self, name: str) -> Query | None:
        """Get a single query. Returns None is not found.

        :param name: str
        :return: Query
        """
        if self.app.db.key_in_table(Query, name):
            return self.app.db.get_object(Query, name)
        return None

    def set_response_to_enforce_json(self):
        self.response.errormsg = "Only json data supported."
        self.response.success = False

    @staticmethod
    def req_dict_to_search_dict(req_dict):
        if len(req_dict["formal"]) > 0:
            req_dict["tags"].append(current_app.db.get_object(SessionValue, "TAG_has_formalization").value.name)

        result = {
            "Id": req_dict["id"],
            "Description": req_dict["desc"],
            "Type": req_dict["type"],
            "Tags": " ".join(req_dict["tags"]),
            **req_dict["csv_data"],
            "Formalization": " ".join(req_dict["formal"]),
            "Status": req_dict["status"],
        }

        return result

    @staticmethod
    def get_target_names(app: HanforFlask):
        result = list()
        for req in app.db.get_objects(Requirement).values():
            result = [key for key in QueryAPI.req_dict_to_search_dict(req.to_dict()).keys()]
            result = sorted(result)
            break
        return result

    def eval_query(self, query: Query):
        query.results = []
        tree = SearchNode.from_query(query.query)
        for rid, data in self.requirement_data.items():
            if SearchNode.evaluate_tree(tree, data):
                query.results.append(rid)
        self.app.db.update()

    def GET(self):
        """Returns the `name` associated query. Or all stored queries if no name is given."""
        name = self.request.args.get("name", "").strip()
        show = self.request.args.get("show", "").strip()
        reload = self.request.args.get("reload", "").strip()
        if show:
            if show == "targets":
                self.response.data = QueryAPI.get_target_names(self.app)
        elif name:
            if reload:
                self.eval_query(self.get_query(name))
            self.response.data = self.get_query(name).get_dict()
        else:
            if reload:
                for name in self.queries.keys():
                    self.eval_query(self.get_query(name))
            self.response.data = {k: v.get_dict() for k, v in self.queries.items()}

    def POST(self):
        """Add a new query. Expects json encoded data like
        {
            "name": "query name, can be blank.",
            "query": "the search query"
        }
        """
        if not self.request.is_json:
            self.set_response_to_enforce_json()
        else:
            name = self.request.json.get("name", "").__str__().strip()
            query = self.request.json.get("query", "").__str__().strip()
            store = self.request.json.get("store", True)

            if not name:
                name = str(uuid4())
            if self.app.db.key_in_table(Query, name):
                store = True
                q = self.app.db.get_object(Query, name)
                q.query = query
                q.results = []
            else:
                q = Query(name, query)
            self.eval_query(q)
            self.response.data = q.get_dict()
            if store:
                self.app.db.add_object(q)

    def DELETE(self):
        """Delete one or multiple queries by name
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
            name = self.request.json.get("name", "").__str__().strip()
            names = self.request.json.get("names", [])
            if self.app.db.key_in_table(Query, name):
                self.app.db.remove_object(self.app.db.get_object(Query, name))
            if isinstance(names, list):
                for name in names:
                    if self.app.db.key_in_table(Query, name):
                        self.app.db.remove_object(self.app.db.get_object(Query, name))
