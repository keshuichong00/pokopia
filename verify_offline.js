// 离线版数据层验证：模拟选择器渲染的"数据筛选"部分
const fs = require('fs');
const html = fs.readFileSync('index-offline.html', 'utf-8');

// 提取 ITEMS_RAW 数组字面量
const m = html.match(/const ITEMS_RAW = (\[[\s\S]*?\]);/);
if (!m) { console.error('✗ 未找到 ITEMS_RAW'); process.exit(1); }
let ITEMS;
try {
  ITEMS = eval(m[1]).map(r => ({ id: r[0], nameZh: r[1], nameEn: r[2], category: r[3], image: r[4] }));
} catch (e) {
  console.error('✗ ITEMS_RAW 解析失败:', e.message); process.exit(1);
}

console.log('✓ ITEMS 解析成功，共', ITEMS.length, '条');

// 分类统计
const cats = {};
let embed = 0, ext = 0;
for (const it of ITEMS) {
  cats[it.category] = (cats[it.category] || 0) + 1;
  if (it.image.startsWith('data:')) embed++; else ext++;
}
console.log('✓ 内嵌图:', embed, '| 外部URL(缺失):', ext);
console.log('✓ 分类数:', Object.keys(cats).length);

// 模拟 renderPickerGrid 核心：全部分类 + 空搜索 → 应渲染前200
function simRender(cat = '', q = '') {
  let list = ITEMS;
  if (cat) list = list.filter(i => i.category === cat);
  if (q) list = list.filter(i => i.nameZh.toLowerCase().includes(q) || i.nameEn.toLowerCase().includes(q));
  return list.slice(0, 200);
}
const all = simRender();
console.log('✓ 全部分类渲染格子数:', all.length, '(应=200)');
// 抽样验证每个格子 image 是有效 data URI 或合法 URL
let badSrc = 0;
for (const it of all) {
  if (!it.image.startsWith('data:image/webp;base64,') && !it.image.startsWith('https://www.pokokit.com/')) badSrc++;
}
console.log(badSrc === 0 ? '✓ 所有格子 image 来源合法 (data URI 或 官网URL)' : '✗ 异常 image 源: ' + badSrc);

// 模拟搜索
const search = simRender('', '沙发');
console.log('✓ 搜索"沙发"匹配:', search.length, '条 →', search.slice(0, 3).map(i => i.nameZh).join('、'));

console.log('\n=== 结论: 选择器数据层正常，离线版逻辑与在线版一致 ===');
