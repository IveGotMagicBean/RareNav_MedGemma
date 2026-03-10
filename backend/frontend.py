HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0"/>
<title>RareNav — Rare Disease AI Navigator</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f8f9fa;--surface:white;--surface2:#f1f3f5;--border:#e9ecef;--border2:#dee2e6;
  --text:#212529;--text2:#495057;--text3:#6c757d;--text4:#adb5bd;
  --blue:#2563eb;--blue-l:#dbeafe;--blue-d:#1d4ed8;
  --teal:#0d9488;--rose:#e11d48;--rose-l:#ffe4e6;
  --amber:#d97706;--amber-l:#fef3c7;--violet:#7c3aed;--violet-l:#ede9fe;
  --green:#059669;--green-l:#d1fae5;
  --shadow-sm:0 1px 2px rgba(0,0,0,.06);
  --shadow:0 4px 6px -1px rgba(0,0,0,.08),0 2px 4px -1px rgba(0,0,0,.04);
  --shadow-md:0 10px 15px -3px rgba(0,0,0,.08);
  --shadow-lg:0 20px 25px -5px rgba(0,0,0,.08);
  --r:12px;--r-sm:8px;--r-lg:16px;--r-xl:20px;
  --nav-h:60px;--bottom-nav-h:64px;
  --font:'Inter',system-ui,sans-serif;--serif:'Instrument Serif',Georgia,serif;
}
[data-theme="dark"]{
  --bg:#0f1117;--surface:#1a1d27;--surface2:#242736;--border:#2d3148;--border2:#363b52;
  --text:#e8eaf0;--text2:#b0b8d0;--text3:#7880a0;--text4:#4a5070;
  --blue:#4f8ef7;--blue-l:rgba(79,142,247,.15);--blue-d:#6aa0ff;
  --blue-l-solid:#1a2545;
  --rose-l:rgba(225,29,72,.15);--amber-l:rgba(217,119,6,.15);
  --violet-l:rgba(124,58,237,.15);--green-l:rgba(5,150,105,.15);
  --shadow-sm:0 1px 2px rgba(0,0,0,.3);
  --shadow:0 4px 6px -1px rgba(0,0,0,.4);
  --shadow-md:0 10px 15px -3px rgba(0,0,0,.5);
  --shadow-lg:0 20px 25px -5px rgba(0,0,0,.6);
}
html{scroll-behavior:smooth;font-size:15px}
body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh;-webkit-font-smoothing:antialiased;transition:background .2s,color .2s}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--border2);border-radius:99px}
button{cursor:pointer;font-family:var(--font)}input,textarea{font-family:var(--font)}a{color:var(--blue);text-decoration:none}

/* ── NAV ── */
#nav{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(255,255,255,.96);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);height:var(--nav-h);transition:background .2s,border-color .2s}
[data-theme="dark"] #nav{background:rgba(26,29,39,.96)}
#nav-inner{max-width:1400px;margin:0 auto;padding:0 16px;height:100%;display:flex;align-items:center;gap:4px}
#logo{display:flex;align-items:center;gap:9px;text-decoration:none;flex-shrink:0;margin-right:4px}
#logo-mark{width:32px;height:32px;background:linear-gradient(135deg,var(--blue),var(--teal));border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px}
#logo-text{font-size:16px;font-weight:700;color:var(--text);letter-spacing:-.03em}
#logo-sub{font-size:10px;color:var(--text4)}
.nsep{width:1px;height:18px;background:var(--border);margin:0 2px;flex-shrink:0}
.nbtn{display:flex;align-items:center;gap:5px;padding:5px 10px;border-radius:7px;font-size:13px;font-weight:500;color:var(--text3);background:transparent;border:none;transition:all .15s;white-space:nowrap}
.nbtn:hover{background:var(--surface2);color:var(--text)}
.nbtn.active{background:var(--blue-l);color:var(--blue)}
#nav-space{flex:1}
/* compact SVG icon buttons — subtle, not emoji */
.nic{width:32px;height:32px;border-radius:7px;border:none;background:transparent;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--text4);transition:all .15s;flex-shrink:0;text-decoration:none;padding:0}
.nic:hover{background:var(--surface2);color:var(--text2)}
.nic.on{background:var(--blue-l);color:var(--blue)}
.nic svg{display:block}
/* tool group — visually lighter than main nav */
.nav-tools{display:flex;align-items:center;gap:1px}
.clin-pill{padding:4px 10px;border-radius:99px;font-size:11px;font-weight:600;background:var(--surface2);color:var(--text3);border:1px solid var(--border);transition:all .15s;cursor:pointer;letter-spacing:.01em}
.clin-pill:hover{background:var(--violet-l);color:var(--violet);border-color:transparent}
.clin-pill.on{background:var(--violet);color:white;border-color:var(--violet)}
#status-pill{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--text3);padding:4px 9px;border-radius:6px;background:var(--surface2);border:1px solid var(--border);white-space:nowrap}
.sdot{width:6px;height:6px;border-radius:50%;background:var(--text4);flex-shrink:0}
.sdot.ok{background:var(--green)}.sdot.warn{background:var(--amber)}

/* ── APP ── */
#app{padding-top:var(--nav-h);min-height:100vh}
.page{display:none}.page.active{display:block}
#page-home{display:none}
#page-home.active{display:flex;height:calc(100vh - var(--nav-h))}

/* ── LEFT PANEL ── */
#left-panel{width:340px;flex-shrink:0;border-right:1px solid var(--border);background:var(--surface);display:flex;flex-direction:column;overflow-y:auto;transition:transform .3s,background .2s}
.lp-head{padding:20px 18px 14px;border-bottom:1px solid var(--border)}
.lp-head h2{font-size:15px;font-weight:700;color:var(--text);margin-bottom:2px}
.lp-head p{font-size:11px;color:var(--text4);line-height:1.4}
#caps{padding:10px;flex:1}
.cap-grp{margin-bottom:2px}
.cap-grp-lbl{font-size:9px;font-weight:700;color:var(--text4);letter-spacing:.1em;padding:5px 8px 3px}
.cap-item{display:flex;align-items:flex-start;gap:9px;padding:8px 9px;border-radius:8px;background:transparent;border:none;width:100%;text-align:left;cursor:pointer;transition:background .12s}
.cap-item:hover{background:var(--surface2)}
.cap-item.hi{background:rgba(37,99,235,.07);border:1px solid rgba(37,99,235,.12)}
[data-theme="dark"] .cap-item.hi{background:rgba(79,142,247,.08);border-color:rgba(79,142,247,.15)}
.cap-item.hi:hover{background:rgba(37,99,235,.12)}
.ci-ico{width:30px;height:30px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.ci-title{font-size:12px;font-weight:600;color:var(--text);line-height:1.2;margin-bottom:1px}
.ci-desc{font-size:10px;color:var(--text4);line-height:1.3}
.ci-new{font-size:8px;font-weight:700;background:var(--blue);color:white;padding:1px 4px;border-radius:3px;margin-left:3px;vertical-align:middle}
.lp-foot{padding:12px 14px;border-top:1px solid var(--border);margin-top:auto}
.disc{font-size:10px;color:var(--text4);line-height:1.5;text-align:center}

/* ── CHAT RIGHT ── */
#chat-right{flex:1;display:flex;flex-direction:column;overflow:hidden;background:var(--bg);min-width:0;transition:background .2s}
#chat-scroll{flex:1;overflow-y:auto;padding:24px 0}
#chat-inner{max-width:700px;width:100%;margin:0 auto;padding:0 20px}
#welcome{text-align:center;padding:36px 0 28px}
.w-ico{font-size:42px;margin-bottom:12px}
.w-title{font-size:24px;font-weight:300;color:var(--text);font-family:var(--serif);margin-bottom:7px}
.w-title em{font-style:italic;color:var(--blue)}
.w-sub{font-size:13px;color:var(--text3);max-width:360px;margin:0 auto 24px;line-height:1.6}
.starters{display:grid;grid-template-columns:1fr 1fr;gap:7px;max-width:500px;margin:0 auto}
.starter{padding:11px 13px;border-radius:var(--r);background:var(--surface);border:1px solid var(--border);text-align:left;cursor:pointer;transition:all .18s;box-shadow:var(--shadow-sm)}
.starter:hover{border-color:var(--blue);box-shadow:var(--shadow);transform:translateY(-1px)}
.si-ico{font-size:16px;margin-bottom:4px;display:block}
.si-txt{font-size:11px;color:var(--text2);font-weight:500;line-height:1.4}
#msgs{display:flex;flex-direction:column;gap:16px}
.msg{display:flex;gap:9px;animation:fadeUp .25s ease}
.msg.user{flex-direction:row-reverse}
.av{width:28px;height:28px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700}
.av-ai{background:linear-gradient(135deg,var(--blue),var(--teal));color:white}
.av-u{background:var(--text2);color:white}
.bub{max-width:77%;padding:11px 15px;border-radius:var(--r-lg);font-size:13px;line-height:1.7}
.bub.user{background:var(--blue);color:white;border-radius:var(--r-lg) 4px var(--r-lg) var(--r-lg)}
.bub.ai{background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px var(--r-lg) var(--r-lg) var(--r-lg);box-shadow:var(--shadow-sm)}
.bub.ai .prose h1,.bub.ai .prose h2{font-size:14px;font-weight:700;color:var(--text);margin:12px 0 4px}
.bub.ai .prose h3{font-size:13px;font-weight:600;color:var(--text2);margin:9px 0 3px}
.bub.ai .prose p{margin-bottom:6px}
.bub.ai .prose ul{padding-left:15px;margin:4px 0 7px}
.bub.ai .prose li{margin-bottom:2px}
.bub.ai .prose strong{font-weight:600;color:var(--text)}
.mfoot{margin-top:6px;display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.mmeta{font-size:10px;color:var(--text4)}
.cd-btn{font-size:10px;padding:2px 7px;border-radius:99px;background:var(--surface2);border:1px solid var(--border);color:var(--text3);cursor:pointer;transition:all .12s}
.cd-btn:hover,.cd-btn.on{background:var(--blue-l);border-color:rgba(37,99,235,.2);color:var(--blue)}
.typing{display:flex;gap:4px;padding:12px 14px;align-items:center}
.td{width:6px;height:6px;background:var(--text4);border-radius:50%;animation:tdB .9s ease infinite}
.td:nth-child(2){animation-delay:.15s}.td:nth-child(3){animation-delay:.3s}

/* ── INPUT ── */
#input-wrap{background:var(--surface);border-top:1px solid var(--border);padding:12px 20px;max-width:700px;width:100%;margin:0 auto;align-self:center;transition:background .2s}
#ctx-bar{display:none;align-items:center;gap:6px;padding:5px 9px;background:var(--blue-l);border-radius:7px;margin-bottom:8px;font-size:11px;color:var(--blue)}
[data-theme="dark"] #ctx-bar{background:rgba(79,142,247,.12);color:var(--blue-d)}
.ctx-pill{background:var(--surface);border:1px solid rgba(37,99,235,.25);border-radius:99px;padding:2px 7px;font-size:10px;font-weight:500;color:var(--blue)}
#irow{display:flex;gap:7px;align-items:flex-end}
#up-btn{width:36px;height:36px;border-radius:7px;border:1px solid var(--border);background:var(--surface);display:flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;transition:all .15s;flex-shrink:0}
#up-btn:hover{border-color:var(--blue);background:var(--blue-l)}
#cin{flex:1;border:1px solid var(--border2);border-radius:var(--r);padding:8px 12px;font-size:13px;resize:none;outline:none;line-height:1.5;min-height:38px;max-height:110px;transition:border-color .15s,background .2s;background:var(--bg);color:var(--text)}
#cin:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(37,99,235,.07)}
#cin::placeholder{color:var(--text4)}
#send-btn{width:36px;height:36px;border-radius:7px;background:var(--blue);border:none;color:white;font-size:16px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:background .15s;flex-shrink:0}
#send-btn:hover{background:var(--blue-d)}
#send-btn:disabled{background:var(--border2);cursor:not-allowed}
.ihint{font-size:10px;color:var(--text4);margin-top:4px;text-align:center}

/* ── CTX PANEL ── */
#ctx-panel{display:none;width:240px;flex-shrink:0;border-left:1px solid var(--border);background:var(--surface);overflow-y:auto;padding:16px;transition:background .2s}
#ctx-panel.show{display:block}
.ctx-lbl{font-size:9px;font-weight:700;color:var(--text4);letter-spacing:.1em;margin-bottom:7px}
.ctx-vcard{padding:10px;border-radius:8px;border:1px solid var(--border);background:var(--surface2);margin-bottom:9px}
.ctx-act{width:100%;padding:7px 9px;border-radius:7px;border:1px solid var(--border);background:var(--surface);font-size:11px;font-weight:500;color:var(--text2);cursor:pointer;text-align:left;margin-bottom:4px;transition:all .12s}
.ctx-act:hover{background:var(--blue-l);border-color:rgba(37,99,235,.2);color:var(--blue)}
.ctx-act.p{background:var(--blue);color:white;border-color:var(--blue)}
.ctx-act.p:hover{background:var(--blue-d)}

/* ── SHARED PAGE ── */
.pg-head{padding:24px 24px 18px;border-bottom:1px solid var(--border);background:var(--surface);transition:background .2s}
.pg-head h1{font-size:22px;font-weight:700;color:var(--text);margin-bottom:3px}
.pg-head p{font-size:13px;color:var(--text3)}
.pg-body{max-width:1140px;margin:0 auto;padding:20px 24px}
.sbar{display:flex;gap:7px;margin-bottom:14px;flex-wrap:wrap}
.si-w{position:relative;flex:1;min-width:150px}
.si-ico2{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--text4);font-size:14px}
.sinput{width:100%;padding:8px 11px 8px 32px;border:1px solid var(--border2);border-radius:var(--r-sm);font-size:13px;outline:none;transition:border-color .15s,background .2s;background:var(--surface);color:var(--text)}
.sinput:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(37,99,235,.07)}
.sinput::placeholder{color:var(--text4)}
.fsel{padding:8px 11px;border:1px solid var(--border2);border-radius:var(--r-sm);font-size:12px;color:var(--text2);background:var(--surface);outline:none;cursor:pointer;transition:background .2s}
.sbtn{padding:8px 16px;background:var(--blue);color:white;border:none;border-radius:var(--r-sm);font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;transition:background .15s}
.sbtn:hover{background:var(--blue-d)}
.rmeta{font-size:12px;color:var(--text3);margin-bottom:11px;display:flex;justify-content:space-between;align-items:center}
.ibox{padding:9px 12px;border-radius:7px;font-size:11px;display:flex;gap:6px;line-height:1.5;margin-bottom:12px}
.ib{background:var(--blue-l);border:1px solid rgba(37,99,235,.15);color:var(--blue)}
.ia{background:var(--amber-l);border:1px solid rgba(217,119,6,.15);color:#92400e}
[data-theme="dark"] .ia{color:#fbbf24}

/* ── VARIANT TABLE ── */
#page-variants{background:var(--bg);min-height:calc(100vh - var(--nav-h));transition:background .2s}
.vtbl{width:100%;border-collapse:collapse}
.vtbl th{text-align:left;padding:8px 12px;font-size:10px;font-weight:600;color:var(--text3);letter-spacing:.06em;border-bottom:2px solid var(--border);background:var(--surface2);white-space:nowrap}
.vtbl td{padding:10px 12px;border-bottom:1px solid var(--border);font-size:12px;vertical-align:middle}
.vtbl tr:hover td{background:var(--surface2);cursor:pointer}
.vtbl tr.sel td{background:var(--blue-l)}
[data-theme="dark"] .vtbl tr.sel td{background:rgba(79,142,247,.1)}
.gtag{font-family:monospace;font-size:11px;font-weight:700;color:var(--blue);background:var(--blue-l);padding:2px 6px;border-radius:4px}
.sbadge{display:inline-flex;align-items:center;padding:2px 7px;border-radius:99px;font-size:10px;font-weight:600;white-space:nowrap}
.sp{background:var(--rose-l);color:var(--rose)}
.slp{background:var(--amber-l);color:var(--amber)}
.sv{background:var(--violet-l);color:var(--violet)}
.sb2{background:var(--green-l);color:var(--green)}
.sc{background:var(--surface2);color:var(--text3)}
.pheno{font-size:11px;color:var(--text3);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.vname{font-family:monospace;font-size:10px;color:var(--text3);max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* ── DRAWER ── */
#vdrawer{position:fixed;right:0;top:var(--nav-h);bottom:0;width:360px;background:var(--surface);border-left:1px solid var(--border);box-shadow:var(--shadow-lg);transform:translateX(100%);transition:transform .3s cubic-bezier(.4,0,.2,1),background .2s;overflow-y:auto;z-index:50}
#vdrawer.open{transform:translateX(0)}
#vdh{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;justify-content:space-between;position:sticky;top:0;background:var(--surface);z-index:1;transition:background .2s}
.vdclose{width:28px;height:28px;border-radius:6px;border:1px solid var(--border);background:transparent;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--text3)}
.vdclose:hover{background:var(--surface2)}
#vdb{padding:16px 20px}
.drow{display:flex;gap:7px;margin-bottom:10px}
.dlbl{font-size:10px;font-weight:600;color:var(--text4);letter-spacing:.05em;width:90px;flex-shrink:0;padding-top:1px}
.dval{font-size:12px;color:var(--text);flex:1;word-break:break-word}
.dval.mono{font-family:monospace;font-size:10px;line-height:1.5}
.dsec{margin-bottom:16px}
.dsec-t{font-size:10px;font-weight:600;color:var(--text3);margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid var(--border)}
.elink{display:flex;align-items:center;justify-content:space-between;padding:7px 10px;border:1px solid var(--border);border-radius:7px;font-size:11px;color:var(--text2);text-decoration:none;margin-bottom:4px;transition:all .12s}
.elink:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-l)}
.ask-btn{width:100%;padding:10px;background:var(--blue);color:white;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;margin-top:5px;transition:background .15s}
.ask-btn:hover{background:var(--blue-d)}

/* ── DISEASE PAGE ── */
#page-diseases{background:var(--bg);min-height:calc(100vh - var(--nav-h));transition:background .2s}
.cat-tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.ctab{padding:4px 12px;border-radius:99px;font-size:11px;font-weight:500;border:1px solid var(--border);background:var(--surface);color:var(--text3);cursor:pointer;transition:all .15s}
.ctab:hover{border-color:var(--blue);color:var(--blue)}
.ctab.on{background:var(--blue);color:white;border-color:var(--blue)}
.dgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:12px}
.dcard{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:16px;cursor:pointer;transition:all .18s;box-shadow:var(--shadow-sm)}
.dcard:hover{border-color:var(--blue);box-shadow:var(--shadow-md);transform:translateY(-2px)}
.dico{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:10px}
.dname{font-size:13px;font-weight:700;color:var(--text);margin-bottom:3px}
.dgene{font-family:monospace;font-size:10px;color:var(--blue);background:var(--blue-l);padding:2px 6px;border-radius:4px;display:inline-block;margin-bottom:6px}
.dmeta{font-size:10px;color:var(--text4);margin-bottom:6px}
.dtags{display:flex;flex-wrap:wrap;gap:3px}
.dtag{font-size:9px;padding:2px 6px;border-radius:99px;background:var(--surface2);color:var(--text3)}

/* ── DISEASE MODAL ── */
#dmodal{display:none;position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.4);backdrop-filter:blur(4px);align-items:center;justify-content:center;padding:16px}
#dmodal.open{display:flex}
#dmbox{background:var(--surface);border-radius:var(--r-xl);width:100%;max-width:580px;max-height:88vh;overflow-y:auto;box-shadow:var(--shadow-lg);transition:background .2s}
#dmhdr{padding:20px 24px 16px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--surface);border-radius:var(--r-xl) var(--r-xl) 0 0;z-index:1;display:flex;justify-content:space-between;align-items:flex-start;transition:background .2s}
#dmbody{padding:20px 24px}
.dgrid2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
.dcell{padding:10px;border-radius:7px;background:var(--surface2);border:1px solid var(--border)}
.dcl{font-size:9px;font-weight:600;color:var(--text4);letter-spacing:.06em;margin-bottom:2px}
.dcv{font-size:12px;color:var(--text);font-weight:500}
.dmsec{margin-bottom:14px}
.dmsect{font-size:10px;font-weight:600;color:var(--text3);letter-spacing:.06em;margin-bottom:6px}
.chiplist{display:flex;flex-wrap:wrap;gap:4px}
.chip{padding:3px 8px;border-radius:99px;font-size:11px}
.chip-b{background:var(--blue-l);color:var(--blue)}
.chip-g{background:var(--green-l);color:var(--green)}
.chip-gr{background:var(--surface2);color:var(--text2)}
#dmfoot{padding:12px 24px;border-top:1px solid var(--border);display:flex;gap:7px;justify-content:flex-end;background:var(--surface);border-radius:0 0 var(--r-xl) var(--r-xl);transition:background .2s}
.closex{width:28px;height:28px;border-radius:6px;border:1px solid var(--border);background:transparent;cursor:pointer;font-size:13px;color:var(--text3);display:flex;align-items:center;justify-content:center}
.closex:hover{background:var(--surface2)}

/* ── UPLOAD MODAL ── */
#umodal{display:none;position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.4);backdrop-filter:blur(4px);align-items:center;justify-content:center;padding:16px}
#umodal.open{display:flex}
#ubox{background:var(--surface);border-radius:var(--r-xl);padding:24px;width:440px;max-width:100%;box-shadow:var(--shadow-lg);transition:background .2s}
#ubox h3{font-size:16px;font-weight:700;color:var(--text);margin-bottom:4px}
#ubox>p{font-size:12px;color:var(--text3);margin-bottom:18px;line-height:1.5}
#dropzone{border:2px dashed var(--border2);border-radius:var(--r);padding:28px;text-align:center;cursor:pointer;transition:all .18s;background:var(--bg)}
#dropzone:hover,#dropzone.drag{border-color:var(--blue);background:var(--blue-l)}
.dz-ico{font-size:28px;margin-bottom:8px}
.dz-txt{font-size:13px;font-weight:500;color:var(--text2);margin-bottom:2px}
.dz-sub{font-size:11px;color:var(--text4)}
#fin{display:none}
#uprev{display:none;margin-top:12px;padding:9px 12px;border-radius:7px;background:var(--green-l);border:1px solid rgba(5,150,105,.2);font-size:12px;color:var(--green)}
.mact{display:flex;gap:7px;margin-top:16px;justify-content:flex-end}
.btn{display:inline-flex;align-items:center;gap:5px;padding:8px 16px;border-radius:var(--r-sm);font-size:12px;font-weight:600;border:none;cursor:pointer;transition:all .15s}
.btnp{background:var(--blue);color:white}.btnp:hover{background:var(--blue-d)}
.btns{background:var(--surface2);color:var(--text2);border:1px solid var(--border)}.btns:hover{background:var(--border2)}
.btn:disabled{opacity:.45;cursor:not-allowed}

/* ── INFO MODAL (video / docs) ── */
#info-modal{display:none;position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.45);backdrop-filter:blur(4px);align-items:center;justify-content:center;padding:16px}
#info-modal.open{display:flex}
#info-box{background:var(--surface);border-radius:var(--r-xl);width:100%;max-width:900px;height:92vh;box-shadow:var(--shadow-lg);overflow:hidden;display:flex;flex-direction:column;transition:background .2s}
#info-hdr{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-shrink:0}
#info-hdr h3{font-size:15px;font-weight:600;color:var(--text);display:flex;align-items:center;gap:8px}
#info-body{flex:1;overflow:hidden;display:flex;flex-direction:column;min-height:0}
.info-embed{flex:1;width:100%;border:none;display:block;min-height:0;height:100%}
.info-embed-video{width:100%;aspect-ratio:16/9;background:#000;display:block}
.info-empty{padding:40px 24px;text-align:center;color:var(--text3)}
.info-empty-ico{font-size:36px;margin-bottom:12px}
.info-empty p{font-size:13px;line-height:1.6}

/* ── PHONE PREVIEW MODAL ── */
#phone-modal{display:none;position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.75);backdrop-filter:blur(8px);align-items:center;justify-content:center}
#phone-modal.open{display:flex}
.phone-frame{width:375px;height:720px;border-radius:44px;background:#111;box-shadow:0 0 0 12px #222,0 0 0 13px #333,0 30px 80px rgba(0,0,0,.8);overflow:hidden;position:relative;flex-shrink:0}
.phone-notch{position:absolute;top:0;left:50%;transform:translateX(-50%);width:120px;height:30px;background:#111;border-radius:0 0 18px 18px;z-index:10}
.phone-iframe-wrap{position:absolute;inset:0;border-radius:44px;overflow:hidden}
.phone-iframe-wrap iframe{width:100%;height:100%;border:none;transform-origin:top left}
#phone-close{position:absolute;top:16px;right:16px;width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.15);border:none;color:white;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center}
#phone-close:hover{background:rgba(255,255,255,.25)}
.phone-label{color:rgba(255,255,255,.6);font-size:12px;margin-top:16px;text-align:center}

/* ── EMPTY / LOADING ── */
.empty{text-align:center;padding:50px 20px;color:var(--text4)}
.empty-ico{font-size:32px;margin-bottom:9px}
.ldrow{display:flex;align-items:center;gap:8px;padding:18px;color:var(--text4);font-size:12px}
.spin{width:16px;height:16px;border:2px solid var(--border2);border-top-color:var(--blue);border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0}

/* ── MOBILE BOTTOM NAV ── */
#mobile-nav{display:none;position:fixed;bottom:0;left:0;right:0;z-index:100;background:var(--surface);border-top:1px solid var(--border);height:var(--bottom-nav-h);transition:background .2s}
.mnav-inner{display:flex;height:100%}
.mnav-btn{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;border:none;background:transparent;cursor:pointer;color:var(--text3);font-size:10px;font-weight:500;transition:color .15s;padding-bottom:env(safe-area-inset-bottom,0px)}
.mnav-btn .mico{display:flex;align-items:center;justify-content:center;width:22px;height:22px}
.mnav-btn.active{color:var(--blue)}
.mnav-btn.active .mico svg{transform:scale(1.1)}

/* ── LEFT DRAWER (mobile) ── */
#left-drawer{display:none;position:fixed;inset:0;z-index:150}
#left-drawer.open{display:block}
.ld-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.4);backdrop-filter:blur(2px)}
.ld-panel{position:absolute;left:0;top:0;bottom:0;width:300px;background:var(--surface);box-shadow:var(--shadow-lg);overflow-y:auto;display:flex;flex-direction:column;animation:slideRight .25s ease;transition:background .2s}
@keyframes slideRight{from{transform:translateX(-100%)}to{transform:translateX(0)}}

/* ── ANIMATIONS ── */
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes tdB{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}

/* ── RESPONSIVE ── */
@media(max-width:768px){
  :root{--nav-h:52px}
  #left-panel{display:none}
  #ctx-panel{display:none!important}
  #mobile-nav{display:block}
  #app{padding-bottom:var(--bottom-nav-h)}
  #page-home.active{height:auto;min-height:calc(100vh - var(--nav-h) - var(--bottom-nav-h))}
  #chat-right{height:calc(100vh - var(--nav-h) - var(--bottom-nav-h))}
  #input-wrap{padding:10px 14px}
  #chat-inner{padding:0 14px}
  .starters{grid-template-columns:1fr}
  .pg-body{padding:14px 14px}
  .sbar{gap:5px}
  .sinput{font-size:14px}
  .dgrid{grid-template-columns:1fr}
  #vdrawer{width:100%;top:var(--nav-h);border-left:none;border-top:1px solid var(--border)}
  /* on mobile: hide tool icons and text labels, keep main nav compact */
  .nav-tools{display:none}
  .nsep{display:none}
  .clin-pill{display:none}
  #status-pill{display:none}
  .nlab{display:none}
  #logo-sub{display:none}
  #nav-inner{gap:2px;padding:0 12px}
}
@media(min-width:769px){
  #mobile-nav{display:none!important}
  #left-drawer{display:none!important}
}

/* ── AGENT TRACE ── */
.agent-trace{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.trace-tag{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:99px;font-size:10px;font-weight:600;background:var(--surface2);border:1px solid var(--border);color:var(--text3)}
.trace-tag.ok{background:var(--green-l);border-color:rgba(5,150,105,.2);color:var(--green)}
.trace-tag.error{background:var(--rose-l);border-color:rgba(225,29,72,.15);color:var(--rose)}
.trace-tag.empty{background:var(--amber-l);border-color:rgba(217,119,6,.15);color:var(--amber)}
/* ── FOLLOWUP OPTIONS ── */
.followup-wrap{margin-top:8px;padding:10px 12px;border-radius:var(--r);background:var(--blue-l);border:1px solid rgba(37,99,235,.15)}
[data-theme="dark"] .followup-wrap{background:rgba(79,142,247,.08);border-color:rgba(79,142,247,.2)}
.followup-q{font-size:12px;color:var(--text2);margin-bottom:7px;font-weight:500}
.followup-opts{display:flex;flex-wrap:wrap;gap:5px}
.fopt-btn{padding:5px 12px;border-radius:99px;border:1px solid rgba(37,99,235,.3);background:var(--surface);font-size:11px;font-weight:500;color:var(--blue);cursor:pointer;transition:all .15s}
.fopt-btn:hover{background:var(--blue);color:white;border-color:var(--blue)}

/* ── AGENT TOOL CALLS ── */
.tool-calls{display:flex;flex-direction:column;gap:5px;margin-bottom:10px}
.tool-card{display:flex;align-items:center;gap:8px;padding:7px 12px;border-radius:8px;background:var(--surface2);border:1px solid var(--border);font-size:12px;color:var(--text2);animation:fadeUp .2s ease}
.tool-card.running{background:var(--blue-l);border-color:rgba(37,99,235,.2);color:var(--blue)}
[data-theme="dark"] .tool-card.running{background:rgba(79,142,247,.1)}
.tool-card.ok{background:var(--green-l);border-color:rgba(5,150,105,.2);color:var(--green)}
.tool-card.empty{background:var(--amber-l);border-color:rgba(217,119,6,.15);color:var(--amber)}
.tool-card.error{background:var(--rose-l);border-color:rgba(225,29,72,.15);color:var(--rose)}
.tool-ico{font-size:14px;flex-shrink:0}
.tool-label{font-weight:600;flex:1}
.tool-detail{font-size:10px;opacity:.75;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:160px}
.tool-spin{width:12px;height:12px;border:2px solid currentColor;border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite;flex-shrink:0;opacity:.7}
/* ── STREAMING ── */
.stream-cursor{display:inline-block;width:2px;height:1em;background:currentColor;margin-left:1px;animation:blink .7s step-end infinite;vertical-align:text-bottom}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
/* ── FOLLOWUP ── */
.followup-wrap{margin-top:8px;padding:10px 12px;border-radius:var(--r);background:var(--blue-l);border:1px solid rgba(37,99,235,.15)}
[data-theme="dark"] .followup-wrap{background:rgba(79,142,247,.08);border-color:rgba(79,142,247,.2)}
.followup-q{font-size:12px;color:var(--text2);margin-bottom:7px;font-weight:500}
.followup-opts{display:flex;flex-wrap:wrap;gap:5px}
.fopt-btn{padding:5px 12px;border-radius:99px;border:1px solid rgba(37,99,235,.3);background:var(--surface);font-size:11px;font-weight:500;color:var(--blue);cursor:pointer;transition:all .15s}
.fopt-btn:hover{background:var(--blue);color:white;border-color:var(--blue)}
</style>
</head>
<body>

<nav id="nav">
  <div id="nav-inner">
    <a id="logo" href="#" onclick="showPage('home');return false">
      <div id="logo-mark">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M9 3H5a2 2 0 0 0-2 2v4"/><path d="M9 3h6"/><path d="M15 3h4a2 2 0 0 1 2 2v4"/><path d="M3 9v6"/><path d="M21 9v6"/><path d="M3 15v4a2 2 0 0 0 2 2h4"/><path d="M21 15v4a2 2 0 0 1-2 2h-4"/><path d="M9 21h6"/><circle cx="12" cy="12" r="3"/></svg>
      </div>
      <div><div id="logo-text">RareNav</div><div id="logo-sub">Rare Disease AI</div></div>
    </a>
    <div class="nsep"></div>
    <button class="nbtn active" id="nb-home" onclick="showPage('home')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      <span class="nlab">Assistant</span>
    </button>
    <button class="nbtn" id="nb-variants" onclick="showPage('variants')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
      <span class="nlab">Variants</span>
    </button>
    <button class="nbtn" id="nb-diseases" onclick="showPage('diseases')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
      <span class="nlab">Diseases</span>
    </button>
    <div id="nav-space"></div>
    <div class="nav-tools">
      <a class="nic" href="https://github.com/IveGotMagicBean/RareNav_MedGemma" target="_blank" title="GitHub">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.341-3.369-1.341-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.268 2.75 1.026A9.578 9.578 0 0 1 12 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.026 2.747-1.026.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/></svg>
      </a>
      <button class="nic" onclick="openInfo('video')" title="Demo Video">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
      </button>
      <button class="nic" onclick="openInfo('docs')" title="Documentation">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      </button>
      <button class="nic" onclick="openPhone()" title="Mobile Preview">
        <svg width="13" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18" stroke-width="3"/></svg>
      </button>
      <button class="nic" id="theme-btn" onclick="toggleTheme()" title="Toggle Theme">
        <svg id="theme-moon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <svg id="theme-sun" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
      </button>
    </div>
    <div class="nsep"></div>
    <button class="clin-pill" id="clin-btn" onclick="toggleClinician()">Clinician</button>
    <div class="nsep"></div>
    <div id="status-pill"><div class="sdot" id="sdot"></div><span id="stxt">connecting</span></div>
  </div>
</nav>

<div id="app">

<!-- ══ HOME ══ -->
<div class="page" id="page-home">
  <div id="left-panel">
    <div class="lp-head">
      <h2>What can I help with?</h2>
      <p>MedGemma · ClinVar 5M+ · HPO ontology</p>
    </div>
    <div id="caps">
      <div class="cap-grp">
        <div class="cap-grp-lbl">REPORT ANALYSIS</div>
        <button class="cap-item hi" onclick="openUpload()">
          <div class="ci-ico" style="background:var(--blue-l)">📄</div>
          <div><div class="ci-title">Upload Genetic Report <span class="ci-new">AI</span></div><div class="ci-desc">PDF or image → MedGemma extracts all variants</div></div>
        </button>
      </div>
      <div class="cap-grp">
        <div class="cap-grp-lbl">UNDERSTAND YOUR RESULTS</div>
        <button class="cap-item" onclick="qs('What does it mean if my variant is classified as Pathogenic?')">
          <div class="ci-ico" style="background:#fef3c7">🧬</div>
          <div><div class="ci-title">Explain a variant</div><div class="ci-desc">Pathogenic, VUS, Benign — what does it mean?</div></div>
        </button>
        <button class="cap-item" onclick="qs('Is my genetic condition hereditary? What is the risk for my children?')">
          <div class="ci-ico" style="background:#f0fdf4">👨‍👩‍👧</div>
          <div><div class="ci-title">Inheritance & family risk</div><div class="ci-desc">Patterns and risk for relatives</div></div>
        </button>
        <button class="cap-item" onclick="qs('What treatment options exist for rare genetic conditions?')">
          <div class="ci-ico" style="background:#fdf2f8">💊</div>
          <div><div class="ci-title">Treatments & clinical trials</div><div class="ci-desc">Therapies and ongoing research</div></div>
        </button>
      </div>
      <div class="cap-grp">
        <div class="cap-grp-lbl">DIAGNOSIS SUPPORT</div>
        <button class="cap-item" onclick="qs('My child has seizures, muscle weakness, and developmental delay. What rare diseases should we investigate?')">
          <div class="ci-ico" style="background:#f0f9ff">🔍</div>
          <div><div class="ci-title">Symptom-based diagnosis</div><div class="ci-desc">Describe symptoms → rare disease differential</div></div>
        </button>
        <button class="cap-item" onclick="showPage('diseases')">
          <div class="ci-ico" style="background:#f5f3ff">📖</div>
          <div><div class="ci-title">Browse disease library</div><div class="ci-desc">50+ rare diseases with full clinical profiles</div></div>
        </button>
        <button class="cap-item" onclick="showPage('variants')">
          <div class="ci-ico" style="background:#fff1f2">🗄</div>
          <div><div class="ci-title">Search variant database</div><div class="ci-desc">ClinVar 5M+ variants, real-time search</div></div>
        </button>
      </div>
    </div>
    <div class="lp-foot">
      <p class="disc">⚠ RareNav uses MedGemma (Google HAI-DEF). Research tool only — not a medical device. Consult qualified healthcare professionals for clinical decisions.</p>
    </div>
  </div>

  <div id="chat-right">
    <div id="chat-scroll">
      <div id="chat-inner">
        <div id="welcome">
          <div class="w-ico">🧬</div>
          <h1 class="w-title">Navigate rare disease with <em>AI clarity</em></h1>
          <p class="w-sub">Ask about genetic variants, symptoms, or upload your genetic report for instant AI analysis.</p>
          <div class="starters">
            <button class="starter" onclick="qsend('What does a Pathogenic BRCA1 variant mean for my health?')"><span class="si-ico">📋</span><span class="si-txt">What does a Pathogenic BRCA1 variant mean?</span></button>
            <button class="starter" onclick="qsend('My child has unusual symptoms — could it be a rare genetic disease?')"><span class="si-ico">👶</span><span class="si-txt">My child has unusual symptoms — rare disease?</span></button>
            <button class="starter" onclick="qsend('What is a VUS and should I be worried?')"><span class="si-ico">❓</span><span class="si-txt">What is a VUS and should I be worried?</span></button>
            <button class="starter" onclick="qsend('I was just diagnosed with a rare condition — what should I do next?')"><span class="si-ico">🗺</span><span class="si-txt">Just diagnosed — what should I do next?</span></button>
          </div>
        </div>
        <div id="msgs"></div>
      </div>
    </div>
    <div style="padding:0 20px">
      <div id="input-wrap">
        <div id="ctx-bar">
          <span>🔬 Context:</span>
          <span id="ctx-pills"></span>
          <button onclick="clearCtx()" style="margin-left:auto;background:none;border:none;cursor:pointer;color:var(--blue);font-size:11px;font-weight:500">✕ clear</button>
        </div>
        <div id="irow">
          <button id="up-btn" onclick="openUpload()" title="Upload report">📎</button>
          <textarea id="cin" rows="1" placeholder="Ask about your variant, symptoms, or upload a report…" oninput="aResize(this)" onkeydown="chatKey(event)"></textarea>
          <button id="send-btn" onclick="doSend()">➤</button>
        </div>
        <div class="ihint">Enter to send · Shift+Enter new line · MedGemma 4B (Google HAI-DEF)</div>
      </div>
    </div>
  </div>

  <div id="ctx-panel">
    <div class="ctx-lbl">ACTIVE CONTEXT</div>
    <div id="ctx-panel-inner"></div>
  </div>
</div>

<!-- ══ VARIANTS ══ -->
<div class="page" id="page-variants">
  <div class="pg-head"><h1>🗄 Variant Database</h1><p>Real-time search across ClinVar clinical variant submissions</p></div>
  <div class="pg-body">
    <div class="ibox ib">💡 Type a gene name to search. Pathogenic variants are pre-indexed. Try: <strong>HFE · CFTR · BRCA1 · LDLR · GBA</strong></div>
    <div class="sbar">
      <div class="si-w"><span class="si-ico2">🔍</span><input class="sinput" id="vg-in" placeholder="Gene name (HFE, CFTR, BRCA1…)" onkeydown="if(event.key==='Enter')vSearch()"></div>
      <div class="si-w" style="max-width:180px"><span class="si-ico2">🔬</span><input class="sinput" id="vv-in" placeholder="Variant (optional)"></div>
      <select class="fsel" id="vsig-in">
        <option value="">All significance</option>
        <option value="pathogenic">Pathogenic</option>
        <option value="likely pathogenic">Likely Pathogenic</option>
        <option value="vus">VUS</option>
        <option value="benign">Benign</option>
      </select>
      <button class="sbtn" onclick="vSearch()">Search</button>
    </div>
    <div id="gchips" style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px"></div>
    <div id="rmeta" class="rmeta" style="display:none"></div>
    <div id="vres"></div>
  </div>
  <div id="vdrawer"><div id="vdh"><div><div id="dg" style="font-family:monospace;font-size:16px;font-weight:700;color:var(--blue)"></div><div id="ds" style="margin-top:3px"></div></div><button class="vdclose" onclick="closeDrawer()">✕</button></div><div id="vdb"></div></div>
</div>

<!-- ══ DISEASES ══ -->
<div class="page" id="page-diseases">
  <div class="pg-head"><h1>📖 Disease Library</h1><p>Curated rare disease profiles — genetics, symptoms, management and resources</p></div>
  <div class="pg-body">
    <div class="sbar">
      <div class="si-w"><span class="si-ico2">🔍</span><input class="sinput" id="dis-in" placeholder="Search diseases, genes, symptoms…" oninput="dSearch(this.value)"></div>
    </div>
    <div id="cat-tabs" class="cat-tabs"></div>
    <div id="dmeta" class="rmeta"></div>
    <div id="dgrid" class="dgrid"></div>
  </div>
</div>

</div><!-- #app -->

<!-- ══ MOBILE BOTTOM NAV ══ -->
<nav id="mobile-nav">
  <div class="mnav-inner">
    <button class="mnav-btn active" id="mnb-home" onclick="showPage('home')">
      <span class="mico"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span>
      Assistant
    </button>
    <button class="mnav-btn" id="mnb-variants" onclick="showPage('variants')">
      <span class="mico"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg></span>
      Variants
    </button>
    <button class="mnav-btn" id="mnb-diseases" onclick="showPage('diseases')">
      <span class="mico"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg></span>
      Diseases
    </button>
    <button class="mnav-btn" onclick="openLeftDrawer()">
      <span class="mico"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg></span>
      More
    </button>
  </div>
</nav>

<!-- ══ MOBILE LEFT DRAWER ══ -->
<div id="left-drawer">
  <div class="ld-backdrop" onclick="closeLeftDrawer()"></div>
  <div class="ld-panel">
    <div class="lp-head" style="padding-top:calc(var(--nav-h) + 12px)">
      <h2>What can I help with?</h2>
      <p>MedGemma · ClinVar 5M+ · HPO</p>
    </div>
    <div id="caps-mobile" style="padding:10px;flex:1"></div>
    <div class="lp-foot" style="border-top:1px solid var(--border)">
      <div style="display:flex;gap:6px;justify-content:center;margin-bottom:10px;flex-wrap:wrap;align-items:center">
        <a class="nic" href="https://github.com/IveGotMagicBean/RareNav_MedGemma" target="_blank" title="GitHub" style="border:1px solid var(--border);border-radius:7px;width:34px;height:34px">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.341-3.369-1.341-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.268 2.75 1.026A9.578 9.578 0 0 1 12 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.026 2.747-1.026.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/></svg>
        </a>
        <button class="nic" onclick="closeLeftDrawer();openInfo('video')" title="Demo Video" style="border:1px solid var(--border);border-radius:7px;width:34px;height:34px">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
        </button>
        <button class="nic" onclick="closeLeftDrawer();openInfo('docs')" title="Docs" style="border:1px solid var(--border);border-radius:7px;width:34px;height:34px">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </button>
        <button class="nic" onclick="toggleTheme()" title="Theme" style="border:1px solid var(--border);border-radius:7px;width:34px;height:34px">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
        <button class="clin-pill" id="clin-btn-m" onclick="toggleClinician()">Clinician</button>
      </div>
      <p class="disc">⚠ Research tool only. Not a medical device.</p>
    </div>
  </div>
</div>

<!-- ══ UPLOAD MODAL ══ -->
<div id="umodal">
  <div id="ubox">
    <h3>📄 Upload Genetic Report</h3>
    <p>Upload your genetic test report (PDF or image). MedGemma will read and extract all variants automatically.</p>
    <div id="dropzone" onclick="document.getElementById('fin').click()" ondragover="event.preventDefault();this.classList.add('drag')" ondragleave="this.classList.remove('drag')" ondrop="handleDrop(event)">
      <div class="dz-ico">📁</div>
      <div class="dz-txt">Drop file here or click to browse</div>
      <div class="dz-sub">PDF, JPG, PNG · Max 10MB</div>
    </div>
    <input type="file" id="fin" accept=".pdf,.jpg,.jpeg,.png" onchange="handleFile(this)">
    <div id="uprev"></div>
    <div class="mact">
      <button class="btn btns" onclick="closeUpload()">Cancel</button>
      <button class="btn btnp" id="usub" onclick="doUpload()" disabled>Analyze Report</button>
    </div>
  </div>
</div>

<!-- ══ DISEASE MODAL ══ -->
<div id="dmodal">
  <div id="dmbox">
    <div id="dmhdr"><div id="dmtitle"></div><button class="closex" onclick="closeDM()">✕</button></div>
    <div id="dmbody"></div>
    <div id="dmfoot">
      <button class="btn btns" onclick="closeDM()">Close</button>
      <button class="btn btnp" id="dask-btn">💬 Ask AI about this</button>
    </div>
  </div>
</div>

<!-- ══ INFO MODAL (video / docs) ══ -->
<div id="info-modal">
  <div id="info-box">
    <div id="info-hdr">
      <h3 id="info-title">Resources</h3>
      <button class="closex" onclick="closeInfo()">✕</button>
    </div>
    <div id="info-body"></div>
  </div>
</div>

<!-- ══ PHONE PREVIEW MODAL ══ -->
<div id="phone-modal">
  <button id="phone-close" onclick="closePhone()">✕</button>
  <div style="display:flex;flex-direction:column;align-items:center">
    <div class="phone-frame">
      <div class="phone-notch"></div>
      <div class="phone-iframe-wrap">
        <iframe id="phone-iframe" src="about:blank" title="Mobile Preview"></iframe>
      </div>
    </div>
    <div class="phone-label">📱 Mobile Preview (375×720) — actual mobile experience may vary</div>
  </div>
</div>

<script>
// ─── State ────────────────────────────────────────────────────────────
const S={page:'home',clin:false,sid:'sess_'+Date.now(),ctx:null,chat:[],vres:[],dsel:null,theme:'light',upload:{}}

// ─── Theme ────────────────────────────────────────────────────────────
function toggleTheme(){
  S.theme=S.theme==='light'?'dark':'light'
  document.documentElement.setAttribute('data-theme',S.theme)
  const isDark=S.theme==='dark'
  const moon=document.getElementById('theme-moon'); if(moon) moon.style.display=isDark?'none':'block'
  const sun=document.getElementById('theme-sun'); if(sun) sun.style.display=isDark?'block':'none'
  try{localStorage.setItem('rn-theme',S.theme)}catch{}
}
function initTheme(){
  try{
    const t=localStorage.getItem('rn-theme')
    if(t){
      S.theme=t; document.documentElement.setAttribute('data-theme',t)
      const isDark=t==='dark'
      const moon=document.getElementById('theme-moon'); if(moon) moon.style.display=isDark?'none':'block'
      const sun=document.getElementById('theme-sun'); if(sun) sun.style.display=isDark?'block':'none'
    }
  }catch{}
}

// ─── Nav ──────────────────────────────────────────────────────────────
function showPage(p){
  document.querySelectorAll('.page').forEach(e=>e.classList.remove('active'))
  document.querySelectorAll('.nbtn,.mnav-btn').forEach(e=>e.classList.remove('active'))
  document.getElementById('page-'+p).classList.add('active')
  const nb=document.getElementById('nb-'+p); if(nb)nb.classList.add('active')
  const mb=document.getElementById('mnb-'+p); if(mb)mb.classList.add('active')
  S.page=p
  if(p==='diseases'&&!S.dLoaded){loadDiseases();S.dLoaded=true}
  if(p==='variants')initVPage()
  window.scrollTo(0,0)
}
function toggleClinician(){
  S.clin=!S.clin
  ;['clin-btn','clin-btn-m'].forEach(id=>{const el=document.getElementById(id);if(el)el.classList.toggle('on',S.clin)})
  if(S.chat.length)appendMsg('ai','_Mode: '+(S.clin?'Clinician (clinical terminology)':'Patient (plain language)')+'_')
}
function openLeftDrawer(){
  // populate mobile caps
  const mc=document.getElementById('caps-mobile')
  mc.innerHTML=document.getElementById('caps').innerHTML
  document.getElementById('left-drawer').classList.add('open')
  document.body.style.overflow='hidden'
}
function closeLeftDrawer(){document.getElementById('left-drawer').classList.remove('open');document.body.style.overflow=''}

// ─── API ──────────────────────────────────────────────────────────────
async function api(path,opts={}){
  const r=await fetch('/api'+path,{headers:{'Content-Type':'application/json'},...opts,body:opts.body?JSON.stringify(opts.body):undefined})
  if(!r.ok){const e=await r.json().catch(()=>({error:'Failed'}));throw new Error(e.error||'Error')}
  return r.json()
}

// ─── Health ───────────────────────────────────────────────────────────
async function ping(){
  try{
    const h=await api('/health')
    document.getElementById('sdot').className='sdot '+(h.demo_mode?'warn':'ok')
    document.getElementById('stxt').textContent=h.demo_mode?'Demo mode':'Ready'
  }catch{document.getElementById('sdot').className='sdot';document.getElementById('stxt').textContent='Offline'}
}

// ─── Chat ─────────────────────────────────────────────────────────────
function aResize(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,110)+'px'}
function chatKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();doSend()}}
function qs(t){document.getElementById('cin').value=t;aResize(document.getElementById('cin'));document.getElementById('cin').focus()}
function qsend(t){qs(t);doSend()}

async function doSend(optVal){
  var inp=document.getElementById('cin');
  var t=optVal||inp.value.trim();if(!t)return;
  inp.value='';inp.style.height='auto';
  document.getElementById('welcome').style.display='none';
  appendMsg('user',t);S.chat.push({role:'user',content:t});
  document.getElementById('send-btn').disabled=true;
  var msgs=document.getElementById('msgs');
  var row=document.createElement('div');row.className='msg ai';
  var bub=document.createElement('div');bub.className='bub ai';
  var toolArea=document.createElement('div');toolArea.className='tool-calls';
  var prose=document.createElement('div');prose.className='prose';
  var foot=document.createElement('div');foot.className='mfoot';foot.style.display='none';
  bub.appendChild(toolArea);bub.appendChild(prose);bub.appendChild(foot);
  row.innerHTML='<div class="av av-ai">AI</div>';
  row.appendChild(bub);
  msgs.appendChild(row);
  row.scrollIntoView({behavior:'smooth',block:'nearest'});
  var body={session_id:S.sid,message:t,context:S.ctx,mode:S.clin?'clinician':'patient'};
  if(optVal){body.selected_option=optVal;}
  var fullText='';
  var runningCards={};
  try{
    var resp=await fetch('/api/chat/stream',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(body)
    });
    var reader=resp.body.getReader();
    var decoder=new TextDecoder();
    var buf='';
    while(true){
      var chunk=await reader.read();
      if(chunk.done)break;
      buf+=decoder.decode(chunk.value,{stream:true});
      var lines=buf.split('\n');
      buf=lines.pop();
      for(var i=0;i<lines.length;i++){
        var line=lines[i].trim();
        if(!line.startsWith('data:'))continue;
        var evt;
        try{evt=JSON.parse(line.slice(5).trim());}catch(ex){continue;}
        if(evt.type==='tool_start'){
          var card=document.createElement('div');
          card.className='tool-card running';
          card.id='tc-'+evt.step;
          var ico=evt.step==='clinvar'?'DB':'HP';
          var spin=document.createElement('span');spin.className='tool-spin';
          card.innerHTML='<span class="tool-ico">'+ico+'</span><span class="tool-label">'+evt.label+'</span>';
          card.appendChild(spin);
          toolArea.appendChild(card);
          runningCards[evt.step]=card;
          row.scrollIntoView({behavior:'smooth',block:'nearest'});
        }
        else if(evt.type==='tool_done'){
          var existing=runningCards[evt.step];
          if(existing){
            var statusIcon=evt.status==='ok'?'OK':evt.status==='empty'?'--':'ERR';
            existing.className='tool-card '+evt.status;
            existing.innerHTML='<span class="tool-ico">'+(evt.step==='clinvar'?'DB':'HP')+'</span>'
              +'<span class="tool-label">'+evt.label+'</span>'
              +'<span class="tool-detail">'+statusIcon+' '+evt.detail+'</span>';
          }
        }
        else if(evt.type==='reply_start'){
          prose.innerHTML='<span class="stream-cursor"></span>';
        }
        else if(evt.type==='token'){
          fullText+=evt.text;
          prose.innerHTML=md(fullText)+'<span class="stream-cursor"></span>';
          row.scrollIntoView({behavior:'smooth',block:'nearest'});
        }
        else if(evt.type==='done'){
          prose.innerHTML=md(fullText);
          if(evt.followup_question&&evt.followup_options&&evt.followup_options.length){
            var fwrap=document.createElement('div');fwrap.className='followup-wrap';
            var fq=document.createElement('div');fq.className='followup-q';
            fq.textContent=evt.followup_question;
            var fopts=document.createElement('div');fopts.className='followup-opts';
            for(var j=0;j<evt.followup_options.length;j++){
              var ob=document.createElement('button');ob.className='fopt-btn';
              ob.textContent=evt.followup_options[j];
              ob.dataset.v=evt.followup_options[j];
              ob.onclick=function(){doSend(this.dataset.v);};
              fopts.appendChild(ob);
            }
            fwrap.appendChild(fq);fwrap.appendChild(fopts);
            bub.insertBefore(fwrap,foot);
          }
          if(evt.latency){
            foot.style.display='flex';
            var enc=b64e(fullText);
            foot.innerHTML='<span class="mmeta">'+(evt.demo?'Demo':'MedGemma')+' '+evt.latency+'s</span>';
            var cdbtn=document.createElement('button');cdbtn.className='cd-btn';
            cdbtn.textContent='Clinical detail';
            cdbtn.setAttribute('data-enc',enc);
            cdbtn.onclick=function(){toggleCD(this,this.getAttribute('data-enc'));};
            foot.appendChild(cdbtn);
          }
          S.chat.push({role:'assistant',content:fullText});
        }
      }
    }
  }catch(e){
    prose.innerHTML='Error: '+e.message;
  }
  document.getElementById('send-btn').disabled=false;
}

function appendMsg(role,text,lat,demo){
  var msgs=document.getElementById('msgs');
  var row=document.createElement('div');row.className='msg '+role;
  var isU=role==='user';
  var av=isU?'<div class="av av-u">You</div>':'<div class="av av-ai">AI</div>';
  var body=isU?esc(text):md(text);
  var foot='';
  if(!isU&&lat){
    foot='<div class="mfoot"><span class="mmeta">'+(demo?'Demo':'MedGemma')+' '+lat.toFixed(1)+'s</span>'
        +'<button class="cd-btn" onclick="toggleCD(this,b64e(text))">Clinical detail</button></div>';
  }
  if(isU){
    row.innerHTML=av+'<div class="bub user">'+body+'</div>';
  }else{
    row.innerHTML=av+'<div class="bub ai"><div class="prose">'+body+'</div>'+foot+'</div>';
  }
  msgs.appendChild(row);row.scrollIntoView({behavior:'smooth',block:'nearest'});return row;
}
function appendTyping(){
  const msgs=document.getElementById('msgs');const row=document.createElement('div');row.className='msg ai'
  row.innerHTML=`<div class="av av-ai">AI</div><div class="bub ai"><div class="typing"><div class="td"></div><div class="td"></div><div class="td"></div></div></div>`
  msgs.appendChild(row);row.scrollIntoView({behavior:'smooth',block:'nearest'});return row
}
async function toggleCD(btn,enc){
  const on=btn.classList.toggle('on');const prose=btn.closest('.bub').querySelector('.prose')
  if(on){
    btn.textContent='Patient view';prose.innerHTML='<div class="ldrow"><div class="spin"></div> Generating clinical summary…</div>'
    try{const res=await api('/chat/message',{method:'POST',body:{session_id:S.sid+'_c',message:'Clinical summary: '+b64d(enc),mode:'clinician'}});prose.innerHTML=md(res.reply)}
    catch{prose.innerHTML=md(b64d(enc))}
  }else{btn.textContent='Clinical detail';prose.innerHTML=md(b64d(enc))}
}

function setCtx(ctx){
  S.ctx=ctx
  document.getElementById('ctx-bar').style.display='flex'
  document.getElementById('ctx-pills').innerHTML=Object.entries(ctx).filter(([,v])=>v).map(([k,v])=>`<span class="ctx-pill">${k}: <b>${String(v).slice(0,28)}</b></span>`).join('')
  const panel=document.getElementById('ctx-panel');panel.classList.add('show')
  document.getElementById('ctx-panel-inner').innerHTML=`
    <div class="ctx-vcard">
      <div style="font-family:monospace;font-size:14px;font-weight:700;color:var(--text);margin-bottom:2px">${ctx.gene||''}</div>
      <div style="font-size:10px;color:var(--text3);margin-bottom:5px">${(ctx.variant||'').slice(0,50)}</div>
      ${sbadge(ctx.significance||'')}
    </div>
    <button class="ctx-act" onclick="qsend('What does this ${ctx.gene} variant mean?')">💬 What does this mean?</button>
    <button class="ctx-act" onclick="qsend('What treatment options exist?')">💊 Treatment options</button>
    <button class="ctx-act" onclick="qsend('Is this inherited? Family risk?')">👨‍👩‍👧 Family risk</button>
    <button class="ctx-act p" onclick="qsend('Generate a patient-friendly summary of this variant')">📋 Generate summary</button>`
}
function clearCtx(){S.ctx=null;document.getElementById('ctx-bar').style.display='none';document.getElementById('ctx-panel').classList.remove('show')}

// ─── Upload ───────────────────────────────────────────────────────────
function openUpload(){document.getElementById('umodal').classList.add('open')}
function closeUpload(){
  document.getElementById('umodal').classList.remove('open')
  document.getElementById('uprev').style.display='none'
  document.getElementById('usub').disabled=true
  document.getElementById('usub').textContent='Analyze Report'
  document.getElementById('fin').value=''
  // NOTE: do NOT clear S.upload here — doUpload() needs the data
}
function resetUploadState(){S.upload={}}
function handleDrop(e){e.preventDefault();document.getElementById('dropzone').classList.remove('drag');const f=e.dataTransfer.files[0];if(f)procFile(f)}
function handleFile(inp){if(inp.files[0])procFile(inp.files[0])}
function procFile(f){
  if(f.size>20*1024*1024){alert('File too large (max 20MB)');return}
  S.upload.file=f
  S.upload.type=f.type||'image/jpeg'
  const r=new FileReader()
  r.onload=ev=>{
    const full=ev.target.result  // "data:image/jpeg;base64,XXXX"
    S.upload.data=full.includes(',') ? full.split(',')[1] : full
    document.getElementById('uprev').style.display='block'
    document.getElementById('uprev').innerHTML=`✅ <b>${f.name}</b> (${(f.size/1024).toFixed(0)} KB) — ready to analyze`
    document.getElementById('usub').disabled=false
  }
  r.onerror=()=>alert('Failed to read file. Please try again.')
  r.readAsDataURL(f)
}
async function doUpload(){
  if(!S.upload.data){alert('No file selected or file not yet loaded.');return}
  // save refs before closing modal
  const fileData=S.upload.data
  const fileType=S.upload.type||'image/jpeg'
  const fileName=S.upload.file?.name||'report'
  closeUpload()   // close UI — data is in local vars, safe
  showPage('home')
  document.getElementById('welcome').style.display='none'
  appendMsg('user','📄 Uploaded: '+fileName)
  const ty=appendTyping()
  document.getElementById('send-btn').disabled=true
  try{
    const res=await api('/upload/report',{method:'POST',body:{file_data:fileData,file_type:fileType}})
    ty.remove()
    const ext=res.extracted||{},vs=ext.variants||[]
    let reply='## Report Analysis Complete\n\n'
    if(ext.report_type) reply+='**Report type:** '+ext.report_type+'\n\n'
    if(ext.summary) reply+='**Summary:** '+ext.summary+'\n\n'
    if(vs.length){
      reply+='### Variants Found ('+vs.length+')\n\n'
      vs.forEach(v=>{
        reply+='**'+v.gene+'** — '+v.variant+'\n'
        reply+='Classification: **'+v.significance+'**'+(v.condition?' · '+v.condition:'')+'\n\n'
      })
      reply+='\nWould you like me to explain what any of these variants means in detail?'
      const p=vs.find(v=>(v.significance||'').toLowerCase().includes('pathogenic'))||vs[0]
      if(p) setCtx({gene:p.gene,variant:p.variant,significance:p.significance,condition:p.condition})
    }else{
      reply+='No genetic variants were detected in this file. Please ensure the image clearly shows the genetic results section of your report.'
    }
    appendMsg('ai',reply,res.latency,res.demo)
    S.chat.push({role:'assistant',content:reply})
  }catch(e){
    ty.remove()
    appendMsg('ai','❌ Report analysis failed: '+e.message+'\n\nPlease check the file is a clear image or PDF of a genetic test report and try again.')
  }finally{
    document.getElementById('send-btn').disabled=false
    resetUploadState()
  }
}

// ─── Info Modal (video / docs) ────────────────────────────────────────
function openInfo(type){
  document.getElementById('info-modal').classList.add('open')
  document.body.style.overflow='hidden'
  if(type==='video'){
    document.getElementById('info-title').innerHTML='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:6px"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>Demo Video'
    document.getElementById('info-body').innerHTML=`
      <video class="info-embed-video" controls controlsList="nodownload">
        <source src="/file/demo.mp4" type="video/mp4">
        <div class="info-empty"><div class="info-empty-ico">🎬</div><p>Video file not available yet.<br>Please check back later.</p></div>
      </video>`
  }else{
    document.getElementById('info-title').innerHTML='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:6px"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Documentation'
    document.getElementById('info-body').innerHTML=`<iframe class="info-embed" src="/file/demo.pdf"></iframe>`
  }
}
function closeInfo(){document.getElementById('info-modal').classList.remove('open');document.body.style.overflow=''}

// ─── Phone Preview ────────────────────────────────────────────────────
function openPhone(){
  document.getElementById('phone-modal').classList.add('open')
  document.body.style.overflow='hidden'
  const iframe=document.getElementById('phone-iframe')
  if(iframe.src==='about:blank') iframe.src=window.location.href+'?mobile=1'
}
function closePhone(){document.getElementById('phone-modal').classList.remove('open');document.body.style.overflow=''}

// ─── Variants ─────────────────────────────────────────────────────────
const GENES=['HFE','CFTR','BRCA1','BRCA2','FBN1','LDLR','GBA','PAH','PKD1','TSC1','PTEN','GLA','HEXA','NF1','RB1','VHL','WT1','APC']
function initVPage(){
  if(document.getElementById('gchips').innerHTML)return
  document.getElementById('gchips').innerHTML=GENES.map(g=>`<button style="padding:3px 9px;border-radius:99px;border:1px solid var(--border);background:var(--surface);font-size:11px;font-family:monospace;cursor:pointer;color:var(--blue);transition:all .12s" onmouseover="this.style.background='var(--blue-l)'" onmouseout="this.style.background='var(--surface)'" onclick="quickV('${g}')">${g}</button>`).join('')
  document.getElementById('vres').innerHTML=`<div class="empty"><div class="empty-ico">🔍</div><p>Enter a gene name to search ClinVar</p></div>`
}
function quickV(g){document.getElementById('vg-in').value=g;vSearch()}
async function vSearch(){
  const gene=document.getElementById('vg-in').value.trim();const variant=document.getElementById('vv-in').value.trim();const sig=document.getElementById('vsig-in').value
  if(!gene){alert('Please enter a gene name');return}
  document.getElementById('vres').innerHTML=`<div class="ldrow"><div class="spin"></div> Searching ${gene}…</div>`;document.getElementById('rmeta').style.display='none'
  try{
    const p=new URLSearchParams({gene,limit:30});if(variant)p.set('variant',variant);if(sig)p.set('significance',sig)
    const res=await api('/variants/search?'+p);const rs=res.results||[];S.vres=rs
    const meta=document.getElementById('rmeta');meta.style.display='flex';meta.innerHTML=`<span>${rs.length} variant${rs.length!==1?'s':''} for <b>${gene}</b></span><span style="color:var(--text4);font-size:10px">ClinVar · Feb 2026</span>`
    if(!rs.length){document.getElementById('vres').innerHTML=`<div class="empty"><div class="empty-ico">🔍</div><p>No variants found for <b>${gene}</b></p></div>`;return}
    renderVTbl(rs)
  }catch(e){document.getElementById('vres').innerHTML=`<div class="empty"><div class="empty-ico">⚠️</div><p>Search failed: ${e.message}</p></div>`}
}
function renderVTbl(rs){
  document.getElementById('vres').innerHTML=`<div style="overflow-x:auto"><table class="vtbl"><thead><tr><th>Gene</th><th>Variant</th><th>Classification</th><th>Condition</th><th>Chr</th><th>#</th></tr></thead><tbody>${rs.map((v,i)=>`<tr onclick="openDrawer(${i})" id="vr-${i}"><td><span class="gtag">${v.gene}</span></td><td><div class="vname" title="${esc(v.name)}">${esc(v.name)}</div></td><td>${sbadge(v.significance)}</td><td><div class="pheno" title="${esc(v.phenotype)}">${esc((v.phenotype||'').split('|')[0].trim())}</div></td><td style="font-family:monospace;font-size:10px;color:var(--text4)">${v.chromosome?'chr'+v.chromosome:'—'}</td><td style="font-size:11px;color:var(--text4)">${v.submitters||'—'}</td></tr>`).join('')}</tbody></table></div>`
}
function openDrawer(i){
  const v=S.vres[i];if(!v)return
  document.querySelectorAll('.vtbl tr').forEach(r=>r.classList.remove('sel'));const row=document.getElementById('vr-'+i);if(row)row.classList.add('sel')
  document.getElementById('dg').textContent=v.gene;document.getElementById('ds').innerHTML=sbadge(v.significance)
  document.getElementById('vdb').innerHTML=`<div class="dsec"><div class="dsec-t">VARIANT DETAILS</div>${dr('Full name',`<span class="dval mono">${esc(v.name)}</span>`)}${dr('Type',v.type||'—')}${dr('Position',v.position||'—')}${dr('Ref / Alt',v.ref&&v.alt?v.ref+' → '+v.alt:'—')}${dr('dbSNP',v.dbsnp&&v.dbsnp!=='nan'?`<a href="https://www.ncbi.nlm.nih.gov/snp/${v.dbsnp}" target="_blank">${v.dbsnp}</a>`:'—')}${dr('Last reviewed',v.last_evaluated||'—')}${dr('Review status',v.review_status||'—')}${dr('Submitters',String(v.submitters)||'—')}</div><div class="dsec"><div class="dsec-t">CONDITIONS</div><div style="display:flex;flex-wrap:wrap;gap:4px">${(v.phenotype||'').split('|').filter(Boolean).map(p=>`<span style="padding:2px 8px;border-radius:99px;background:var(--surface2);color:var(--text2);font-size:10px">${p.trim()}</span>`).join('')||'—'}</div></div><div class="dsec"><div class="dsec-t">LINKS</div>${v.variation_id&&v.variation_id!=='nan'?`<a class="elink" href="https://www.ncbi.nlm.nih.gov/clinvar/variation/${v.variation_id}/" target="_blank">ClinVar Entry <span>↗</span></a>`:''}<a class="elink" href="https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(v.gene+' '+v.name)}" target="_blank">PubMed <span>↗</span></a><a class="elink" href="https://clinicaltrials.gov/search?cond=${encodeURIComponent((v.phenotype||'').split('|')[0])}" target="_blank">Clinical Trials <span>↗</span></a></div><div class="ibox ia">⚠ For research use only.</div><button class="ask-btn" onclick="askAbout(${i})">💬 Ask AI to explain this variant</button>`
  document.getElementById('vdrawer').classList.add('open')
}
function dr(l,v){return`<div class="drow"><div class="dlbl">${l}</div><div class="dval">${v}</div></div>`}
function closeDrawer(){document.getElementById('vdrawer').classList.remove('open');document.querySelectorAll('.vtbl tr').forEach(r=>r.classList.remove('sel'))}
function askAbout(i){const v=S.vres[i];setCtx({gene:v.gene,variant:v.name,significance:v.significance,condition:(v.phenotype||'').split('|')[0].trim()});showPage('home');qsend(`Explain: ${v.gene} ${v.name} (${v.significance}). Condition: ${(v.phenotype||'').split('|')[0]}`)}

// ─── Diseases ─────────────────────────────────────────────────────────
const DISEASES=[
  // Metabolic
  {id:'CF',name:'Cystic Fibrosis',gene:'CFTR',icon:'🫁',col:'#dbeafe',cat:'Metabolic',inh:'AR',prev:'1 in 3,500',omim:'219700',syms:['Chronic cough','Lung infections','Pancreatic insufficiency','Salty skin'],tx:['CFTR modulators (Trikafta)','Physiotherapy','Enzyme supplements'],specs:['Pulmonologist','Gastroenterologist','Geneticist'],dx:'Sweat chloride, newborn screening, CFTR sequencing',desc:'CFTR mutations cause thick mucus in lungs and pancreas.'},
  {id:'PKU',name:'Phenylketonuria',gene:'PAH',icon:'🧠',col:'#fef3c7',cat:'Metabolic',inh:'AR',prev:'1 in 10,000',omim:'261600',syms:['Intellectual disability (untreated)','Seizures','Eczema','Musty odor'],tx:['Low-Phe diet','Sapropterin','Pegvaliase'],specs:['Metabolic dietitian','Neurologist'],dx:'Newborn screening, PAH sequencing, plasma amino acids',desc:'PAH mutations impair phenylalanine metabolism — early dietary treatment prevents neurological damage.'},
  {id:'GD',name:'Gaucher Disease',gene:'GBA',icon:'🧫',col:'#d1fae5',cat:'Metabolic',inh:'AR',prev:'1 in 40,000',omim:'230800',syms:['Splenomegaly','Hepatomegaly','Bone pain','Anemia'],tx:['Enzyme replacement (imiglucerase)','Substrate reduction','BMT'],specs:['Hematologist','Metabolic specialist'],dx:'Beta-glucocerebrosidase activity, GBA sequencing',desc:'GBA mutations cause lysosomal accumulation in macrophages.'},
  {id:'FD',name:'Fabry Disease',gene:'GLA',icon:'🫀',col:'#fdf2f8',cat:'Metabolic',inh:'X-linked',prev:'1 in 40,000',omim:'301500',syms:['Neuropathic pain','Angiokeratomas','Renal failure','Cardiomyopathy','Stroke'],tx:['Enzyme replacement (agalsidase)','Migalastat','Supportive care'],specs:['Nephrologist','Cardiologist','Neurologist'],dx:'Alpha-galactosidase A activity, GLA sequencing',desc:'X-linked lysosomal storage disorder causing multi-organ dysfunction.'},
  {id:'WD',name:"Wilson's Disease",gene:'ATP7B',icon:'🟤',col:'#fef3c7',cat:'Metabolic',inh:'AR',prev:'1 in 30,000',omim:'277900',syms:['Liver disease','Kayser-Fleischer rings','Neurological symptoms','Psychiatric symptoms'],tx:['Copper chelation (penicillamine)','Zinc','Liver transplant'],specs:['Hepatologist','Neurologist','Ophthalmologist'],dx:'Ceruloplasmin, urine copper, slit-lamp, ATP7B sequencing',desc:"ATP7B mutations cause toxic copper accumulation in liver and brain."},
  {id:'HCU',name:'Homocystinuria',gene:'CBS',icon:'🔵',col:'#ede9fe',cat:'Metabolic',inh:'AR',prev:'1 in 200,000',omim:'236200',syms:['Lens dislocation','Skeletal abnormalities','Thrombosis','Intellectual disability'],tx:['Pyridoxine (B6)','Low-methionine diet','Betaine'],specs:['Metabolic specialist','Ophthalmologist'],dx:'Plasma amino acids, CBS sequencing, homocysteine levels',desc:'CBS mutations impair methionine metabolism causing multi-system disease.'},
  {id:'PA',name:'Propionic Acidemia',gene:'PCCA',icon:'⚗️',col:'#fef3c7',cat:'Metabolic',inh:'AR',prev:'1 in 100,000',omim:'606054',syms:['Metabolic crisis','Vomiting','Hypotonia','Intellectual disability','Cardiomyopathy'],tx:['Low-protein diet','Biotin','Carnitine','Liver transplant'],specs:['Metabolic specialist','Cardiologist'],dx:'Urine organic acids, plasma amino acids, PCCA/PCCB sequencing',desc:'Organic acidemia causing toxic propionate accumulation.'},
  // Cardiovascular
  {id:'FH',name:'Familial Hypercholesterolemia',gene:'LDLR',icon:'❤️',col:'#fee2e2',cat:'Cardiovascular',inh:'AD',prev:'1 in 250',omim:'143890',syms:['Very high LDL','Premature CAD','Xanthomas','Corneal arcus'],tx:['Statins','Ezetimibe','PCSK9 inhibitors','LDL apheresis'],specs:['Cardiologist','Lipidologist'],dx:'LDL-C levels, Dutch Lipid Clinic criteria, LDLR panel',desc:'Most common monogenic cardiovascular disorder — dramatically increases MI risk.'},
  {id:'MFS',name:'Marfan Syndrome',gene:'FBN1',icon:'🦴',col:'#f3e8ff',cat:'Cardiovascular',inh:'AD',prev:'1 in 5,000',omim:'154700',syms:['Tall stature','Aortic dilation','Lens dislocation','Scoliosis','Arachnodactyly'],tx:['Beta-blockers','Aortic surgery','Ophthalmologic care'],specs:['Cardiologist','Ophthalmologist','Geneticist'],dx:'Ghent criteria, FBN1 sequencing, echocardiogram',desc:'FBN1 mutations weaken connective tissue, especially the cardiovascular system.'},
  {id:'LQTS',name:'Long QT Syndrome',gene:'KCNQ1/KCNH2',icon:'💓',col:'#fee2e2',cat:'Cardiovascular',inh:'AD',prev:'1 in 2,000',omim:'192500',syms:['Prolonged QT','Syncope','Ventricular arrhythmia','Sudden cardiac death'],tx:['Beta-blockers','ICD implantation','Activity restriction'],specs:['Electrophysiologist','Cardiologist','Geneticist'],dx:'ECG, exercise stress test, KCNQ1/KCNH2 sequencing',desc:'Cardiac ion channel mutations causing arrhythmia risk.'},
  {id:'HCM',name:'Hypertrophic Cardiomyopathy',gene:'MYH7/MYBPC3',icon:'🫀',col:'#fee2e2',cat:'Cardiovascular',inh:'AD',prev:'1 in 500',omim:'192600',syms:['Dyspnea','Chest pain','Syncope','Palpitations','Sudden death'],tx:['Beta-blockers','Calcium channel blockers','Myectomy','ICD'],specs:['Cardiologist','Geneticist'],dx:'Echocardiogram, cardiac MRI, sarcomere gene panel',desc:'Sarcomere gene mutations causing heart muscle thickening.'},
  // Renal
  {id:'ADPKD',name:'Polycystic Kidney Disease',gene:'PKD1',icon:'🫘',col:'#ede9fe',cat:'Renal',inh:'AD',prev:'1 in 500',omim:'173900',syms:['Hypertension','Flank pain','Kidney cysts','Hematuria','Renal failure'],tx:['Blood pressure control','Tolvaptan','Dialysis','Transplant'],specs:['Nephrologist','Geneticist'],dx:'Ultrasound (cyst count), PKD1/PKD2 sequencing',desc:'Most common hereditary kidney disease — cysts replace kidney tissue.'},
  {id:'AS',name:'Alport Syndrome',gene:'COL4A5',icon:'🫧',col:'#f0f9ff',cat:'Renal',inh:'X-linked/AR',prev:'1 in 5,000',omim:'301050',syms:['Hematuria','Progressive renal failure','Sensorineural hearing loss','Anterior lenticonus'],tx:['ACE inhibitors','Kidney transplant','Hearing aids'],specs:['Nephrologist','Audiologist','Geneticist'],dx:'Renal biopsy (EM), COL4A3/4/5 sequencing, urine protein',desc:'Collagen IV mutations affecting basement membranes in kidney, ear, and eye.'},
  // Neurological
  {id:'HD',name:"Huntington's Disease",gene:'HTT',icon:'🧠',col:'#fef3c7',cat:'Neurological',inh:'AD',prev:'1 in 10,000',omim:'143100',syms:['Chorea','Psychiatric symptoms','Cognitive decline','Dysarthria','Dysphagia'],tx:['Tetrabenazine (chorea)','Psychiatric medications','Physiotherapy'],specs:['Neurologist','Psychiatrist','Geneticist'],dx:'CAG repeat expansion in HTT gene (>35 repeats)',desc:'CAG repeat expansion causing progressive neurodegeneration — predictive testing available.'},
  {id:'SMA',name:'Spinal Muscular Atrophy',gene:'SMN1',icon:'💪',col:'#f0fdf4',cat:'Neurological',inh:'AR',prev:'1 in 6,000',omim:'253300',syms:['Progressive muscle weakness','Hypotonia','Respiratory failure','Scoliosis'],tx:['Nusinersen','Onasemnogene (gene therapy)','Risdiplam','Ventilatory support'],specs:['Neurologist','Pulmonologist','Orthopedist'],dx:'SMN1 deletion analysis, newborn screening in many countries',desc:'SMN1 deletions cause motor neuron degeneration — gene therapy transforming outcomes.'},
  {id:'FRDA',name:'Friedreich Ataxia',gene:'FXN',icon:'🚶',col:'#f3e8ff',cat:'Neurological',inh:'AR',prev:'1 in 50,000',omim:'229300',syms:['Progressive ataxia','Cardiomyopathy','Diabetes','Loss of reflexes','Scoliosis'],tx:['Omaveloxolone','Physical therapy','Cardiac monitoring','Diabetes management'],specs:['Neurologist','Cardiologist','Geneticist'],dx:'GAA repeat expansion in FXN, frataxin protein levels',desc:'GAA triplet repeat expansion causing frataxin deficiency and neurodegeneration.'},
  {id:'TS',name:'Tuberous Sclerosis',gene:'TSC1/TSC2',icon:'🧬',col:'#f0f9ff',cat:'Neurological',inh:'AD',prev:'1 in 6,000',omim:'191100',syms:['Epilepsy','Facial angiofibromas','Hamartomas','Intellectual disability','Autism'],tx:['mTOR inhibitors (everolimus)','Anti-epileptics','Surgery'],specs:['Neurologist','Dermatologist','Nephrologist'],dx:'Clinical criteria, TSC1/TSC2 sequencing, brain/kidney MRI',desc:'TSC1/TSC2 mutations drive benign tumor growth via mTOR dysregulation.'},
  {id:'NF1',name:'Neurofibromatosis Type 1',gene:'NF1',icon:'🔵',col:'#dbeafe',cat:'Neurological',inh:'AD',prev:'1 in 3,000',omim:'162200',syms:['Café-au-lait spots','Neurofibromas','Lisch nodules','Learning disabilities','Optic gliomas'],tx:['Selumetinib (plexiform neurofibromas)','Surgical removal','Surveillance'],specs:['Neurologist','Dermatologist','Ophthalmologist'],dx:'Clinical NIH criteria, NF1 sequencing',desc:'NF1 mutations impair RAS pathway regulation causing widespread neurofibromas.'},
  {id:'RTT',name:'Rett Syndrome',gene:'MECP2',icon:'👧',col:'#fdf2f8',cat:'Neurological',inh:'X-linked',prev:'1 in 10,000 females',omim:'312750',syms:['Regression','Hand stereotypies','Breathing irregularities','Seizures','Scoliosis'],tx:['Trofinetide','Anti-epileptics','Physiotherapy','Communication aids'],specs:['Neurologist','Respirologist','Physiotherapist'],dx:'Clinical criteria, MECP2 sequencing',desc:'MECP2 mutations in girls causing neurodevelopmental regression after normal early development.'},
  {id:'AT',name:'Ataxia-Telangiectasia',gene:'ATM',icon:'⚡',col:'#fef3c7',cat:'Neurological',inh:'AR',prev:'1 in 40,000-100,000',omim:'208900',syms:['Cerebellar ataxia','Telangiectasias','Immunodeficiency','Cancer predisposition','Radiation sensitivity'],tx:['IVIG for immunodeficiency','Physical therapy','Cancer surveillance'],specs:['Neurologist','Immunologist','Oncologist'],dx:'ATM sequencing, alpha-fetoprotein, lymphocyte chromosome breakage',desc:'ATM mutations impair DNA repair causing neurodegeneration and cancer risk.'},
  // Hematologic
  {id:'SCD',name:'Sickle Cell Disease',gene:'HBB',icon:'🩸',col:'#fee2e2',cat:'Hematologic',inh:'AR',prev:'1 in 500 (African descent)',omim:'603903',syms:['Painful crises','Anemia','Organ damage','Stroke','Infections'],tx:['Hydroxyurea','Voxelotor','Crizanlizumab','BMT','Gene therapy'],specs:['Hematologist','Pain specialist'],dx:'Newborn screening, HBB sequencing, hemoglobin electrophoresis',desc:'HBB mutation causing hemoglobin polymerization and red cell sickling.'},
  {id:'HA',name:'Hemophilia A',gene:'F8',icon:'🩹',col:'#fee2e2',cat:'Hematologic',inh:'X-linked',prev:'1 in 5,000 males',omim:'306700',syms:['Prolonged bleeding','Hemarthrosis','Spontaneous bleeds','Hematomas'],tx:['Factor VIII replacement','Emicizumab','Gene therapy (valoctocogene)'],specs:['Hematologist','Physiotherapist'],dx:'APTT, factor VIII activity, F8 sequencing',desc:'F8 mutations causing factor VIII deficiency — gene therapy now transforming treatment.'},
  {id:'TH',name:'Thalassemia',gene:'HBA1/HBB',icon:'💊',col:'#f0fdf4',cat:'Hematologic',inh:'AR',prev:'Common in Mediterranean/Asia',omim:'604131',syms:['Severe anemia','Hepatosplenomegaly','Bone deformities','Growth failure','Iron overload'],tx:['Regular transfusions','Iron chelation','BMT','Gene therapy (betibeglogene)'],specs:['Hematologist','Endocrinologist'],dx:'CBC, hemoglobin electrophoresis, HBA1/HBB sequencing',desc:'Globin chain synthesis defects causing severe hemolytic anemia.'},
  // Connective Tissue
  {id:'EDS',name:'Ehlers-Danlos Syndrome',gene:'COL5A1',icon:'🤸',col:'#fdf2f8',cat:'Connective Tissue',inh:'AD',prev:'1 in 5,000',omim:'130000',syms:['Joint hypermobility','Skin hyperextensibility','Chronic pain','Fatigue','Frequent dislocations'],tx:['Physical therapy','Pain management','Joint protection'],specs:['Rheumatologist','Physical therapist','Geneticist'],dx:'Beighton score, collagen gene panel',desc:'Connective tissue disorder affecting collagen synthesis.'},
  {id:'OI',name:'Osteogenesis Imperfecta',gene:'COL1A1',icon:'🦴',col:'#fef3c7',cat:'Connective Tissue',inh:'AD',prev:'1 in 10,000-20,000',omim:'166200',syms:['Bone fragility','Blue sclerae','Short stature','Hearing loss','Scoliosis'],tx:['Bisphosphonates','Intramedullary rodding','Physical therapy'],specs:['Orthopedist','Endocrinologist','Geneticist'],dx:'Bone density, collagen biochemistry, COL1A1/2 sequencing',desc:'Collagen I mutations causing brittle bones — highly variable severity.'},
  {id:'ACH',name:'Achondroplasia',gene:'FGFR3',icon:'📏',col:'#d1fae5',cat:'Connective Tissue',inh:'AD (mostly de novo)',prev:'1 in 25,000',omim:'100800',syms:['Short stature','Macrocephaly','Midface hypoplasia','Spinal stenosis','Rhizomelic shortening'],tx:['Vosoritide (growth factor)','Surgical decompression','Orthopedic management'],specs:['Orthopedist','Neurosurgeon','Geneticist'],dx:'Skeletal X-ray, FGFR3 pathogenic variant (p.Gly380Arg in >97%)',desc:'FGFR3 gain-of-function mutation causing impaired endochondral bone growth.'},
  // Immunological
  {id:'SCID',name:'Severe Combined Immunodeficiency',gene:'IL2RG/ADA',icon:'🛡️',col:'#f0fdf4',cat:'Immunological',inh:'X-linked/AR',prev:'1 in 40,000-100,000',omim:'300400',syms:['Recurrent severe infections','Failure to thrive','Absent thymic shadow','No T/B cells'],tx:['Hematopoietic stem cell transplant','Gene therapy (ADA-SCID)','IVIG','Isolation'],specs:['Immunologist','Infectious disease','Geneticist'],dx:'Lymphocyte counts/function, TREC (newborn screening), gene panel',desc:'Complete T and/or B cell deficiency — a pediatric emergency, treatable if detected early.'},
  {id:'CGD',name:'Chronic Granulomatous Disease',gene:'CYBB',icon:'🦠',col:'#fef3c7',cat:'Immunological',inh:'X-linked/AR',prev:'1 in 200,000',omim:'306400',syms:['Recurrent bacterial/fungal infections','Granulomas','Lymphadenopathy','Abscess formation'],tx:['Prophylactic antibiotics/antifungals','IFN-gamma','Hematopoietic SCT'],specs:['Immunologist','Infectious disease','Geneticist'],dx:'DHR flow cytometry, CYBB sequencing',desc:'NADPH oxidase deficiency causing phagocyte killing failure.'},
  // Oncological/Cancer Predisposition
  {id:'LS',name:'Lynch Syndrome',gene:'MLH1/MSH2',icon:'🎗️',col:'#fee2e2',cat:'Cancer Predisposition',inh:'AD',prev:'1 in 279',omim:'120435',syms:['Colorectal cancer','Endometrial cancer','Ovarian cancer','Urinary tract cancer','Family cancer history'],tx:['Surveillance colonoscopy','Prophylactic surgery','Aspirin chemoprevention'],specs:['Gastroenterologist','Gynecologist','Geneticist'],dx:'MSI testing, IHC, MLH1/MSH2/MSH6/PMS2 sequencing',desc:'MMR gene mutations causing hereditary colorectal and endometrial cancer.'},
  {id:'HBOC',name:'Hereditary Breast/Ovarian Cancer',gene:'BRCA1/BRCA2',icon:'🩺',col:'#ffe4e6',cat:'Cancer Predisposition',inh:'AD',prev:'1 in 400',omim:'604370',syms:['Breast cancer','Ovarian cancer','Pancreatic cancer','Prostate cancer (BRCA2)'],tx:['Increased surveillance','Risk-reducing surgery','PARP inhibitors','Chemoprevention'],specs:['Oncologist','Gynecologist','Geneticist'],dx:'BRCA1/BRCA2 sequencing, family history assessment',desc:'BRCA1/2 mutations dramatically increase breast and ovarian cancer risk.'},
  {id:'VHL',name:'Von Hippel-Lindau Disease',gene:'VHL',icon:'🔬',col:'#f3e8ff',cat:'Cancer Predisposition',inh:'AD',prev:'1 in 36,000',omim:'193300',syms:['Hemangioblastomas','Clear cell RCC','Pheochromocytoma','Retinal angiomas','Pancreatic cysts'],tx:['Belzutifan (HIF-2α inhibitor)','Surgical resection','Surveillance'],specs:['Oncologist','Ophthalmologist','Nephrologist'],dx:'VHL sequencing, MRI surveillance protocol',desc:'VHL mutations impair HIF regulation causing vascular tumors.'},
  // Iron/Mineral
  {id:'HHC',name:'Hereditary Hemochromatosis',gene:'HFE',icon:'🔴',col:'#fee2e2',cat:'Metabolic',inh:'AR',prev:'1 in 200',omim:'235200',syms:['Fatigue','Joint pain','Liver disease','Diabetes','Bronze skin'],tx:['Phlebotomy','Iron chelation','Dietary restriction'],specs:['Hepatologist','Hematologist'],dx:'Serum ferritin, transferrin saturation, HFE sequencing',desc:'Iron overload disorder — highly treatable when detected early.'},
  // Endocrine
  {id:'MEN2',name:'Multiple Endocrine Neoplasia 2',gene:'RET',icon:'🦋',col:'#fef3c7',cat:'Endocrine',inh:'AD',prev:'1 in 30,000',omim:'171400',syms:['Medullary thyroid cancer','Pheochromocytoma','Parathyroid hyperplasia','Marfanoid habitus'],tx:['Prophylactic thyroidectomy','Surgical resection','Selpercatinib/cabozantinib'],specs:['Endocrinologist','Surgeon','Geneticist'],dx:'Calcitonin, RET sequencing, annual surveillance',desc:'RET gain-of-function mutations causing hereditary thyroid cancer and pheochromocytoma.'},
  // Eye
  {id:'LCA',name:'Leber Congenital Amaurosis',gene:'RPE65',icon:'👁️',col:'#f0f9ff',cat:'Ophthalmologic',inh:'AR',prev:'1 in 80,000',omim:'204000',syms:['Severe visual impairment at birth','Nystagmus','Photophobia','Absent pupillary response'],tx:['Voretigene neparvovec (gene therapy)','Low vision aids','Orientation/mobility training'],specs:['Ophthalmologist','Geneticist'],dx:'ERG, RPE65 sequencing',desc:'RPE65 mutations — first approved in vivo gene therapy (Luxturna).'},
  // Skin
  {id:'XP',name:'Xeroderma Pigmentosum',gene:'XPC/ERCC2',icon:'☀️',col:'#fef3c7',cat:'Dermatologic',inh:'AR',prev:'1 in 250,000',omim:'278700',syms:['Extreme UV sensitivity','Early skin cancers','Ocular complications','Neurological features'],tx:['Strict UV avoidance','Topical fluorouracil','Surgical excision','DNA repair enzyme creams'],specs:['Dermatologist','Ophthalmologist','Neurologist'],dx:'UV-sensitivity testing, NER gene panel',desc:'DNA nucleotide excision repair deficiency causing extreme skin cancer susceptibility.'},
  // Skeletal muscle
  {id:'DMD',name:'Duchenne Muscular Dystrophy',gene:'DMD',icon:'💪',col:'#f0fdf4',cat:'Neuromuscular',inh:'X-linked',prev:'1 in 3,500 males',omim:'310200',syms:['Progressive muscle weakness','Gower sign','Calf pseudohypertrophy','Cardiomyopathy','Respiratory failure'],tx:['Corticosteroids','Ataluren/exon skipping','Delandistrogene (gene therapy)','Ventilatory support'],specs:['Neurologist','Cardiologist','Pulmonologist'],dx:'CK elevation, DMD sequencing/deletion panel, muscle biopsy',desc:'Dystrophin deficiency causing progressive muscle wasting — gene therapy era transforming outlook.'},
]

const CATS=[...new Set(DISEASES.map(d=>d.cat))].sort()
let curCat='All'

function loadDiseases(){
  // Build category tabs
  const tabs=document.getElementById('cat-tabs')
  tabs.innerHTML=`<button class="ctab on" onclick="setCat('All',this)">All (${DISEASES.length})</button>`+
    CATS.map(c=>`<button class="ctab" onclick="setCat('${c}',this)">${c} (${DISEASES.filter(d=>d.cat===c).length})</button>`).join('')
  renderDiseases()
}

function setCat(cat,btn){
  curCat=cat
  document.querySelectorAll('.ctab').forEach(e=>e.classList.remove('on'));btn.classList.add('on')
  renderDiseases()
}

function dSearch(q){
  const ql=q.toLowerCase();const inp=q
  const filtered=DISEASES.filter(d=>{
    const matchCat=curCat==='All'||d.cat===curCat
    if(!inp) return matchCat
    return matchCat&&(d.name.toLowerCase().includes(ql)||d.gene.toLowerCase().includes(ql)||(d.syms||[]).some(s=>s.toLowerCase().includes(ql)))
  })
  document.getElementById('dmeta').textContent=filtered.length+' disease'+(filtered.length!==1?'s':'')
  renderDiseaseList(filtered)
}

function renderDiseases(){
  const filtered=curCat==='All'?DISEASES:DISEASES.filter(d=>d.cat===curCat)
  document.getElementById('dmeta').textContent=filtered.length+' disease'+(filtered.length!==1?'s':'')
  renderDiseaseList(filtered)
}

function renderDiseaseList(list){
  const g=document.getElementById('dgrid')
  if(!list.length){g.innerHTML=`<div class="empty" style="grid-column:1/-1"><div class="empty-ico">🔍</div><p>No diseases found</p></div>`;return}
  g.innerHTML=list.map(d=>`
    <div class="dcard" onclick="openDM('${d.id}')">
      <div class="dico" style="background:${d.col}">${d.icon}</div>
      <div class="dname">${d.name}</div>
      <span class="dgene">${d.gene}</span>
      <div class="dmeta">${d.inh} · ${d.prev}</div>
      <div class="dtags">${(d.syms||[]).slice(0,3).map(s=>`<span class="dtag">${s}</span>`).join('')}</div>
    </div>`).join('')
}

function openDM(id){
  const d=DISEASES.find(x=>x.id===id);if(!d)return;S.dsel=d
  document.getElementById('dmtitle').innerHTML=`<div style="display:flex;align-items:center;gap:11px"><div style="width:40px;height:40px;border-radius:9px;background:${d.col};display:flex;align-items:center;justify-content:center;font-size:20px">${d.icon}</div><div><div style="font-size:17px;font-weight:700;color:var(--text)">${d.name}</div><span class="dgene">${d.gene}</span></div></div>`
  document.getElementById('dmbody').innerHTML=`
    <p style="font-size:13px;color:var(--text3);margin-bottom:16px;line-height:1.6">${d.desc}</p>
    <div class="dgrid2">${[['Inheritance',d.inh],['Prevalence',d.prev],['OMIM',d.omim||'—'],['Category',d.cat]].map(([l,v])=>`<div class="dcell"><div class="dcl">${l}</div><div class="dcv">${v}</div></div>`).join('')}</div>
    <div class="dmsec"><div class="dmsect">KEY CLINICAL FEATURES</div><div class="chiplist">${(d.syms||[]).map(s=>`<span class="chip chip-gr">${s}</span>`).join('')}</div></div>
    <div class="dmsec"><div class="dmsect">DIAGNOSIS</div><p style="font-size:12px;color:var(--text2)">${d.dx}</p></div>
    <div class="dmsec"><div class="dmsect">TREATMENT OPTIONS</div><div class="chiplist">${(d.tx||[]).map(t=>`<span class="chip chip-g">${t}</span>`).join('')}</div></div>
    <div class="dmsec"><div class="dmsect">SPECIALISTS</div><div class="chiplist">${(d.specs||[]).map(s=>`<span class="chip chip-b">${s}</span>`).join('')}</div></div>
    <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
      ${d.omim?`<a class="elink" href="https://www.omim.org/entry/${d.omim}" target="_blank">OMIM #${d.omim} <span>↗</span></a>`:''}
      <a class="elink" href="https://clinicaltrials.gov/search?cond=${encodeURIComponent(d.name)}" target="_blank">Clinical Trials <span>↗</span></a>
      <a class="elink" href="https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(d.name)}" target="_blank">PubMed <span>↗</span></a>
    </div>`
  document.getElementById('dask-btn').onclick=()=>{closeDM();setCtx({condition:d.name,gene:d.gene});showPage('home');qsend(`Tell me about ${d.name} — causes, symptoms, and treatments`)}
  document.getElementById('dmodal').classList.add('open')
}
function closeDM(){document.getElementById('dmodal').classList.remove('open')}

// ─── Helpers ──────────────────────────────────────────────────────────
function sbadge(sig){
  if(!sig)return''
  const s=sig.toLowerCase();let c='sc',l=sig.slice(0,16)
  if(s.includes('pathogenic')&&!s.includes('likely')&&!s.includes('conflict')){c='sp';l='Pathogenic'}
  else if(s.includes('likely pathogenic')){c='slp';l='Likely Pathogenic'}
  else if(s.includes('likely benign')){c='sb2';l='Likely Benign'}
  else if(s.includes('benign')){c='sb2';l='Benign'}
  else if(s.includes('uncertain')||s.includes('vus')){c='sv';l='VUS'}
  else if(s.includes('conflict')){c='sc';l='Conflicting'}
  return`<span class="sbadge ${c}">${l}</span>`
}
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function md(t){
  if(!t)return''
  return t.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/\*(.+?)\*/g,'<em>$1</em>').replace(/_(.+?)_/g,'<em>$1</em>').replace(/^### (.+)$/gm,'<h3>$1</h3>').replace(/^## (.+)$/gm,'<h2>$1</h2>').replace(/^# (.+)$/gm,'<h1>$1</h1>').replace(/^- (.+)$/gm,'<li>$1</li>').replace(/^(\d+)\. (.+)$/gm,'<li>$2</li>').replace(/(<li>.*?<\/li>\n?)+/gs,m=>'<ul style="padding-left:14px;margin:4px 0">'+m+'</ul>').replace(/\n\n/g,'<br><br>').replace(/\n/g,'<br>')
}
function b64e(s){try{return btoa(unescape(encodeURIComponent(s)))}catch{return btoa(s.slice(0,500))}}
function b64d(s){try{return decodeURIComponent(escape(atob(s)))}catch{return atob(s)}}

// ─── Boot ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded',()=>{
  initTheme();showPage('home');ping();setInterval(ping,30000)
  ;['umodal','dmodal','info-modal','phone-modal'].forEach(id=>{
    const el=document.getElementById(id)
    el.addEventListener('click',e=>{if(e.target===el){el.classList.remove('open');document.body.style.overflow=''}})
  })
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){
      ;['umodal','dmodal','info-modal','phone-modal'].forEach(id=>document.getElementById(id).classList.remove('open'))
      closeDrawer();closeLeftDrawer();document.body.style.overflow=''
    }
  })
})
</script>
</body>
</html>
"""
