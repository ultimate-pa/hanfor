import shlex

from colorama import Fore, Style
from terminaltables import DoubleTable


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