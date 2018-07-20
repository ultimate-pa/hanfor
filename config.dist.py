import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = '8888'
    HOST = '127.0.0.1'
    FLASK_ENV = 'development'
    DEBUG = False

    # Set the log level to increase or decrease the logging sensitivity.
    # You can set LOG_LEVEL (in decreasing sensitivity to):
    # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    LOG_LEVEL = 'DEBUG'

    # Set LOG_TO_FILE to True if vou want to log to the file
    # you specified in LOG_FILE
    LOG_TO_FILE = False
    LOG_FILE = 'hanfor.log'

    ################################################################################
    #                         App and web server section                           #
    ################################################################################

    # If you are running the app with a url prefix set URL_PREFIX like
    # URL_PREFIX = '/hanfor'
    URL_PREFIX = '/hanfor'