from hanfor import create_app, db
from hanfor.utils.hanfor_argument_parser import create_parser

if __name__ == '__main__':
    app = create_app()
    parser = create_parser(app)
    parser.parse_args()

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db}

    app_options = {
        'host': app.config['HOST'],
        'port': app.config['PORT']
    }

    app.run(**app_options)
