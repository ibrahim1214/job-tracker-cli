"""Command line interface for jobtracker."""

from __future__ import annotations

import argparse
import sys

from .store import Store, STATUSES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobtracker", description="Track job applications locally")
    parser.add_argument("--db", default="applications.db")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record a new application")
    add.add_argument("company")
    add.add_argument("role")
    add.add_argument("--source", default="")
    add.add_argument("--pay", type=float, default=None, help="hourly pay")
    add.add_argument("--notes", default="")

    upd = sub.add_parser("status", help="update an application's status")
    upd.add_argument("id", type=int)
    upd.add_argument("status", choices=STATUSES)

    ls = sub.add_parser("list", help="list applications")
    ls.add_argument("--status", choices=STATUSES)

    sub.add_parser("summary", help="counts per status")

    args = parser.parse_args(argv)
    store = Store(args.db)
    try:
        if args.command == "add":
            app_id = store.add(args.company, args.role, args.source, args.pay, notes=args.notes)
            print(f"Added #{app_id}: {args.role} at {args.company}")
        elif args.command == "status":
            store.set_status(args.id, args.status)
            print(f"#{args.id} -> {args.status}")
        elif args.command == "list":
            for a in store.list(args.status):
                pay = f"${a.pay_per_hour:.2f}/h" if a.pay_per_hour else "-"
                print(f"#{a.id:<3} {a.applied_on}  {a.status:<10} {a.company} | {a.role} | {pay}")
        else:
            for key, value in store.summary().items():
                print(f"{key:<10} {value}")
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
