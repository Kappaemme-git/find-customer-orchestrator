# Find Customer Orchestrator

Skill Codex e registro locale per cercare attività senza sito ufficiale, preparare un brief verificato per Claude Code `/design`, creare una demo e pubblicare una preview Vercel. Francesco sceglie il cliente e invia personalmente il messaggio. Il registro controlla i follow-up dopo quattro giorni.

## Installazione su Windows

Servono Node.js, Python, Claude Code, Vercel CLI e Codex già configurati. In PowerShell:

```powershell
npx.cmd --yes find-customer-orchestrator@latest install
```

Il comando crea `%USERPROFILE%\Documents\FindCustomerAutomation` e installa le tre skill in `%USERPROFILE%\.codex\skills`. Non sovrascrive cartelle già esistenti. Aprire la cartella del progetto in Codex e riavviare l'app per caricare le skill.

Per aggiornare un'installazione esistente senza perdere registro, demo, template o skill di ricerca:

```powershell
npx.cmd --yes find-customer-orchestrator@latest upgrade
```

Il comando aggiorna solo la skill orchestratrice e le istruzioni del progetto, salvando una copia dei file precedenti. Se il progetto è in un'altra cartella, aggiungere `--project "C:\percorso\cartella"`.

```powershell
cd "$env:USERPROFILE\Documents\FindCustomerAutomation"
py scripts\workflow.py list
```

La ricerca usa `local-client-prospector` e, quando utile, `first-customer-finder`. La skill `find-customer-orchestrator` coordina brief, Claude `/design`, verifica e preview. [WORKFLOW.md](WORKFLOW.md) descrive le regole operative. Il comando `/design` va provato nella CLI di Claude sul PC Windows prima di usarlo con un cliente reale; non è stato ancora verificato in quella configurazione.

Il pacchetto non invia messaggi Instagram, non effettua deploy di produzione e non elimina preview senza la conferma esplicita di mancata risposta.
