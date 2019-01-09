from datetime import datetime as dt

import pytest
from mock import patch

from arctic.date import datetime_to_ms, ms_to_datetime, mktz, to_pandas_closed_closed, DateRange, OPEN_OPEN, \
    CLOSED_CLOSED
from arctic.date._util import to_dt, utc_dt_to_local_dt


@pytest.mark.parametrize('pdt', [
                            dt(2007, 3, 25, 1, tzinfo=mktz('Europe/London')),
                            dt(2004, 10, 31, 23, 3, tzinfo=mktz('Europe/London')),
                            dt(1990, 4, 5, 0, 0, tzinfo=mktz('Europe/London')),
                            dt(2007, 3, 25, 1, tzinfo=mktz('EST')),
                            dt(2004, 10, 31, 23, 3, tzinfo=mktz('EST')),
                            dt(1990, 4, 5, 0, 0, tzinfo=mktz('EST')),
                            ]
)
@pytest.mark.parametrize('local_tz', [
    mktz('EST'),
    mktz('CET'),
    mktz('Asia/Tokyo'),
    mktz('Cuba'),
    mktz('US/Alaska'),
    mktz(),
    mktz('Europe/London'),
]
)
def test_datetime_to_ms_and_back(pdt, local_tz):
    i = datetime_to_ms(pdt)
    pdt = pdt.astimezone(local_tz)
    pdt2 = ms_to_datetime(i, tzinfo=local_tz)
    assert datetime_to_ms(pdt) == datetime_to_ms(pdt2)


def test_datetime_to_ms_and_back_microseconds():
    pdt = dt(2012, 8, 1, 12, 34, 56, 999999, tzinfo=mktz())
    i = datetime_to_ms(pdt)
    pdt2 = ms_to_datetime(i)

    assert pdt != pdt2
    assert pdt.year == pdt2.year
    assert pdt.month == pdt2.month
    assert pdt.day == pdt2.day
    assert pdt.hour == pdt2.hour
    assert pdt.minute == pdt2.minute
    assert pdt.second == pdt2.second
    #   Microsecond precision loss inevitable.
    assert pdt.microsecond // 1000 == pdt2.microsecond // 1000


def test_daterange_closedclosed_None():
    assert to_pandas_closed_closed(None) is None


def test_daterange_closedclosed():
    date_range = DateRange(dt(2013, 1, 1, tzinfo=mktz('Europe/London')),
                           dt(2014, 2, 1, tzinfo=mktz('Europe/London')), OPEN_OPEN)
    expected = DateRange(dt(2013, 1, 1, 0, 0, 0, 1000, tzinfo=mktz('Europe/London')),
                         dt(2014, 1, 31, 23, 59, 59, 999000, tzinfo=mktz('Europe/London')),
                         CLOSED_CLOSED)
    act = to_pandas_closed_closed(date_range)
    assert act == expected


def test_daterange_closedclosed_no_tz():
    date_range = DateRange(dt(2013, 1, 1),
                           dt(2014, 2, 1), OPEN_OPEN)
    expected = DateRange(dt(2013, 1, 1, 0, 0, 0, 1000, tzinfo=mktz()),
                         dt(2014, 1, 31, 23, 59, 59, 999000, tzinfo=mktz()),
                         CLOSED_CLOSED)
    act = to_pandas_closed_closed(date_range)
    assert act == expected


def test_to_dt_0():
    assert to_dt(0) == dt(1970, 1, 1, tzinfo=mktz('UTC'))


def test_to_dt_0_default():
    assert to_dt(0, mktz('UTC')) == dt(1970, 1, 1, tzinfo=mktz('UTC'))


def test_to_dt_dt_no_tz():
    with pytest.raises(ValueError):
        assert to_dt(dt(1970, 1, 1)) == dt(1970, 1, 1, tzinfo=mktz())


def test_to_dt_dt_no_tz_default():
    assert to_dt(dt(1970, 1, 1), mktz('UTC')) == dt(1970, 1, 1, tzinfo=mktz('UTC'))


def test_to_dt_dt_tz():
    assert to_dt(dt(1970, 1, 1, tzinfo=mktz('UTC'))) == dt(1970, 1, 1, tzinfo=mktz('UTC'))


def test_to_dt_dt_tz_default():
    assert to_dt(dt(1970, 1, 1, tzinfo=mktz('UTC')), mktz('Europe/London')) == dt(1970, 1, 1, tzinfo=mktz('UTC'))


def test_daterange_raises():
    with pytest.raises(ValueError):
        assert(DateRange(dt(2013, 1, 1), dt(2000, 1, 1)))


def test_daterange_eq():
    dr = DateRange(dt(2013, 1, 1))
    assert((dr == None) == False)
    assert(dr == dr)


def test_daterange_lt():
    dr = DateRange(dt(2013, 1, 1))
    dr2 = DateRange(dt(2001, 1, 1))

    assert(dr2 < dr)
    dr.start = None
    assert((dr2 < dr) == False)


@patch("arctic.date._util.mktz", lambda zone="Asia/Shanghai": mktz(zone))
def test_utc_dt_to_local_dt():
    with pytest.raises(ValueError):
        assert(utc_dt_to_local_dt(
            dt(2000, 1, 1, 0, 0, 0, tzinfo=mktz("Asia/Shanghai"))
        ))

    utc_time = dt(2000, 1, 1, 10, 0, 0)
    pek_time = utc_dt_to_local_dt(utc_time)  # GMT +0800
    assert(pek_time.hour - utc_time.hour == 8)
