These are the source files for the [Hanfor Documentation](https://ultimate-pa.github.io/hanfor/).
# Contribute to this Doku
1. Install [MkDocs](https://www.mkdocs.org/).
```bash
$ pip install mkdocs
```
1.2 Install the mkdocs `material` theme:
```bash
$ pip install mkdocs-material
``` 

2. Serve this Documentation locally to track your changes.
```bash
$ cd to_here
$ mkdocs serve
```
Open your Browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

3. Publish your changes.
```bash
$ mkdocs gh-deploy
```
This will build the Docu and commit them to the `gh-pages` branch and push the `gh-pages` branch to GitHub.
