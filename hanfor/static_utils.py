import hashlib
import os
import pickle
import shlex

from colorama import Style, Fore
from terminaltables import DoubleTable


def pickle_dump_obj_to_file(obj, filename):
    """ Pickle-dumps given object to file.

    :param obj: Python object
    :type obj: object
    :param filename: Path to output file
    :type filename: str
    """
    with open(filename, mode='wb') as out_file:
        pickle.dump(obj, out_file)


def pickle_load_from_dump(filename):
    """ Loads python object from pickle dump file.

    :param filename: Path to the pickle dump
    :type filename: str
    :return: Object dumped in file
    :rtype: object
    """
    if os.path.getsize(filename) > 0:
        with open(filename, mode='rb') as f:
            return pickle.load(f)


def get_filenames_from_dir(input_dir):
    """ Returns the list of filepaths for all files in input_dir.

    :param input_dir: Location of the input directory
    :type input_dir: str
    :return: List of file locations [<input_dir>/<filename>, ...]
    :rtype: list
    """
    return [os.path.join(input_dir, f) for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]


def choice(choices, default):
    """ Asks the user which string he wants from a list of strings.
    Returns the selected string.

    :param choices: List of choices (one choice is a string)
    :type choices: list
    :param default: One element from the choices list.
    :type default: str
    :return: The choice selected by the user.
    :rtype: str
    """
    idx = 0
    data = list()
    for choice in choices:
        if choice == default:
            data.append([
                '{}-> {}{}'.format(Fore.GREEN, idx, Style.RESET_ALL),
                '{}{}{}'.format(Fore.GREEN, choice, Style.RESET_ALL)
            ])
        else:
            data.append([idx, choice])
        idx = idx + 1

    table = DoubleTable(data, title='Choices')
    table.inner_heading_row_border = False
    print(table.table)

    while True:
        last_in = input('{}[Choice or Enter for {} -> default{}]> {}'.format(
            Fore.LIGHTBLUE_EX,
            Fore.GREEN,
            Fore.LIGHTBLUE_EX,
            Style.RESET_ALL))

        if len(last_in) == 0:
            return default

        choice, *args = shlex.split(last_in)
        if len(args) > 0:
            print('What did you mean?')
            continue

        try:
            choice = int(choice)
        except ValueError:
            print('Illegal choice "' + str(choice) + '", choose again')
            continue

        if choice >= 0 and choice < idx:
            return choices[choice]

        print('Illegal choice "' + str(choice) + '", choose again')


def hash_file_sha1(path, encoding='utf-8'):
    """ Returns md5 hash for a csv (text etc.) file.

    :param path: Path to file to hash.
    :param encoding: Defaults to utf-8
    :return: md5 hash (hex formatted).
    """
    sha1sum = hashlib.sha1()

    with open(path, 'r') as f:
        while True:
            data = f.readline().encode(encoding=encoding)
            if not data:
                break
            sha1sum.update(data)

    return sha1sum.hexdigest()


def replace_prefix(string: str, prefix_old: str, prefix_new: str):
    """ Replace the prefix (prefix_old) of a string with (prefix_new).
    String remains unchanged if prefix_old is not matched.

    :param string: To be changed.
    :param prefix_old: Existing prefix of the string.
    :param prefix_new: Replacement prefix.
    :return: String with prefix_old replaced by prefix_new.
    """
    if string.startswith(prefix_old):
        string = ''.join((prefix_new, string[len(prefix_old):]))
    return string
