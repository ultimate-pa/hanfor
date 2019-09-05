toc_depth: 3

# Workflow

## Example input
Consider a CSV file `example_input.csv` with the following content:

``` bash
ID,Description,Type
META1,This is an example for some requirements,meta
META2,Next we define some requirements,meta
REQ1,var1 is always greater than 5,requirement
REQ2,var2 is always smaller than 10,requirement
REQ3,constraint1 always holds,requirement
REQ4,constraint2 always holds,requirement
REQ5,var1 is always smaller than 5,requirement
REQ6,constraint1 and constraint2 never hold at the same time,requirement
```
In this case every row consists of the fields `ID`, `Description`, `Formalized Requirement` and `Type`.

- `ID` is a unique identifier, 
- `Description` is the description ,
- `Formalized Requirement`, is the formalization,  
- `Type`, is a type, in this example `meta` or `requirement`, where rows with type `meta` contain some meta-information
and rows with type `requirement` contain actual requirements of the module you want to formalize.

## Fire up Hanfor
1. Configure Hanfor as explained in [Configuration](/installation/configuration)
2. Start Hanfor: 
```bash
cd hanfor
python3 app.py -c example_input.csv example_tag
```
- `-c example_input.csv` specifies the csv input file we pass.
- `example_tag` is some meaningful tag you want to give this session.
If you start hanfor later with the same tag, you'll start exactly this session.

you can now reach Hanfor by visiting [http://127.0.0.1:5000](http://127.0.0.1:5000)

![Hanfor_Example](../img/hanfor01.png "This is how Hanfor looks like after you started it")

## Preprocessing
By default, all rows now have the status **Todo**. 
It might be the case that you want to change this for a certain set of rows to another status.

In this example we want to set every row of type `meta` to the status **Done**. 

To accomplish this we use the [Search Query Language](/usage/requirements/#search-in-requirements-table). 

1. In Hanfor, search  `:COL_INDEX_04:meta`. This will search for rows which match "meta" in the 4. coloumn (Type). You should now only see the rows of type `meta`.
2. Select all rows by clicking  **All**.
3. Click **Edit selected** and select **Done** in the field **Set status**.
4. Finally, click **Apply changes to selected requirements**

