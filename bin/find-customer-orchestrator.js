#!/usr/bin/env node

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const usage = 'Uso: npx find-customer-orchestrator <install|upgrade> [--project CARTELLA]';
const skillNames = ['first-customer-finder', 'local-client-prospector', 'find-customer-orchestrator'];
const projectFiles = ['AGENTS.md', 'AUTOMATION_PROMPT.md', 'WORKFLOW.md', 'SETUP_WINDOWS.md', 'install-windows.ps1'];
const projectFolders = ['scripts', 'skills', 'templates'];

function main(argv) {
  if (!argv.length || argv[0] === '--help' || argv[0] === '-h' || argv.some((arg) => arg === '--help' || arg === '-h')) {
    console.log(usage);
    return;
  }
  if (!['install', 'upgrade'].includes(argv[0])) {
    throw new Error(usage);
  }
  let project = path.join(os.homedir(), 'Documents', 'FindCustomerAutomation');
  for (let i = 1; i < argv.length; i += 1) {
    if (argv[i] === '--project' && argv[i + 1]) {
      project = path.resolve(argv[++i]);
    } else {
      throw new Error(`Argomento non riconosciuto: ${argv[i]}\n${usage}`);
    }
  }

  const packageRoot = path.resolve(__dirname, '..');
  const skillTarget = process.env.FIND_CUSTOMER_SKILLS_DIR || path.join(os.homedir(), '.codex', 'skills');
  if (argv[0] === 'upgrade') {
    const updates = [
      ['skills/find-customer-orchestrator/SKILL.md', path.join(project, 'skills', 'find-customer-orchestrator', 'SKILL.md')],
      ['skills/find-customer-orchestrator/SKILL.md', path.join(skillTarget, 'find-customer-orchestrator', 'SKILL.md')],
      ['WORKFLOW.md', path.join(project, 'WORKFLOW.md')],
      ['SETUP_WINDOWS.md', path.join(project, 'SETUP_WINDOWS.md')],
    ];
    if (!fs.existsSync(path.join(project, 'scripts', 'workflow.py'))) {
      throw new Error(`Progetto non riconosciuto: ${project}. Usa --project con la cartella corretta.`);
    }
    for (const [source, target] of updates) {
      if (!fs.existsSync(path.join(packageRoot, source)) || !fs.existsSync(target)) {
        throw new Error(`File necessario mancante: ${target}. Nessun file aggiornato.`);
      }
    }
    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    for (const [source, target] of updates) {
      fs.copyFileSync(target, `${target}.backup-${stamp}`);
      fs.copyFileSync(path.join(packageRoot, source), target);
    }
    console.log(`Skill orchestratrice e istruzioni aggiornate nel progetto: ${project}`);
    console.log('Registro, demo, template e skill di ricerca conservati. Riavvia Codex per caricare la skill aggiornata.');
    return;
  }
  const existingProject = fs.existsSync(project) && fs.readdirSync(project).length > 0;
  if (existingProject) {
    throw new Error(`La cartella esiste e non e vuota: ${project}. Nessun file sovrascritto.`);
  }
  const installedSkills = skillNames.filter((name) => fs.existsSync(path.join(skillTarget, name)));
  if (installedSkills.length) {
    throw new Error(`Skill gia presenti in Codex: ${installedSkills.join(', ')}. Nessun file sovrascritto.`);
  }

  fs.mkdirSync(project, { recursive: true });
  fs.mkdirSync(skillTarget, { recursive: true });
  for (const name of projectFiles) {
    fs.copyFileSync(path.join(packageRoot, name), path.join(project, name));
  }
  for (const name of projectFolders) {
    fs.cpSync(path.join(packageRoot, name), path.join(project, name), { recursive: true });
  }
  for (const name of skillNames) {
    fs.cpSync(path.join(packageRoot, 'skills', name), path.join(skillTarget, name), { recursive: true });
  }

  console.log(`Progetto installato: ${project}`);
  console.log(`Skill installate: ${skillNames.join(', ')}`);
  console.log('Riavvia Codex e apri la cartella del progetto. Poi verifica: py scripts\\workflow.py list');
  console.log('Prova /design di Claude con un lead fittizio prima del primo cliente reale.');
}

try {
  main(process.argv.slice(2));
} catch (error) {
  console.error(`Errore: ${error.message}`);
  process.exitCode = 1;
}
