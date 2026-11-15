# cron-explain

Paste a cron expression, get plain English and the next run times. One file, standard library only.

## Usage

```
python cron_explain.py "0 9 * * mon-fri"
python cron_explain.py "*/15 * * * *" -n 3
python cron_explain.py @daily
```

Example output:

```
at 09:00, on Monday, Tuesday, Wednesday, Thursday and Friday
  next: 2026-01-05 09:00 (Mon)
  ...
```

## Supported syntax

- Five fields: minute, hour, day of month, month, day of week.
- `*`, lists (`1,15`), ranges (`1-5`), steps (`*/10`, `10-30/10`).
- Month and weekday names (`jan`, `mon-fri`); `7` means Sunday.
- Aliases: `@hourly`, `@daily`, `@weekly`, `@monthly`, `@yearly`.
- When both day-of-month and day-of-week are restricted, a run matches either, like standard cron.

## Limitations

- No seconds field, no `L`, `W`, `#` or `?` extensions.
- Next runs use your local clock and ignore daylight saving changes.

## Tests

```
python -m unittest discover -s tests -v
```

## License

MIT
