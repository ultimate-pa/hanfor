import logging

from hanfor import create_app, db
from hanfor.utils.hanfor_argument_parser import create_parser
from hanfor.utils.setup_logging import setup_logging

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db}


if __name__ == '__main__':
    setup_logging(app)
    parser = create_parser(app)
    args = parser.parse_args()

    app_options = {
        'host': app.config['HOST'],
        'port': app.config['PORT']
    }

    if args.subparser_name == 'init':
        logging.info('Initialize a new session.')

    if args.subparser_name == 'start':
        app.run(**app_options)
