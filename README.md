# servo-batch
Optune adjust and measure driver for batch jobs

## Overview
This driver runs a batch job and returns the time it took to complete it, as well as user-configurable (optional) metrics extracted from the output of the batch job.

Unlike a typical Optune driver, servo-batch is meant to perform the functions on both an adjust and a measure driver. It uses the name of the file (i.e. `./adjust` or `./measure`) to decide what operation is requested.

Note: This driver is not intended or tested to work with driver aggregators.

When invoked as an adjust driver, it simply stores the state it was asked to adjust to. When asked to describe the state of the application (i.e. invoked as `./adjust --query`), it takes the state defined in the driver config (lists all components and their settings, including default values), updates the settings values with the last state that it received on adjust (if present) and returns the result.

When invoked as a measure driver, it runs a command (specified in the driver's configuration), waits for it to complete and returns the time it took to run the command as a metric named `total_runtime`, value in seconds. Optionally, the driver can be configured to extract more metrics from the output of the command (stdout), where the value for a metric is extracted based on a regular expression specified in the driver's config. The first group in the defined regular expression is used to extract a value. For example, if a command outputs "It took 20 minutes to bake the cake" and the driver is configured with a metric that looks for a regular expression `^It took (\d+) minutes`, the value for the metric would be `20`.

The job to run is specified as an executable command. Optune parameters can be passed as part of the command, enclosed by curly braces, to allow setting values and measurement control parameters to be used. Said parameters are made available via the following (See sample `config.yaml` below for examples):

- `component.setting` - The application state that was last adjusted to (or the value of `default` from the configuration file, if there was no previous adjust) can be referenced in the form [component_name].[setting_name]
- `_control` - a dictionary with the control section of the measurement request that was passed to the driver as part of a measure operation.

__NOTE__ Command formatting occurs via invocation of python's `str.format()` function. Therefore, any pair of enclosing curly braces ( `{` and `}` ) is considered to be a “replacement field”. If you need to include literal brace fields in the command that are not meant to be substituted, they must be escaped by doubling the braces ( `{{` and `}}` )

## Dependencies

The following files from opsani/servo repository must be included with deployment in the same folder as the adjust and measure drivers

- https://raw.githubusercontent.com/opsani/servo/master/adjust.py
- https://raw.githubusercontent.com/opsani/servo/master/measure.py
- https://raw.githubusercontent.com/opsani/servo/master/state_store.py

## Driver configuration

```yaml
batch:
  # Command to run (required)
  command: ./run_job.sh --inst_type {web.inst_type} --replicas {web.replicas:.0f} --timeout {_control.userdata.timeout}

  # Default state to use when no previous adjust (required)
  application:
    components:
      web:
        settings:
          inst_type:
            type: enum
            unit: ec2
            step: 1
            value: c5.2xlarge
            values:
            - c5.2xlarge
            - m5.xlarge
            - m5a.xlarge
          replicas:
            type: range
            min: 1
            max: 50
            step: 1
            unit: count

  # expected measure duration in seconds, used to calculate progress (optional, default 3600)
  expected_duration: 3600

  # Extra metrics to extract from command output (optional)
  metrics:
    my_metric_name: # specify metric name
      # Regex to be run against stdoutput of command. Return first match or triggers an error when no match is found.
      # NOTE: Do not use double quotes as it will cause the yaml load to intererpret the backslashes meant for regex as escape sequences
      output_regex: 'Job took (\.d) seconds'
      unit: seconds
```

## Build servo container and push to docker registry

```bash
docker build -t opsani/servo-batch .
```

## Run Servo (as a docker container)

```bash
docker run -d --name opsani-servo \
    -v /path/to/optune_auth_token:/opt/optune/auth_token \
    -v /path/to/config.yaml:/servo/config.yaml \
    opsani/servo-batch --auth-token /opt/optune/auth_token --account my_account my_app
```

Where:
 * `/path/to/optune_auth_token` - file containing the authentication token for the Optune backend service
 * `/path/to/config.yaml` - config file containing (see above for details).
 * `my_account` - your Optune account name
 * `my_app` - the application name

There may be additional files that the command specified in `config.yaml` depends on (i.e. scripts, modules, etc.). Those can be passed as part of the `docker run` command and mounted inside the container.

## How to run tests

Prerequisites:

* Python 3.5 or higher
* PyTest 4.3.0 or higher

Follow these steps:

1. Download dependencies. From `test/`:
```
curl --remote-name-all \
    https://raw.githubusercontent.com/opsani/servo/master/adjust.py \
    https://raw.githubusercontent.com/opsani/servo/master/measure.py \
    https://raw.githubusercontent.com/opsani/servo/master/state_store.py
```
1. Run `pytest -s` from the servo-batch project folder
