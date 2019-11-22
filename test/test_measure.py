import pytest

import json
import io
import sys

from common import query_state
from measure_driver import BatchMeasureDriver, DESC, HAS_CANCEL, VERSION, config_path, DRIVER_NAME

measure_json_stdin = '''\
{
    "metrics": [
        "total_runtime",
        "test_metric"
    ],
    "control": {
        "duration": 120
    }
}
'''

def test_info(monkeypatch):
    with monkeypatch.context() as m:
        # replicate command line arguments fed in by servo
        m.setattr(sys, 'argv', ['', '--info', '1234'])
        driver = BatchMeasureDriver(cli_desc=DESC, supports_cancel=HAS_CANCEL, version=VERSION)
        with pytest.raises(SystemExit) as exit_exception:
            driver.run()
        assert exit_exception.type == SystemExit
        assert exit_exception.value.code == 0

def test_describe(monkeypatch):
    with monkeypatch.context() as m:
        # replicate command line arguments fed in by servo
        m.setattr(sys, 'argv', ['', '--describe', '1234'])
        driver = BatchMeasureDriver(cli_desc=DESC, supports_cancel=HAS_CANCEL, version=VERSION)
        with pytest.raises(SystemExit) as exit_exception:
            driver.run()
        assert exit_exception.type == SystemExit
        assert exit_exception.value.code == 0

def test_measure(monkeypatch, capsys):
    with monkeypatch.context() as m:
        # replicate command line arguments fed in by servo
        m.setattr(sys, 'argv', ['', '1234'])
        m.setattr(sys, 'stdin', io.StringIO(measure_json_stdin))
        driver = BatchMeasureDriver(cli_desc=DESC, supports_cancel=HAS_CANCEL, version=VERSION)
        driver.run()
        out_str = capsys.readouterr()[0]
        out_data = json.loads(out_str.split("\n")[-2])
        assert json.loads(measure_json_stdin)["control"]["duration"] == int(round(out_data["metrics"]["total_runtime"]["value"]))
        state = query_state(DRIVER_NAME, config_path)
        assert state["application"]["components"]["web"]["settings"]["cpu"]["value"] \
            + state["application"]["components"]["web"]["settings"]["mem"]["value"] \
            == int(out_data["metrics"]["test_metric"]["value"])
        print(out_str)
