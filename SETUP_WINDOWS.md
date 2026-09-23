# Installazione sul PC Windows

Installazione più semplice dal registro npm pubblico (quando la versione è stata pubblicata):

```powershell
npx --yes find-customer-orchestrator@latest install
```

Questo comando crea la cartella `Documents\FindCustomerAutomation` e copia le tre skill in Codex. Se la cartella del progetto o una delle skill esiste già, si ferma senza sovrascrivere. Il pacchetto non contiene login o token.

## Alternativa ZIP

Se npm non è disponibile, il pacchetto ZIP si può trasferire dal Mac con una chiavetta o un servizio di sincronizzazione scelto da Francesco.

1. Copiare `FindCustomerAutomation-Windows.zip` nella cartella Download del Windows. Aprire PowerShell e incollare questi comandi, uno alla volta:

   ```powershell
   $zip = Join-Path $env:USERPROFILE 'Downloads\FindCustomerAutomation-Windows.zip'
   $project = Join-Path $env:USERPROFILE 'Documents\FindCustomerAutomation'
   Expand-Archive -LiteralPath $zip -DestinationPath $project -Force
   Set-Location $project
   powershell -NoProfile -ExecutionPolicy Bypass -File .\install-windows.ps1
   ```

   Se il file ZIP è stato copiato altrove, sostituire solo il percorso della variabile `$zip`. La cartella estratta deve contenere `install-windows.ps1`, `skills`, `scripts` e `templates`. Lo script copia le tre skill in `%USERPROFILE%\.codex\skills` senza sovrascrivere skill già presenti e inizializza il registro in `state\leads.sqlite3`. Il bypass della policy vale solo per il processo di installazione.
2. Chiudere e riaprire l'app ChatGPT/Codex su Windows. Aggiungere la cartella `Documents\FindCustomerAutomation` come progetto locale.
3. Nel nuovo progetto chiedere a Codex di verificare la presenza delle tre skill e provare `py scripts\workflow.py list`.
4. Fare il test con un'attività fittizia. In particolare verificare il comando integrato `/design` di Claude Code dalla CLI: deve produrre un canvas consultabile, poi file del sito in `demos\<id>`. La prova già avviata Claude → Vercel non prova necessariamente questo passaggio.
5. Solo dopo il test, chiedere a Codex di creare l'automazione descritta in `AUTOMATION_PROMPT.md` sul Windows.

Se una delle due skill di ricerca è già presente sul Windows, lo script la lascia intatta. Prima di sostituirla, confrontare la versione e conservarne una copia.

## Limiti verificati

- `/design` è documentato come flusso interattivo che pubblica artboard e richiede una scelta prima dell'implementazione. La piena automazione della CLI va dimostrata sul Windows; il pacchetto non la dichiara già funzionante.
- Codex Remote controlla il task sul Windows; non trasferisce automaticamente i file delle skill dal Mac.
- Il registro, l'automazione e la rimozione delle preview funzionano solo quando il progetto è stato installato sul Windows e i comandi vengono eseguiti lì.
