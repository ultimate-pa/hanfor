toc_depth: 2

# Workflow

## Example input
Consider a CSV file `example_input.csv` which contains requirements of a realtime-system:
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
REQ7,if var1 = True then var3 = True,requirement
REQ8,if var1 = True then var3 = False,requirement
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

![Hanfor requirement overview](../img/hanfor01.png "This is how Hanfor looks like after you started it")

## Preprocessing
By default, all rows now have the status **Todo**. 
It might be the case that you want to change this for a certain set of rows to another status.

In this example we want to set every row of type `meta` to the status **Done**. 

To accomplish this we use the [Search Query Language](/usage/requirements/#search-in-requirements-table). 

1. In Hanfor, search  `:COL_INDEX_04:meta`. This will search for rows which match "meta" in the 4. coloumn (Type). You should now only see the rows of type `meta`.
2. Select all rows by clicking  **All**.
3. Click **Edit selected** and select **Done** in the field **Set status**.
4. Finally, click **Apply changes to selected requirements**

## Formalization
Order your requirement overview by **Pos** by clicking on the table column.
### REQ1
To formalize this requirement, we click on the ID **REQ1** to open then formalization-modal:

![Formalization modal](../img/hanfor02.png "This is how a formalization modal looks like")

1. Click on **+** to add a new formalization and then on **..(click to open)**
2. We now have to select a *Scope* and a *Pattern*.
- The scope is **Globally**, because the requirement states that "var1 is **always** greater than 5".
- The pattern is **it is always the case that {R} holds**.
- For **{R}** we insert the condition: `var1 > 5` and then press **save changes**.
If you save a requirement, Hanfor will automatically create the used variables and derive their type.
You can examine and even alter them in the section **Variables**, for the case that Hanfor did not derive a variable-type correctly.

![Definition of Scope and Pattern](../img/hanfor_req1_formalization.png "This is how we formalize REQ1")

The same procedure can be applied to REQ2 - REQ6

### REQ7 and REQ8
REQ7 and REQ8 are different.
Consider REQ7: `if var3 = True then var4 := True`.

- The scope is still **Globally** 
- The pattern is **it is always the case that if "{R}" holds, then "{S}" holds after at most "{T}" time units**, because in a realtime-system a variable assignment does not happen instantly, there can be delays.
- For **{R}** we insert `var3`, because the variable type is boolean.
- For **{S}** insert `var4`,
- For **{T}** we need a certain amount of time units, for example 50. We do not want to hardcode values, 
we introduce a new variable and insert `MAX_TIME`.

We end up with the following: 
``` 
Globally, it is always the case that if "var3" holds, then "var4" holds after at most "MAX_TIME" time units.
```

Save the formalization. 

You will now recognize that Hanfor automatically added a new *Tag* **Type_inference_error** to your freshly
formalized requirement. To fix that, to go the **Variables** section and open the `MAX_TIME` variable.
You see that Hanfor derived the type `bool`, but we actually want it to be of type `CONST` as the variable represents time units. Change the type and
also assign a value, for example `50`.

![Example for the `MAX_TIME` variable](../img/hanfor_var_maxtime.png "This is how you should edit the MAX_TIME variable")
