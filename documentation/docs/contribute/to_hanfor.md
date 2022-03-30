toc_depth: 1

# To Hanfor

In this guide we are going to talk about required tools to install in order to set up a development environment for Hanfor.

However, to contribute, you know the drill, 
head over to [Hanfor's Git repository](https://github.com/ultimate-pa/hanfor) and fork it, then work in your changes and PR.

## Environment Setup

_Hanfor_ is a web based tool running on java script on the client side and python on the server side.

### Backend

Prepare the python environment as described in the [installation guide](../installation/installation.md#install-dependencies).

Additionally install the development requirements

```sh
pip install -r requirements-dev.txt
```

### Frontend

To prepare the client side java script code development (and also some static assets),
the java script based module bundler [webpack](https://webpack.js.org/) is needed. 
Note, that _webpack_ has to be executed after changing in the frontend.

- Install [Node.js](https://nodejs.org/en/) on your machine (in order to be able to execute java script code).
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