# job-tracker-cli

A tiny command line tool for tracking job applications in a local SQLite file. No accounts, no cloud, no dependencies beyond the Python standard library.

## Features

- Record applications with company, role, source, hourly pay, and notes
- Move applications through `applied`, `screening`, `interview`, `offer`, `rejected`, `withdrawn`
- Filter the list by status and print a per-status summary

## Usage

```bash
python -m jobtracker.cli add "Acme Corp" "IT Support Specialist" --source indeed --pay 32
python -m jobtracker.cli status 1 interview
python -m jobtracker.cli list --status interview
python -m jobtracker.cli summary
```

The database defaults to `applications.db` in the current directory; use `--db path` to change it.

## Tests

```bash
pip install pytest
pytest
```
