# Data migration

Script to migrate pickle based Hanfor session to JsonDatabase based Hanfor sessions.

## Usage

The script has to be run as a module in the root folder of this repo. It requires the path to the old session folder as argument. Sessions need to be updated to the latest Hanfor version using pickles before migrating to the JsonDatabase.

````bash
python -m hanfor.data_migration.data_migration [PATH_TO_SESSION_FOLDER]
````

The script saves the old pickle session folder by prefixing it with `.old_` e.g. `[SOME_PATH]/test` to `[SOME_PATH]/.old_test`. After saving the pickles it loads the saved pickle session, migrates it to the new JsonDatabase and  saves it under the old path (`[SOME_PATH]/test`).
