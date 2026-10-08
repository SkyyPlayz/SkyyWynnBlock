// Attachment test only: open vanilla Player.blockymodel (READ-ONLY), import the 4 pieces with the plugin's own
// "Import Attachment" action, take viewport screenshots (local work/ only). Polls instead of one long evaluate.
// Usage: node bb_attach_shots.js <models_dir> <work_out_dir> <player.blockymodel>
const WebSocket = require('/workspace/bbcdp/node_modules/ws');
const fs = require('fs'), path = require('path');
const [MODELS, WORK, PLAYER] = process.argv.slice(2);
const PIECES = ['Head', 'Chest', 'Hands', 'Legs'];
let ws, seq = 0; const pending = {};
const ev = expr => new Promise(res => { const id = ++seq; pending[id] = res;
  ws.send(JSON.stringify({id, method: 'Runtime.evaluate', params: {expression: expr, awaitPromise: false, returnByValue: true}})); });
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const list = await (await fetch('http://127.0.0.1:9333/json')).json();
  ws = new WebSocket(list.find(p => p.type === 'page').webSocketDebuggerUrl, {maxPayload: 512 * 1024 * 1024});
  ws.on('message', m => { const d = JSON.parse(m); if (pending[d.id]) { pending[d.id](d.result); delete pending[d.id]; } });
  ws.on('close', () => console.error('ws closed'));
  await new Promise(r => ws.on('open', r));
  const files = PIECES.map(p => ({name: p + '.blockymodel', path: path.join(MODELS, p + '.blockymodel'),
                                  content: fs.readFileSync(path.join(MODELS, p + '.blockymodel'), 'utf8')}));
  await ev(`window.__att = null; window.__attStage = 'start'; (async () => { try {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    for (const p of ModelProject.all.slice()) { try { await p.close(true); } catch(e){} }
    await sleep(500); window.__attStage = 'opening player';
    await new Promise(res => Blockbench.read([${JSON.stringify(PLAYER)}], {readtype: 'text'}, fl => { loadModelFile(fl[0]); res(); }));
    for (let i = 0; i < 60 && !(Texture.all.length && Texture.all.every(t => t.loaded)); i++) await sleep(500);
    const before = {groups: Group.all.length, cubes: Cube.all.length};
    window.__attStage = 'importing';
    const files = ${JSON.stringify(files)};
    const orig = Filesystem.importFile; Filesystem.importFile = (o, cb) => cb(files);
    try { BarItems.import_as_hytale_attachment.click(); } finally { Filesystem.importFile = orig; }
    for (let i = 0; i < 120 && !(Texture.all.length >= 5 && Texture.all.every(t => t.loaded)); i++) await sleep(500);
    await sleep(1500); Canvas.updateAll(); window.__attStage = 'shots';
    const P = Preview.selected; P.setProjectionMode(false); P.camPers.fov = 30; P.camPers.updateProjectionMatrix();
    try { scene.remove(Canvas.grid); } catch(e) {}
    const shots = {}; const T = [0, 60, 0], d = 280;
    const views = {att_front: [0, 60 + d*0.1, d], att_left: [d, 60 + d*0.06, 0], att_back: [0, 60 + d*0.1, -d], att_34: [d*0.55, 60 + d*0.25, d*0.8]};
    for (const k in views) { P.camera.position.set(...views[k]); P.controls.target.set(...T); P.controls.update();
      await sleep(1200); P.render(); await sleep(200); P.render();
      const url = await new Promise(res => P.screenshot({crop: false}, res)); shots[k] = url.replace(/^data:image\\/png;base64,/, ''); }
    window.__att = JSON.stringify({before, after: {groups: Group.all.length, cubes: Cube.all.length,
      textures: Texture.all.map(t => t.name + ' ' + t.width + 'x' + t.height + (t.loaded ? '' : ' NOT LOADED'))},
      collections: Collection.all.map(c => ({name: c.name, children: c.getChildren().length})), shots});
  } catch (e) { window.__att = JSON.stringify({error: String(e && e.stack || e)}); } })(); true`);
  for (let i = 0; i < 200; i++) {
    await sleep(4000);
    const r = await ev(`window.__att ? window.__att : ('STAGE:' + window.__attStage)`);
    const v = r && r.result && r.result.value;
    if (typeof v === 'string' && !v.startsWith('STAGE:')) {
      const o = JSON.parse(v);
      if (o.shots) for (const k in o.shots) fs.writeFileSync(path.join(WORK, k + '.png'), Buffer.from(o.shots[k], 'base64'));
      delete o.shots; fs.writeFileSync(path.join(WORK, 'bb_attach.json'), JSON.stringify(o, null, 1));
      console.log(JSON.stringify(o)); break;
    } else if (i % 5 === 0) console.log(v);
  }
  ws.close(); process.exit(0);
})().catch(e => { console.error('FAILED', e.message); process.exit(1); });
