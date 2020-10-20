import os
import json


PARAMETERS = None

CONFIG_FILE = 'config.json'
PARAMS_LIST = ('AUTOMATES_DATA', )


def get(verbose=False, config_file=CONFIG_FILE, params_list=PARAMS_LIST):
    """
    Sets global PARAMETERS in PARAMS_LIST from one of two sources:
        (1) Active user environment (highest precedence)
        (2) Config file (a dict of key=<parameter_string_name>, val=<parameter_value>)
    Raises RuntimeError if neither source provides parameter value
        for any parameter in PARAMS_LIST.

    Args:
        verbose: Flag to control verbose print
        config_file: Path to config file (default: CONFIG_FILE)
        params_list: List of parameters

    Returns: PARAMETERS dict

    """

    global PARAMETERS

    if verbose:
        print('parameters.get():')

    PARAMETERS = dict()
    config_params = dict()

    if os.path.exists(CONFIG_FILE):
        if verbose:
            print(f'  Reading Config parameters from {config_file}')
        config_params = json.load(open(config_file))
    else:
        if verbose:
            print(f'  No Config file found at {config_file}')

    for param in params_list:
        if param in os.environ:
            PARAMETERS[param] = os.environ[param]
            if verbose:
                print(f'  Environment: Setting parameter {param}: {PARAMETERS[param]}')
        elif param in config_params:
            PARAMETERS[param] = config_params[param]
            if verbose:
                print(f'  Config: Setting parameter {param}: {PARAMETERS[param]}')
        else:
            raise RuntimeError(f'No definition found for parameter {param}'
                               '\n    Provide definition in local config.json or user environment')

    if verbose:
        print('parameters.get(): DONE')

    return PARAMETERS


if __name__ == '__main__':
    # TODO Provide argparse interface
    get(verbose=True)
