import sys
import os
import yaml

DFLT_FILE="/servo/state/state.yaml"


def get_state(file=DFLT_FILE):
    """
    Get state, returns an object
    """
    if not os.path.exists("/servo/state"):
        os.makedirs("/servo/state")

    try:
        f = open(file, 'r+')
        state = yaml.safe_load(f)
    except IOError as e:
        state = {}
    else:
        state = {}

    return state


def set_state(state, file=DFLT_FILE):
    """
    Set state, may raise an exception
    """

    with open(file, 'w') as f:
        try:
            yaml.dump(state, f, default_flow_style=False)
        except IOError as e:
            print(f"IOError => {e.errno}: {e.strerror}", file=sys.stderr)
        except:
            print("Unknown error", file=sys.stderr)
