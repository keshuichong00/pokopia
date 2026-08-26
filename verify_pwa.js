// PWA 配置合法性验证
const fs = require('fs');
const { execSync } = require('child_process');
let ok = true;

// 1. manifest.json
try {
  const m = JSON.parse(fs.readFileSync('manifest.json', 'utf-8'));
  const req = ['name', 'short_name', 'start_url', 'display', 'icons'];
  const miss = req.filter(k => !(k in m));
  console.log(miss.length === 0 ? '✓ manifest.json 字段齐全' : '✗ manifest 缺失: ' + miss.join(','));
  if (m.display !== 'standalone') { console.log('⚠ display 应为 standalone，当前: ' + m.display); }
  if (!m.icons.some(i => i.purpose === 'maskable')) { console.log('⚠ 缺少 maskable 图标（安卓自适应图标推荐）'); }
  if (miss.length) ok = false;
} catch (e) { console.log('✗ manifest.json 解析失败: ' + e.message); ok = false; }

// 2. sw.js 语法
try {
  execSync('node --check sw.js');
  console.log('✓ sw.js 语法正确');
} catch (e) { console.log('✗ sw.js 语法错误'); ok = false; }

// 3. index.html 关键标签
const h = fs.readFileSync('index.html', 'utf-8');
const checks = [
  ['manifest link', h.includes('rel="manifest"')],
  ['theme-color', h.includes('name="theme-color"')],
  ['apple-touch-icon', h.includes('rel="apple-touch-icon"')],
  ['viewport', h.includes('width=device-width')],
  ['sw 注册', h.includes("serviceWorker.register('sw.js')")],
  ['sw 协议保护', h.includes("location.protocol.startsWith('http')")],
];
for (const [name, pass] of checks) {
  console.log((pass ? '✓' : '✗') + ' index.html 含 ' + name);
  if (!pass) ok = false;
}

console.log('\n' + (ok ? '=== PWA 配置验证通过 ===' : '=== 存在问题，需修复 ==='));
process.exit(ok ? 0 : 1);
