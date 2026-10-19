#!/usr/bin/env python3
"""Build a public LEGO catalogue from Rebrickable's downloadable CSV exports."""
import csv, gzip, io, json, urllib.request, datetime, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://cdn.rebrickable.com/media/downloads/'
def rows(filename):
    req=urllib.request.Request(BASE+filename+'.csv.gz',headers={'User-Agent':'LastPieceLtdCatalog/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r:
        raw=r.read()
    return list(csv.DictReader(io.StringIO(gzip.decompress(raw).decode('utf-8-sig'))))
def main():
    themes=rows('themes'); sets=rows('sets')
    theme_by_id={int(t['id']):t for t in themes}
    def root_name(tid):
        seen=set()
        while tid in theme_by_id and tid not in seen:
            seen.add(tid); t=theme_by_id[tid]
            if not t.get('parent_id'):return t['name']
            tid=int(t['parent_id'])
        return ''
    selected=[]
    for s in sets:
        root=root_name(int(s['theme_id']))
        if root not in ('Star Wars','Harry Potter'):continue
        set_num=s['set_num']
        if not set_num.endswith('-1'):continue
        id=set_num[:-2]
        if not id.isdigit():continue
        selected.append({'id':id,'name':s['name'],'theme':root,'year':int(s['year']),
          'parts':int(s['num_parts']), 'image':s.get('img_url') or '',
          'source':'rebrickable','price':None,'sales':None,'growth':None,'buy':None,
          'retired':None})
    selected.sort(key=lambda x:(x['theme'], -x['year'],x['id']))
    if len(selected)<100:raise RuntimeError(f'Suspiciously small catalogue: {len(selected)} sets')
    dest=ROOT/'data'/'catalog.json';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source':'Rebrickable downloads: sets.csv.gz + themes.csv.gz',
        'sets':selected},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Wrote {len(selected)} sets to {dest}')
if __name__=='__main__':main()
