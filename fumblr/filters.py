from fumblr import app
from datetime import datetime
from math import floor

@app.template_filter()
def timesince(dt, default="just now"):
    """
        Returns string representing "time since" e.g.
        3 days ago, 5 hours ago etc.
        """

    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        period_floor = floor(period)
        if period_floor:
            return "{} {} ago".format(period_floor, singular if period_floor == 1 else plural)

    return default


@app.template_filter()
def friendly_time(dt, past_="ago",
                  future_="from now",
                  default="just now"):
    """
    Returns string representing "time since"
    or "time until" e.g.
    3 days ago, 5 hours from now etc.
    """

    now = datetime.utcnow()
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        period_floor = floor(period)
        if period_floor:
            return "{} {} {}".format(period, singular if period == 1 else plural, past_ if dt_is_past else future_)

    return default