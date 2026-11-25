"""Render animated SVGs from GitHub public repository and contribution data."""
import os, json, urllib.request, datetime, collections, math, html, pathlib, sys
from metrics_design import stats, streak
ROOT=pathlib.Path(__file__).resolve().parents[1]/'assets'
USER='mmandled'
TOKEN=os.environ.get('GITHUB_TOKEN','')
def api(url, payload=None):
    headers={'Accept':'application/vnd.github+json','User-Agent':'mmandled-profile','X-GitHub-Api-Version':'2022-11-28'}
    if TOKEN: headers['Authorization']='Bearer '+TOKEN
    if payload is not None: headers['Content-Type']='application/json'
    req=urllib.request.Request(url, data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as res: return json.load(res)
def esc(s): return html.escape(str(s),quote=True)
def text(x,y,s,size=14,color='#F4E7DF',extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{esc(s)}</text>'
def frame(h,title,subtitle,tag):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" viewBox="0 0 900 {h}" font-family="Arial, sans-serif"><defs><radialGradient id="glow"><stop stop-color="#C0392B" stop-opacity=".24"/><stop offset="1" stop-color="#080205" stop-opacity="0"/></radialGradient><linearGradient id="bar"><stop stop-color="#79251F"/><stop offset="1" stop-color="#E36C5E"/></linearGradient><linearGradient id="scan"><stop stop-color="#C0392B" stop-opacity="0"/><stop offset=".5" stop-color="#E36C5E" stop-opacity=".28"/><stop offset="1" stop-color="#C0392B" stop-opacity="0"/></linearGradient></defs><rect x="1" y="1" width="898" height="{h-2}" rx="15" fill="#080205" stroke="#49201F"/><ellipse cx="680" cy="65" rx="245" ry="65" fill="url(#glow)"/><rect x="18" y="18" width="864" height="{h-36}" rx="11" fill="#140809" fill-opacity=".82" stroke="#49201F"/>'''+text(34,48,title,23,extra='font-weight="bold"')+text(35,68,subtitle,12,'#D5ADA7')+text(864,47,tag,11,'#E36C5E','text-anchor="end" font-family="monospace"')
def stack(data=None):
    rows=sorted((data or {}).items(),key=lambda p:-p[1]); total=sum(v for _,v in rows)
    if len(rows)>6: rows=rows[:5]+[('Other',sum(v for _,v in rows[5:]))]
    h=max(220,100+30*len(rows)); s=frame(h,'Language Stack','Public, non-fork repositories / language bytes','> stack.scan')
    if not rows: s+=text(35,115,'Awaiting first GitHub Actions data refresh',15,'#D5ADA7')
    for i,(name,value) in enumerate(rows):
        y=99+i*30; pct=100*value/total; w=540*pct/100
        s+=f'<circle cx="40" cy="{y-4}" r="4" fill="#E36C5E"/>'+text(53,y,name,13,extra='font-weight="bold"')+text(274,y,f'{pct:.1f}%',12,'#E36C5E','text-anchor="end"')+f'<rect x="300" y="{y-11}" width="540" height="9" rx="4.5" fill="#35201F"/><rect x="300" y="{y-11}" width="{w:.2f}" height="9" rx="4.5" fill="url(#bar)"><animate attributeName="width" values="0;{w:.2f};{w:.2f}" keyTimes="0;0.22;1" dur="8s" begin="{i*.12}s" repeatCount="indefinite"/></rect>'
    s+='<rect x="34" y="'+str(h-32)+'" width="95" height="2" fill="#C0392B"><animate attributeName="opacity" values=".25;1;.25" dur="3s" repeatCount="indefinite"/></rect></svg>'
    (ROOT/'language-stack.svg').write_text(s,encoding='utf-8')
def heatmap(calendar=None):
    weeks=calendar['weeks'] if calendar else []
    s=frame(224,'Contribution Activity',f"{calendar['totalContributions']:,} contributions in the past year" if calendar else 'Awaiting first GitHub Actions data refresh','> activity.scan')
    palette=['#281719','#55201E','#893029','#C0392B','#F07868']; levels={'NONE':0,'FIRST_QUARTILE':1,'SECOND_QUARTILE':2,'THIRD_QUARTILE':3,'FOURTH_QUARTILE':4}
    s+=text(720,69,'Less',10,'#D5ADA7')+text(860,69,'More',10,'#D5ADA7','text-anchor="end"')
    for i,c in enumerate(palette): s+=f'<rect x="{749+15*i}" y="60" width="11" height="11" rx="2" fill="{c}"/>'
    previous=None
    for col in range(len(weeks) if weeks else 53):
        days=weeks[col]['contributionDays'] if weeks else []
        if days:
            d=datetime.date.fromisoformat(days[0]['date']); month=d.strftime('%b')
            if month!=previous and col<52: s+=text(49+col*15,91,month,10,'#D5ADA7');previous=month
        for day in (days if weeks else [{'weekday':r,'contributionLevel':'NONE'} for r in range(7)]):
            row=day['weekday']; x=49+col*15;y=100+row*15;level=levels[day['contributionLevel']]; tooltip=f"{day['date']}: {day['contributionCount']} contributions" if weeks else 'Data not loaded'
            s+=f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{palette[level]}"><title>{esc(tooltip)}</title>'
            if level: s+=f'<animate attributeName="opacity" values="1;.45;1;1" keyTimes="0;.12;.25;1" dur="6s" begin="{col*.055+row*.025:.2f}s" repeatCount="indefinite"/>'
            s+='</rect>'
    s+='<rect x="34" y="98" width="22" height="105" fill="url(#scan)"><animate attributeName="x" values="34;840;34" dur="12s" repeatCount="indefinite"/></rect></svg>'
    (ROOT/'contribution-heatmap.svg').write_text(s,encoding='utf-8')
def main():
    if '--placeholder' in sys.argv: stack();heatmap();stats();streak();return
    totals=collections.Counter(); page=1; stars=0; repo_count=0
    while True:
        repos=api(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner')
        for repo in repos:
            if not repo['private'] and not repo['fork']:
                stars+=repo['stargazers_count']; repo_count+=1
            if not repo['fork'] and not repo['private'] and repo['name'].lower()!=USER.lower(): totals.update(api(repo['languages_url']))
        if len(repos)<100: break
        page+=1
    query='''query($login:String!){user(login:$login){contributionsCollection{totalCommitContributions totalPullRequestContributions totalIssueContributions contributionCalendar{totalContributions weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}'''
    result=api('https://api.github.com/graphql',{'query':query,'variables':{'login':USER}})
    if result.get('errors'): raise RuntimeError(str(result['errors']))
    collection=result['data']['user']['contributionsCollection']
    calendar=collection['contributionCalendar']
    stack(totals); heatmap(calendar); stats(collection,stars,repo_count); streak(calendar)
if __name__=='__main__': main()
