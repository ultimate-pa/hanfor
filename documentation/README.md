These are the source files for the [Hanfor Documentation](https://ultimate-pa.github.io/hanfor/).

# Contribute to this Documentation.


#### 0. (Optional) setup a virtual environment

=== ":material-linux: Linux"
    ```bash
    $ cd hanfor/documentation
    $ python3 -m venv venv
    $ source venv/bin/activate
    ```
=== ":fontawesome-brands-windows: Windows"
    ```ps
    $ cd hanfor\documentation
    $ python3 -m venv venv
    $ venv\Scripts\activate.bat
    ```

#### 1. Install [MkDocs](https://www.mkdocs.org/) and all dependencies.

=== ":material-linux: Linux"
    ```bash
    $ cd hanfor/documentation
    $ pip3 install -r requirements.txt
    ```
=== ":fontawesome-brands-windows: Windows"
    ```ps
    $ cd hanfor\documentation
    $ pip3 install -r requirements.txt
    ```

#### 2. Serve this Documentation locally to track your changes.

```bash
$ mkdocs serve
```

Open your Browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

#### 3. Publish your changes to the staging directory.

```bash
$ mkdocs gh-deploy --remote-branch gh-pages-staging
```

This will build the Documentation and commit them to the `gh-pages-staging` branch and push the `gh-pages-staging` branch to GitHub.
If you have the necessary rights, you can then see the results on https://struebli.informatik.uni-freiburg.de/hanfor-docs-staging.

#### 4. Publish your changes to the live directory

```bash
$ mkdocs gh-deploy
```

This will build the Documentation and commit them to the `gh-pages` branch and push the `gh-pages` branch to GitHub.
They will then be immediately available to the world at https://ultimate-pa.github.io/hanfor.
