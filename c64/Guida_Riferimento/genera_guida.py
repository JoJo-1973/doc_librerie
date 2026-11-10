import re,html,subprocess,pypdf
from playwright.sync_api import sync_playwright
import argparse,os,tempfile
ap=argparse.ArgumentParser(description='Bozza della guida di riferimento ai contratti (HTML con CSS di stampa -> PDF con Chromium/Playwright).')
ap.add_argument('--libs',required=True,help='cartella che contiene le librerie (es. C:\\...\\VICE\\libs)')
ap.add_argument('--out',required=True,help='file PDF da scrivere')
ap.add_argument('--max-contratti',type=int,default=0,help='0 = tutti; N = solo i primi N per modulo (bozze)')
A=ap.parse_args()
SC=tempfile.mkdtemp(prefix='guida_')
U=os.path.join(A.libs,'')
LIBS=[('mem',['mem16.asm','mem24.asm']),('math',['math_mult.asm','math_div.asm'])]
NMAX=A.max_contratti or None
e=html.escape
sep='; '+'='*78
def read(p): return open(U+p,encoding='utf-8').read().replace('\r\n','\n').split('\n')
def field(L,k):
    for i,l in enumerate(L):
        if l.startswith('; '+k+':'):
            v=[l.split(':',1)[1].strip()];j=i+1
            while L[j].startswith(';  ') : v.append(L[j][1:].strip()); j+=1
            return v
def notes(L):
    for i,l in enumerate(L):
        if l=="; NOTE D'USO":
            end=i+2
            while not L[end].startswith('; ****'): end+=1
            body=L[i+2:end]
            while body and body[0]==';': body=body[1:]
            while body and body[-1]==';': body=body[:-1]
            return body
    return None
def notepages(nt,key,h):
    nn=[];cur=None
    for l in nt:
        if l.startswith('; NOTA #'):
            cur=[l];nn.append(cur)
        elif cur is not None: cur.append(l)
    nn=[[x for x in b] for b in nn]
    for b in nn:
        while b and b[-1]==';': b.pop()
    pgs=[];cur=[];used=2   # 2 righe per l'intestazione sulla prima pagina
    def flush():
        nonlocal cur,used
        if cur: pgs.append(cur)
        cur=[];used=0
    for b in nn:
        parts=[b[k:k+CAP-2] for k in range(0,len(b),CAP-2)]
        for pi,pt in enumerate(parts):
            cost=len(pt)+1
            if used+cost>CAP-1 and cur: flush()
            cur.append((pt,pi<len(parts)-1));used+=cost+1
    flush()
    for c,items in enumerate(pgs):
        hh=f'<h3>{h}'+(' <small>(continua)</small>' if c else '')+'</h3>'
        bx=''.join(f'<pre>{e(chr(10).join(t))}</pre>'+('<p class="segue">segue...</p>' if sg else '') for t,sg in items)
        pages.append((key if c==0 else key+'-c%d'%c,f'<section class="pg">{hh}{bx}</section>'))
def contracts(L):
    out=[];i=0
    while i<len(L):
        if L[i]==sep and re.match(r'; (MACRO|SUBROUTINE): ',L[i+1]):
            j=i+1
            while L[j]!=sep: j+=1
            out.append((L[i+1].split(': ')[1],L[i:j+1]));i=j+1
        else:i+=1
    return out
CAP=52
pages=[];toc=[]   # toc: (livello, numero, titolo, chiave)
def page(key,h,txt=None,extra=''):
    pages.append((key,f'<section class="pg"><h3 id="{key}">{h}</h3>{extra}'+(txt or '')+'</section>'))
def odd(k):
    if (len(pages)+1)%2==0: pages.append(('B'+k,'<section class="pg blank"></section>'))
def box(lines,key,h,tag=''):
    odd(key)
    ch=[lines[k:k+CAP] for k in range(0,len(lines),CAP)]
    for c,t in enumerate(ch):
        hh=h+(' <small>(continua)</small>' if c else '')
        seg='<p class="segue">segue...</p>' if c<len(ch)-1 else ''
        pages.append((key if c==0 else key+'-c%d'%c,f'<section class="pg"><h3>{hh}</h3><pre>{e(chr(10).join(t))}</pre>{seg}</section>'))
for li,(lib,files) in enumerate(LIBS,1):
    pages.append((f'F{li}',f'<section class="pg front"><div><p class=f1>Libreria</p><p class=f2>{lib}</p></div></section>'))
    if (len(pages)+1)%2==0: pages.append((f'B{li}','<section class="pg blank"></section>'))
    mods=''.join(f'<div class=mr><span class=mn>{f}</span><span class=md>{e(" ".join(field(read(lib+"/"+f),"DESCRIZIONE")))}</span></div>' for f in files)
    pages.append((f'L{li}',f'<section class="pg"><h2>{li}&ensp;Libreria {lib}</h2>{mods}</section>'))
    toc.append((0,f'{li}',f'Libreria {lib}',f'L{li}'))
    for mi,f in enumerate(files,1):
        L=read(f'{lib}/{f}');n=f'{li}.{mi}'
        nt=notes(L);cs=contracts(L)[:NMAX]
        cont=field(L,'CONTENUTO')
        extra=f'<h3>{n}.1&ensp;Descrizione</h3><p>{e(" ".join(field(L,"DESCRIZIONE")))}</p><p class=cont>{e(chr(10).join(cont))}</p>'
        extra+=f'<h3>{n}.2&ensp;Note d\'uso</h3><p>'+('Vedi le pagine seguenti.' if nt else 'Nessuna nota in questo modulo.')+'</p>'
        odd(f'M{n}')
        pages.append((f'M{n}',f'<section class="pg"><h2 id="x">{n}&ensp;{f}</h2>{extra}</section>'))
        toc.append((1,n,f,f'M{n}'))
        if nt:
            toc.append((2,f'{n}.2','Note d\'uso',f'N{n}'))
            notepages(nt,f'N{n}',f'{n}.2&ensp;Note d\'uso')
        for k,(name,b) in enumerate(cs,3):
            toc.append((2,f'{n}.{k}',name,f'C{n}.{k}'))
            box(b,f'C{n}.{k}',f'{n}.{k}&ensp;{e(name)}')
css='''
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
.idx .r{display:flex;align-items:baseline;margin:1.2mm 0}
.idx .r .t{flex:none}.idx .r .d{flex:1;border-bottom:.6pt dotted #666;margin:0 2mm}.idx .r .p{flex:none}
.l0{font-weight:bold;margin-top:4mm}.l1{padding-left:6mm}.l2{padding-left:14mm}
.pg{break-before:page;height:255mm}
.front{page:front;display:flex;align-items:center;justify-content:center;text-align:center}.f1{font-size:22pt;margin:0}.f2{font-size:48pt;font-weight:bold;margin:4mm 0 0}
.blank{page:blank}
.mr{display:flex;gap:6mm;margin:0 0 4mm}.mn{flex:none;width:34mm;font:9pt/1.5 'DejaVu Sans Mono',monospace;font-weight:bold}.md{flex:1}
h2{font-size:15pt;margin:0 0 3mm}h3{font-size:13pt;margin:0 0 4mm}
pre{font:9pt/11.5pt "DejaVu Sans Mono",monospace;background:#f4f4f4;border:.4pt solid #888;padding:2mm 3mm;margin:0;white-space:pre;overflow:hidden}
pre+pre,.segue+pre{margin-top:11.5pt}
.segue{text-align:right;font-style:italic;margin:2mm 0 0}
.cont{font:9pt/11.5pt "DejaVu Sans Mono",monospace;white-space:pre}
small{font-weight:normal;font-size:10pt}
'''
head=f'<!doctype html><meta charset=utf-8><style>{css}</style>'
def rend(name,body):
    open(f'{SC}/{name}.html','w',encoding='utf-8').write(head+body)
    with sync_playwright() as p:
        b=p.chromium.launch();pg=b.new_page();pg.goto(f'file://{SC}/{name}.html');pg.pdf(path=f'{SC}/{name}.pdf',prefer_css_page_size=True,print_background=True);b.close()
    return len(pypdf.PdfReader(f'{SC}/{name}.pdf').pages)
rend('cov2','<section class=cover><h1>Guida di riferimento<br>ai contratti</h1><p>Bozza di struttura — campione: librerie mem e math, due moduli ciascuna</p></section><section class=cover style="break-before:page;height:1px"></section>')
body=''.join(h.replace(' class="pg"',' class="pg" style="break-before:auto"',1) if i==0 else h for i,(k,h) in enumerate(pages))
rend('body2',body)
# numeri di pagina del corpo
R=pypdf.PdfReader(SC+'/body2.pdf');txt=[pg.extract_text() or '' for pg in R.pages]
def find(key,i0):
    pass
pgno={}
keys=[k for k,_ in pages]
for i,k in enumerate(keys): pgno[k]=i+1   # una pagina HTML = una pagina PDF (verificato sotto)
assert len(keys)==len(txt),(len(keys),len(txt))
def idx():
    rows=''.join(f'<div class="r l{l}"><span class=t>{n}&ensp;{e(t)}</span><span class=d></span><span class=p>{pgno[k]}</span></div>' for l,n,t,k in toc)
    return f'<section class="idx"><h2>Indice</h2>{rows}</section>'
ni=rend('idx2',idx())
w=pypdf.PdfWriter()
for f in ('cov2',):
    for pg in pypdf.PdfReader(f'{SC}/{f}.pdf').pages: w.add_page(pg)
for pg in pypdf.PdfReader(SC+'/idx2.pdf').pages: w.add_page(pg)
if ni%2: w.add_blank_page(width=595.28,height=841.89)
for pg in R.pages: w.add_page(pg)
w.write(A.out)
print('indice pagine',ni,'corpo',len(keys))
