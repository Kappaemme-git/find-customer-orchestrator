# Find Customer: flusso operativo

Il PC Windows esegue Codex, Claude Code e Vercel CLI. Francesco può controllare Codex dal telefono con Remote. Computer Use e invio automatico dei messaggi non fanno parte del flusso.

## Ricerca e demo

1. Usare `local-client-prospector` per trovare attività senza sito ufficiale e `first-customer-finder` per segnali pubblici di bisogno quando applicabili. Includere solo candidati per cui la verifica aggiornata non trovi un sito autonomo; escludere i casi incerti.
2. Francesco sceglie il candidato. Codex prepara un brief con fonti e dati verificati, colori, logo e foto disponibili. Ogni asset ha fonte e permesso d'uso. Le foto social possono guidare il design ma non vengono automaticamente ripubblicate.
   Da questa scelta, Codex procede con lettura dei file, mockup, implementazione, correzioni, apertura della preview, test e deploy preview senza chiedere un permesso conversazionale per ciascuna azione. Può chiedere a Francesco quale artboard scegliere se non riesce a consultare il canvas.
3. Codex invoca Claude Code dalla CLI sul PC Windows con `--permission-mode auto` e il comando integrato `/design`. Questo produce artboard; Codex sceglie quello più adatto, o chiede a Francesco se non riesce a consultare il canvas. Claude implementa l'artboard scelto in una cartella dedicata.
4. Codex verifica il risultato e pubblica una preview tramite la CLI di Vercel. Registrare cartella locale, URL del canvas, artboard scelto, URL della preview e account.
5. Francesco invia manualmente il messaggio al candidato e conferma a Codex la data dell'invio. Il timer dei quattro giorni parte dall'invio del messaggio, non dalla creazione del sito.

L'uso automatico di `/design` va verificato con un'attività fittizia prima di far partire una demo reale. Non sostituire silenziosamente `/design` con il plugin Frontend Design o con un prompt generico.

Le approvazioni tecniche di Codex e Claude sono separate dalle scelte conversazionali. Prima di avviare la fase di sito su Windows, usare per quel task Codex `Full access` se si vogliono evitare richieste di autorizzazione Codex; `Approva per me` può comunque fermarsi. Claude va avviato con `--permission-mode auto` per ridurre i suoi prompt. Nessuna di queste modalità garantisce che un blocco di sicurezza o una richiesta esplicita di un servizio esterno venga approvato; in quel caso Codex deve mostrare il blocco preciso invece di attendere indefinitamente.

## Controllo dopo quattro giorni

- Una verifica giornaliera raggruppa tutti i candidati contattati nello stesso giorno il cui messaggio è stato inviato almeno quattro giorni prima. Codex chiede a Francesco quali hanno risposto.
- Se Francesco conferma che un candidato ha risposto, mantenere la preview e segnare `risposto` nel registro.
- Se Francesco conferma che non ha risposto, eliminare il relativo deployment di preview da Vercel, segnare `nessuna risposta / preview rimossa` e conservare nel registro URL, data e motivo della rimozione. Conservare i file locali per poter ripristinare la demo.
- Se Francesco non fornisce ancora uno stato, non eliminare la preview; lasciare il candidato `in attesa di verifica` e riproporlo al controllo successivo.
- Nessun messaggio Instagram viene inviato automaticamente.

## Registro persistente minimo

Per ogni candidato conservare: identificatore stabile, nome, luogo, fonti della verifica del sito assente, stato del lead, data di scelta, brief, fonti di colori/logo/foto e relativi permessi, cartella locale, URL del canvas, artboard scelto, deployment Vercel, account, data di invio del messaggio, lingua del messaggio, data prevista del controllo, esito della risposta e data di eventuale rimozione della preview.
