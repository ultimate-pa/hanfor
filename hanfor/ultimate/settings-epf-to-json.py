import sys
import json


def parse_line(line: str) -> None | dict:
    # filter relevant lines
    if not line.startswith("/instance"):
        return None

    # split value from plugin_id and key
    tmp = line.split("=")
    val = tmp[1][:-1]
    tmp = tmp[0].split("/")
    plugin = tmp[2]
    name = tmp[3].replace("\\ ", "+")

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


def convert_file(epf_file_name: str, json_file_name: str) -> None:
    # read epf file and parse lines
    r_list = []
    with open(epf_file_name, "r") as epf:
        for l in epf.readlines():
            r = parse_line(l)
            if r is not None:
                r_list.append(r)

    # generate json and write json file
    result = {"user_settings": r_list}
    with open(json_file_name, "w") as json_file:
        json_file.write(json.dumps(result, indent=4))


if __name__ == "__main__":
    # parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 %s <epf-file> [json-file]" % sys.argv[0])
        sys.exit(1)
    epf_file_name = sys.argv[1]
    if len(sys.argv) > 2:
        json_file_name = sys.argv[2]
    else:
        json_file_name = epf_file_name.removesuffix(".epf") + ".json"

    convert_file(epf_file_name, json_file_name)
