#!/usr/bin/env python3
# Generatore della guida di riferimento ai contratti (guida C, DOC-12).
# HTML con CSS di stampa convertito in PDF con Chromium (Playwright); pypdf unisce le parti.
#
# Uso: python genera_guida.py --libs <cartella delle librerie> --out <file.pdf> [--max-contratti N]
import argparse, html, os, re, tempfile
import pypdf
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser(description='Guida di riferimento ai contratti (DOC-12).')
ap.add_argument('--libs', required=True, help='cartella che contiene le librerie (per esempio ...\\VICE\\libs)')
ap.add_argument('--out', required=True, help='file PDF da scrivere')
ap.add_argument('--max-contratti', type=int, default=0, help='0 = tutti; N = solo i primi N per modulo (bozze)')
A = ap.parse_args()
LIBS = A.libs
NMAX = A.max_contratti or None
TMP = tempfile.mkdtemp(prefix='guida_')
CAP = 52                      # righe di un riquadro per pagina
NB = ' '                 # spazio breve non separabile (DOC-10)
TEST = re.compile(r'^fp_(int_tests|test_integers|test_suite|tests)\.asm$')   # moduli di test: esclusi
e = html.escape
SEP = '; ' + '=' * 78
warnings = []

def natural(s):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]

def read(path):
    return open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')

# ---------------------------------------------------------------- tipografia (DOC-10, DOC-11)
def group(d):
    out = []
    while d:
        out.insert(0, d[-3:]); d = d[:-3]
    return NB.join(out)

def typo(t):
    t = re.sub(r'(?<![\w$%.#])(\d{5,})(?![\w.])', lambda m: group(m.group(1)), t)
    t = re.sub(r'(\d) (?=(?:cicli|KB|MHz|kHz|Hz|ms|µs)\b)', '\\1' + NB, t)
    t = re.sub(r'(\(-?\d+;) (?=-?\d)', '\\1' + NB, t)
    acc = {'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'}
    t = re.sub(r"(?<![A-Za-zÀ-ÿ'])([AEIOU])'(?=[\s.,;:)]|$)", lambda m: acc[m.group(1)], t)
    return t

# ---------------------------------------------------------------- lettura dei sorgenti
def field(L, k):
    for i, l in enumerate(L[:40]):
        if l.startswith('; ' + k + ':'):
            v = [l.split(':', 1)[1].strip()]
            j = i + 1
            while j < len(L) and L[j].startswith(';  '):
                v.append(L[j][1:].strip()); j += 1
            return v
    return None

def notes(L):
    for i, l in enumerate(L):
        if l == "; NOTE D'USO":
            end = i + 2
            while not L[end].startswith('; ****'): end += 1
            body = L[i + 2:end]
            while body and body[0] == ';': body = body[1:]
            while body and body[-1] == ';': body.pop()
            return body
    return None

def contracts(L):
    out = []; i = 0
    while i < len(L):
        if L[i] == SEP and i + 1 < len(L) and re.match(r'; (MACRO|SUBROUTINE): ', L[i + 1]):
            j = i + 1
            while L[j] != SEP: j += 1
            out.append((L[i + 1].split(': ')[1].strip(), L[i:j + 1])); i = j + 1
        else:
            i += 1
    return out

def utility_rows(cont):
    rows = []
    for l in cont or []:
        m = re.match(r'^([A-Za-z_]\w*)\s{2,}(.*)$', l)
        if m: rows.append([m.group(1), m.group(2).strip()])
        elif rows: rows[-1][1] += ' ' + l.strip()
    return rows

def symbol_sections(L):
    secs = [[None, []]]; i = 0
    dash = re.compile(r'^; -{60,}$')
    while i < len(L):
        l = L[i]
        if dash.match(l) and i + 2 < len(L) and dash.match(L[i + 2]):
            secs.append([L[i + 1][2:].strip(), []]); i += 3; continue
        m = re.match(r'^\s*([A-Za-z_]\w*)\s*=\s*([^;]+?)\s*(?:;\s?(.*))?$', l)
        if m and not l.lstrip().startswith(('!', '*')): secs[-1][1].append(m.groups())
        i += 1
    return [s for s in secs if s[1]]

# ---------------------------------------------------------------- raccolta delle librerie
def modules_of(lib):
    fs = [f for f in os.listdir(os.path.join(LIBS, lib)) if f.endswith('.asm') and not TEST.match(f)]
    fs.sort(key=natural)
    if lib == 'system' and 'standard.asm' in fs:
        fs.remove('standard.asm'); fs.insert(0, 'standard.asm')
    elif lib + '.asm' in fs:
        fs.remove(lib + '.asm'); fs.insert(0, lib + '.asm')
    return fs

data = {}
for lib in sorted(d for d in os.listdir(LIBS) if os.path.isdir(os.path.join(LIBS, d)) and not d.startswith(('_', '.')) and d != 'doc_librerie'):
    mods = modules_of(lib)
    if not mods: continue
    info = []
    for f in mods:
        L = read(os.path.join(LIBS, lib, f))
        info.append(dict(file=f, L=L, contracts=contracts(L), notes=notes(L)))
    data[lib] = info
symbol_libs = sorted(l for l, ms in data.items() if not any(m['contracts'] for m in ms))
utility_libs = sorted(l for l in data if l not in symbol_libs and l != 'system')
order = (['system'] if 'system' in data else []) + utility_libs + symbol_libs

# ---------------------------------------------------------------- costruzione delle pagine
pages = []   # (chiave, html | funzione) ; ('ODD', None) = pagina dispari
toc = []     # (livello, numero, titolo, chiave)

def noteboxes(nt):
    nn = []; cur = None
    for l in nt:
        if l.startswith('; NOTA #'): cur = [l]; nn.append(cur)
        elif cur is not None: cur.append(l)
    out = ''
    for b in nn:
        while b and b[-1] == ';': b.pop()
        parts = [b[k:k + CAP - 2] for k in range(0, len(b), CAP - 2)]
        for pi, pt in enumerate(parts):
            out += f'<pre{" class=cnt" if pi else ""}>{e(chr(10).join(pt))}</pre>' + ('<p class="segue">segue...</p>' if pi < len(parts) - 1 else '')
    return out

CW = 1.911      # larghezza in mm di un carattere del carattere a larghezza fissa a 9 pt
PAD = 4.4       # rientri e bordi di una cella, in mm
TEXTW = 162.0   # larghezza dell'area di testo, in mm
MIN_DESC = 45.0 # larghezza minima della colonna Descrizione, in mm
flagged = set()
split_ok = set()   # etichette spezzate dopo un "_" (ammesso)

def widths(head, mono, rows):
    need = [max(max((len(r[j] or '') for r in rows), default=1) * CW, len(html.unescape(head[j])) * 2.3) + PAD for j in range(mono)]
    free = TEXTW - MIN_DESC
    w = [None] * mono
    todo = list(range(mono))
    while todo:
        share = free / len(todo)
        small = [j for j in todo if need[j] <= share]
        if not small:
            for j in todo: w[j] = share
            break
        for j in small:
            w[j] = need[j]; free -= need[j]; todo.remove(j)
    return w + [TEXTW - sum(w)], need

def mono_cell(t, w, ctx):
    # le etichette si spezzano solo dopo un "_"; se un segmento non sta nella colonna si segnala
    parts = re.split(r'(?<=_)', t)
    longest = max(len(p) for p in parts) * CW + PAD
    cls = 'm'
    if len(t) * CW + PAD > w + 0.01 and longest <= w + 0.01 and (ctx, t) not in split_ok:
        split_ok.add((ctx, t))
    if longest > w + 0.01:
        cls = 'm brk'
        if (ctx, t) not in flagged:
            flagged.add((ctx, t)); warnings.append(f'{ctx}: "{t}" non sta nella colonna ({longest:.0f} mm contro {w:.0f} mm), spezzata in mezzo a una parola')
    return f'<td class="{cls}">' + '<wbr>'.join(e(p) for p in parts) + '</td>'

def table(kind, head, rows, brk, ctx=''):
    mono = 1 if kind == 'u' else 2
    w, need = widths(head, mono, rows)
    cols = ''.join(f'<col style="width:{x:.2f}mm">' for x in w)
    h = ''.join(f'<th>{x}</th>' for x in head)
    body = ''
    for i, r in enumerate(rows):
        cells = ''.join(mono_cell(c or '', w[j], ctx) if j < mono else f'<td>{e(typo(c or ""))}</td>' for j, c in enumerate(r))
        body += f'<tr{" class=pbk" if i == brk else ""}>{cells}</tr>'
    return f'<table class={kind}><colgroup>{cols}</colgroup><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'

def contract_pages(lines, key, title):
    pages.append(('ODD', None))
    ch = [lines[k:k + CAP] for k in range(0, len(lines), CAP)]
    for c, t in enumerate(ch):
        hh = title + (' <small>(continua)</small>' if c else '')
        seg = '<p class="segue">segue...</p>' if c < len(ch) - 1 else ''
        pages.append((key if c == 0 else f'{key}-c{c}', f'<section class="pg"><h3>{hh}</h3><pre>{e(chr(10).join(t))}</pre>{seg}</section>'))

for li, lib in enumerate(order, 1):
    mods = data[lib]
    pages.append((f'F{li}', f'<section class="pg front"><div><p class=f1>Libreria</p><p class=f2>{e(lib)}</p></div></section>'))
    pages.append(('ODD', None))
    rows = [[m['file'], (' '.join(field(m['L'], 'DESCRIZIONE') or []))] for m in mods]
    pages.append((f'L{li}', lambda brk=None, li=li, lib=lib, rows=rows: f'<section class="pg"><h2>{li}&ensp;Libreria {e(lib)}</h2>{table("u", ["Modulo", "Descrizione"], rows, None, f"{lib} (elenco dei moduli)")}</section>'))
    toc.append((0, f'{li}', f'Libreria {lib}', f'L{li}'))
    for mi, m in enumerate(mods, 1):
        n = f'{li}.{mi}'; f = m['file']; L = m['L']
        desc = ' '.join(field(L, 'DESCRIZIONE') or [])
        pages.append(('ODD', None))
        toc.append((1, n, f, f'M{n}'))
        if lib in symbol_libs:
            secs = symbol_sections(L)
            def gen(brks=None, n=n, f=f, desc=desc, secs=secs, lib=lib):
                x = f'<h2>{n}&ensp;{e(f)}</h2><p>{e(typo(desc))}</p>'
                for si, (t, rs) in enumerate(secs):
                    if t: x += f'<h3 class=sh>{e(t)}</h3>'
                    x += table('s', ['Etichetta', 'Valore', 'Descrizione'], rs, (brks or {}).get(si), f'{lib}/{f}')
                return f'<section class="pg">{x}</section>'
            pages.append((f'M{n}', gen, [[r[0] for r in rs] for t, rs in secs], None))
            continue
        urows = utility_rows(field(L, 'CONTENUTO'))
        cs = m['contracts'][:NMAX]
        if NMAX is None and urows and len(urows) != len(m['contracts']):
            warnings.append(f'{lib}/{f}: {len(urows)} voci in CONTENUTO, {len(m["contracts"])} contratti')
        def gen(brks=None, n=n, f=f, desc=desc, urows=urows, nt=m['notes'], lib=lib):
            x = f'<h2>{n}&ensp;{e(f)}</h2><h3>{n}.1&ensp;Descrizione</h3><p>{e(typo(desc))}</p>'
            if urows: x += table('u', ['Utilit&agrave;', 'Descrizione'], urows, (brks or {}).get(0), f'{lib}/{f}')
            x += f'<h3 class=nh>{n}.2&ensp;Note d\'uso</h3>' + (noteboxes(nt) if nt else '<p>Nessuna nota in questo modulo.</p>')
            return f'<section class="pg">{x}</section>'
        pages.append((f'M{n}', gen, [[r[0] for r in urows]], n if m['notes'] else None))
        if m['notes']: toc.append((2, f'{n}.2', "Note d'uso", f'N{n}'))
        for k, (name, b) in enumerate(cs, 3):
            toc.append((2, f'{n}.{k}', name, f'C{n}.{k}'))
            contract_pages(b, f'C{n}.{k}', f'{n}.{k}&ensp;{e(name)}')

# ---------------------------------------------------------------- CSS
css = '''
@page{size:A4;margin:20mm 20mm 22mm 28mm}
@page:left{margin:20mm 28mm 22mm 20mm;@bottom-left{content:counter(page);font:10pt "DejaVu Sans"}}
@page:right{@bottom-right{content:counter(page);font:10pt "DejaVu Sans"}}
@page idx:left{@bottom-left{content:counter(page,lower-roman)}}
@page idx:right{@bottom-right{content:counter(page,lower-roman)}}
@page front{@bottom-left{content:none}@bottom-right{content:none}}
@page blank{@bottom-left{content:none}@bottom-right{content:none}}
@page cover{@bottom-left{content:none}@bottom-right{content:none}}
body{font:11pt/1.4 "DejaVu Sans",sans-serif;color:#111;margin:0}
.cover{page:cover;height:250mm;display:flex;flex-direction:column;justify-content:center}
.cover h1{font-size:26pt;margin:0 0 6mm}
.idx{page:idx}.idx h2{margin:0 0 5mm}
.idx .r{display:flex;align-items:baseline;margin:1.2mm 0;break-inside:avoid}
.idx .r .t{flex:none}.idx .r .d{flex:1;border-bottom:.6pt dotted #666;margin:0 2mm}.idx .r .p{flex:none}
.l0{font-weight:bold;margin-top:4mm}.l1{padding-left:6mm}.l2{padding-left:14mm}
.pg{break-before:page}
.front,.blank{height:250mm}
.front{page:front;display:flex;align-items:center;justify-content:center;text-align:center}.f1{font-size:22pt;margin:0}.f2{font-size:48pt;font-weight:bold;margin:4mm 0 0}
.blank{page:blank}
h2{font-size:15pt;margin:0 0 3mm}h3{font-size:13pt;margin:0 0 4mm}h3.sh{font-size:12pt;margin:7mm 0 2mm;break-after:avoid}h3.nh{margin-top:6mm}
table{border-collapse:collapse;width:100%;table-layout:fixed;margin:0 0 4mm}
thead{display:table-header-group}tr{break-inside:avoid}tr.pbk{break-before:page}
th{text-align:left;background:#e6e6e6;border:.5pt solid #777;padding:1mm 2mm;font-size:9.5pt}
td{border:.5pt solid #999;padding:.8mm 2mm;vertical-align:top;overflow-wrap:break-word;font-size:9.5pt}
td.m{font-family:"DejaVu Sans Mono",monospace;font-size:9pt}
td.m{overflow-wrap:normal;word-break:normal}td.brk{overflow-wrap:anywhere}
pre{font:9pt/11.5pt "DejaVu Sans Mono",monospace;background:#f4f4f4;border:.4pt solid #888;padding:2mm 3mm;margin:0;white-space:pre;overflow:hidden;break-inside:avoid}
pre.cnt{break-before:page}
pre+pre,.segue+pre,table+h3+pre,h3+pre.n{margin-top:11.5pt}
h3.nh+pre{margin-top:0}
.segue{text-align:right;font-style:italic;margin:2mm 0 0}
small{font-weight:normal;font-size:10pt}
'''
head = f'<!doctype html><meta charset=utf-8><style>{css}</style>'

def rend(pg, name, body):
    path = os.path.join(TMP, name + '.html')
    open(path, 'w', encoding='utf-8').write(head + body)
    pg.goto('file:///' + path.replace('\\', '/'))
    out = os.path.join(TMP, name + '.pdf')
    pg.pdf(path=out, prefer_css_page_size=True, print_background=True)
    return out

def first(h):
    return h.replace(' class="pg', ' style="break-before:auto" class="pg', 1)

# ---------------------------------------------------------------- misura e assemblaggio
final = []; pgno = {}; pos = 1
BL = '<section class="pg blank"></section>'
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page()
    def measure(h, brks=None):
        html_ = h(brks) if callable(h) else h
        r = pypdf.PdfReader(rend(pg, 'm', first(html_)))
        return html_, [(x.extract_text() or '') for x in r.pages]
    def count_on(names, text):
        return sum(1 for nm in names if re.search(r'(^|\n)' + re.escape(nm) + r'\s', text))
    for ent in pages:
        k, h = ent[0], ent[1]
        if k == 'ODD':
            if pos % 2 == 0: final.append(BL); pos += 1
            continue
        html_, tx = measure(h)
        if callable(h) and len(ent) > 2:
            tables = ent[2]; brks = {}
            for _ in range(3):
                changed = False
                for ti, names in enumerate(tables):
                    if len(names) < 4 or ti in brks: continue
                    wp = [i for i, x in enumerate(tx) if count_on(names, x)]
                    if len(wp) > 1 and count_on(names, tx[wp[-1]]) < 3:
                        brks[ti] = len(names) - 3; changed = True
                if not changed: break
                html_, tx = measure(h, brks)
            if len(ent) > 3 and ent[3]:
                nn = ent[3]
                idx = [i for i, x in enumerate(tx) if f'{nn}.2' in x and "Note d'uso" in x]
                pgno['N' + nn] = pos + (idx[0] if idx else 0)
        pgno[k] = pos; final.append(html_); pos += len(tx)
    nb_pages = pos - 1
    body = ''.join(first(x) if i == 0 else x for i, x in enumerate(final))
    body_pdf = rend(pg, 'body', body)
    assert len(pypdf.PdfReader(body_pdf).pages) == nb_pages, 'impaginazione incoerente'
    rows = ''.join(f'<div class="r l{l}"><span class=t>{n}&ensp;{e(t)}</span><span class=d></span><span class=p>{pgno[k]}</span></div>' for l, n, t, k in toc)
    idx_pdf = rend(pg, 'idx', f'<section class="idx"><h2>Indice</h2>{rows}</section>')
    cov_pdf = rend(pg, 'cov', '<section class=cover><h1>Guida di riferimento<br>ai contratti</h1></section><section class=cover style="break-before:page;height:1px"></section>')
    br.close()

n_idx = len(pypdf.PdfReader(idx_pdf).pages)
w = pypdf.PdfWriter()
for src in (cov_pdf, idx_pdf):
    for x in pypdf.PdfReader(src).pages: w.add_page(x)
if n_idx % 2: w.add_blank_page(width=595.28, height=841.89)
for x in pypdf.PdfReader(body_pdf).pages: w.add_page(x)
w.write(A.out)
print(f'{len(order)} librerie ({", ".join(order)}); indice {n_idx} pagine; corpo {nb_pages} pagine; totale {len(w.pages)}')
print(f'{len(split_ok)} etichette spezzate dopo un "_"')
for x in warnings: print('AVVISO:', x)
