toc_depth: 2

# FAQ
## Add, remove, change patterns available.
The patterns available in hanfor are defined in the _config.py_ file at the `Available patterns` section.

## Change the order the patterns appear in hanfors frontend pattern selection.
Patterns can be ordered by assigned groups or within their group.

**Assign a Pattern to a Group:**

* Edit `PATTERNS` in the _config.py_
* Set `PATTERN['Pattern_name']['group'] = 'your group name'`.

**Change the order of the Groups:**

* Edit `PATTERNS_GROUP_ORDER` in the _config.py_ file.
* The order the groups appear in the list `PATTERNS_GROUP_ORDER` determine how they are ordered in the frontend.

**Change the order of pattern within groups**

* Edit `PATTERNS` in the _config.py_ file.
* Set `PATTERN['Pattern_name']['pattern_order'] = 5` all patterns will be ordered ascending with respect to this
 setting.

## Change description or a field text in requirements table.
Currently there is only one way to achieve this: “Creating a new revision”:

* Edit the Description in the CSV -> _edited.csv_.
* Create a revision with the edited CSV as baseline:<br>
  `python app.py TAG_NAME -c path/to/edited.csv --revision`

This will check for changes in the CSV against the old one and create a new “Version” aka. “Revision”.
