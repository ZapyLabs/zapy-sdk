import sys
import textwrap
import argparse


class ZapyCLI:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Zapy CLI',
            usage=textwrap.dedent('''\
                    zapy <command> [<args>]
                    The most commonly used git commands are:
                        start_server     Start the zapy service
                        connection       Read or create connection config
                    ''')
        )
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()
        exit(0)

    def start_server(self):
        parser = argparse.ArgumentParser(description='Start the zapy service')
        args = parser.parse_args(sys.argv[2:])
        from zapy.api.bootstrapper import start_server

        start_server()

    def connection(self):
        parser = argparse.ArgumentParser(description='Read or create connection')
        args = parser.parse_args(sys.argv[2:])
        from zapy.api import connection

        conn_config = connection.load_server_config()

        print(conn_config.model_dump_json())
