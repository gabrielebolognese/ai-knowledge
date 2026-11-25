#!/usr/bin/env node
/**
 * Builds the simplified SVG illustrations used by the Setup track for things a headless browser cannot
 * capture: operating-system dialogs, installers and terminal sessions.
 *
 *   node scripts/build-setup-illustrations.mjs
 *
 * Every image is drawn from scratch in the site's own style (no Microsoft/Apple artwork is copied) and
 * carries an "Illustration" tag, because a real screen can differ slightly. Labels come from the official
 * documentation cited in research/04-setup.md. Output: public/screenshots/setup/ill-*.svg
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'public', 'screenshots', 'setup');
const ACCENT = '#3340C9';
const SANS = "'Segoe UI', Inter, system-ui, -apple-system, Arial, sans-serif";
const MONO = "'Cascadia Mono', Consolas, 'JetBrains Mono', Menlo, monospace";

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const T = (x, y, s, o = {}) =>
  `<text xml:space="preserve" x="${x}" y="${y}" font-family="${o.mono ? MONO : SANS}" font-size="${o.size || 15}" fill="${o.fill || '#1b1d29'}"${o.weight ? ` font-weight="${o.weight}"` : ''}${o.anchor ? ` text-anchor="${o.anchor}"` : ''}>${esc(s)}</text>`;
const R = (x, y, w, h, o = {}) =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${o.r ?? 6}" fill="${o.fill || '#fff'}"${o.stroke ? ` stroke="${o.stroke}" stroke-width="${o.sw || 1}"` : ''}/>`;
/** Accent ring + numbered badge (badge on the left unless side = 'right' or 'top'). */
const ring = (x, y, w, h, n, side = 'left', p = 6) => {
  let bx = x - p - 24, by = y + h / 2;
  if (side === 'right') bx = x + w + p + 24;
  if (side === 'top') { bx = x - p; by = y - p - 22; }
  return `<rect x="${x - p}" y="${y - p}" width="${w + 2 * p}" height="${h + 2 * p}" rx="9" fill="none" stroke="#fff" stroke-width="9" opacity="0.9"/>` +
    `<rect x="${x - p}" y="${y - p}" width="${w + 2 * p}" height="${h + 2 * p}" rx="9" fill="none" stroke="${ACCENT}" stroke-width="4"/>` +
    `<circle cx="${bx}" cy="${by}" r="18" fill="${ACCENT}" stroke="#fff" stroke-width="3"/>` +
    T(bx, by + 6.5, n, { size: 18, weight: 700, fill: '#fff', anchor: 'middle' });
};
const checkbox = (x, y, checked, label, o = {}) =>
  R(x, y - 14, 18, 18, { r: 3, fill: checked ? '#0f6cbd' : '#fff', stroke: checked ? '#0f6cbd' : '#6b6f80', sw: 1.5 }) +
  (checked ? `<path d="M${x + 4} ${y - 5} l4 4 l7 -9" stroke="#fff" stroke-width="2.2" fill="none"/>` : '') +
  T(x + 28, y, label, { size: o.size || 15 });
const button = (x, y, w, h, label, primary = false) =>
  R(x, y, w, h, { r: 5, fill: primary ? '#0f6cbd' : '#fbfbfb', stroke: primary ? '#0f6cbd' : '#c4c6d0' }) +
  T(x + w / 2, y + h / 2 + 5, label, { size: 15, weight: 600, fill: primary ? '#fff' : '#1b1d29', anchor: 'middle' });
const toggle = (x, y, on, label, sub = '') =>
  T(x, y, label, { size: 15, weight: 600 }) + (sub ? T(x, y + 20, sub, { size: 13, fill: '#5b5f70' }) : '') +
  `<rect x="${x + 520}" y="${y - 14}" width="44" height="22" rx="11" fill="${on ? '#0f6cbd' : '#fff'}" stroke="${on ? '#0f6cbd' : '#6b6f80'}" stroke-width="1.5"/>` +
  `<circle cx="${on ? x + 551 : x + 533}" cy="${y - 3}" r="6.5" fill="${on ? '#fff' : '#6b6f80'}"/>` +
  T(x + 500, y + 1, on ? 'On' : 'Off', { size: 14, anchor: 'end' });

/** Wrap content in a window with a title bar and the "Illustration" tag. */
function svg(w, h, title, body, { os = 'win', dark = false, tag = 'Illustration: simplified, your screen may differ' } = {}) {
  const bar = dark ? '#2b2b2b' : '#eef0f6';
  const chrome = os === 'mac'
    ? `<circle cx="34" cy="38" r="7" fill="#ff5f57"/><circle cx="56" cy="38" r="7" fill="#febc2e"/><circle cx="78" cy="38" r="7" fill="#28c840"/>` + T(w / 2, 43, title, { size: 14, fill: dark ? '#ddd' : '#40444f', anchor: 'middle', weight: 600 })
    : T(36, 43, title, { size: 14, fill: dark ? '#ddd' : '#40444f' }) +
      `<g stroke="${dark ? '#bbb' : '#555'}" stroke-width="1.4"><path d="M${w - 128} 38h12"/><rect x="${w - 86}" y="32" width="11" height="11" fill="none"/><path d="M${w - 42} 32l11 11M${w - 31} 32l-11 11"/></g>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h + 44}" width="${w}" height="${h + 44}" role="img">
<rect width="${w}" height="${h + 44}" fill="#f6f7fb"/>
<rect x="12" y="16" width="${w - 24}" height="${h - 4}" rx="10" fill="${dark ? '#0c0c0c' : '#ffffff'}" stroke="#c9ccd8"/>
<path d="M12 26a10 10 0 0 1 10-10h${w - 44}a10 10 0 0 1 10 10v34h-${w - 24}z" fill="${bar}"/>
${chrome}
${body}
<rect x="${w - 372}" y="${h + 16}" width="360" height="22" rx="11" fill="#ffffff" stroke="#c9ccd8"/>
${T(w - 192, h + 31.5, tag, { size: 12, fill: '#5b5f70', anchor: 'middle' })}
</svg>
`;
}

/** Terminal body: lines = [{ t, c, b }] where c = colour, b = badge number (rings the line). */
function terminal(lines, { x0 = 32, y0 = 96, lh = 34, size = 15, cw = size * 0.61 } = {}) {
  let out = '';
  lines.forEach((l, i) => {
    const y = y0 + i * lh;
    if (l.t) out += T(x0, y, l.t, { mono: true, size, fill: l.c || '#e6e6e6' });
    if (l.b) out += ring(x0 - 2, y - size + 1, Math.max(60, l.t.length * cw + 6), size + 5, l.b, l.side || 'right', 4);
  });
  return out;
}
const PS = '#e6e6e6', OK = '#7ee787', ERR = '#ff7b72', DIM = '#9ba1a6', YEL = '#e3b341';

const ILL = {
  'ill-windows-terminal.svg': () => {
    const start = R(40, 80, 420, 330, { fill: '#f3f4f8', stroke: '#d5d8e2', r: 10 }) +
      R(60, 100, 380, 40, { r: 20, fill: '#fff', stroke: '#0f6cbd', sw: 1.5 }) + T(84, 126, 'terminal', { size: 16 }) +
      T(60, 172, 'Best match', { size: 13, weight: 600, fill: '#5b5f70' }) +
      R(60, 184, 380, 64, { r: 8, fill: '#dfe7f6' }) + R(76, 198, 36, 36, { r: 6, fill: '#1b1d29' }) + T(84, 222, '>_', { mono: true, size: 15, fill: '#fff' }) +
      T(126, 212, 'Terminal', { size: 16, weight: 600 }) + T(126, 234, 'System', { size: 13, fill: '#5b5f70' }) +
      T(60, 290, '1. Press the Windows key', { size: 14, fill: '#40444f' }) + T(60, 314, '2. Type terminal', { size: 14, fill: '#40444f' }) + T(60, 338, '3. Press Enter', { size: 14, fill: '#40444f' }) +
      ring(60, 100, 380, 40, 1) + ring(60, 184, 380, 64, 2);
    const term = R(500, 80, 600, 330, { fill: '#0c0c0c', r: 8 }) + R(500, 80, 600, 34, { fill: '#2b2b2b', r: 8 }) + T(520, 103, 'Windows PowerShell', { size: 13, fill: '#ddd' }) +
      terminal([{ t: 'PS C:\\Users\\you> echo hello', c: PS, b: 3 }, { t: 'hello', c: OK }, { t: 'PS C:\\Users\\you> _', c: PS }], { x0: 520, y0: 150 });
    return svg(1140, 450, 'Start menu search and Windows Terminal', start + term);
  },
  'ill-msix-install.svg': () => svg(760, 420, 'App Installer', [
    R(52, 92, 72, 72, { r: 12, fill: '#ffd43b' }), T(88, 140, 'Py', { size: 30, weight: 700, fill: '#306998', anchor: 'middle' }),
    T(148, 112, 'Install Python install manager?', { size: 22, weight: 600 }),
    T(148, 142, 'Publisher: Python Software Foundation', { size: 14, fill: '#5b5f70' }),
    T(148, 164, 'Version: 26.4', { size: 14, fill: '#5b5f70' }),
    T(52, 220, 'Capabilities:', { size: 14, weight: 600 }), T(52, 244, '• Uses all system resources', { size: 14, fill: '#40444f' }),
    checkbox(52, 300, true, 'Launch when ready'),
    button(560, 360, 150, 40, 'Install', true), ring(560, 360, 150, 40, 1),
  ].join(''), { tag: 'Illustration: dialog wording may differ' }),
  'ill-legacy-installer.svg': () => svg(860, 520, 'Python 3.14.10 (64-bit) Setup', [
    R(12, 60, 230, 440, { r: 0, fill: '#e9eef8' }), R(70, 110, 110, 110, { r: 18, fill: '#ffd43b' }), T(125, 180, 'Py', { size: 44, weight: 700, fill: '#306998', anchor: 'middle' }),
    T(280, 108, 'Install Python 3.14.10 (64-bit)', { size: 24, weight: 600 }),
    T(280, 138, 'Select Install Now to install Python with default settings,', { size: 14, fill: '#40444f' }),
    T(280, 158, 'or choose Customize to enable or disable features.', { size: 14, fill: '#40444f' }),
    R(280, 190, 520, 70, { r: 6, fill: '#f3f6fc', stroke: '#c4c6d0' }), T(300, 220, '→ Install Now', { size: 18, weight: 600, fill: '#0f4c99' }),
    T(320, 244, 'Includes IDLE, pip and documentation', { size: 13, fill: '#5b5f70' }),
    R(280, 276, 520, 52, { r: 6, fill: '#fff', stroke: '#c4c6d0' }), T(300, 308, '→ Customize installation', { size: 16, fill: '#0f4c99' }),
    T(280, 360, 'This installer is being retired and will no longer be available after Python 3.15.', { size: 12.5, fill: '#8a4b00' }),
    checkbox(280, 420, false, 'Use admin privileges when installing py.exe'),
    checkbox(280, 458, true, 'Add python.exe to PATH'),
    ring(278, 442, 236, 22, 1), ring(280, 190, 520, 70, 2),
  ].join('')),
  'ill-py-install-terminal.svg': () => svg(940, 380, 'Windows PowerShell', terminal([
    { t: 'PS C:\\Users\\you> py install 3.14', b: 1 },
    { t: 'Installing Python 3.14.10.', c: DIM },
    { t: 'Python 3.14.10 will be launched by python.exe and py.exe.', c: DIM },
    { t: 'PS C:\\Users\\you> py list', b: 2 },
    { t: ' 3.14[-64]  Python 3.14.10  *', c: DIM },
    { t: 'PS C:\\Users\\you> python --version', b: 3 },
    { t: 'Python 3.14.10', c: OK },
    { t: 'PS C:\\Users\\you> _' },
  ]), { dark: true, tag: 'Illustration: exact messages may differ' }),
  'ill-app-execution-aliases.svg': () => svg(900, 470, 'Settings  ›  Apps  ›  Advanced app settings  ›  App execution aliases', [
    T(52, 104, 'App execution aliases', { size: 24, weight: 600 }),
    T(52, 132, 'Apps can declare a name used to run the app from a command prompt.', { size: 14, fill: '#5b5f70' }),
    T(52, 152, 'If several apps use the same name, choose which one to use.', { size: 14, fill: '#5b5f70' }),
    R(40, 172, 820, 70, { r: 8, fill: '#f7f8fb', stroke: '#e1e3ea' }), toggle(64, 202, true, 'Python (default)', 'python.exe'),
    R(40, 250, 820, 70, { r: 8, fill: '#f7f8fb', stroke: '#e1e3ea' }), toggle(64, 280, true, 'Python (default windowed)', 'pythonw.exe'),
    R(40, 328, 820, 70, { r: 8, fill: '#f7f8fb', stroke: '#e1e3ea' }), toggle(64, 358, true, 'Python install manager', 'py.exe, pymanager.exe'),
    ring(584, 188, 44, 22, 1, 'right'),
  ].join('')),
  'ill-vscode-setup-tasks.svg': () => svg(820, 500, 'Setup - Microsoft Visual Studio Code (User)', [
    T(40, 100, 'Select Additional Tasks', { size: 18, weight: 600 }),
    T(40, 124, 'Which additional tasks should be performed?', { size: 14, fill: '#40444f' }),
    T(40, 162, 'Additional icons:', { size: 14 }), checkbox(60, 190, false, 'Create a desktop icon', { size: 14 }),
    T(40, 226, 'Other:', { size: 14 }),
    checkbox(60, 254, false, 'Add "Open with Code" action to Windows Explorer file context menu', { size: 14 }),
    checkbox(60, 284, false, 'Add "Open with Code" action to Windows Explorer directory context menu', { size: 14 }),
    checkbox(60, 314, true, 'Register Code as an editor for supported file types', { size: 14 }),
    checkbox(60, 344, true, 'Add to PATH (requires shell restart)', { size: 14 }),
    ring(58, 326, 300, 24, 1),
    button(520, 420, 110, 34, '< Back'), button(640, 420, 110, 34, 'Next >', true), ring(640, 420, 110, 34, 2, 'top'),
  ].join(''), { tag: 'Illustration: simplified, your installer may differ' }),
  'ill-venv-execution-policy.svg': () => svg(1100, 470, 'Windows PowerShell', terminal([
    { t: 'PS C:\\dev\\ai-knowledge> python -m venv .venv', b: 1 },
    { t: 'PS C:\\dev\\ai-knowledge> .venv\\Scripts\\Activate.ps1' },
    { t: '.venv\\Scripts\\Activate.ps1 : File C:\\dev\\ai-knowledge\\.venv\\Scripts\\Activate.ps1', c: ERR },
    { t: 'cannot be loaded because running scripts is disabled on this system.', c: ERR, b: 2 },
    { t: 'PS C:\\dev\\ai-knowledge> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser', b: 3 },
    { t: 'PS C:\\dev\\ai-knowledge> .venv\\Scripts\\Activate.ps1' },
    { t: '(.venv) PS C:\\dev\\ai-knowledge> _', c: OK, b: 4 },
  ], { size: 14.5 }), { dark: true, tag: 'Illustration: exact messages may differ' }),
  'ill-vscode-select-interpreter.svg': () => svg(940, 360, 'Visual Studio Code', [
    R(150, 74, 640, 250, { r: 8, fill: '#fff', stroke: '#c4c6d0' }),
    R(166, 88, 608, 34, { r: 4, fill: '#fff', stroke: '#0f6cbd', sw: 1.5 }), T(178, 111, 'Select Interpreter', { size: 14, fill: '#5b5f70' }),
    T(170, 150, '+ Create Virtual Environment...', { size: 14 }),
    R(160, 162, 620, 52, { r: 4, fill: '#e3ecfb' }), T(172, 184, "Python 3.14.10 ('.venv': venv)", { size: 14, weight: 600 }),
    T(172, 204, '.\\.venv\\Scripts\\python.exe', { size: 12.5, fill: '#5b5f70', mono: true }), T(766, 184, 'Recommended', { size: 12.5, fill: '#0f6cbd', anchor: 'end' }),
    T(170, 244, 'Global', { size: 12.5, weight: 600, fill: '#5b5f70' }),
    T(172, 268, 'Python 3.14.10 64-bit', { size: 14 }), T(172, 288, '~\\AppData\\Local\\Python\\bin\\python.exe', { size: 12.5, fill: '#5b5f70', mono: true }),
    ring(160, 162, 620, 52, 1),
    T(40, 348, 'Open with Ctrl+Shift+P, type "Python: Select Interpreter", press Enter.', { size: 13, fill: '#40444f' }),
  ].join('')),
  'ill-pip-install.svg': () => svg(1040, 330, 'Windows PowerShell', terminal([
    { t: '(.venv) PS C:\\dev\\ai-knowledge> python -m pip install -r code\\requirements.txt', b: 1 },
    { t: 'Collecting numpy>=2.0 (from -r code\\requirements.txt (line 19))', c: DIM },
    { t: '  Downloading numpy-2.5.5-cp314-cp314-win_amd64.whl', c: DIM },
    { t: '...', c: DIM },
    { t: 'Successfully installed chess-1.11.2 jupyterlab-4.6.6 matplotlib-3.11.2 numpy-2.5.5 ...', c: OK, b: 2 },
    { t: '(.venv) PS C:\\dev\\ai-knowledge> _' },
  ], { size: 14.5 }), { dark: true, tag: 'Illustration: versions and lines will differ' }),
  'ill-verify-output.svg': () => svg(1000, 560, 'Windows PowerShell', terminal([
    { t: '(.venv) PS C:\\dev\\ai-knowledge> python code\\setup\\verify_setup.py' },
    { t: 'Python       : 3.14.10 Windows-11-10.0.26200-SP0', b: 1 },
    { t: 'numpy        : 2.5.5' },
    { t: 'matplotlib   : 3.11.2' },
    { t: 'pillow       : 13.0.0' },
    { t: 'tqdm         : 4.70.1' },
    { t: 'python-chess : 1.11.2' },
    { t: 'torch        : 2.15.0+cpu' },
    { t: 'torchvision  : 0.29.2+cpu' },
    { t: 'CUDA GPU     : False  (normal on a CPU install)', c: YEL, b: 2 },
    { t: 'Apple MPS    : False' },
    { t: 'tensor OK    : (5, 3)', c: OK },
    { t: 'venv active  : True  (C:\\dev\\ai-knowledge\\.venv)' },
    { t: 'All checks passed.', c: OK, b: 3 },
  ], { size: 14.5, lh: 30 }), { dark: true, tag: 'Illustration: versions will differ' }),
  'ill-mac-terminal.svg': () => svg(1000, 380, 'Spotlight and Terminal', [
    R(40, 80, 400, 56, { r: 14, fill: '#f1f1f4', stroke: '#c9ccd8' }), T(70, 116, '🔍  Terminal', { size: 20 }),
    R(40, 146, 400, 50, { r: 8, fill: '#dfe7f6' }), T(70, 177, 'Terminal — Application', { size: 15 }),
    T(40, 240, '⌘ Space opens Spotlight.', { size: 14, fill: '#40444f' }), T(40, 264, 'Type Terminal, press Return.', { size: 14, fill: '#40444f' }),
    ring(40, 80, 400, 56, 1, 'right'),
    R(500, 80, 460, 260, { r: 8, fill: '#ffffff', stroke: '#c9ccd8' }), R(500, 80, 460, 30, { r: 8, fill: '#eceef2' }), T(730, 100, 'you — zsh — 80×24', { size: 12, fill: '#40444f', anchor: 'middle' }),
    T(516, 140, 'you@Mac ~ % python3 --version', { mono: true, size: 14.5 }), T(516, 166, 'Python 3.14.10', { mono: true, size: 14.5, fill: '#1a7f37' }), T(516, 192, 'you@Mac ~ % _', { mono: true, size: 14.5 }),
    ring(514, 126, 262, 20, 2, 'right'),
  ].join(''), { os: 'mac' }),
  'ill-mac-certificates.svg': () => svg(860, 400, 'Python 3.14', [
    R(12, 60, 190, 336, { r: 0, fill: '#f1f1f4' }), T(30, 92, 'Favourites', { size: 12, weight: 600, fill: '#8a8d99' }), T(30, 118, 'Applications', { size: 14 }), T(30, 142, 'Desktop', { size: 14 }), T(30, 166, 'Downloads', { size: 14 }),
    ...[['IDLE.app', 240, 120], ['Install Certificates.command', 470, 120], ['License.rtf', 700, 120], ['Python Launcher.app', 240, 270], ['ReadMe.rtf', 470, 270], ['Update Shell Profile.command', 700, 270]].map(([n, x, y]) =>
      R(x - 30, y - 40, 60, 60, { r: 10, fill: n.endsWith('.command') ? '#2b2b2b' : n.endsWith('.rtf') ? '#fff' : '#ffd43b', stroke: '#c9ccd8' }) + T(x, y + 44, n, { size: 13, anchor: 'middle' })),
    ring(380, 74, 180, 120, 1),
    T(230, 380, 'Double-click Install Certificates.command once after installing.', { size: 13, fill: '#40444f' }),
  ].join(''), { os: 'mac' }),
  'ill-linux-apt.svg': () => svg(900, 330, 'Terminal', terminal([
    { t: 'you@host:~$ sudo apt update', b: 1 },
    { t: 'you@host:~$ sudo apt install -y python3 python3-venv python3-pip', b: 2 },
    { t: '...', c: DIM },
    { t: 'you@host:~$ python3 --version', b: 3 },
    { t: 'Python 3.14.3', c: OK },
    { t: 'you@host:~$ _' },
  ], { size: 14.5 }), { dark: true, tag: 'Illustration: version depends on your distribution' }),
  'ill-colab-runtime.svg': () => svg(860, 440, 'Google Colab', [
    T(40, 92, 'File   Edit   View   Insert', { size: 14, fill: '#40444f' }), T(250, 92, 'Runtime', { size: 14, weight: 700 }), T(330, 92, 'Tools   Help', { size: 14, fill: '#40444f' }),
    ring(246, 76, 64, 22, 1, 'top'),
    R(230, 104, 270, 120, { r: 6, fill: '#fff', stroke: '#c4c6d0' }), T(246, 132, 'Run all', { size: 14 }), T(246, 160, 'Restart session', { size: 14 }),
    R(234, 176, 262, 30, { r: 4, fill: '#e3ecfb' }), T(246, 197, 'Change runtime type', { size: 14, weight: 600 }), ring(234, 176, 262, 30, 2),
    R(540, 120, 290, 270, { r: 10, fill: '#fff', stroke: '#c4c6d0' }), T(560, 152, 'Change runtime type', { size: 17, weight: 600 }),
    T(560, 184, 'Runtime type: Python 3', { size: 14, fill: '#40444f' }), T(560, 214, 'Hardware accelerator', { size: 14, weight: 600 }),
    `<circle cx="570" cy="240" r="7" fill="#fff" stroke="#6b6f80" stroke-width="1.5"/>`, T(586, 245, 'CPU', { size: 14 }),
    `<circle cx="570" cy="268" r="7" fill="#fff" stroke="#0f6cbd" stroke-width="1.5"/><circle cx="570" cy="268" r="3.5" fill="#0f6cbd"/>`, T(586, 273, 'T4 GPU', { size: 14 }),
    ring(560, 256, 100, 24, 3, 'right'),
    button(720, 340, 90, 34, 'Save', true),
  ].join(''), { tag: 'Illustration: menu labels and GPU names change' }),
  'ill-colab-verify.svg': () => svg(900, 330, 'Google Colab: Untitled0.ipynb', [
    R(40, 80, 820, 44, { r: 6, fill: '#f7f8fb', stroke: '#d5d8e2' }), T(60, 108, '▶', { size: 14, fill: '#40444f' }), T(90, 108, '!pip install chess', { mono: true, size: 14.5 }),
    T(90, 146, 'Successfully installed chess-1.11.2', { mono: true, size: 13.5, fill: '#5b5f70' }), ring(56, 90, 205, 26, 1),
    R(40, 170, 820, 70, { r: 6, fill: '#f7f8fb', stroke: '#d5d8e2' }), T(60, 198, '▶', { size: 14, fill: '#40444f' }),
    T(90, 198, 'import torch, chess', { mono: true, size: 14.5 }), T(90, 222, 'print(torch.__version__, torch.cuda.is_available())', { mono: true, size: 14.5 }),
    T(90, 266, '2.x.x+cu12x True', { mono: true, size: 14.5, fill: '#1a7f37' }), ring(88, 252, 170, 20, 2),
    T(40, 310, 'True appears only when a GPU runtime is selected.', { size: 13, fill: '#40444f' }),
  ].join(''), { tag: 'Illustration: versions will differ' }),
};

fs.mkdirSync(OUT, { recursive: true });
for (const [file, make] of Object.entries(ILL)) {
  fs.writeFileSync(path.join(OUT, file), make());
  console.log('wrote', file);
}
