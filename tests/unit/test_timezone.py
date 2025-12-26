import pytest
from datetime import datetime, timedelta
from common.timezone import UTC, Eastern, first_sunday_on_or_after, ZERO, HOUR
import pytz

def test_utc_timezone():
    """Test UTC timezone behavior."""
    utc = UTC()
    dt = datetime(2023, 1, 1, 12, 0, 0)
    assert utc.utcoffset(dt) == ZERO
    assert utc.tzname(dt) == "UTC"
    assert utc.dst(dt) == ZERO

def test_first_sunday_on_or_after():
    """Test helper for finding the first Sunday."""
    # Sunday
    dt = datetime(2023, 1, 1)  # Jan 1 2023 is a Sunday
    assert first_sunday_on_or_after(dt) == dt

    # Monday
    dt = datetime(2023, 1, 2)
    expected = datetime(2023, 1, 8)  # Next Sunday
    assert first_sunday_on_or_after(dt) == expected

    # Saturday
    dt = datetime(2023, 1, 7)
    expected = datetime(2023, 1, 8)
    assert first_sunday_on_or_after(dt) == expected

def test_eastern_standard_time():
    """Test Eastern Standard Time (winter)."""
    # Jan 1st is clearly standard time
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=Eastern)

    assert Eastern.dst(dt) == ZERO
    assert Eastern.utcoffset(dt) == timedelta(hours=-5)
    assert Eastern.tzname(dt) == "EST"

def test_eastern_daylight_time():
    """Test Eastern Daylight Time (summer)."""
    # July 1st is clearly daylight time
    dt = datetime(2023, 7, 1, 12, 0, 0, tzinfo=Eastern)

    assert Eastern.dst(dt) == HOUR
    assert Eastern.utcoffset(dt) == timedelta(hours=-4)
    assert Eastern.tzname(dt) == "EDT"

def test_eastern_dst_transition_start():
    """Test DST start transition (March)."""
    # 2023: DST starts March 12 (Sunday) at 2am

    # Before 2am: Standard Time
    dt_before = datetime(2023, 3, 12, 1, 59, 0, tzinfo=Eastern)
    assert Eastern.dst(dt_before) == ZERO
    assert Eastern.tzname(dt_before) == "EST"

    # At 3am (2am doesn't exist/skipped, effectively 3am is first DST moment)
    # The pytz implementation usually handles normalization.
    # Our manual implementation checks if start <= dt < end (stripped of tz)

    # Let's check 3am EDT (which is 7am UTC)
    dt_after = datetime(2023, 3, 12, 3, 0, 0, tzinfo=Eastern)
    assert Eastern.dst(dt_after) == HOUR
    assert Eastern.tzname(dt_after) == "EDT"

def test_eastern_dst_transition_end():
    """Test DST end transition (November)."""
    # 2023: DST ends Nov 5 (Sunday) at 2am

    # Nov 4 is still DST
    dt_before = datetime(2023, 11, 4, 12, 0, 0, tzinfo=Eastern)
    assert Eastern.dst(dt_before) == HOUR

    # Nov 5 1am (could be DST or ST due to repeat, usually DST first pass)
    # The simple implementation might map it strictly based on wall clock comparison
    # start <= dt < end.

    # Nov 5 3am is definitely Standard
    dt_after = datetime(2023, 11, 5, 3, 0, 0, tzinfo=Eastern)
    assert Eastern.dst(dt_after) == ZERO
    assert Eastern.tzname(dt_after) == "EST"

def test_historical_dst_rules():
    """Test historical DST rules (pre-2007)."""
    # 2000 (1987-2006 rules): Starts first Sunday in April (April 2nd)

    # March 15 in 2000 was Standard (unlike 2023 where it is DST)
    dt = datetime(2000, 3, 15, 12, 0, 0, tzinfo=Eastern)
    assert Eastern.dst(dt) == ZERO

    # July is DST
    dt = datetime(2000, 7, 1, 12, 0, 0, tzinfo=Eastern)
    assert Eastern.dst(dt) == HOUR
