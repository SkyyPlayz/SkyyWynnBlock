// Blockbench 5.2.1 + Hytale Models plugin check for the SkyWynn pets, driven over CDP (port 9333).
// Per pet: open the .blockymodel (texture + ../Animations auto-load), read format / groups / cubes / textures / Validator,
// list the loaded animations, screenshot the rest pose, save source/<Pet>.bbmodel. Only projects this script opens are closed.
// Usage: node bb_validate_pets.js <art_dir> <work_dir> [Pet ...]
const WebSocket = require('/workspace/bbcdp/node_modules/ws');
const fs = require('fs'), path = require('path');
const [ART, WORK, ...ONLY] = process.argv.slice(2);
const PETS = ONLY.length ? ONLY : fs.readdirSync(path.join(ART, 'Common/NPC/SkyyPets')).sort();
let ws, seq = 0; const pending = {};
function ev(expr) { return new Promise((res) => { const id = ++seq; pending[id] = res;
  ws.send(JSON.stringify({id, method: 'Runtime.evaluate', params: {expression: expr, awaitPromise: true, returnByValue: true}})); }); }
async function run(expr) { const r = await ev(expr); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 1500)); return r.result.value; }
const PRE = `const sleep = ms => new Promise(r => setTimeout(r, ms));
async function openFile(p){ await new Promise(res => Blockbench.read([p], {readtype: 'text'}, files => { loadModelFile(files[0]); res(); })); await sleep(1500); }
function checks(){ Validator.validate(); return Validator.checks.map(c => ({id: c.id, errors: c.errors.map(e=>e.message), warnings: c.warnings.map(e=>e.message)})).filter(c => c.errors.length || c.warnings.length); }
async function shot(name, pos, target){ const P = Preview.selected; P.setProjectionMode(false); P.camPers.fov = 30; P.camPers.updateProjectionMatrix();
  P.camera.position.set(...pos); P.controls.target.set(...target); P.controls.update(); Canvas.updateAll(); await sleep(1000); P.render(); await sleep(300); P.render();
  const url = await new Promise(res => P.screenshot({crop: false}, res)); window.__shots[name] = url.replace(/^data:image\\/png;base64,/, ''); }
`;
(async () => {
  const list = await (await fetch('http://127.0.0.1:9333/json')).json();
  ws = new WebSocket(list.find(p => p.type === 'page').webSocketDebuggerUrl, {maxPayload: 512 * 1024 * 1024});
  ws.on('message', m => { const d = JSON.parse(m); if (pending[d.id]) { pending[d.id](d.result); delete pending[d.id]; } });
  await new Promise(r => ws.on('open', r));
  await run(`window.__errs = []; if (!window.__errHooked) { window.__errHooked = true; const o = console.error; console.error = function(...a){ window.__errs.push(a.map(String).join(' ').slice(0,300)); o.apply(console, a); }; } true`);
  const report = {};
  fs.mkdirSync(path.join(ART, 'source'), {recursive: true}); fs.mkdirSync(path.join(WORK, 'bb'), {recursive: true});
  for (const pet of PETS) {
    const file = path.join(ART, 'Common/NPC/SkyyPets', pet, 'Models', pet + '.blockymodel');
    const out = JSON.parse(await run(`(async () => { ${PRE}
      window.__shots = {}; window.__errs.length = 0;
      await openFile(${JSON.stringify(file)});
      const proj = Project;
      Modes.options.edit.select(); await sleep(300);
      const info = {format: Format.id, groups: Group.all.length, cubes: Cube.all.length,
        textures: Texture.all.map(t => ({name: t.name, w: t.width, h: t.height, error: t.error||0})), checks: checks()};
      let bb = 0; const box = new THREE.Box3(); Cube.all.forEach(c => { if (c.mesh) box.expandByObject(c.mesh); });
      const c = box.getCenter(new THREE.Vector3()), sz = box.getSize(new THREE.Vector3()); const r = Math.max(sz.x, sz.y, sz.z);
      info.size = sz.toArray().map(v => +v.toFixed(1));
      await shot('rest', [c.x + r * 1.3, c.y + r * 0.6, c.z + r * 1.9], [c.x, c.y, c.z]);
      Modes.options.animate.select(); await sleep(2000);
      info.animations = Animation.all.map(a => ({name: a.name, length: a.length, loop: a.loop,
        animators: Object.values(a.animators).filter(b => b.keyframes.length).length,
        missingGroups: Object.values(a.animators).filter(b => b.keyframes.length && !b.group).map(b => b.name)}));
      const W = Animation.all.find(a => /Walk/.test(a.name));
      if (W) { W.select(); Timeline.setTime(W.length * 0.25); Animator.preview(); await shot('walk', [c.x + r * 1.3, c.y + r * 0.6, c.z + r * 1.9], [c.x, c.y, c.z]); }
      Modes.options.edit.select(); await sleep(300);
      for (const t of Texture.all) { t.path = ''; t.saved = false; }
      for (const a of Animation.all) { a.path = ''; a.saved = false; }
      const bbm = Codecs.project.compile({raw: false});
      info.errors = window.__errs.slice();
      try { await proj.close(true); } catch (e) {}
      return JSON.stringify({info, bb: bbm, shots: window.__shots});
    })()`));
    fs.writeFileSync(path.join(ART, 'source', pet + '.bbmodel'), out.bb);
    for (const k in out.shots) fs.writeFileSync(path.join(WORK, 'bb', pet + '_' + k + '.png'), Buffer.from(out.shots[k], 'base64'));
    report[pet] = out.info;
    console.log(pet, JSON.stringify({g: out.info.groups, c: out.info.cubes, tex: out.info.textures, checks: out.info.checks, anims: out.info.animations.map(a => a.name + ':' + a.length + (a.missingGroups.length ? ' MISSING ' + a.missingGroups : '')), errs: out.info.errors.length, size: out.info.size}));
  }
  fs.writeFileSync(path.join(WORK, 'bb', 'bb_report.json'), JSON.stringify(report, null, 1));
  ws.close();
})().catch(e => { console.error('FAILED', e.message); process.exit(1); });
