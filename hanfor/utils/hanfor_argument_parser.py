import argparse
from terminaltables import DoubleTable


class ListStoredSessions(argparse.Action):
    """ List available session tags. """

    def __init__(self, option_strings, app, dest, *args, **kwargs):
        self.app = app
        super(ListStoredSessions, self).__init__(
            option_strings=option_strings, dest=dest, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        data = []
        data.append(['Tag', 'Created'])
        data.append(['nothing', 'found'])
        # @TODO: decide on how to implement sessions.. (All in one DB? or Multiple?)
        print('Stored sessions: ')
        if len(data) > 1:
            print(DoubleTable(data).table)
        else:
            print('No sessions in found.')
        raise NotImplementedError
        exit(0)


def create_parser(app):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_init = subparsers.add_parser('init', help='Initialize a new session.')
    parser_init.add_argument("input_csv", help="Path to the csv to be parsed.")
    parser_init.add_argument("tag", help="A unique name for the session.")
    parser_start = subparsers.add_parser('start', help='Start an existing session. Use -L to list available ones.')
    parser_start.add_argument("tag", help="The unique name of the session.")
    parser_start.add_argument("revision", help="The revision of the session.")
    parser.add_argument(
        '-L', '--list',
        nargs=0,
        help="List available sessions.",
        action=ListStoredSessions,
        app=app
    )

    return parser
