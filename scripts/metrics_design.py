"""Editable designs for the local animated metrics cards."""
from datetime import date, timedelta
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]/'assets'
BG='#080205'; PANEL='#140809'; BORDER='#49201F'; RED='#C0392B'; LIGHT='#F07868'; INK='#F4E7DF'; MUTED='#D5ADA7'

def label(x,y,value,size=12,color=INK,attrs=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {attrs}>{escape(str(value))}</text>'

def frame(h,title,subtitle,tag):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" viewBox="0 0 900 {h}" font-family="Arial, sans-serif"><defs><radialGradient id="glow"><stop stop-color="{RED}" stop-opacity=".24"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient><linearGradient id="line"><stop stop-color="{RED}" stop-opacity="0"/><stop offset=".5" stop-color="{LIGHT}"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient></defs><rect x="1" y="1" width="898" height="{h-2}" rx="15" fill="{BG}" stroke="{BORDER}"/><ellipse cx="735" cy="52" rx="160" ry="48" fill="url(#glow)"/><rect x="18" y="18" width="864" height="{h-36}" rx="11" fill="{PANEL}" fill-opacity=".8" stroke="{BORDER}"/>'''+label(35,48,title,23,attrs='font-weight="bold"')+label(35,68,subtitle,12,MUTED)+label(844,46,tag,11,LIGHT,'text-anchor="end" font-family="monospace"')+f'<circle cx="859" cy="42" r="4" fill="{LIGHT}"><animate attributeName="opacity" values="1;.25;1" dur="2.5s" repeatCount="indefinite"/></circle>'

def finish(s,h,name):
    s+=f'<rect x="35" y="{h-32}" width="830" height="2" rx="1" fill="{BORDER}"/><rect x="35" y="{h-32}" width="95" height="2" fill="url(#line)"><animate attributeName="x" values="35;770;35" dur="9s" repeatCount="indefinite"/></rect></svg>'
    (ROOT/name).write_text(s,encoding='utf-8')

def number(v): return '—' if v is None else f'{v:,}'

def stats(collection=None, stars=None, repos=None):
    s=frame(200,'GitHub Stats','Public repository totals / contributions in the past year' if collection is not None else 'Awaiting first GitHub Actions data refresh','> metrics.scan')
    c=collection or {}
    items=[('COMMITS',c.get('totalCommitContributions')),('PULL REQUESTS',c.get('totalPullRequestContributions')),('ISSUES',c.get('totalIssueContributions')),('STARS',stars),('PUBLIC REPOS',repos)]
    for i,(name,value) in enumerate(items):
        x=35+i*168
        s+=f'<rect x="{x}" y="86" width="158" height="68" rx="8" fill="{BG}" stroke="{BORDER}"/><rect x="{x+10}" y="94" width="3" height="45" rx="1.5" fill="{RED}"><animate attributeName="opacity" values=".4;1;.4" dur="3s" begin="{i*.25}s" repeatCount="indefinite"/></rect>'
        s+=label(x+79,119,number(value),26,attrs='text-anchor="middle" font-weight="bold"')+label(x+79,139,name,10,MUTED,'text-anchor="middle" letter-spacing=".5"')
    finish(s,200,'github-stats.svg')

def streak_values(calendar):
    days=sorted((date.fromisoformat(d['date']),d['contributionCount']) for w in calendar['weeks'] for d in w['contributionDays'])
    if not days:return 0,0
    best=run=0; prev=None
    for day,count in days:
        run=(run+1 if prev is not None and day-prev==timedelta(days=1) else 1) if count else 0
        best=max(best,run);prev=day
    # Allow the latest calendar day to be empty without breaking yesterday's streak.
    if not days[-1][1]: days=days[:-1]
    current=0; expected=days[-1][0] if days else None
    for day,count in reversed(days):
        if day!=expected or not count:break
        current+=1;expected-=timedelta(days=1)
    return current,best

def streak(calendar=None):
    current,best=streak_values(calendar) if calendar is not None else (None,None)
    total=calendar['totalContributions'] if calendar is not None else None
    s=frame(235,'Contribution Streak','Rolling year / calendar-day activity' if calendar is not None else 'Awaiting first GitHub Actions data refresh','> streak.scan')
    for x,title,value in [(35,'TOTAL CONTRIBUTIONS',total),(595,'LONGEST STREAK',best)]:
        s+=f'<rect x="{x}" y="92" width="270" height="94" rx="9" fill="{BG}" stroke="{BORDER}"/>'
        s+=label(x+135,137,number(value),35,attrs='text-anchor="middle" font-weight="bold"')+label(x+135,160,title,11,MUTED,'text-anchor="middle" letter-spacing=".5"')
    s+=f'<circle cx="450" cy="132" r="47" fill="{BG}" stroke="{BORDER}" stroke-width="3"/><circle cx="450" cy="132" r="47" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="96 199.31" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 450 132" to="360 450 132" dur="8s" repeatCount="indefinite"/></circle><circle cx="450" cy="132" r="39" fill="none" stroke="{LIGHT}" stroke-opacity=".18"><animate attributeName="stroke-opacity" values=".12;.55;.12" dur="3s" repeatCount="indefinite"/></circle>'
    s+=label(450,142,number(current),32,attrs='text-anchor="middle" font-weight="bold"')+label(450,195,'CURRENT STREAK / DAYS',11,LIGHT,'text-anchor="middle" letter-spacing=".5"')
    finish(s,235,'streak-stats.svg')
