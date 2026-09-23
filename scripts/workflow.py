#!/usr/bin/env python3
"""Persistent lead register and guarded Vercel preview lifecycle."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import unicodedata
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "state" / "leads.sqlite3"
DEMOS = ROOT / "demos"
VALID_WEBSITE_STATUSES = {"no_site_found", "social_only"}


def fail(message: str) -> None:
    raise SystemExit(f"Errore: {message}")


def connect() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            identity_key TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            category TEXT NOT NULL,
            language TEXT NOT NULL,
            website_status TEXT NOT NULL,
            website_checked_on TEXT NOT NULL,
            lead_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            selected_on TEXT,
            brief_path TEXT,
            design_canvas_url TEXT,
            selected_artboard TEXT,
            site_folder TEXT,
            deployment_url TEXT,
            deploy_account TEXT,
            sent_on TEXT,
            due_on TEXT,
            response_status TEXT,
            response_recorded_on TEXT,
            preview_removed_on TEXT
        )
        """
    )
    connection.commit()
    return connection


def today() -> date:
    return date.today()


def iso_day(value: str | None) -> str:
    if value is None:
        return today().isoformat()
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        fail("data non valida; usa YYYY-MM-DD")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def identity_key(data: dict) -> str:
    parts = [data["name"], data["city"], data["country"]]
    normalized = []
    for part in parts:
        text = unicodedata.normalize("NFKD", part).casefold()
        normalized.append(re.sub(r"[^a-z0-9]+", "", text))
    return "|".join(normalized)


def valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def preview_url(value: str) -> bool:
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    return (
        parsed.scheme == "https"
        and host.endswith(".vercel.app")
        and host != "vercel.app"
        and parsed.path in {"", "/"}
        and not parsed.query
        and not parsed.fragment
    )


def validate_lead(data: object) -> dict:
    if not isinstance(data, dict):
        fail("il file del lead deve contenere un oggetto JSON")
    for field in ("name", "city", "country", "category", "language", "website_checked_on"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            fail(f"campo obbligatorio mancante: {field}")
    if data.get("website_status") not in VALID_WEBSITE_STATUSES:
        fail("sono ammessi solo no_site_found o social_only")
    iso_day(data["website_checked_on"])
    evidence = data.get("website_evidence")
    if not isinstance(evidence, list) or not evidence:
        fail("website_evidence deve includere almeno una fonte")
    for item in evidence:
        if not isinstance(item, dict) or not valid_url(str(item.get("url", ""))):
            fail("ogni verifica sito deve avere un URL http/https")
        if not isinstance(item.get("finding"), str) or not item["finding"].strip():
            fail("ogni verifica sito deve descrivere il risultato")
    for field in ("verified_facts", "source_urls", "assets"):
        if field in data and not isinstance(data[field], list):
            fail(f"{field} deve essere una lista")
    return data


def row_for(connection: sqlite3.Connection, lead_id: str) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    if row is None:
        fail(f"lead non trovato: {lead_id}")
    return row


def public_row(row: sqlite3.Row) -> dict:
    result = dict(row)
    result["lead"] = json.loads(result.pop("lead_json"))
    return result


def cmd_add(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    path = Path(args.file)
    try:
        data = validate_lead(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"impossibile leggere il lead: {exc}")
    lead_id = uuid.uuid4().hex[:10]
    try:
        connection.execute(
            """
            INSERT INTO leads
            (id, identity_key, name, city, country, category, language,
             website_status, website_checked_on, lead_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lead_id,
                identity_key(data),
                data["name"].strip(),
                data["city"].strip(),
                data["country"].strip(),
                data["category"].strip(),
                data["language"].strip(),
                data["website_status"],
                data["website_checked_on"],
                json.dumps(data, ensure_ascii=False),
                now_utc(),
            ),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        fail("attività già presente nel registro (stesso nome e luogo)")
    print(lead_id)


def cmd_select(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    row = row_for(connection, args.id)
    if row["selected_on"]:
        print(f"{args.id}: già selezionato")
        return
    connection.execute(
        "UPDATE leads SET selected_on = ? WHERE id = ?",
        (today().isoformat(), args.id),
    )
    connection.commit()
    print(f"{args.id}: selezionato")


def cmd_design(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    row = row_for(connection, args.id)
    if not row["selected_on"]:
        fail("seleziona prima il lead")
    if not valid_url(args.canvas):
        fail("URL del canvas non valido")
    if not args.artboard.strip():
        fail("indica l'artboard scelto")
    connection.execute(
        """
        UPDATE leads SET design_canvas_url = ?, selected_artboard = ?, brief_path = ?
        WHERE id = ?
        """,
        (args.canvas, args.artboard.strip(), args.brief, args.id),
    )
    connection.commit()
    print(f"{args.id}: design registrato")


def vercel_bin() -> str:
    name = os.environ.get("FIND_CUSTOMER_VERCEL_BIN", "vercel.cmd" if os.name == "nt" else "vercel")
    binary = shutil.which(name)
    if not binary:
        fail(f"Vercel CLI non trovata nel PATH: {name}")
    return binary


def run_vercel(binary: str, argv: list[str], folder: Path) -> str:
    try:
        result = subprocess.run(
            [binary, *argv],
            cwd=folder,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"Vercel CLI non completata: {exc}")
    if result.returncode != 0:
        fail(f"Vercel CLI ha restituito {result.returncode}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def check_account(binary: str, folder: Path, expected: str) -> None:
    output = run_vercel(binary, ["whoami"], folder)
    actual = output.splitlines()[-1].strip() if output else ""
    if actual.casefold() != expected.casefold():
        fail(f"account Vercel diverso: atteso {expected}, trovato {actual or 'nessuno'}")


def demo_folder(value: str) -> Path:
    folder = Path(value).expanduser().resolve()
    try:
        folder.relative_to(DEMOS.resolve())
    except ValueError:
        fail(f"la cartella del sito deve stare dentro {DEMOS}")
    if not folder.is_dir():
        fail(f"cartella sito inesistente: {folder}")
    return folder


def cmd_deploy(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    row = row_for(connection, args.id)
    if not row["design_canvas_url"] or not row["selected_artboard"]:
        fail("registra prima il canvas /design e l'artboard scelto")
    if row["deployment_url"]:
        fail("questo lead ha già un deployment registrato")
    folder = demo_folder(args.folder)
    if not (folder / "index.html").exists() and not (folder / "package.json").exists():
        fail("la cartella non contiene index.html o package.json")
    binary = vercel_bin()
    check_account(binary, folder, args.account)
    output = run_vercel(binary, ["deploy", "--yes"], folder)
    url = output.splitlines()[-1].strip() if output else ""
    if not preview_url(url):
        fail(f"deploy eseguito ma URL preview inatteso: {url!r}; verifica su Vercel prima di ritentare")
    connection.execute(
        """
        UPDATE leads SET site_folder = ?, deployment_url = ?, deploy_account = ?
        WHERE id = ?
        """,
        (str(folder), url, args.account, args.id),
    )
    connection.commit()
    print(url)


def cmd_sent(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    row = row_for(connection, args.id)
    if not row["deployment_url"]:
        fail("registra prima un deployment preview")
    if row["sent_on"]:
        fail("messaggio già marcato come inviato")
    sent_on = date.fromisoformat(iso_day(args.date))
    if sent_on > today():
        fail("la data di invio non può essere futura")
    due_on = sent_on + timedelta(days=4)
    connection.execute(
        "UPDATE leads SET sent_on = ?, due_on = ? WHERE id = ?",
        (sent_on.isoformat(), due_on.isoformat(), args.id),
    )
    connection.commit()
    print(f"{args.id}: invio registrato; controllo il {due_on.isoformat()}")


def cmd_due(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    check_day = iso_day(args.date)
    rows = connection.execute(
        """
        SELECT id, name, city, country, sent_on, due_on, deployment_url
        FROM leads
        WHERE due_on <= ? AND response_status IS NULL AND preview_removed_on IS NULL
        ORDER BY sent_on, name
        """,
        (check_day,),
    ).fetchall()
    print(json.dumps([dict(row) for row in rows], ensure_ascii=False, indent=2))


def cmd_answer(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    row = row_for(connection, args.id)
    if not row["sent_on"]:
        fail("messaggio non ancora marcato come inviato")
    if row["response_status"]:
        fail(f"esito già registrato: {row['response_status']}")
    answer_day = date.fromisoformat(iso_day(args.date))
    if args.outcome == "no_reply" and answer_day < date.fromisoformat(row["due_on"]):
        fail("i quattro giorni non sono ancora trascorsi")
    connection.execute(
        "UPDATE leads SET response_status = ?, response_recorded_on = ? WHERE id = ?",
        (args.outcome, answer_day.isoformat(), args.id),
    )
    connection.commit()
    print(f"{args.id}: {args.outcome} registrato")


def cmd_cleanup(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    row = row_for(connection, args.id)
    if row["response_status"] != "no_reply":
        fail("rimozione consentita solo dopo conferma esplicita no_reply")
    if not row["due_on"] or date.fromisoformat(row["due_on"]) > today():
        fail("i quattro giorni non sono ancora trascorsi")
    if row["preview_removed_on"]:
        fail("preview già marcata rimossa")
    url = row["deployment_url"] or ""
    if not preview_url(url):
        fail("URL di preview registrato non valido; non rimuovo nulla")
    if not row["deploy_account"]:
        fail("account Vercel non registrato")
    folder = demo_folder(row["site_folder"])
    binary = vercel_bin()
    check_account(binary, folder, row["deploy_account"])
    run_vercel(binary, ["remove", url, "--yes"], folder)
    connection.execute(
        "UPDATE leads SET preview_removed_on = ? WHERE id = ?",
        (now_utc(), args.id),
    )
    connection.commit()
    print(f"{args.id}: rimossa solo la preview {url}")


def cmd_list(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    rows = connection.execute(
        """
        SELECT id, name, city, country, website_status, selected_on,
               deployment_url, sent_on, due_on, response_status, preview_removed_on
        FROM leads ORDER BY created_at DESC
        """
    ).fetchall()
    print(json.dumps([dict(row) for row in rows], ensure_ascii=False, indent=2))


def cmd_detail(connection: sqlite3.Connection, args: argparse.Namespace) -> None:
    print(json.dumps(public_row(row_for(connection, args.id)), ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    add = sub.add_parser("add")
    add.add_argument("file", help="file JSON con il lead verificato")
    select = sub.add_parser("select")
    select.add_argument("id")
    design = sub.add_parser("design")
    design.add_argument("id")
    design.add_argument("--canvas", required=True)
    design.add_argument("--artboard", required=True)
    design.add_argument("--brief", required=True)
    deploy = sub.add_parser("deploy")
    deploy.add_argument("id")
    deploy.add_argument("--folder", required=True)
    deploy.add_argument("--account", required=True)
    sent = sub.add_parser("sent")
    sent.add_argument("id")
    sent.add_argument("--date")
    due = sub.add_parser("due")
    due.add_argument("--date")
    answer = sub.add_parser("answer")
    answer.add_argument("id")
    answer.add_argument("outcome", choices=["replied", "no_reply"])
    answer.add_argument("--date")
    cleanup = sub.add_parser("cleanup")
    cleanup.add_argument("id")
    sub.add_parser("list")
    detail = sub.add_parser("detail")
    detail.add_argument("id")
    return p


def main() -> None:
    args = parser().parse_args()
    connection = connect()
    try:
        handlers = {
            "add": cmd_add,
            "select": cmd_select,
            "design": cmd_design,
            "deploy": cmd_deploy,
            "sent": cmd_sent,
            "due": cmd_due,
            "answer": cmd_answer,
            "cleanup": cmd_cleanup,
            "list": cmd_list,
            "detail": cmd_detail,
        }
        if args.command == "init":
            print(str(DB))
        else:
            handlers[args.command](connection, args)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
