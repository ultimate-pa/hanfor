toc_depth: 1

# To Hanfor

In this guide we are going to talk about required tools to install in order to set up a development environment for Hanfor.

However, to contribute, you know the drill, 
head over to [Hanfor's Git repository](https://github.com/ultimate-pa/hanfor) and fork it, then work in your changes and PR.

## Environment Setup

_Hanfor_ is a web based tool running on java script on the client side and python on the server side.

### Frontend

To prepare the client side java script code (and also some static assets),
the java script based module bundler [webpack](https://webpack.js.org/) is needed. 
Also, _webpack_ has to be executed before trying out changes in the frontend.

- Install [Node.js](https://nodejs.org/en/) on your machine (in order to be able to execute java script code).
- Run the package manager [npm](https://www.npmjs.com/) (part of the _Node.js_ installation) to install webpack.

```sh
npm install --save-dev webpack
```

### Backend

To prepare for server side development:

- install the latest version of [python](https://www.python.org/)
- install all dependencies using the python package manager

```sh
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Build and Run

The frontend of _Hanfor_ has to be built before deploying.

### Frontend

TBA
<!--
How to build the frontend (webpack)
Is there a development build where webpack is more lenient
-->

### Backend

TBA
<!--
Just run app.py
-->