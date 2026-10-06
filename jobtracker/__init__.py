"""jobtracker: a tiny CLI for tracking job applications in a local SQLite file."""

from .store import Store, Application, STATUSES

__all__ = ["Store", "Application", "STATUSES"]
__version__ = "0.1.0"
