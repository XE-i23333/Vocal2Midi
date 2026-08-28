from __future__ import annotations
import math, xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
import numpy as np
from inference.LyricFA.tools.ZhG2p import ZhG2p
NS='http://www.yamaha.co.jp/vocaloid/schema/vsq3/'; XSI='http://www.w3.org/2001/XMLSchema-instance'; PPQ=480
_G2P = None
def _t(s,b): return int(round(s*b*8.0))
def _e(p,t,v=None,**a):
    x=ET.SubElement(p,t,a)
    if v is not None:x.text=str(v)
    return x
def _vsqx_lyric(value):
    global _G2P
    value = (value or 'a').strip()
    if any(0x4E00 <= ord(ch) <= 0x9FFF for ch in value):
        if _G2P is None: _G2P = ZhG2p('mandarin')
        value = _G2P.convert(value, include_tone=False, convert_number=True)
    return value.split()[0] if value.split() else 'a'
def _lyric_phoneme(value, language='zh'):
    return _vsqx_lyric(value)
def save_vsqx(notes:list[Any],filepath:Path,tempo:float=120.0,language:str='zh')->None:
    filepath=Path(filepath); valid=[]
    for n in notes:
        vals=[getattr(n,k,math.nan) for k in ('onset','offset','pitch')]
        if all(np.isfinite(v) for v in vals) and vals[1]>vals[0]:valid.append(n)
    valid.sort(key=lambda n:n.onset); end=max((_t(n.offset,tempo) for n in valid),default=PPQ)
    ET.register_namespace('',NS); ET.register_namespace('xsi',XSI)
    r=ET.Element('{%s}vsq3'%NS,{'{%s}schemaLocation'%XSI:NS+' vsq3.xsd'}); _e(r,'vender','Yamaha corporation'); _e(r,'version','3.0.0.11')
    vt=_e(r,'vVoiceTable'); v=_e(vt,'vVoice')
    for t,x in (('vBS',4),('vPC',0),('compID','BHHBLFZQFJFBHCFQ'),('vVoiceName','Default Singer')):_e(v,t,x)
    vp=_e(v,'vVoiceParam')
    for t in ('bre','bri','cle','gen','ope'):_e(vp,t,0)
    m=_e(r,'mixer'); u=_e(m,'masterUnit')
    for t,x in (('outDev',0),('retLevel',0),('vol',0)): _e(u,t,x)
    u=_e(m,'vsUnit')
    for t,x in (('vsTrackNo',0),('inGain',0),('sendLevel',-898),('sendEnable',0),('mute',0),('solo',0),('pan',64),('vol',0)):_e(u,t,x)
    for name in ('seUnit','karaokeUnit'):
        u=_e(m,name)
        fields = (('inGain',0),('mute',0),('solo',0),('vol',0)) if name == 'karaokeUnit' else (('inGain',0),('sendLevel',-898),('sendEnable',0),('mute',0),('solo',0),('pan',64),('vol',0))
        for t,x in fields:_e(u,t,x)
    mt=_e(r,'masterTrack'); _e(mt,'seqName',filepath.stem); _e(mt,'comment',''); _e(mt,'resolution',PPQ); _e(mt,'preMeasure',1)
    q=_e(mt,'timeSig'); _e(q,'posMes',0); _e(q,'nume',4); _e(q,'denomi',4); q=_e(mt,'tempo'); _e(q,'posTick',0); _e(q,'bpm',int(round(tempo*100)))
    tr=_e(r,'vsTrack'); _e(tr,'vsTrackNo',0); _e(tr,'trackName',filepath.stem); _e(tr,'comment',''); p=_e(tr,'musicalPart'); start=PPQ*4; _e(p,'posTick',start); _e(p,'playTime',start+end); _e(p,'partName',filepath.stem); _e(p,'comment','')
    s=_e(p,'stylePlugin'); _e(s,'stylePluginID','ACA9C502-A04B-42b5-B2EB-5CEA36D16FCE'); _e(s,'stylePluginName','VOCALOID2 Compatible Style'); _e(s,'version','3.0.0.1'); s=_e(p,'singer'); _e(s,'posTick',0); _e(s,'vBS',4); _e(s,'vPC',0)
    for n0 in valid:
        z=_t(n0.onset,tempo); lyric = _lyric_phoneme(getattr(n0,'lyric',''), language); n=_e(p,'note'); _e(n,'posTick',z); _e(n,'durTick',max(1,_t(n0.offset,tempo)-z)); _e(n,'noteNum',int(np.clip(round(n0.pitch),0,127))); _e(n,'velocity',64); _e(n,'lyric',lyric)
        _e(n,'phnms','',lock='0')
        st=_e(n,'noteStyle')
        for k,x in (('accent',50),('bendDep',8),('bendLen',0),('decay',50),('fallPort',0),('opening',127),('risePort',0),('vibLen',0),('vibType',0)):_e(st,'attr',x,id=k)
    _e(r,'seTrack'); _e(r,'karaokeTrack'); a=_e(r,'aux'); _e(a,'auxID','AUX_VST_HOST_CHUNK_INFO'); _e(a,'content','VlNDSwcAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'); ET.indent(r,space='  '); filepath.parent.mkdir(parents=True,exist_ok=True); ET.ElementTree(r).write(filepath,encoding='UTF-8',xml_declaration=True); print(f'Saved VSQX file: {filepath}')
