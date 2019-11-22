import pytest

import io
import os
import sys

from adjust_driver import BatchAdjustDriver, DRIVER_DESC, HAS_CANCEL, DRIVER_VERSION

adjust_json_stdin = '''\
{
    "application": {
        "components": {
            "web": {
                "settings": {
                    "cpu": {"value": 512},
                    "mem": {"value": 200}
                }
            }
        },
        "annotations": {
            "annotation1": "test3",
            "annotation2": "test4"
        }
    }
}
'''

def test_version(monkeypatch):
    with monkeypatch.context() as m:
        # replicate command line arguments fed in by servo
        m.setattr(sys, 'argv', ['', '--version', '1234'])
        driver = BatchAdjustDriver(cli_desc=DRIVER_DESC, supports_cancel=HAS_CANCEL, version=DRIVER_VERSION)
        with pytest.raises(SystemExit) as exit_exception:
            driver.run()
        assert exit_exception.type == SystemExit
        assert exit_exception.value.code == 0

def test_info(monkeypatch):
    with monkeypatch.context() as m:
        # replicate command line arguments fed in by servo
        m.setattr(sys, 'argv', ['', '--info', '1234'])
        driver = BatchAdjustDriver(cli_desc=DRIVER_DESC, supports_cancel=HAS_CANCEL, version=DRIVER_VERSION)
        with pytest.raises(SystemExit) as exit_exception:
            driver.run()
        assert exit_exception.type == SystemExit
        assert exit_exception.value.code == 0

def test_adjust(monkeypatch):
    with monkeypatch.context() as m:
        # replicate command line arguments fed in by servo
        m.setattr(sys, 'argv', ['', '1234'])
        m.setattr(sys, 'stdin', io.StringIO(adjust_json_stdin))
        driver = BatchAdjustDriver(cli_desc=DRIVER_DESC, supports_cancel=HAS_CANCEL, version=DRIVER_VERSION)
        driver.run()
        assert True

def test_query(monkeypatch):
    with monkeypatch.context() as m:
        # replicate command line arguments fed in by servo
        m.setattr(sys, 'argv', ['', '--query', '1234'])
        driver = BatchAdjustDriver(cli_desc=DRIVER_DESC, supports_cancel=HAS_CANCEL, version=DRIVER_VERSION)
        with pytest.raises(SystemExit) as exit_exception:
            driver.run()
        assert exit_exception.type == SystemExit
        assert exit_exception.value.code == 0

# Comment this test out to persist state file for testing with test_measure
# def test_query_defaults(monkeypatch):
#     try:
#         os.remove('./_state.yaml')
#     except:
#         pass
#     with monkeypatch.context() as m:
#         # replicate command line arguments fed in by servo
#         m.setattr(sys, 'argv', ['', '--query', '1234'])
#         driver = BatchAdjustDriver(cli_desc=DRIVER_DESC, supports_cancel=HAS_CANCEL, version=DRIVER_VERSION)
#         with pytest.raises(SystemExit) as exit_exception:
#             driver.run()
#         assert exit_exception.type == SystemExit
#         assert exit_exception.value.code == 0

