from os import path, listdir
from collections import defaultdict
import sys
import json


def parse_line(line: str) -> None | dict:
    # filter relevant lines
    if not line.startswith("/instance"):
        return None

    # split value from plugin_id and key
    tmp = line.split("=", 1)
    val = tmp[1][:-1].replace("\\", "")
    tmp = tmp[0].split("/")
    plugin = tmp[2]
    name = tmp[3].replace("\\ ", " ")

    # generate plugin/key json object
    if val == "true" or val == "false":
        result = {
            "plugin_id": plugin,
            "default": val == "true",
            "visible": False,
            "name": name,
            "id": plugin.split(".")[-1] + "." + name.replace("+", "."),
            "type": "bool",
            "key": name,
            "value": val == "true",
        }
    else:
        result = {
            "plugin_id": plugin,
            "default": val,
            "visible": False,
            "name": name,
            "id": plugin.split(".")[-1] + "." + name.replace("+", "."),
            "type": "string",
            "key": name,
        }
    return result


def convert_file(epf_file_name: str, json_file_name: str, settings: dict[str, set[str]]) -> None:
    # read epf file and parse lines
    r_list = []
    with open(epf_file_name, "r") as epf:
        for line in epf.readlines():
            r = parse_line(line)
            if r is not None:
                r_list.append(r)
                settings[r["plugin_id"]].add(r["name"])

    # generate json and write json file
    result = {"user_settings": r_list}
    with open(json_file_name, "w") as json_write_file:
        json_write_file.write(json.dumps(result, indent=4))


if __name__ == "__main__":
    """Convert all settings epf-files in the <epf-folder> to json-files for the Hanfor Ultimate feature"""
    # parse command line arguments
    if len(sys.argv) != 3:
        print("Usage: python3 %s <epf-folder> <json-folder>" % sys.argv[0])
        sys.exit(1)
    epf_folder = sys.argv[1]
    json_folder = sys.argv[2]
    if not path.isdir(epf_folder):
        print("epf-folder is not a folder")
        sys.exit(2)
    if not path.isdir(json_folder):
        print("json-folder is not a folder")
        sys.exit(3)

    used_settings: dict[str, set[str]] = defaultdict(set)
    for epf_file in [f for f in listdir(epf_folder) if (path.isfile(path.join(epf_folder, f)) and f.endswith(".epf"))]:
        json_file = epf_file.removesuffix(".epf") + ".json"
        convert_file(path.join(epf_folder, epf_file), path.join(json_folder, json_file), used_settings)

    # create json file with all used setting to add to the `settings_whitelist.json` of the ultimate backend
    printable_settings_whitelist = {k: list(v) for k, v in used_settings.items()}
    with open(path.join(json_folder, "_settings_whitelist.json"), "w") as json_file:
        json_file.write(json.dumps(printable_settings_whitelist, indent=4))
