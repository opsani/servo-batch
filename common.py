import math
import re
import yaml

import state_store

REQUIRED_SETTINGS_FIELDS = [ "default", "type" ]

def parse_config(driver_name, config_path):
    try:
        f = open(config_path)
        d = yaml.safe_load(f)
    except yaml.error.YAMLError as e:
        raise Exception("syntax error in {}: {}".format(config_path, str(e)))

    assert isinstance(d, dict), "Config file located at {} was malformed; top-level data type must be dict, found {}".format(config_path, d.__class__.__name__)
    assert(driver_name in d), "Config file located at {} is missing {} configureation section".format(config_path, driver_name)

    cfg = d[driver_name]
    assert cfg and isinstance(cfg, dict), "Config located at {} was malformed; must provide non-empty `{}` dictionary, found: {}".format(config_path, driver_name, cfg)

    bad_top_keys = cfg.keys() - {'application', 'command', 'expected_duration', 'metrics'}
    if bad_top_keys:
        raise Exception('Unknown top level key(s) in `{}` section of file {}: {}'.format(driver_name, config_path, bad_top_keys))

    app = cfg.get('application')
    assert app and isinstance(app, dict), "Config located at {} was malformed; `{}` section must include `application` dictionary, found: {}".format(config_path, driver_name, app.__class__.__name__)

    comps = app.get('components')
    assert comps and isinstance(comps, dict), "Config located at {} was malformed; `{}`'s `application` section must include `components` dictionary, found: {}".format(config_path, driver_name, comps.__class__.__name__)

    command = cfg.get('command')
    assert isinstance(command, str), 'The `command` attribute in `{}` section must be a string, found {}'.format(driver_name, type(command).__name__)

    ed = cfg.get('expected_duration')
    if ed is not None:
        assert (isinstance(ed, int) or isinstance(ed, float)) and ed > 0, 'The `expected_duration` attribute in `{}` section must be a numeric type greater than zero when specified. Found: {} `{}`'.format(driver_name, type(ed).__name__, ed)

    metrics = cfg.get('metrics')
    if metrics is not None:
        assert isinstance(metrics, dict), 'The `metrics` attribute in `{}` section must be a dict when provided, found {}'.format(driver_name, type(metrics).__name__)

        for m_name, m_data in metrics.items():
            out_reg = m_data.get('output_regex')
            assert isinstance(out_reg, str), 'The `output_regex` attribute is required in metric `{}` under `{}` section and must be a string, found {}'.format(m_name, driver_name, type(metrics).__name__)
            try:
                re.compile(out_reg)
            except re.error as e:
                raise Exception('Failed to compile the `output_regex` of metric `{}` in `{}` section'.format(m_name, driver_name)) from e

    for c_name, c_data in comps.items():
        assert isinstance(c_data, dict),  "Config located at {} was malformed; `{}` application component `{}` value must be a dictionary, found: {}".format(config_path, driver_name, c_name, c_data.__class__.__name__)
        settings = c_data.get('settings')
        assert isinstance(settings, dict), "Config located at {} was malformed; `{}` application component `{}` must contain `settings` dict, found: {}".format(config_path, driver_name, c_name, c_data.__class__.__name__)
        assert settings, "Config located at {} was malformed; `{}` application component `{}` provided no settings".format(config_path, driver_name, c_name)

        for s_name, s_data in settings.items():
            for s in REQUIRED_SETTINGS_FIELDS:
                assert s in s_data, \
                    "missing required key '{}' from driver configuration for setting {}, component {}".format(
                        s, s_name, c_name)

            if s_data['type'] == 'enum':
                bad_keys = s_data.keys() - {'type', 'unit', 'values', 'default'}
                assert len(bad_keys) < 1, \
                    "comp {}: enum setting {} config was malformed, contained unknown key(s) {}".format(c_name, s_name, ', '.join(bad_keys))

                assert isinstance(s_data.get('unit', ''), str), \
                    "comp {}: setting {} unit must be string type when provided. Found {}".format(c_name, s_name, s_data.get('unit').__class__.__name__)

                assert isinstance(s_data.get('values'), list), \
                    "comp {}: setting {} must provide a list of acceptable values. Found: {}".format(c_name, s_name, s_data.get('values'))
            # validate_range_config()
            # adapted from https://github.com/opsani/servo/blob/4f672b97e430847e827bb122dbf0e2f6e4b95628/encoders/base.py#L83
            else:
                bad_keys = s_data.keys() - {'type', 'unit', 'min', 'max', 'step', 'default'}
                assert len(bad_keys) < 1, \
                    "comp {}: range setting {} config was malformed, contained unknown key(s) {}".format(c_name, s_name, ', '.join(bad_keys))

                assert isinstance(s_data.get('min'), (int, float)), \
                    'comp {}: range setting {} config was malformed; min value is required, must be a number. Found {}.'.format(c_name, s_name, s_data.get('min'))
                assert isinstance(s_data.get('max'), (int, float)), \
                    'comp {}: range setting {} config was malformed; max value is required, must be a number. Found {}.'.format(c_name, s_name, s_data.get('max'))
                assert isinstance(s_data.get('step'), (int, float)), \
                    'comp {}: range setting {} config was malformed; step value is required, must be a number. Found {}.'.format(c_name, s_name, s_data.get('step'))
                # Optional param, pass if missing
                assert isinstance(s_data.get('default', 0), (int, float)), \
                    'comp {}: range setting {} config was malformed; default must be a number when provided. Found {}.'.format(c_name, s_name, s_data.get('default'))
                    
                assert s_data['min'] <= s_data['max'], \
                    'comp {}: range setting {} config was malformed; supplied min is higher than max'.format(c_name, s_name)

                if s_data['min'] != s_data['max']:
                    assert s_data['step'] != 0, \
                        'comp {}: range setting {} config was malformed; step cannot be zero when min != max.'.format(c_name, s_name)
                    assert s_data['step'] > 0, \
                        'comp {}: range setting {} config was malformed; step must be a positive number.'.format(c_name, s_name)

                    c = (s_data['max'] - s_data['min']) / float(s_data['step'])
                    if not math.isclose(c, round(c, 0), abs_tol = 1/1024):
                        raise Exception(
                            'comp {}: range setting {} config was malformed; step value must allow to get from {} to {} in equal steps of {}.'.format(
                                c_name, s_name, s_data['min'], s_data['max'], s_data['step']))

    return cfg

def query_state(driver_name, config_path_path_or_dict):
    if isinstance(config_path_path_or_dict, str):
        cfg = parse_config(driver_name, config_path_path_or_dict)
    else:
        cfg = config_path_path_or_dict

    q = {
        "components": cfg["application"]["components"]
    }

    state = state_store.get_state()
    if state:
        assert ("application" in state), "Invalid state: missing application key"

    for key, val in cfg["application"].items():
        if key == "components":
            continue
        try:            
            q[key] = state["application"][key]
        except:
            q[key] = val

    for c_name, c_data in cfg["application"]["components"].items():
        for s_name, _ in c_data["settings"].items():
            # Update 'value' key from state if present (and contained by config)
            try:
                q["components"][c_name]["settings"][s_name]["value"] = state["application"]["components"][c_name]["settings"][s_name]["value"]
            except:
                q["components"][c_name]["settings"][s_name]["value"] = q["components"][c_name]["settings"][s_name]["default"]

            q["components"][c_name]["settings"][s_name].pop('default')                

    return { "application": q }