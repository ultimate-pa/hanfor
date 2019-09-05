toc_depth: 2

# Deployment
To start a fresh session use
```bash
$ python app.py <tag> -c <path_to_input_csv>.csv
```
    
Point your browser to [`http://127.0.0.1:<port in config.py>`](http://127.0.0.1:5000)

If you want to start an existing session, use
```bash
$ python app.py <tag>
```

You can see all available tags using the ''-L'' switch:
```bash
$ python app.py -L
```

## How it works
The app will create a *session* naming it by the given `<tag>` argument.
A session creation process has the following steps:

 1. Create a session in a folder `config.py_SESSION_BASE_FOLDER/<tag>`.
 2. Read the given .csv file containing one requirement each row.
 3. Ask the user about a mapping of the csv-header-names for:
    * "ID", 
    * "Description", 
    * "Formalized Requirement", 
    * "Type"
 4. Create a Hanfor-Requirement for each row in the csv and store it to the session folder.
 5. Provide the Web-interface on the port specified in config.py

