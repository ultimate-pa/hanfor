#!/bin/sh
# Start hanfor
echo "Starting server"
python3 app.py -c example/example_input.csv --headers='{ "csv_id_header": "ID", "csv_desc_header": "Description", "csv_formal_header": "Hanfor_Formalization", "csv_type_header" : "Type"}' awesome_tag
