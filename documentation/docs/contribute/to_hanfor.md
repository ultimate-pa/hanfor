toc_depth: 1

# To Hanfor

In this guide we are going to talk about required tools to install in order to set up a development environment for Hanfor.

However, to contribute, you know the drill, 
head over to [Hanfor's Git repository](https://github.com/ultimate-pa/hanfor) and fork it, then work in your changes and PR.

## Environment Setup

_Hanfor_ is a web based tool running on JavaScript on the client side and python on the server side.

### Backend

Prepare the python environment as described in the [installation guide](../installation/installation.md#install-dependencies).

Additionally install the development requirements

```sh
pip install -r requirements-dev.txt
```

We use [python black](https://black.readthedocs.io/en/stable/) with the settings defined in `hanfor/pyproject.toml`.

### Frontend

To prepare the client side JavaScript code development (and also some static assets),
the JavaScript based module bundler [webpack](https://webpack.js.org/) is needed. 
Note, that _webpack_ has to be executed after changing in the frontend.

- Install [Node.js](https://nodejs.org/en/) on your machine (in order to be able to execute JavaScript code).
- Run the package manager [npm](https://www.npmjs.com/) (part of the _Node.js_ installation) to install webpack.

```sh
npm install --save-dev webpack
```

## Build and Run

The frontend of _Hanfor_ has to be built before deploying.

### Frontend

To build the frontend change your path to the ``static`` folder, and execute _webpack_ as follows

```sh
cd static
npm run build
```

If you want to debug java-script code in your browser, you can tell _webpack_ to include a source map by running the following command instead. Note: please do not commit the resulting build to the repository.

```sh
npm run dev-build
```



### Backend

Launch a Hanfor session as explained in the [installation guide](../installation/installation.md#launch-a-hanfor-session).


## Analysis Connector

To start analyses directly from the web frontend, Hanfor has the option to connect to an existing Ultimate-PA server 
instance via its web api. For the use of Ultimate-PA a toolchain and user-settings are required. For simplification a
toolchain and a set of user settings are combined to a configuration witch can be selected at the frontend. All 
configurations addressing the analysis and Ultimate-PA can be set in `/hanfor/configuration/ultimate_config.py`.

### Toolchains

In the ultimate_config file the folder for the toolchain xml files can be set with `ULTIMATE_TOOLCHAIN_FOLDER`. If this 
variable is '' the default folder is uses (`configuration/ultimate/toolchains`).

### User Settings

In the ultimate_config file the folder for the user_setting json files can be set with `ULTIMATE_USER_SETTINGS_FOLDER`. 
If this variable is '' the default folder is uses (`configuration/ultimate/user_settings`).

When using Ultimate-PA locally the user settings are saved in an `.epf` file. For the web api these user settings have 
to be in a json format. To convert the `.epf` file to a `.json` file the `settings-epf-to-json.py` can be used. It is 
located in `/hanfor/ultimate`. Usage: `python3 settings-epf-to-json.py <epf-file> [json-file]` if `[json-file]` is not
provided the `.json` file will be named like the `.epf` file (e.g. `name.epf -> name.json`).

### Configurations

When starting an analysis an Ultimate-PA configuration can be chosen. These configurations are set in the 
ultimate-config file. Each configuration consists of a toolchain and user-settings. To add a new configuration add a
new key, representing the displayed name, to the `ULTIMATE_CONFIGURATIONS` dict, like shown below. The values of the 
`toolchain` and the `user_settings` key are the file_names of the corresponding files without the file ending. 

```python
ULTIMATE_CONFIGURATIONS = {
    'Standard': {'toolchain': 'ReqCheck', 'user_settings': 'ReqCheck-non-lin'},
    'Standard 2': {'toolchain': 'ReqCheck', 'user_settings': 'ReqCheck-non-lin'}
}
```
