#!/usr/bin/env python3
"""cron-explain: turn a 5-field cron expression into plain English and list next run times."""
import argparse
import datetime as dt
import sys

NAMES = ["minute", "hour", "day of month", "month", "day of week"]
RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
ALIASES = {"@hourly": "0 * * * *", "@daily": "0 0 * * *", "@midnight": "0 0 * * *",
           "@weekly": "0 0 * * 0", "@monthly": "0 0 1 * *", "@yearly": "0 0 1 1 *",
           "@annually": "0 0 1 1 *"}
MON_ABBR = {m[:3].lower(): i + 1 for i, m in enumerate(MONTHS)}
DAY_ABBR = {d[:3].lower(): i for i, d in enumerate(DAYS)}


def parse_field(text, idx):
    """Return the sorted set of values a field matches."""
    lo, hi = RANGES[idx]
    names = MON_ABBR if idx == 3 else DAY_ABBR if idx == 4 else {}
    values = set()
    for part in text.split(","):
        step = 1
        if "/" in part:
            part, s = part.split("/", 1)
            step = int(s)
            if step < 1:
                raise ValueError("bad step in %s" % NAMES[idx])
        if part == "*":
            a, b = lo, hi
        elif "-" in part:
            x, y = part.split("-", 1)
            a, b = _num(x, names), _num(y, names)
        else:
            a = _num(part, names)
            b = hi if step > 1 else a
        if not (lo <= a <= hi and lo <= b <= hi and a <= b):
            raise ValueError("%s out of range: %s" % (NAMES[idx], text))
        values.update(range(a, b + 1, step))
    if idx == 4:
        values = {v % 7 for v in values}
    return sorted(values)


def _num(tok, names):
    tok = tok.strip().lower()
    if tok in names:
        return names[tok]
    return int(tok)


def parse(expr):
    expr = ALIASES.get(expr.strip(), expr)
    fields = expr.split()
    if len(fields) != 5:
        raise ValueError("expected 5 fields, got %d" % len(fields))
    parsed = [parse_field(f, i) for i, f in enumerate(fields)]
    return fields, parsed


def _list(vals, fmt):
    items = [fmt(v) for v in vals]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def explain(expr):
    fields, p = parse(expr)
    m, h, dom, mon, dow = fields
    if m == "*" and h == "*":
        when = "every minute"
    elif h == "*" and m.startswith("*/"):
        when = "every %s minutes" % m[2:]
    elif h == "*":
        when = "at minute %s of every hour" % _list(p[0], str)
    elif len(p[0]) == 1 and len(p[1]) == 1:
        when = "at %02d:%02d" % (p[1][0], p[0][0])
    else:
        when = "at minute %s past hour %s" % (_list(p[0], str), _list(p[1], str))
    parts = [when]
    if dom != "*":
        parts.append("on day %s of the month" % _list(p[2], str))
    if mon != "*":
        parts.append("in " + _list(p[3], lambda v: MONTHS[v - 1]))
    if dow != "*":
        parts.append("on " + _list(p[4], lambda v: DAYS[v]))
    return ", ".join(parts)


def matches(p, t):
    dow = (t.weekday() + 1) % 7
    dom_ok, dow_ok = t.day in p[2], dow in p[4]
    day_ok = (dom_ok or dow_ok) if (len(p[2]) < 31 and len(p[4]) < 7) else (dom_ok and dow_ok)
    return t.minute in p[0] and t.hour in p[1] and t.month in p[3] and day_ok


def next_runs(expr, start, count=5):
    _, p = parse(expr)
    t = start.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)
    out, limit = [], 366 * 24 * 60 * 5
    while len(out) < count and limit > 0:
        if matches(p, t):
            out.append(t)
        t += dt.timedelta(minutes=1)
        limit -= 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Explain a cron expression.")
    ap.add_argument("expression", help='e.g. "*/15 9-17 * * mon-fri"')
    ap.add_argument("-n", type=int, default=5, help="how many next runs to show")
    args = ap.parse_args(argv)
    try:
        print(explain(args.expression))
        for t in next_runs(args.expression, dt.datetime.now(), args.n):
            print("  next: " + t.strftime("%Y-%m-%d %H:%M (%a)"))
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
