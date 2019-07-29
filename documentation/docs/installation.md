<h1>Installation</h1>

## Preliminaries
Clone the repository:
```bash
$ git clone https://github.com/ultimate-pa/hanfor.git -b master --single-branch /your/hanfor/destination 
```

Hanfor requires [Python](https://www.python.org/) and is only tested with Python 3.6.x.
You can check if you have python already installed from the command line:
```bash
$ python -- version
Python 3.5.2
```

We recommend using a [virtual environment](https://virtualenv.pypa.io/en/latest/installation/). Create a new virtual environment with: 
```bash
$ virtualenv hanfor_python 
```
And activate it by sourcing:
```bash
$ source hanfor_python/bin/activate
```

Now the python dependencies needed to be installed into the virtual environment.
Inside the repository run:
```bash
$ pip install -r requirements.txt
```

## Configure
* Copy `./hanfor/config.dist.py` to `./hanfor/config.py`.
* Edit the `config.py` according your needs.

## Start
To start a fresh session use
```bash
$ python app.py <tag> -c <path_to_input_csv>.csv
```
    
Point your browser to [`http://127.0.0.1:<port in config.py>`](http://127.0.0.1:5000)

Start an existing session:
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
    * "ID", "Description", "Formalized Requirement", "Type"
 4. Create a Hanfor-Requirement for each row in the csv and store it to the session folder.
 5. Provide the Web-interface on the port specified in config.py

