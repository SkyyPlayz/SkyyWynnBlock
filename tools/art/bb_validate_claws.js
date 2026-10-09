// Blockbench 5.2.1 + Hytale Models plugin check for the Monk claws, driven over CDP (port 9333).
// For each tier: open the .blockymodel as its own project (texture auto-loads), read format / groups / cubes / textures /
// Validator results, re-compile with the plugin codec (round-trip file) and save source/<name>.bbmodel. For the first tier also
// enter Animate mode (the plugin auto-loads ../Animations/*/*.blockyanim) and screenshot the rest pose + a mid-extend frame.
// Only the projects this script opens are closed. Usage: node bb_validate_claws.js <art_dir> <work_dir>
const WebSocket = require('/workspace/bbcdp/node_modules/ws');
const fs = require('fs'), path = require('path');
const [ART, WORK] = process.argv.slice(2);
const TIERS = ['Copper', 'Iron', 'Thorium', 'Cobalt', 'Adamantite', 'Mithril', 'Onyxium'];
let ws, seq = 0; const pending = {};
function ev(expr) { return new Promise((res) => { const id = ++seq; pending[id] = res;
  ws.send(JSON.stringify({id, method: 'Runtime.evaluate', params: {expression: expr, awaitPromise: true, returnByValue: true}})); }); }
async function run(expr) { const r = await ev(expr); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 1500)); return r.result.value; }
const PRE = `const sleep = ms => new Promise(r => setTimeout(r, ms));
async function openFile(p){ await new Promise(res => Blockbench.read([p], {readtype: 'text'}, files => { loadModelFile(files[0]); res(); })); await sleep(1500); }
function checks(){ Validator.validate(); return Validator.checks.map(c => ({id: c.id, errors: c.errors.map(e=>e.message), warnings: c.warnings.map(e=>e.message)})).filter(c => c.errors.length || c.warnings.length); }
async function shot(name, pos, target){ const P = Preview.selected; P.setProjectionMode(false); P.camPers.fov = 30; P.camPers.updateProjectionMatrix();
  P.camera.position.set(...pos); P.controls.target.set(...target); P.controls.update(); Canvas.updateAll(); await sleep(1200); P.render(); await sleep(300); P.render();
  const url = await new Promise(res => P.screenshot({crop: false}, res)); window.__shots[name] = url.replace(/^data:image\\/png;base64,/, ''); }
`;
(async () => {
  const list = await (await fetch('http://127.0.0.1:9333/json')).json();
  ws = new WebSocket(list.find(p => p.type === 'page').webSocketDebuggerUrl, {maxPayload: 512 * 1024 * 1024});
  ws.on('message', m => { const d = JSON.parse(m); if (pending[d.id]) { pending[d.id](d.result); delete pending[d.id]; } });
  await new Promise(r => ws.on('open', r));
  await run(`window.__errs = []; if (!window.__errHooked) { window.__errHooked = true; const o = console.error; console.error = function(...a){ window.__errs.push(a.map(String).join(' ').slice(0,300)); o.apply(console, a); }; } true`);
  const report = {};
  for (const [i, t] of TIERS.entries()) {
    const name = 'SkyyArmory_Claws_' + t;
    const file = path.join(ART, 'Common/Items/Weapons/Fist', name + '.blockymodel');
    const out = JSON.parse(await run(`(async () => { ${PRE}
      window.__shots = {}; window.__errs.length = 0;
      await openFile(${JSON.stringify(file)});
      const proj = Project;
      Modes.options.edit.select(); await sleep(300);
      const info = {format: Format.id, name: Project.name, groups: Group.all.length, cubes: Cube.all.length,
        pieceGroups: Group.all.filter(g => g.is_piece).map(g => g.name),
        textures: Texture.all.map(t => ({name: t.name, w: t.width, h: t.height, uvw: t.uv_width, uvh: t.uv_height, error: t.error||0})),
        checks: checks()};
      let bm = Codecs.blockymodel.compile(); if (typeof bm !== 'string') bm = JSON.stringify(bm);
      if (${i === 0}) {
        await shot('rest_34', [-70, 55, 80], [0, 0, 8]);
        Modes.options.animate.select(); await sleep(2500);
        info.animations = Animation.all.map(a => ({name: a.name, length: a.length, loop: a.loop,
          animators: Object.values(a.animators).filter(b => b.keyframes.length).length,
          missingGroups: Object.values(a.animators).filter(b => b.keyframes.length && !b.group).map(b => b.name)}));
        const A = Animation.all[0];
        if (A) { for (const [k, tm] of [['anim_010', 0.10], ['anim_018', 0.18], ['anim_end', 0.40]]) {
          A.select(); Timeline.setTime(tm); Animator.preview(); await shot(k, [-70, 55, 80], [0, 0, 8]); } }
        Modes.options.edit.select(); await sleep(300);
      }
      for (const t of Texture.all) { t.path = ''; t.saved = false; }
      for (const a of Animation.all) { a.path = ''; a.saved = false; }
      const bb = Codecs.project.compile({raw: false});
      info.errors = window.__errs.slice();
      try { await proj.close(true); } catch (e) {}
      return JSON.stringify({info, bm, bb, shots: window.__shots});
    })()`));
    fs.writeFileSync(path.join(ART, 'source', name + '.bbmodel'), out.bb);
    fs.writeFileSync(path.join(WORK, name + '_roundtrip.blockymodel'), out.bm);
    for (const k in out.shots) fs.writeFileSync(path.join(WORK, k + '.png'), Buffer.from(out.shots[k], 'base64'));
    report[t] = out.info;
    console.log(t, JSON.stringify(out.info).slice(0, 600));
  }
  fs.writeFileSync(path.join(WORK, 'bb_report.json'), JSON.stringify(report, null, 1));
  ws.close();
})().catch(e => { console.error('FAILED', e.message); process.exit(1); });
