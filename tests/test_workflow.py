"""Exercise the register's safety gates without contacting Vercel."""

import contextlib
import io
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import workflow


class WorkflowLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for key, value in {
            "ROOT": self.root,
            "DB": self.root / "state" / "leads.sqlite3",
            "DEMOS": self.root / "demos",
        }.items():
            mocked = patch.object(workflow, key, value)
            mocked.start()
            self.addCleanup(mocked.stop)
        self.conn = workflow.connect()
        self.addCleanup(self.conn.close)

    def call(self, handler, **kwargs):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            handler(self.conn, SimpleNamespace(**kwargs))
        return output.getvalue().strip()

    def make_lead(self, name="Trattoria Esempio", status="social_only"):
        lead = {
            "name": name,
            "city": "Milano",
            "country": "Italia",
            "category": "ristorante",
            "language": "it",
            "website_status": status,
            "website_checked_on": date.today().isoformat(),
            "website_evidence": [{"url": "https://example.org/listing", "finding": "Solo pagina social"}],
        }
        file = self.root / f"{name}.json"
        file.write_text(json.dumps(lead), encoding="utf-8")
        return file

    def test_reject_existing_site_and_duplicate(self):
        with self.assertRaises(SystemExit):
            self.call(workflow.cmd_add, file=str(self.make_lead(status="has_site")))
        file = self.make_lead()
        self.call(workflow.cmd_add, file=str(file))
        with self.assertRaises(SystemExit):
            self.call(workflow.cmd_add, file=str(file))

    def test_four_day_gate_and_exact_preview_removal(self):
        lead_id = self.call(workflow.cmd_add, file=str(self.make_lead()))
        self.call(workflow.cmd_select, id=lead_id)
        brief = self.root / "brief.md"
        brief.write_text("Test brief", encoding="utf-8")
        self.call(workflow.cmd_design, id=lead_id, canvas="https://example.org/canvas", artboard="A", brief=str(brief))
        folder = workflow.DEMOS / lead_id
        folder.mkdir(parents=True)
        (folder / "index.html").write_text("<!doctype html><title>Demo</title>", encoding="utf-8")
        preview = "https://example-project-abc123.vercel.app"
        calls = []

        def fake_vercel(_binary, argv, _folder):
            calls.append(argv)
            return "demo-account" if argv == ["whoami"] else preview if argv == ["deploy", "--yes"] else "Removed"

        with patch.object(workflow, "vercel_bin", return_value="vercel"), patch.object(workflow, "run_vercel", side_effect=fake_vercel):
            self.assertEqual(preview, self.call(workflow.cmd_deploy, id=lead_id, folder=str(folder), account="demo-account"))
            self.call(workflow.cmd_sent, id=lead_id, date=(date.today() - timedelta(days=3)).isoformat())
            self.assertEqual("[]", self.call(workflow.cmd_due, date=None))
            with self.assertRaises(SystemExit):
                self.call(workflow.cmd_answer, id=lead_id, outcome="no_reply", date=None)
            with self.assertRaises(SystemExit):
                self.call(workflow.cmd_cleanup, id=lead_id)
            self.assertNotIn(["remove", preview, "--yes"], calls)

            # Move the simulated contact date back so four calendar days have passed.
            old_day = date.today() - timedelta(days=4)
            self.conn.execute("UPDATE leads SET sent_on = ?, due_on = ? WHERE id = ?", (old_day.isoformat(), date.today().isoformat(), lead_id))
            self.conn.commit()
            due = json.loads(self.call(workflow.cmd_due, date=None))
            self.assertEqual([lead_id], [item["id"] for item in due])
            with self.assertRaises(SystemExit):
                self.call(workflow.cmd_cleanup, id=lead_id)
            self.call(workflow.cmd_answer, id=lead_id, outcome="no_reply", date=None)
            self.call(workflow.cmd_cleanup, id=lead_id)

        self.assertIn(["remove", preview, "--yes"], calls)
        self.assertTrue(folder.exists(), "Local site files must be retained")
        self.assertIsNotNone(workflow.row_for(self.conn, lead_id)["preview_removed_on"])

    def test_replied_lead_cannot_be_removed(self):
        lead_id = self.call(workflow.cmd_add, file=str(self.make_lead()))
        self.conn.execute(
            "UPDATE leads SET sent_on = ?, due_on = ? WHERE id = ?",
            ((date.today() - timedelta(days=5)).isoformat(), (date.today() - timedelta(days=1)).isoformat(), lead_id),
        )
        self.conn.commit()
        self.call(workflow.cmd_answer, id=lead_id, outcome="replied", date=None)
        with self.assertRaises(SystemExit):
            self.call(workflow.cmd_cleanup, id=lead_id)


if __name__ == "__main__":
    unittest.main()
