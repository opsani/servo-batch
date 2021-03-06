# adapted from https://github.com/opsani/servo-ec2asg-newrelic/blob/master/Dockerfile
FROM python:3.6-slim

WORKDIR /servo

# Install dependencies
RUN pip3 install requests PyYAML python-dateutil

# Install servo:  batch adjust (which uses the servo base adjust.py) and
# batch measure (which uses the servo base measure.py) and
# servo/state_store used by both measure and adjust
ADD https://raw.githubusercontent.com/opsani/servo/master/servo \
    https://raw.githubusercontent.com/opsani/servo/master/adjust.py \
    https://raw.githubusercontent.com/opsani/servo/master/measure.py \
    https://raw.githubusercontent.com/opsani/servo/master/state_store.py \
    ./adjust \
    ./common.py \
    ./measure \
    /servo/

RUN chmod a+x /servo/adjust /servo/measure

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "python3", "servo" ]
