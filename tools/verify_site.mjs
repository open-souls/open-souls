// 本地发布门禁：在不开浏览器的情况下，真正执行 docs/index.html 里的 <script>，
// 捕获 build()/apply() 这类运行时错误（例如作用域问题导致的 ReferenceError）。
// 这正是 curl / python 检查抓不到、只有浏览器才会暴露的那类 bug。
//
// 用法: node tools/verify_site.mjs   (exit 0 = 通过, 非0 = 不要发布)
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const html = readFileSync(join(ROOT, 'docs/index.html'), 'utf8');
const chronicle = readFileSync(join(ROOT, 'docs/chronicle.json'), 'utf8');
const rows = JSON.parse(chronicle); // 顺带校验 JSON 合法

const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
if (!script) { console.error('✗ 找不到 index.html 里的 <script>'); process.exit(1); }

// 极简 DOM stub —— 只够让页面脚本跑完、暴露异常
const els = {};
const mkEl = () => ({
  _html: '',
  get innerHTML() { return this._html; },
  set innerHTML(v) { this._html = String(v); },
  textContent: '', href: '',
  classList: { add(){}, remove(){}, toggle(){}, contains(){ return false; } },
  dataset: {},
  children: [],
  querySelector: () => mkEl(),
  querySelectorAll: () => [],
  closest: () => null,
  set onclick(_) {}, set oninput(_) {},
});
['toc','seg','who','q','count','stat','resume'].forEach(id => els[id] = mkEl());

let failed = null;
const sandbox = {
  document: {
    getElementById: id => els[id] || mkEl(),
    querySelector: () => mkEl(),
    querySelectorAll: () => [],
  },
  localStorage: { getItem: () => null, setItem: () => {} },
  fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve(rows) }),
  JSON, Math, Set, Array, Object, Date, console,
  setTimeout, // safety
};
sandbox.window = sandbox;

try {
  vm.createContext(sandbox);
  vm.runInContext(script, sandbox, { timeout: 5000 });
} catch (e) {
  failed = '脚本同步执行抛错: ' + e.message;
}

// 等 fetch().then 链跑完
await new Promise(r => setTimeout(r, 200));

const toc = els.toc.innerHTML;
const checks = [
  [rows.length > 0, `chronicle.json 有 ${rows.length} 条`],
  [!failed, failed || '脚本执行无异常'],
  [!toc.includes('目录加载失败'), '目录未落入错误态 (build/apply 没抛错)'],
  [toc.includes('class="season"'), '目录成功渲染出分卷'],
  [els.stat.textContent.includes('回'), `首页进度: "${els.stat.textContent}"`],
];

let ok = true;
for (const [pass, msg] of checks) {
  console.log((pass ? '✓ ' : '✗ ') + msg);
  if (!pass) ok = false;
}
console.log(ok ? '\n通过：可以发布。' : '\n失败：先修好再发布，别 push。');
process.exit(ok ? 0 : 1);
