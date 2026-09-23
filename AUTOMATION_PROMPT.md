# Controllo giornaliero da creare su Windows

Quando il progetto e il registro sono sul PC Windows, chiedere a Codex in quel progetto di creare un'automazione giornaliera alle 10:00, fuso Europe/Rome, con questo prompt:

> Controlla il registro di questo progetto con `py scripts/workflow.py due`. Se l'elenco è vuoto, resta in silenzio. Se ci sono contatti scaduti, raggruppali per data di invio e chiedi a Francesco quali hanno risposto, mostrando ID, nome e link della demo. Non dedurre l'esito dal silenzio. Quando Francesco conferma un ID come `replied`, registra `answer <id> replied` e conserva la preview. Quando conferma `no_reply`, registra `answer <id> no_reply` e usa `cleanup <id>` per rimuovere solo il deployment preview registrato. Se mancano informazioni o il comando fallisce, conserva la preview e segnala il problema. Non inviare messaggi a terzi.

L'automazione non è attiva finché non viene creata sul Windows. Il PC deve essere acceso e online per eseguirla.
