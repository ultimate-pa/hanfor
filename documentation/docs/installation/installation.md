toc_depth: 2

# Installation

## Preliminaries
* [Python](https://www.python.org/) - Hanfor is only tested with **Python 3.6.x**.
* [pip](https://pypi.org/project/pip/) - Used to install all required dependencies.

If python and pip are installed, their version can be checked from command line.
```bash
python --version

pip --version
```

## Install Hanfor
To get Hanfor either download the .zip file or clone the repository.

### Download .zip file
Download [Hanfor](https://github.com/ultimate-pa/hanfor/archive/master.zip) and unzip it.  
Rename the root folder `hanfor-master` to `hanfor`.
```bash
# Linux
mv hanfor-master hanfor

# Windows
move hanfor-master hanfor
```

### Clone the repository
```bash
$ git clone https://github.com/ultimate-pa/hanfor.git -b master --single-branch 
```

## Install dependencies
We recommend to use a [virtual environment](https://docs.python.org/3/tutorial/venv.html).
```bash
# Linux
cd hanfor/hanfor
python -m venv hanfor_venv
source hanfor_venv/bin/activate

# Windows
cd hanfor\hanfor
python -m venv hanfor_venv
hanfor_venv\Scripts\activate.bat
```

error: Microsoft Visual C++ 14.0 is required.
Workloads > C++ build tools
Installation details > Optional > MSVC v142 - VS 2019 C++ x64/x86 build tools && Windows 10 SDK

Use [pip](https://pypi.org/project/pip/) to install all required dependencies listed in `requirements.txt`.
```bash
$ pip install -r requirements.txt
```

## Configuration
Copy the default config file `config.dist.py` to `config.py`.
```bash
# Linux
$ cp config.dist.py config.py

# Windows
$ copy config.dist.py config.py
```

The config file `config.py` allows to change parameters like ...

- `SESSION_BASE_FOLDER` where Hanfor sessions are stored
- `HOST` and `PORT` of Hanfor's web interface
- ...

## Launch a Hanfor session

### Launch a new session
```bash
$ python app.py <tag> -c <path_to_input_csv>
```
1. This creates a new session named by `<tag>` in the `SESSION_BASE_FOLDER`.
2. It asks the user for a mapping of the the following csv header names.
    * "ID"
    * "Description"
    * "Formalized Requirement"
    * "Type"
3. It reads requirements from the .csv file and stores them in separate files in the `SESSION_BASE_FOLDER`.
4. It serves the web interface on `HOST` and `PORT`.

Open the web interface in your web browser at [`http://<HOST>:<PORT>`](http://127.0.0.1:5000).

### Launch an existing session
```bash
$ python app.py <tag>
```
To see all available tags use the `-L` switch.
```bash
$ python app.py -L
```
Open the web interface in your web browser at [`http://<HOST>:<PORT>`](http://127.0.0.1:5000).
 
 
## ReqAnalyzer
With Hanfor you can formalize requirements and export them. 
The ReqAnalyzer is a tool to analyze the formalized requirements and part of the released tools of [Ultimate](https://github.com/ultimate-pa/ultimate).

#### Variant 1: Use the latest release

1. Install `Java JRE (1.8)`

Download the latest [Release](https://monteverdi.informatik.uni-freiburg.de/ultimate-nightly/).
The asset you need is called `UReqCheck-linux.zip`. 


#### Variant 2: Build the latest dev-version

https://github.com/ultimate-pa/ultimate/wiki/Usage

1. Install `Java JDK (1.8)` and `Maven (>3.0)`
2. Clone the repository: `git clone https://github.com/ultimate-pa/ultimate`.
3. Navigate to the release scripts `cd ultimate/releaseScripts/default`
4. Generate a fresh binary `./makeFresh.sh`

The binaries are located in `UReqCheck-linux`.

In the [Workflow](../usage/workflow.md) section we explain how to use the tool.