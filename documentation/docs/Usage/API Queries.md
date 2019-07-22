To generate reports or search for requirements not using the frontend Hanfor can be queried with HTTP requests at 
`http(s)://{{your host}}/{{your URL_PREFIX}}/api/query`

## Show stored queries
`GET /api/query`

### Arguments 
* `name` (string): The name of the query.
* `reload` (bool | optional | default=false): Reevaluates all stored queries.

### Examples
```bash
# Show all stored queries
$ curl http://localhost:5000/api/query

# Show only queries which are named 'MyQuery' and re-evaluate the stored query 
$ curl http://localhost:5000/api/query?name=MyQuery&reload=true
```

## Adding queries
#### Add new query
`POST /api/query`
Creates and evaluates a new query. 
##### JSON body parameters:
| Name| Type | Description |
|---|---|---|
| name | string | Name for the query. Existing ones will be overridden. |
| query | string | The search query. |

#### Example
```bash
$ curl -X POST -H 'Content-Type: application/json' \
 --data '{"name": "MyQuery", "query": "foo:AND:bar"}' http://localhost:5000/api/query
```

## Deleting Queries
#### Delete a single or multiple queries.
`DELETE /api/query`
##### JSON body parameters:
| Name| Type | Description |
|---|---|---|
| name | string | Name for the query to be deleted.|
| names | list of strings | Queries by name to be deleted. |

#### Example
Delete a single query:
```bash
$ curl -X DELETE -H 'Content-Type: application/json' \
 --data '{"name": "MyQuery"}' http://localhost:5000/api/query
```
Delete multiple queries:
```bash
$ curl -X DELETE -H 'Content-Type: application/json' \
 --data '{"names": ["MyQuery", "Another"]' http://localhost:5000/api/query
```

## Query syntax
Much like in the frontend the query syntax supports operators, nesting, exact- exclusive matches and targeting 
specific attributes.

### Search Operators
You can concatenate search queries by

* `search_1:OR:search_2` yields the union of search_1 and search_2.
* `search_1:AND:search_2` yields the intersection of search_1 and search_2.
* `:AND:` binds stronger than `:OR:`.

To **invert the result** use `:NOT:` before your search string.

To change the precedence and for nesting you query use `(` and `)`.

### Exact searches
You can get exact search results by using `"` to indicate the beginning or end of a sequence.

* `"fast` Includes faster but not breakfast.
* `fast"` Includes breakfast but not faster.
* `"fast"` Includes only exact matches of fast.

### Target specific target attributes
To limit a part of the search query use the syntax

    :DATA_TARGET:`<the target attribute name>`

**Note:** the target attribute name must be enclosed with backticks. 
#### Get available attributes
`GET /api/quer?show=targets`
#### Example
```bash
$ curl http://localhost:5000/api/query?show=targets
```
#### Default targets
The available targets are composed of
```json
[
    "Description",
    "Formalization",
    "Id",
    "Status",
    "Tags",
    "Type"
]
```
Plus the fields available in the associated CSV file the requirements origin from.
