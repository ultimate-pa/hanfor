<h1>API Queries</h1>

To generate reports or search for requirements not using the frontend Hanfor can be queried with HTTP requests at 
`http(s)://{{your host}}/{{your URL_PREFIX}}/api/query`

## Show stored Queries
`GET /api/query`

<h5>URL Arguments</h5>
| Name| Type | Description |
|---|---|---|
| name | string | Name of the Query to retrieve a single Query. |
| reload | bool, optional |  Reevaluates all stored Queries. |

<h5>Examples</h5>
```bash
# Show all stored Queries
$ curl http://localhost:5000/api/query

# Show only Queries which are named 'MyQuery' and re-evaluate the stored Query 
$ curl http://localhost:5000/api/query?name=MyQuery&reload=true

# Using jq to parse the JSON response. Show only the name of the query with associated hits.
$ curl http://localhost:5000/api/query\?reload\=true | jq -r '.data[] | {name: .name, hits: .hits}'
```

## Adding new Queries
`POST /api/query Content-Type: application/json`

<h5>JSON body parameters</h5>
| Name| Type | Description |
|---|---|---|
| name | string | Name for the Query. Existing ones will be overridden. |
| query | string | The search Query. |

<h5>Example</h5>
```bash
$ curl -X POST -H 'Content-Type: application/json' \
 --data '{"name": "MyQuery", "query": "foo:AND:bar"}' http://localhost:5000/api/query
```

## Deleting Queries
`DELETE /api/query`

<h5>JSON body parameters</h5>
| Name| Type | Description |
|---|---|---|
| name | string | Name for the Query to be deleted.|
| names | list of strings | Queries by name to be deleted. |

<h5>Examples</h5>
```bash
# Delete a single Query:
$ curl -X DELETE -H 'Content-Type: application/json' \
 --data '{"name": "MyQuery"}' http://localhost:5000/api/query

# Delete multiple Queries:
$ curl -X DELETE -H 'Content-Type: application/json' \
 --data '{"names": ["MyQuery", "Another"]' http://localhost:5000/api/query
```

## Query syntax
Much like in the frontend the Query syntax supports operators, nesting, exact- exclusive matches and targeting 
specific attributes.

<h5>Search Operators</h5>
You can concatenate search Queries by

* `search_1:OR:search_2` yields the union of search_1 and search_2.
* `search_1:AND:search_2` yields the intersection of search_1 and search_2.
* `:AND:` binds stronger than `:OR:`.

To **invert the result** use `:NOT:` before your search string.

To change the precedence or to nest a Query `(` and `)`.

<h5>Exact searches</h5>
You can get exact search results by using `"` to indicate the beginning or end of a sequence.

* `"fast` Includes faster but not breakfast.
* `fast"` Includes breakfast but not faster.
* `"fast"` Includes only exact matches of fast.

<h5>Target specific attributes</h5>
To limit a part of the search Query to one attribute use the syntax

    :DATA_TARGET:`<the attribute name>`

**Note:** the attribute name must be enclosed with backticks. 

<h5>Get available attributes</h5>
`GET /api/quer?show=targets`

<h5>Example</h5>
```bash
# Show attribute names available for specific search.
$ curl http://localhost:5000/api/query?show=targets
```

**Default targets:**

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
