if __name__ == '__main__':
    from .exposures_test import exposures_test
    from .graph_demo import graph_demo
    import argparse

    commands = {
        'exposure': exposures_test,
        'graph': graph_demo,
    }

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    for command in commands.keys():
        subparsers.add_parser(command)

    args = parser.parse_args()

    commands[args.command]()

