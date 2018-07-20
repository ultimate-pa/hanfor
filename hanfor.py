from hanfor import create_app, db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db}


if __name__ == '__main__':
    app_options = {
        'host': app.config['HOST'],
        'port': app.config['PORT']
    }

    app.run(**app_options)
