toc_depth: 2

# API queries

To generate reports or search for requirements not using the frontend Hanfor can be queried with HTTP requests at 
`http(s)://{{your host}}/{{your URL_PREFIX}}/api/query`

## Show stored queries
`GET /api/query`

### URL arguments

Name    | Type           | Description
------- | --------------- | ------
name   | string         | Name of the Query to retrieve a single Query. 
reload | bool, optional |  Reevaluates all stored Queries. 

### Examples
``` bash
# Show all stored Queries
curl http://localhost:5000/api/query

# Show only Queries which are named 'MyQuery' and re-evaluate the stored Query 
curl http://localhost:5000/api/query?name=MyQuery&reload=true

# Using jq to parse the JSON response. Show only the name of the query with associated hits.
curl http://localhost:5000/api/query\?reload\=true | jq -r '.data[] | {name: .name, hits: .hits}'
```

## Adding new queries
`POST /api/query Content-Type: application/json`

### JSON body parameters

Name | Type   | Description
----- | -------- | -----------
name | string | Name for the Query. Existing ones will be overridden.
query | string | The search Query.

### Examples
``` bash
curl -X POST -H 'Content-Type: application/json' \
  --data '{"name": "MyQuery", "query": "foo:AND:bar"}' http://localhost:5000/api/query
```

## Deleting queries
`DELETE /api/query`

### JSON body parameters

 Name| Type | Description 
---  | ---   |---
name | string | Name for the Query to be deleted.
names | list of strings | Queries by name to be deleted. 

### Examples
``` bash
# Delete a single Query:
curl -X DELETE -H 'Content-Type: application/json' \
  --data '{"name": "MyQuery"}' http://localhost:5000/api/query

# Delete multiple Queries:
curl -X DELETE -H 'Content-Type: application/json' \
  --data '{"names": ["MyQuery", "Another"]' http://localhost:5000/api/query
```

## Query syntax
Much [like in the frontend](requirements.md#Search in requirements table) the Query syntax supports operators, nesting, exact- exclusive matches 
and targeting 
specific attributes.

### Search operators
You can concatenate search Queries by

* `search_1:OR:search_2` yields the union of search_1 and search_2.
* `search_1:AND:search_2` yields the intersection of search_1 and search_2.
* `:AND:` binds stronger than `:OR:`.

To **invert the result** use `:NOT:` before your search string.

To change the precedence or to nest a Query `(` and `)`.

###  Exact searches
You can get exact search results by using `"` to indicate the beginning or end of a sequence.

* `"fast` Includes faster but not breakfast.
* `fast"` Includes breakfast but not faster.
* `"fast"` Includes only exact matches of fast.

### Target specific attributes
To limit a part of the search Query to one attribute use the syntax
`:DATA_TARGET:<the attribute name>`

**Note:** the attribute name must be enclosed with backticks. 

### Get available attributes
`GET /api/quer?show=targets`

### Example
``` bash
# Show attribute names available for specific search.
curl http://localhost:5000/api/query?show=targets
```

**Default targets:**

The available targets are composed of
``` json
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
