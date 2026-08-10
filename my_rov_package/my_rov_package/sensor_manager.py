from collections import deque
import time
import pytest

@pytest.fixture
def depth_sensor():
    return SensorManager(min_val=0.0, max_val=100.0, window_size=5)

class SensorManager:
    def __init__(self, min_val: float, max_val: float, window_size: int = 5):
        self._min_val = min_val
        self._max_val = max_val

        self.last_valid_time = None

        self._window_size = window_size

        self.queue = deque(maxlen=window_size)

    def update(self, raw_value: float | None):
        if raw_value is None: return False

        if not self._min_val <= raw_value <= self._max_val:
            return False

        self.queue.append(raw_value)
        self.last_valid_time = time.monotonic()
        return True

    def smoothing_average(self) -> float:
        if len(self.queue) == 0: return None
        return sum(self.queue) / len(self.queue)


def test_depth_sensor(depth_sensor):
    updated: bool = depth_sensor.update(-1)
    assert updated is False

def test_above_max_rejected(depth_sensor):
    updated: bool = depth_sensor.update(100.1)
    assert updated is False

def test_valid_boundary_values_accepted(depth_sensor):
    low = depth_sensor.update(0.0)
    high = depth_sensor.update(100.0)

    assert low is True
    assert high is True