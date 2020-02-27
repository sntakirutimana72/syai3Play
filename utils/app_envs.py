import sys
from os import getenv, path


def appDataDir():
    package = 'SYAI'
    tool_name = 'v3Play'
    program_data = getenv('PROGRAMDATA')
    return '.'  # path.join(program_data, package, tool_name)


def instDir():
    return '.'  # path.dirname(sys.executable)
