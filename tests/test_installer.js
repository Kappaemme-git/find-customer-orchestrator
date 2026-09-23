const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const test = require('node:test');

const bin = path.resolve(__dirname, '..', 'bin', 'find-customer-orchestrator.js');

test('upgrade refreshes the orchestrator without touching leads, demos, or research skills', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'find-customer-upgrade-'));
  const project = path.join(root, 'project');
  const skills = path.join(root, 'codex-skills');
  const run = (command) => spawnSync(process.execPath, [bin, command, '--project', project], {
    env: { ...process.env, FIND_CUSTOMER_SKILLS_DIR: skills },
    encoding: 'utf8',
  });
  try {
    assert.equal(run('install').status, 0);
    const globalSkill = path.join(skills, 'find-customer-orchestrator', 'SKILL.md');
    const researchSkill = path.join(skills, 'local-client-prospector', 'SKILL.md');
    const registry = path.join(project, 'state', 'leads.sqlite3');
    const demo = path.join(project, 'demos', 'lead-1', 'index.html');
    fs.mkdirSync(path.dirname(registry), { recursive: true });
    fs.mkdirSync(path.dirname(demo), { recursive: true });
    fs.writeFileSync(registry, 'existing-registry');
    fs.writeFileSync(demo, 'existing-demo');
    fs.writeFileSync(globalSkill, 'old-orchestrator');
    fs.writeFileSync(researchSkill, 'custom-research-skill');

    const result = run('upgrade');
    assert.equal(result.status, 0, result.stderr);
    assert.match(fs.readFileSync(globalSkill, 'utf8'), /permission-mode auto/);
    assert.equal(fs.readFileSync(researchSkill, 'utf8'), 'custom-research-skill');
    assert.equal(fs.readFileSync(registry, 'utf8'), 'existing-registry');
    assert.equal(fs.readFileSync(demo, 'utf8'), 'existing-demo');
    const backups = fs.readdirSync(path.dirname(globalSkill)).filter((name) => name.startsWith('SKILL.md.backup-'));
    assert.equal(backups.length, 1);
    assert.equal(fs.readFileSync(path.join(path.dirname(globalSkill), backups[0]), 'utf8'), 'old-orchestrator');
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
