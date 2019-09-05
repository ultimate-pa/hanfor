toc_depth: 2

# Preliminaries
## Install Hanfor 
Clone the repository:
```bash
$ git clone https://github.com/ultimate-pa/hanfor.git -b master --single-branch /your/hanfor/destination 
```

Hanfor requires [Python](https://www.python.org/) and is only tested with Python 3.6.x.
You can check if you have python already installed from the command line:
```bash
$ python -- version
Python 3.6.2
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

## Install ReqAnalyzer
*Coming soon*