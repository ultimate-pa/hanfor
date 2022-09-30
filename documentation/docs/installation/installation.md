toc_depth: 2

# Installation

## Prerequisites
* [Python](https://www.python.org/) (**Note**: Hanfor is only tested with Python 3.10.x)
* [pip](https://pypi.org/project/pip/)


## Install Hanfor
To get Hanfor either download the .zip file or clone the repository.

### Download .zip file
Download [Hanfor](https://github.com/ultimate-pa/hanfor/archive/master.zip) and unzip it.
Rename the root folder `hanfor-master` to `hanfor`.

=== ":material-linux: Linux"
    ``` bash
    mv hanfor-master hanfor
    ```
=== ":fontawesome-brands-windows: Windows"
    ``` bash
    move hanfor-master hanfor
    ```

### Clone the repository
``` bash
git clone https://github.com/ultimate-pa/hanfor.git -b master --single-branch 
```

## Install dependencies
We recommend using a [virtual environment](https://docs.python.org/3/tutorial/venv.html).

=== ":material-linux: Linux"
    ``` bash
    cd hanfor/hanfor
    python -m venv hanfor_venv
    source hanfor_venv/bin/activate
    ```
=== ":fontawesome-brands-windows: Windows"
    ``` bash
    cd hanfor\hanfor
    python -m venv hanfor_venv
    hanfor_venv\Scripts\activate.bat
    ```

Install all Python dependencies. 
``` bash
pip install -r requirements.txt
```

Install the Z3 Theorem Prover.
``` bash
pysmt-install --z3
```

## Configuration
Copy the default config file `config.dist.py` to `config.py`.

=== ":material-linux: Linux"
    ``` bash
    cp config.dist.py config.py
    ```
=== ":fontawesome-brands-windows: Windows"
    ``` bash
    copy config.dist.py config.py
    ```

The config file `config.py` allows you to change various parameters -- see the comments in [`config.dist.py`](https://github.com/ultimate-pa/hanfor/blob/master/hanfor/config.dist.py).

## Launch a Hanfor session

### Launch a new session
``` bash
python app.py <tag> -c <path_to_input_csv>
```
1. This creates a new session named by `<tag>` in the `SESSION_BASE_FOLDER`.
2. It asks the user for a mapping of the following .csv header names.
    * "ID"
    * "Description"
    * "Formalized Requirement"
    * "Type"
3. It reads requirements from the .csv file and stores them in separate files in the `SESSION_BASE_FOLDER`.
4. It serves the web interface on `HOST` and `PORT`.

Open the web interface in your web browser at [`http://<HOST>:<PORT>`](http://127.0.0.1:5000).

### Launch an existing session
``` bash
python app.py <tag>
```
To see all available tags use the `-L` switch.
``` bash
python app.py -L
```
Open the web interface in your web browser at [`http://<HOST>:<PORT>`](http://127.0.0.1:5000).
 
 
## ReqAnalyzer
With Hanfor you can formalize requirements and export them. 
Ultimate ReqAnalyzer is a tool to analyze the formalized requirements and part of the released tools of [Ultimate](https://github.com/ultimate-pa/ultimate).

#### Variant 1: Use the latest release

1. Install `Java JRE (11)`
2. Download one of the latest [nightly builds](https://monteverdi.informatik.uni-freiburg.de/ultimate-nightly/).  
   Depending on your OS, you need to download `UReqCheck-linux.zip` or `UReqCheck-win32.zip`.


#### Variant 2: Build the latest development version

1. Install `Java JDK (11)` and `Maven (>=3.6)`
2. Clone the repository: `git clone https://github.com/ultimate-pa/ultimate`.
3. Navigate to the release scripts `cd ultimate/releaseScripts/default`
4. Build the latest binaries by executing `./makeFresh.sh`. This also works on Windows if you use a `bash` shell (e.g., from WSL or GitBash). 

After a successful build, the binaries are located in `UReqCheck-linux` and `UReqCheck-win32`, respectively.

In the [Workflow](../usage/workflow.md) section we explain how to use the tool.
