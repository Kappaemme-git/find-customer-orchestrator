param(
    [switch]$SkipChecks
)

$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillSource = Join-Path $project "skills"
$skillTarget = Join-Path $env:USERPROFILE ".codex\skills"
$names = @("first-customer-finder", "local-client-prospector", "find-customer-orchestrator")

New-Item -ItemType Directory -Force -Path $skillTarget | Out-Null
foreach ($name in $names) {
    $source = Join-Path $skillSource $name
    $target = Join-Path $skillTarget $name
    if (-not (Test-Path (Join-Path $source "SKILL.md"))) {
        throw "Skill mancante nel pacchetto: $name"
    }
    if (Test-Path $target) {
        Write-Host "Gia presente, non sovrascrivo: $target"
        continue
    }
    Copy-Item -Path $source -Destination $target -Recurse
    Write-Host "Installata: $target"
}

if (-not $SkipChecks) {
    foreach ($command in @("git", "node", "py", "claude", "vercel.cmd")) {
        if (Get-Command $command -ErrorAction SilentlyContinue) {
            Write-Host "OK: $command"
        } else {
            Write-Warning "Non trovato nel PATH: $command"
        }
    }
}

Push-Location $project
try {
    py scripts\workflow.py init
} finally {
    Pop-Location
}

Write-Host "Apri questa cartella come progetto in Codex: $project"
Write-Host "Riavvia ChatGPT/Codex per rendere visibili le skill installate."
