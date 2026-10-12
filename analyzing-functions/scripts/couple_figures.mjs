// scripts/couple_figures.mjs
// 双人报告「图 2 横向 8 槽条」「图 3 关系地图」「图 6 命中徽章」「图 8 纵向汇流图」的纯几何生成器。
// 零外部依赖（仅 Node 内建，Node 18+ ESM）。
// 几何数值唯一依据：references/couple-visual-spec.md §6.2 / §6.3 / §6.6 / §6.8；
// 颜色唯一来源 references/stacks.json function_colors / function_colors_text。
// 本模块只产出图形 markup，不产出任何文字结论——文字 token 仍由 LLM 填。

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));

// ── 色板与原型名：优先读 stacks.json，读不到时用同值兜底 ──
const FALLBACK_COLORS = {
  Fi: '#c0392b', Ni: '#8e44ad', Fe: '#2980b9', Ti: '#16a085',
  Te: '#d35400', Ne: '#e67e22', Se: '#27ae60', Si: '#7f8c8d',
};
const FALLBACK_COLORS_TEXT = {
  Fi: '#c0392b', Ni: '#8e44ad', Fe: '#2473a6', Ti: '#117c67',
  Te: '#bd4b00', Ne: '#a55a18', Se: '#1c7d45', Si: '#656f70',
};
const FALLBACK_ROLES = ['英雄/女英雄', '父母', '永恒少年/少女', '阿尼玛·阿尼姆斯',
  '对立人格', '长老/女巫', '小丑/恶作剧者', '恶魔'];

let STACKS = null;
try {
  STACKS = JSON.parse(fs.readFileSync(path.join(HERE, '..', 'references', 'stacks.json'), 'utf8'));
} catch { STACKS = null; }

export const FUNCTION_COLORS = (STACKS && STACKS.function_colors) || FALLBACK_COLORS;
export const FUNCTION_COLORS_TEXT = (STACKS && STACKS.function_colors_text) || FALLBACK_COLORS_TEXT;
export const ROLES = (STACKS && STACKS.roles) || FALLBACK_ROLES;

// ── 通用色（visual-spec 设计代币）──
const PA = '#2F5D50';         // 甲方身份色（实线）
const PB = '#8A4A2A';         // 乙方身份色（虚线）
const INK = '#29241d';        // 墨
const MUT = '#6f6759';        // 弱灰
const FAINT = '#8d8271';      // 更浅一档灰（图内注）
const BORDER = '#DCD6C8';     // 常规描边
const CARD = '#fffdf8';       // 面板底
const SOFT = '#f2ecdf';       // 阴影面底
const ARROW = '#8d8271';      // 徽章箭头
const ACCENT = '#9A3B26';     // 赭红（mirror 交叉箭头）

const SERIF = "'Noto Serif SC',Source Han Serif SC,Songti SC,SimSun,serif";
const SANS = "'Noto Sans SC',Microsoft YaHei,PingFang SC,sans-serif";

/** XML/HTML 文本转义 */
const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** 文本宽度估算：CJK≈字号，拉丁/数字≈0.62×字号（宁高勿低） */
function estW(s, fs) {
  let w = 0;
  for (const ch of String(s)) w += ch.codePointAt(0) > 0xFF ? fs : fs * 0.62;
  return w;
}

/** 把（已转义）文本按功能码切分成 runs：[{t, code|null}] */
function codeRuns(escapedText) {
  const runs = [];
  let rest = String(escapedText);
  const re = /(Se|Si|Ne|Ni|Te|Ti|Fe|Fi)(?![a-z])/;
  let m;
  while ((m = rest.match(re))) {
    if (m.index > 0) runs.push({ t: rest.slice(0, m.index), code: null });
    runs.push({ t: m[1], code: m[1] });
    rest = rest.slice(m.index + m[1].length);
  }
  if (rest) runs.push({ t: rest, code: null });
  return runs;
}

/** 分段渲染一行（各段独立 <text>，功能码段染功能文本色）：anchor='middle' 时整行以 cx 居中 */
function textRuns(cx, y, escapedText, baseFill, fs, anchor = 'middle', fontFamily = SANS) {
  const runs = codeRuns(escapedText);
  const total = runs.reduce((w, r) => w + estW(r.t, fs), 0);
  let x = anchor === 'middle' ? cx - total / 2 : cx;
  return runs.filter((r) => r.t).map((r) => {
    const fill = r.code ? (FUNCTION_COLORS_TEXT[r.code] || INK) : baseFill;
    const el = `<text x="${fx(x)}" y="${y}" text-anchor="start" font-family="${fontFamily}" font-size="${fs}"${r.code ? ' font-weight="700"' : ''} fill="${fill}">${r.t}</text>`;
    x += estW(r.t, fs);
    return el;
  }).join('');
}

const fx = (v) => Number(v).toFixed(1);

// ════════════════════════════════════════════════════════════════════
// 图 2 —— 单方横向 8 槽条（一条内联 <svg>；visual-spec §6.2）
// ════════════════════════════════════════════════════════════════════
// 两条上下堆叠（甲上乙下）、共用同一横向几何 → 同号位竖直对齐。
// 每槽四行：位号（左上）/ 功能码（大、功能文本色）/ 原型名短式 /（阴影槽）(阴影)。
// 意识槽白底实线、阴影槽 --soft 底虚线；第 4/5 槽之间竖向分隔虚线。不含任何分数。
const VB_W = 712, VB_H = 96;
const GUT = 64, SLOT_W = 80, SLOT_H = 64, SLOT_TOP = 24, SLOT_PAD = 3;
const colX = (k) => GUT + (k - 1) * SLOT_W;
const colCx = (k) => colX(k) + SLOT_W / 2;

const ROLE_SHORT = {
  '英雄/女英雄': '英雄', '父母': '父母', '永恒少年/少女': '少年',
  '阿尼玛·阿尼姆斯': '阿尼玛', '对立人格': '对立', '长老/女巫': '长老',
  '小丑/恶作剧者': '小丑', '恶魔': '恶魔',
};
const shortRole = (r) => ROLE_SHORT[r] || String(r || '').split(/[\/·]/)[0] || '';

export function stackBand({ tag = '', typeCode = '', slots = [] } = {}) {
  const head = [tag, typeCode].filter(Boolean).map(esc).join(' · ');
  const g = [];
  g.push(`<svg viewBox="0 0 ${VB_W} ${VB_H}" role="img" aria-label="${esc(head)} 的横向八槽条：列＝毕比位置 1–8，第 1–4 列意识面、第 5–8 列阴影面；每槽为位号、功能-态度码与原型名；不含任何分数">`);
  g.push(`<text x="2" y="17" font-family="${SERIF}" font-weight="700" font-size="12.5" fill="${INK}">${head}</text>`);
  g.push(`<text x="${(colX(1) + colX(5)) / 2}" y="17" text-anchor="middle" font-family="${SANS}" font-size="10.5" fill="${MUT}">意识面（毕比 1–4）</text>`);
  g.push(`<text x="${(colX(5) + colX(9)) / 2}" y="17" text-anchor="middle" font-family="${SANS}" font-size="10.5" fill="${MUT}">阴影面（毕比 5–8）</text>`);
  for (let k = 1; k <= 8; k++) {
    const s = slots[k - 1] || {};
    const pos = Number(s.pos != null ? s.pos : k);
    const shadow = (s.face ? s.face === 'shadow' : pos >= 5);
    const color = FUNCTION_COLORS_TEXT[s.code] || INK;
    const x = colX(k) + SLOT_PAD;
    const w = SLOT_W - SLOT_PAD * 2;
    const cx = colCx(k);
    g.push(`<rect x="${x}" y="${SLOT_TOP}" width="${w}" height="${SLOT_H}" rx="7" fill="${shadow ? SOFT : CARD}" stroke="${BORDER}" stroke-width="1"${shadow ? ' stroke-dasharray="3 3"' : ''}/>`);
    g.push(`<text x="${x + 7}" y="${SLOT_TOP + 14}" font-family="${SANS}" font-size="9" fill="${MUT}">${esc(pos)}</text>`);
    g.push(`<text x="${cx}" y="${SLOT_TOP + 32}" text-anchor="middle" font-family="${SERIF}" font-weight="700" font-size="17" fill="${color}">${esc(s.code)}</text>`);
    g.push(`<text x="${cx}" y="${SLOT_TOP + 48}" text-anchor="middle" font-family="${SANS}" font-size="9.5" fill="${MUT}">${esc(shortRole(s.role))}</text>`);
    if (shadow) {
      g.push(`<text x="${cx}" y="${SLOT_TOP + 61}" text-anchor="middle" font-family="${SANS}" font-size="8.5" fill="${MUT}">(阴影)</text>`);
    }
  }
  const dv = colX(5);
  g.push(`<line x1="${dv}" y1="${SLOT_TOP - 2}" x2="${dv}" y2="${SLOT_TOP + SLOT_H + 2}" stroke="${BORDER}" stroke-dasharray="4 4"/>`);
  g.push('</svg>');
  return g.join('\n');
}

/** 便捷：由功能码数组（毕比 1–8 位序）构造 slots。图 2 不印分数。 */
export function makeSlots(stack, scoreOf, roles = ROLES) {
  return stack.map((code, i) => ({
    pos: i + 1,
    code,
    role: roles[i] || '',
    score: scoreOf ? scoreOf[code] : undefined,
    face: i < 4 ? 'conscious' : 'shadow',
  }));
}

// ════════════════════════════════════════════════════════════════════
// 图 3 —— 关系地图 64 格（visual-spec §6.3）
// ════════════════════════════════════════════════════════════════════
// 行＝甲方毕比位 1–8（自上而下）、列＝乙方毕比位 1–8（自左而右）；
// 8 个命中格：格底 = 功能原色 13% 淡底（同功能恒同色）+ 只标功能码（功能文本色）；
// 空格：居中「·」。四块归属由模板静态层承载（象限区域洗色 + 十字虚线 + 内嵌象限名），
// 不在本函数编码。无分数、无汇总行；四块穷尽 8 格且两两不交（内部校验，违反即抛错）。
const hexToRgb = (hex) => {
  const h = String(hex).replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
};
export function mapCells(slotsA = [], slotsB = []) {
  const posA = new Map(slotsA.map((s) => [s.code, s.pos]));
  const posB = new Map(slotsB.map((s) => [s.code, s.pos]));
  const hit = new Map();
  for (const [code, a] of posA) {
    const b = posB.get(code);
    if (b) hit.set(`${a}:${b}`, code);
  }
  if (hit.size !== 8) {
    throw new Error(`mapCells: 四块校验失败——命中格数 ${hit.size} ≠ 8（并集须恰为 8 且两两不交）`);
  }
  const rows = [];
  for (let a = 1; a <= 8; a++) {
    const cells = [];
    for (let b = 1; b <= 8; b++) {
      const code = hit.get(`${a}:${b}`);
      if (!code) { cells.push('<div class="q-cell empty">·</div>'); continue; }
      const [r, g, bl] = hexToRgb(FUNCTION_COLORS[code] || INK);
      const ct = FUNCTION_COLORS_TEXT[code] || INK;
      cells.push(`<div class="q-cell" style="background:rgba(${r},${g},${bl},.13)"><b style="color:${ct}">${esc(code)}</b></div>`);
    }
    rows.push('        ' + cells.join(''));
  }
  return rows.join('\n');
}

// ════════════════════════════════════════════════════════════════════
// 图 6 —— 命中徽章（visual-spec §6.6）
// ════════════════════════════════════════════════════════════════════
// 统一语言：空心虚线圆 = 内容出处（平时不用的一侧）；实心圆 = 对方意识落点；
// 箭头方向唯一＝内容所在方 → 对方。类别：mirror / soul-a / soul-b / flow-a / flow-b / p3 / fallback。
// 正文与图内一律不出现 P 编号。

/** 一条投射线：空心虚线圆（出处）→ 箭头 → 实心圆（落点） */
function badgeLine(code, srcLabel, dstLabel, y) {
  const fill = FUNCTION_COLORS[code] || INK;
  const text = FUNCTION_COLORS_TEXT[code] || INK;
  return (
    `<circle cx="50" cy="${y}" r="16" fill="none" stroke="${fill}" stroke-width="2" stroke-dasharray="3 3"/>` +
    `<text x="50" y="${y + 4}" text-anchor="middle" font-family="${SERIF}" font-size="11" font-weight="700" fill="${text}">${esc(code)}</text>` +
    `<text x="50" y="${y + 31}" text-anchor="middle" font-family="${SANS}" font-size="9.5" fill="${MUT}">${esc(srcLabel)}</text>` +
    `<line x1="82" y1="${y}" x2="186" y2="${y}" stroke="${ARROW}" stroke-width="1.6"/>` +
    `<polygon points="196,${y} 186,${y - 4.5} 186,${y + 4.5}" fill="${ARROW}"/>` +
    `<circle cx="232" cy="${y}" r="16" fill="${fill}" fill-opacity="0.88"/>` +
    `<text x="232" y="${y + 4}" text-anchor="middle" font-family="${SERIF}" font-size="11" font-weight="700" fill="#fffdf8">${esc(code)}</text>` +
    `<text x="232" y="${y + 31}" text-anchor="middle" font-family="${SANS}" font-size="9.5" fill="${MUT}">${esc(dstLabel)}</text>`
  );
}

/** soul / flow 徽章：逐行投射线（lines: [{code, src, dst}]） */
function emblemLines(lines = []) {
  const h = 30 + lines.length * 50 + 6;
  const g = [`<svg viewBox="0 0 300 ${h}" role="img" aria-label="投射供给示意：空心虚线圆为内容出处，实心圆为对方意识里的落点">`,
    `<defs><marker id="bd-arw" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="${ARROW}"/></marker></defs>`];
  lines.forEach((ln, i) => g.push(badgeLine(ln.code, ln.src, ln.dst, 30 + i * 50)));
  g.push('</svg>');
  return g.join('');
}

/** mirror 徽章：中轴虚线 + 左右两列意识 1–4 位 + 双向交叉箭头 */
function emblemMirror(aCons = [], bCons = []) {
  const g = [`<svg viewBox="0 0 300 120" role="img" aria-label="互为镜像示意：左右两列为两人各自的意识四位，中轴虚线两侧互为镜像">`,
    `<line x1="150" y1="10" x2="150" y2="110" stroke="#B9B29F" stroke-dasharray="3 4"/>`];
  for (let i = 0; i < 4; i++) {
    const y = 24 + i * 24;
    const ca = aCons[i] || '', cb = bCons[i] || '';
    const fa = FUNCTION_COLORS[ca] || INK, fb = FUNCTION_COLORS[cb] || INK;
    const ta = FUNCTION_COLORS_TEXT[ca] || INK, tb = FUNCTION_COLORS_TEXT[cb] || INK;
    g.push(`<circle cx="90" cy="${y}" r="13" fill="${fa}" fill-opacity="0.85"/>` +
      `<text x="90" y="${y + 4}" text-anchor="middle" font-family="${SERIF}" font-size="10.5" font-weight="700" fill="#fffdf8">${esc(ca)}</text>`);
    g.push(`<circle cx="210" cy="${y}" r="13" fill="${CARD}" stroke="${fb}" stroke-width="2"/>` +
      `<text x="210" y="${y + 4}" text-anchor="middle" font-family="${SERIF}" font-size="10.5" font-weight="700" fill="${tb}">${esc(cb)}</text>`);
  }
  g.push(`<line x1="112" y1="58" x2="182" y2="58" stroke="${ACCENT}" stroke-width="2.2"/>` +
    `<polygon points="192,58 182,53.5 182,62.5" fill="${ACCENT}"/>` +
    `<line x1="188" y1="76" x2="118" y2="76" stroke="${ACCENT}" stroke-width="2.2"/>` +
    `<polygon points="108,76 118,71.5 118,80.5" fill="${ACCENT}"/>`);
  g.push('</svg>');
  return g.join('');
}

/** p3 徽章：两圆重叠 + 贯穿竖线 + 圆心位码 */
function emblemSame(code = '') {
  const text = FUNCTION_COLORS_TEXT[code] || INK;
  return `<svg viewBox="0 0 300 90" role="img" aria-label="同一号位示意：两个部分重叠的圆，两人各占一圆，重叠处是同一名号位">` +
    `<circle cx="120" cy="40" r="26" fill="none" stroke="${PA}" stroke-width="1.6"/>` +
    `<circle cx="180" cy="40" r="26" fill="none" stroke="${PB}" stroke-width="1.6" stroke-dasharray="4 3"/>` +
    `<line x1="150" y1="14" x2="150" y2="66" stroke="${MUT}" stroke-width="1.6"/>` +
    `<text x="150" y="44" text-anchor="middle" font-family="${SERIF}" font-size="12" font-weight="700" fill="${text}">${esc(code)}</text>` +
    `</svg>`;
}

/** fallback 徽章：空心环 + 一条由外指向环心的箭头（尖端止于环缘） */
function emblemFallback() {
  const cx = 150, cy = 40, r = 17;
  const sx = 200, sy = 14;
  const dx = cx - sx, dy = cy - sy;
  const d = Math.hypot(dx, dy) || 1;
  const ux = dx / d, uy = dy / d;
  const tx = cx - r * ux, ty = cy - r * uy;
  const bx = tx - 9 * ux, by = ty - 9 * uy;
  const px = -uy, py = ux;
  const w = 4.6;
  return `<svg viewBox="0 0 300 90" role="img" aria-label="兜底示意：一个空心环与一条由外指向环心的箭头——问自己「触动我的是哪个位置」">` +
    `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${MUT}" stroke-width="1.6"/>` +
    `<line x1="${sx}" y1="${sy}" x2="${fx(bx)}" y2="${fx(by)}" stroke="${MUT}" stroke-width="1.8"/>` +
    `<polygon points="${fx(tx)},${fx(ty)} ${fx(bx + w * px)},${fx(by + w * py)} ${fx(bx - w * px)},${fx(by - w * py)}" fill="${MUT}"/>` +
    `</svg>`;
}

/**
 * hitBadges —— 生成图 6 的整块 .hit-badges HTML。
 * hits 条目：
 *   { kind:'mirror', aCons:[码×4], bCons:[码×4] }                    P4 全对立栈（只此一枚）
 *   { kind:'soul-a'|'soul-b', recv:1|2|3, lines:[{code,src,dst}] }   灵魂位供给（recv=1 即英雄位情形）
 *   { kind:'flow-a'|'flow-b', lines:[{code,src,dst}] }               阴影供给（每方向一枚）
 *   { kind:'p3', code }                                              同一功能同坐第 1 位
 *   { kind:'fallback' }                                              全未命中兜底（唯一例外：无常驻底图仍须出此枚）
 */
export function hitBadges(hits = []) {
  if (!hits.length) hits = [{ kind: 'fallback' }]; // 全未命中 → 兜底徽章，不留空图
  const cards = [];
  for (const h of hits) {
    const kind = h && h.kind;
    let emb = '', dir = '', title = '', desc = '';
    if (kind === 'mirror') {
      emb = emblemMirror(h.aCons || [], h.bCons || []);
      dir = '甲 ⇄ 乙';
      title = '你们互为对方的镜像';
      desc = '对方的英雄位，正是自己心里最深、最不熟练的那一面（第 4 位）——双向投射没有哪一头是单向的，迷恋与摩擦在这里同源；这条共享的轴是整段关系的中央大道。';
    } else if (kind === 'soul-a' || kind === 'soul-b') {
      const lines = h.lines || [];
      emb = emblemLines(lines);
      const who = kind === 'soul-a' ? '甲方' : '乙方';
      const whom = kind === 'soul-a' ? '乙方' : '甲方';
      dir = kind === 'soul-a' ? '甲 → 乙' : '乙 → 甲';
      title = `${who}最深的一面，正是${whom}的日常`;
      desc = `${who}第 4 位的内容，恰是${whom}看家本领所在的位置（见各行标注）——${whom}自然而然把它演出来，${who}却怎么也学不会${h.recv && h.recv > 1 ? '（承接位越靠后，强度越缓）' : ''}。`;
    } else if (kind === 'flow-a' || kind === 'flow-b') {
      const lines = h.lines || [];
      emb = emblemLines(lines);
      const who = kind === 'flow-a' ? '甲方' : '乙方';
      const whom = kind === 'flow-a' ? '乙方' : '甲方';
      dir = kind === 'flow-a' ? '甲 → 乙' : '乙 → 甲';
      title = `${who}平时不用的，正是${whom}天天在用的`;
      desc = `空心侧是内容的出处（${who}平时不用的一侧），实心圆是它在${whom}意识里的落点——${who}最容易把这些当成“${whom}的属性”，其实那是自己没用惯的一块。`;
    } else if (kind === 'p3') {
      emb = emblemSame(h.code || '');
      dir = '同一号位';
      title = '你们占着同一个驾驶座';
      desc = '同一个功能是两人各自最顺手的那一面——既能深度共振，也可能争「谁说了算」。';
    } else if (kind === 'fallback') {
      emb = emblemFallback();
      dir = '';
      title = '触动我的是哪个位置';
      desc = '你们之间没有出现固定的投射机制；当强烈而无来由的反应出现时，先按「我的哪个位置被触动」来读。';
    } else {
      continue; // 未知类别不出图
    }
    const dirHtml = dir ? `<div class="hb-dir">${esc(dir)}</div>` : '';
    cards.push(`<div class="hb">${dirHtml}<h3>${title}</h3>` +
      `<div class="hb-emb">${emb}</div><p>${desc}</p></div>`);
  }
  return `<div class="hit-badges">\n  ${cards.join('\n  ')}\n</div>`;
}

// ════════════════════════════════════════════════════════════════════
// 图 8 —— 纵向汇流图（visual-spec §6.8；画布 viewBox="0 0 640 300"）
// ════════════════════════════════════════════════════════════════════
// 顶部两个立场盒（甲实线 / 乙虚线，各带立场白话 + 位置锚点），两条实线箭头向下汇入
// 「第三条路」盒（行1 短白话 / 行2 容纳对象 / 行3 共同任务）。纯几何、无比喻。
const TN_W = 640, TN_H = 300;

function tnArrowHead(endX, endY, ux, uy, len = 9, half = 3.4, color = MUT) {
  const bx = endX - len * ux, by = endY - len * uy;
  const px = -uy, py = ux;
  return `<polygon points="${fx(endX)},${fx(endY)} ${fx(bx + half * px)},${fx(by + half * py)} ${fx(bx - half * px)},${fx(by - half * py)}" fill="${color}"/>`;
}

export function thirdNode({ aTag = '甲方', aStance = '', aEvidence = '',
  bTag = '乙方', bStance = '', bEvidence = '',
  thirdLine = '', containLine = '', task = '' } = {}) {
  const g = [];
  const aria = `纵向汇流图：顶部左右两个立场盒是双方各自守的一端（甲实线、乙虚线），两条实线箭头向下汇入同一个盒「第三条路」；盒内是容纳对象与共同任务`;
  g.push(`<svg viewBox="0 0 ${TN_W} ${TN_H}" role="img" aria-label="${aria}">`);
  // 立场盒：甲
  g.push(`<rect x="60" y="26" width="210" height="64" rx="10" fill="${CARD}" stroke="${PA}" stroke-width="1.6"/>`);
  g.push(`<text x="165" y="52" text-anchor="middle" font-family="${SANS}" font-size="13" font-weight="700" fill="${PA}">${esc(aTag)}立场 · ${esc(aStance)}</text>`);
  if (aEvidence) g.push(textRuns(165, 74, esc(aEvidence), MUT, 11.5));
  // 立场盒：乙（虚线）
  g.push(`<rect x="370" y="26" width="210" height="64" rx="10" fill="${CARD}" stroke="${PB}" stroke-width="1.6" stroke-dasharray="5 3"/>`);
  g.push(`<text x="475" y="52" text-anchor="middle" font-family="${SANS}" font-size="13" font-weight="700" fill="${PB}">${esc(bTag)}立场 · ${esc(bStance)}</text>`);
  if (bEvidence) g.push(textRuns(475, 74, esc(bEvidence), MUT, 11.5));
  // 汇流箭头（甲实线 / 乙虚线，尖端止于第三条路盒上缘）
  g.push(`<path d="M 165 90 C 165 140, 250 148, 292 168" fill="none" stroke="${PA}" stroke-width="1.8"/>`);
  g.push(tnArrowHead(296, 170, 0.903, 0.43, 9, 3.4, PA));
  g.push(`<path d="M 475 90 C 475 140, 390 148, 348 168" fill="none" stroke="${PB}" stroke-width="1.8" stroke-dasharray="5 3"/>`);
  g.push(tnArrowHead(344, 170, -0.903, 0.43, 9, 3.4, PB));
  // 第三条路盒
  g.push(`<rect x="165" y="176" width="310" height="86" rx="12" fill="rgba(61,54,44,.045)" stroke="#3d362c" stroke-width="1.8"/>`);
  g.push(`<text x="320" y="206" text-anchor="middle" font-family="${SANS}" font-size="14" font-weight="700" fill="${INK}">第三条路：${esc(thirdLine)}</text>`);
  if (containLine) g.push(textRuns(320, 230, esc(containLine), "#5c5548", 12));
  if (task) g.push(textRuns(320, 252, esc("共同任务：" + task), MUT, 11.5));
  g.push('</svg>');
  return `<figure class="third-node">\n    ${g.join('\n    ')}\n  </figure>`;
}

export default { stackBand, makeSlots, hitBadges, thirdNode, mapCells, ROLES, FUNCTION_COLORS };
