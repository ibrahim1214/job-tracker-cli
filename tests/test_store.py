import pytest

from jobtracker import Store
from jobtracker.cli import main


@pytest.fixture
def store(tmp_path):
    s = Store(str(tmp_path / "t.db"))
    yield s
    s.close()


def test_add_and_list(store):
    app_id = store.add("Acme", "IT Support Specialist", source="indeed", pay_per_hour=32.5)
    apps = store.list()
    assert len(apps) == 1
    assert apps[0].id == app_id
    assert apps[0].status == "applied"
    assert apps[0].pay_per_hour == 32.5


def test_add_requires_company_and_role(store):
    with pytest.raises(ValueError):
        store.add("  ", "Engineer")


def test_status_update_and_filter(store):
    a = store.add("Acme", "Dev")
    store.add("Beta", "QA")
    store.set_status(a, "interview")
    assert [x.company for x in store.list("interview")] == ["Acme"]


def test_invalid_status_and_missing_id(store):
    a = store.add("Acme", "Dev")
    with pytest.raises(ValueError):
        store.set_status(a, "ghosted")
    with pytest.raises(KeyError):
        store.set_status(999, "offer")


def test_summary_counts(store):
    a = store.add("A", "x")
    store.add("B", "y")
    store.set_status(a, "rejected")
    s = store.summary()
    assert s["applied"] == 1 and s["rejected"] == 1 and s["total"] == 2


def test_cli_roundtrip(tmp_path, capsys):
    db = str(tmp_path / "cli.db")
    assert main(["--db", db, "add", "Acme", "Dev", "--pay", "40"]) == 0
    assert main(["--db", db, "status", "1", "offer"]) == 0
    assert main(["--db", db, "status", "7", "offer"]) == 1
    assert main(["--db", db, "list"]) == 0
    out = capsys.readouterr().out
    assert "Acme" in out and "offer" in out
