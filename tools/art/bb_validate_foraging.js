// Blockbench (Hytale Models plugin) validation for a SkyWynn Foraging armor set, driven over CDP (port 9333).
//  1) opens each <Piece>.blockymodel as its own project: format, groups/cubes, textures, Validator results,
//     re-compiles it with the plugin codec (for a round-trip diff) and saves source/<Piece>.bbmodel (textures embedded)
//  2) opens the vanilla Player.blockymodel READ-ONLY and imports the 4 pieces through the plugin's own
//     "Import Attachment" action; screenshots go to work/bb/ (local only: they show the vanilla player)
// Usage: node bb_validate.js <models_dir> <source_out_dir> <work_out_dir> <player.blockymodel>
const WebSocket = require('/workspace/bbcdp/node_modules/ws');
const fs = require('fs'), path = require('path');
const [MODELS, SRC, WORK, PLAYER] = process.argv.slice(2);
const PIECES = ['Head', 'Chest', 'Hands', 'Legs'];
let ws, seq = 0; const pending = {};
function ev(expr) {
  return new Promise((res, rej) => {
    const id = ++seq; pending[id] = {res, rej};
    ws.send(JSON.stringify({id, method: 'Runtime.evaluate', params: {expression: expr, awaitPromise: true, returnByValue: true}}));
  });
}
async function run(expr) {
  const r = await ev(expr);
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 1500));
  return r.result.value;
}
const PRE = `const sleep = ms => new Promise(r => setTimeout(r, ms));
async function closeAll(){ for (const p of ModelProject.all.slice()) { try { await p.close(true); } catch(e){} } await sleep(300); }
async function openFile(p){ await new Promise(res => Blockbench.read([p], {readtype: 'text'}, files => { loadModelFile(files[0]); res(); })); await sleep(1500); }
function checks(){ Validator.validate(); return Validator.checks.map(c => ({id: c.id, errors: c.errors.map(e=>e.message), warnings: c.warnings.map(e=>e.message)})).filter(c => c.errors.length || c.warnings.length); }
async function shot(name, pos, target){ const P = Preview.selected; P.setProjectionMode(false); P.camPers.fov = 30; P.camPers.updateProjectionMatrix();
  P.camera.position.set(...pos); P.controls.target.set(...target); P.controls.update(); Canvas.updateAll(); await sleep(1500); P.render(); await sleep(300); P.render();
  const url = await new Promise(res => P.screenshot({crop: false}, res)); window.__shots[name] = url.replace(/^data:image\\/png;base64,/, ''); }
`;
(async () => {
  const list = await (await fetch('http://127.0.0.1:9333/json')).json();
  ws = new WebSocket(list.find(p => p.type === 'page').webSocketDebuggerUrl, {maxPayload: 512 * 1024 * 1024});
  ws.on('message', m => { const d = JSON.parse(m); if (pending[d.id]) { pending[d.id].res(d.result); delete pending[d.id]; } });
  await new Promise(r => ws.on('open', r));
  const report = {pieces: {}, attachment: null};
  await run(`window.__errs = []; if (!window.__errHooked) { window.__errHooked = true; const o = console.error; console.error = function(...a){ window.__errs.push(a.map(String).join(' ').slice(0,300)); o.apply(console, a); }; } true`);
  for (const p of (process.env.ATTACH_ONLY ? [] : PIECES)) {
    const file = path.join(MODELS, p + '.blockymodel');
    const out = JSON.parse(await run(`(async () => { ${PRE}
      window.__shots = {}; window.__errs.length = 0;
      await closeAll(); await openFile(${JSON.stringify(file)});
      Modes.options.edit.select(); await sleep(300);
      const info = {format: Format.id, name: Project.name, groups: Group.all.length, cubes: Cube.all.length,
        pieceGroups: Group.all.filter(g => g.is_piece).map(g => g.name),
        textures: Texture.all.map(t => ({name: t.name, w: t.width, h: t.height, uvw: t.uv_width, uvh: t.uv_height, error: t.error||0})),
        checks: checks()};
      let bm = Codecs.blockymodel.compile(); if (typeof bm !== 'string') bm = JSON.stringify(bm);
      for (const t of Texture.all) { t.path = ''; t.saved = false; }
      const bb = Codecs.project.compile({raw: false});
      const T = [0, 0, 0];
      await shot('${p}_bb', [60, 40, 90], T);
      info.errors = window.__errs.slice();
      return JSON.stringify({info, bm, bb, shots: window.__shots});
    })()`));
    fs.writeFileSync(path.join(SRC, p + '.bbmodel'), out.bb);
    fs.writeFileSync(path.join(WORK, p + '_bb_roundtrip.blockymodel'), out.bm);
    for (const k in out.shots) fs.writeFileSync(path.join(WORK, k + '.png'), Buffer.from(out.shots[k], 'base64'));
    report.pieces[p] = out.info;
  }
  if (process.env.SKIP_ATTACH) { fs.writeFileSync(path.join(WORK, 'bb_report.json'), JSON.stringify(report, null, 1)); console.log(JSON.stringify(report, null, 1)); ws.close(); process.exit(0); }
  // attachment test on the player
  const files = PIECES.map(p => ({name: p + '.blockymodel', path: path.join(MODELS, p + '.blockymodel'),
                                  content: fs.readFileSync(path.join(MODELS, p + '.blockymodel'), 'utf8')}));
  const att = JSON.parse(await run(`(async () => { ${PRE}
    window.__shots = {}; window.__errs.length = 0;
    await closeAll(); await openFile(${JSON.stringify(PLAYER)});
    const before = {groups: Group.all.length, cubes: Cube.all.length, textures: Texture.all.length};
    const files = ${JSON.stringify(files)};
    const orig = Filesystem.importFile;
    Filesystem.importFile = (opts, cb) => cb(files);
    try { BarItems.import_as_hytale_attachment.click(); } finally { Filesystem.importFile = orig; }
    await sleep(2500); Canvas.updateAll();
    const cols = Collection.all.map(c => ({name: c.name, children: c.getChildren().length, texture: (Texture.all.find(t => t.uuid == c.texture)||{}).name || null}));
    const attGroups = Group.all.filter(g => /^(Head|Chest|Hands|Legs):/.test(g.name)).map(g => g.name + ' -> parent ' + (g.parent && g.parent.name));
    const piecesOnBones = Group.all.filter(g => g.is_piece && Collection.all.some(c => c.getChildren().includes(g))).map(g => g.name);
    const T = [0, 60, 0], d = 260;
    await shot('att_front', [0, 60 + d*0.12, d], T);
    await shot('att_left', [d, 60 + d*0.08, 0], T);
    await shot('att_back', [0, 60 + d*0.12, -d], T);
    await shot('att_34', [d*0.55, 60 + d*0.25, d*0.8], T);
    return JSON.stringify({before, after: {groups: Group.all.length, cubes: Cube.all.length, textures: Texture.all.map(t => t.name + ' ' + t.width + 'x' + t.height)},
      collections: cols, attachedGroups: attGroups, errors: window.__errs.slice(), checks: checks(), shots: window.__shots});
  })()`));
  for (const k in att.shots) fs.writeFileSync(path.join(WORK, k + '.png'), Buffer.from(att.shots[k], 'base64'));
  delete att.shots; report.attachment = att;
  await run(`(async () => { for (const p of ModelProject.all.slice()) { try { await p.close(true); } catch(e){} } return true; })()`);
  if (process.env.ATTACH_ONLY) { const old = JSON.parse(fs.readFileSync(path.join(WORK, 'bb_report.json'), 'utf8')); report.pieces = old.pieces; }
  fs.writeFileSync(path.join(WORK, 'bb_report.json'), JSON.stringify(report, null, 1));
  console.log(JSON.stringify(report, null, 1));
  ws.close();
})().catch(e => { console.error('FAILED', e.message); process.exit(1); });
