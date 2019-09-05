toc_depth: 2

# FAQ

## Change description or a field text in requirements table.
Currently there is only one way to achieve this: “Creating a new revision”:

* Edit the Description in the CSV -> _edited.csv_.
* Create a revision with the edited CSV as baseline:<br>
  `python app.py TAG_NAME -c path/to/edited.csv --revision`

This will check for changes in the CSV against the old one and create a new “Version” aka. “Revision”.
