---
name: find-customer-orchestrator
description: Coordinate verified no-website local business prospecting, Claude Code /design site demos, Vercel preview deployment, and four-day follow-up tracking for Francesco. Use when he asks to find website clients or advance a selected prospect.
---

# Find Customer Orchestrator

Work from the Find Customer Automation project folder containing `scripts/workflow.py` and `templates/`. The persistent registry is `state/leads.sqlite3`. Use the installed `local-client-prospector` and `first-customer-finder` skills without changing their own research rules.

## Research

- Let Francesco provide category and geography; infer only safe defaults.
- Use Local Client Prospector as the primary business and website check. Use First Customer Finder for public demand signals when it fits; its lack of signals does not prove a business has a site.
- Search the exact business name with location and cross-check public sources. Offer only `no_site_found` or `social_only` candidates in the selectable shortlist. Exclude existing standalone sites and ambiguous cases. Say "no site found after these checks," not "proved no site exists."
- Give each lead source URLs, check date, confidence and a concise reason. Never invent a prospect or fill a quota with weak matches. Save each qualified lead as JSON with `py scripts/workflow.py add <lead.json>` on Windows, then show Francesco its returned ID. Keep raw research output and registry outside installed skill directories.
- Wait for Francesco to choose an ID, then mark it selected with `py scripts/workflow.py select <id>`. Recheck the absence of an official site before building a demo. If a site is found or evidence becomes ambiguous, stop work on that lead.

## Brief and visual assets

For the chosen lead, write a brief using `templates/brief.md`. Record observed colors, official logo source if available, verified facts, contact route, brand cues and missing facts. Save an asset manifest with local path, source URL, license/use permission and what each image depicts. Social images are visual references unless use permission is clear; for published previews use supplied or suitably licensed images. If no real logo is available, use a temporary wordmark. Never present invented colors as the business's identity or stock photos as photos of the real venue. Do not imply the business endorsed the concept.

## Claude and Vercel

1. Verify `claude` and `vercel.cmd` on Windows, and that Claude can see the brief/assets. Use `templates/design-prompt.md` with Claude Code's built-in `/design` command. It creates artboards, not finished site files. Capture its canvas URL in the register.
2. Prefer an interactive Claude CLI session for the first `/design` test because the documented flow is interactive. Do not assume `claude -p` produces a usable canvas. If a CLI automation mode works in the smoke test, it can be used thereafter.
3. Inspect the artboards and choose one against the brief, or ask Francesco to choose if the canvas cannot be inspected. Pass `templates/implementation-prompt.md` and the chosen artboard back to Claude in the same session to create the files.
4. Verify the site locally: build if applicable, desktop/mobile appearance, links, reduced-motion behavior, factual content, asset rights and visible concept status. Fix material failures before deployment.
5. Deploy only as a Vercel preview with `python scripts/workflow.py deploy <id> --folder <site-folder> --account <expected-vercel-username>`. This records the exact URL and account. Do not use `--prod` or a project name as a removal target.
6. Draft the Italian or English outreach message with the preview link. Francesco sends it manually. Mark sent only after his confirmation with `python scripts/workflow.py sent <id>`.

## Four-day follow-up

On a daily scheduled Codex check, run `python scripts/workflow.py due`. Notify Francesco only when there are due leads and group them by contact date. Ask who replied. Mark each outcome with `answer <id> replied` or `answer <id> no_reply`. For confirmed no-reply leads, run `cleanup <id>`; it removes only the registered preview deployment. Never delete for a missing or ambiguous answer. Keep local files and the register.

Read `WORKFLOW.md` for the full state policy. No Instagram Computer Use, automated outreach, production deploy or deletion of a whole Vercel project is part of this skill.
