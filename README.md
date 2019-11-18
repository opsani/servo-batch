# servo-batch
Optune adjust and measure driver for batch jobs

## Overview
This driver runs a batch job and returns the time it took to complete it, as well as user-configurable (optional) metrics extracted from the output of the batch job.

Unlike a typical Optune driver, servo-batch is meant to perform the functions on both an adjust and a measure driver.

When invoked as an adjust driver, it simply stores the state it was asked to adjust to. When asked to describe the state of the application (i.e. invoked as `./adjust --query`), it returns the last state it was asked to adjust to, or if that is not present - the default state from the driver's configuration.

When invoked as a measure driver, it runs a command (specified in the driver's configuration), waits for it to complete and returns the time it took to run the command as a metric named `total_runtime`, value in seconds. Optionally, the driver can be configured to extract more metrics from the output of the command (stdout), where the value for a metric is extracted based on a regular expression specified in the driver's config. The first group in the defined regular expression is used to extract a value. For example, if a command outputs "It took 20 minutes to bake the cake" and the driver is configured with a metric that looks for a regular expression `^It took (\d+) minutes`, the value for the metric would be `20`.

The job to run is specified as an executable command. Optune parameters can be passed as part of the  command, to allow setting values and measurement control parameters to be used.

The following top level variables can be used as part of the command, specified in format as consumed by Python's `format` function:
 - `state` - a dictionary with the application state that was last adjusted to (or the value of `default_state` from the configuration file, if there was no previous adjust)
 - `control` - a dictionary with the control section of the measurement request that was passed to the driver as part of a measure operation.

See sample `config.yaml` below for examples.

TBD: Dependencies (i.e. adjust.py, measure.py, etc.)

## Driver configuration
```
batch:
    # Command to run (required)
    command: ./run_job.sh --cpu {state[application][components][master][settings][cpu][value]} --mem {state[application][components][master][settings][mem][value]:.0f} --timeout {control.userdata.timeout}

    # Default state to use when no previous adjust (required)
    default_state:
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

    # Extra metrics to extract from command output (optional)
    metrics:
        my_metric_name: # specify metric name
            # Regex to be run against stdoutput of command. Return first match.
            # If no match, return error.
            output_regex: "Job took (\.d) seconds"
            unit: ms
```

## Build servo container and push to docker registry
```
docker build -t opsani/servo-batch .
```

## Run Servo (as a docker container)
```
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

