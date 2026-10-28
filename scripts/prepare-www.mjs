// Builds www/ from a pil-site zip for the Android app.
// Usage: node scripts/prepare-www.mjs /path/to/pil-site-vX.zip
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const zip = process.argv[2];
if (!zip) { console.error('zip path required'); process.exit(1); }
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const www = path.join(root, 'www');
fs.rmSync(www, { recursive: true, force: true });
fs.mkdirSync(www);
execFileSync('unzip', ['-oq', zip, '-d', www]);
// Netlify-only / web-only files
for (const f of ['_headers', 'sw.js', 'gizlilik.html']) fs.rmSync(path.join(www, f), { force: true });

// Bundle the Archivo font so the app looks right offline
const fontSrc = path.join(root, 'node_modules/@fontsource/archivo/files');
fs.mkdirSync(path.join(www, 'fonts'));
let css = '';
for (const sub of ['latin-ext', 'latin']) {
  const range = JSON.parse(fs.readFileSync(path.join(root, 'node_modules/@fontsource/archivo/unicode.json'), 'utf8'))[sub];
  for (const w of [400, 500, 600, 700, 800]) {
    const f = `archivo-${sub}-${w}-normal.woff2`;
    fs.copyFileSync(path.join(fontSrc, f), path.join(www, 'fonts', f));
    css += `@font-face{font-family:'Archivo';font-style:normal;font-display:swap;font-weight:${w};` +
           `src:url(${f}) format('woff2');unicode-range:${range};}\n`;
  }
}
fs.writeFileSync(path.join(www, 'fonts/archivo.css'), css);

const file = path.join(www, 'index.html');
let html = fs.readFileSync(file, 'utf8');
const swap = (from, to) => {
  if (!html.includes(from)) { console.error('patch target not found:\n' + from); process.exit(1); }
  html = html.replace(from, to);
};
swap('<link rel="preconnect" href="https://fonts.googleapis.com">\n', '');
swap('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n', '');
swap('<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
     '<link href="fonts/archivo.css" rel="stylesheet">\n<script src="capacitor.js"></script>');
fs.copyFileSync(path.join(root, 'node_modules/@capacitor/core/dist/capacitor.js'), path.join(www, 'capacitor.js'));

// Backup export: a.download does nothing in Android WebView, so save to
// cache and open the share sheet (Drive, WhatsApp, e-posta...) instead.
swap("    a.download = `studyo-yedek-${iso(new Date())}.json`; a.click(); URL.revokeObjectURL(a.href);\n    toast('Yedek indirildi'); };",
     "    a.download = `studyo-yedek-${iso(new Date())}.json`;\n" +
     "    if (window.Capacitor?.isNativePlatform?.()) { URL.revokeObjectURL(a.href); return nativeBackup(a.download); }\n" +
     "    a.click(); URL.revokeObjectURL(a.href);\n    toast('Yedek indirildi'); };");
swap('function armNotifications(){',
`async function nativeBackup(name){
  try {
    const cap = window.Capacitor;
    const Filesystem = cap.registerPlugin('Filesystem'), Share = cap.registerPlugin('Share');
    const r = await Filesystem.writeFile({ path: name, data: JSON.stringify(DB,null,2),
      directory: 'CACHE', encoding: 'utf8' });
    await Share.share({ title: 'PİL yedeği', files: [r.uri], dialogTitle: 'Yedeği kaydet veya gönder' });
    toast('Yedek hazır');
  } catch (err) {
    if (!/cancel/i.test(String(err?.message||err))) toast('Yedek kaydedilemedi', true);
  }
}

function armNotifications(){`);

fs.writeFileSync(file, html);
console.log('www ready:', fs.readdirSync(www).join(' '));
