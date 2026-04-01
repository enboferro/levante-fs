import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
st.set_page_config(page_title="LUD PRO",layout="wide")
st_autorefresh(interval=1000,key="f5")
ss=st.session_state
st.markdown("""<style>.stApp{background:#F0F2F6}.h-box{background:linear-gradient(90deg,#003D7A,#7A0019);padding:10px;border-radius:10px;color:white;text-align:center}.rel-box{background:#1E1E1E;border:3px solid #FFD700;border-radius:20px;padding:10px}.rel-txt{color:white;font-size:4rem!important;font-weight:bold;text-align:center;margin:0}.m-card{padding:15px;border-radius:15px;color:white;text-align:center;min-height:180px}.stButton>button{height:3rem;font-weight:bold}.j-card{background:white;padding:8px;border-radius:10px;border-left:8px solid #D3D3D3;margin-bottom:5px}</style>""",unsafe_allow_html=True)
if 'js' not in ss:ss.js=[{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss:ss.rt1,ss.rt2,ss.pt,ss.ml,ss.mr,ss.fl,ss.fr=0.0,0.0,"T1",0,0,0,0
if 'ac' not in ss:ss.ac,ss.ig,ss.pos=False,None,"NEU"
if 'tpl' not in ss:ss.tpl,ss.tpr,ss.tpn,ss.lpc=0.0,0.0,0.0,time.time()
now=time.time()
if ss.ac:
    d=now-ss.lpc
    if ss.pos=="LUD":ss.tpl+=d
    elif ss.pos=="RIV":ss.tpr+=d
    else:ss.tpn+=d
ss.lpc=now
with st.container():
    cl,ci,cr=st.columns([1,4,1])
    cl.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png",width=60)
    with ci:
        r1,r2=st.columns(2)
        rvn=r1.text_input("R","RIVAL",label_visibility="collapsed").upper()
        fp=r2.date_input("F",datetime.now(),label_visibility="collapsed")
        st.markdown(f"<div class='h-box'><h2>LUD vs {rvn}</h2></div>",unsafe_allow_html=True)
    if cr.button("RESET"):ss.clear();st.rerun()
c1,c2,c3=st.columns([2,3,2])
with c1:
    st.markdown(f"<div class='m-card' style='background:{'#FF0000' if ss.fl>=5 else '#003D7A'}'><h3>LUD</h3><h1 style='font-size:4rem;color:white'>{ss.ml}</h1><p>F: {ss.fl}</p></div>",unsafe_allow_html=True)
    la,lb=st.columns(2)
    if la.button("⚽",key="gl"):ss.ml+=1;st.rerun()
    if lb.button("⚠️",key="fl"):ss.fl+=1;st.rerun()
with c2:
    tv=ss.rt1 if ss.pt=="T1" else ss.rt2
    if ss.ac and ss.ig:tv+=now-ss.ig
    m,s=divmod(int(tv),60)
    st.markdown(f"<div class='rel-box'><p class='rel-txt'>{m:02d}:{s:02d}</p></div>",unsafe_allow_html=True)
    if not ss.ac:
        if st.button("▶ START",type="primary",key="st",use_container_width=True):
            ss.ac,ss.ig=True,now
            for j in ss.js:
                if j["p"]:j["ini"]=now
            st.rerun()
    else:
        if st.button("⏸ STOP",type="secondary",key="sp",use_container_width=True):
            ss.ac=False
            if ss.pt=="T1":ss.rt1+=now-ss.ig
            else:ss.rt2+=now-ss.ig
            for j in ss.js:
                if j["p"] and j["ini"]:
                    if ss.pt=="T1":j["t1"]+=now-j["ini"]
                    else:j["t2"]+=now-j["ini"]
                    j["ini"]=None
            ss.ig=None;st.rerun()
with c3:
    st.markdown(f"<div class='m-card' style='background:{'#FF0000' if ss.fr>=5 else '#7A0019'}'><h3>{rvn[:5]}</h3><h1 style='font-size:4rem;color:white'>{ss.mr}</h1><p>F: {ss.fr}</p></div>",unsafe_allow_html=True)
    ra,rb=st.columns(2)
    if ra.button("⚽ ",key="gr"):ss.mr+=1;st.rerun()
    if rb.button("⚠️ ",key="fr"):ss.fr+=1;st.rerun()
st.divider()
p1,p2,p3=st.columns(3)
if p1.button("LUD",key="pl",use_container_width=True,type="primary" if ss.pos=="LUD" else "secondary"):ss.pos="LUD";st.rerun()
if p2.button("NEU",key="pn",use_container_width=True,type="primary" if ss.pos=="NEU" else "secondary"):ss.pos="NEU";st.rerun()
if p3.button(rvn,key="pr",use_container_width=True,type="primary" if ss.pos=="RIV" else "secondary"):ss.pos="RIV";st.rerun()
st.divider()
for i in range(0,14,2):
    cols=st.columns(2)
    for idx,col in enumerate(cols):
        ji=i+idx
        if ji<14:
            j=ss.js[ji]
            with col:
                st.markdown(f"<div class='j-card' style='border-left-color:{'#003D7A' if j['p'] else '#D3D3D3'}'>",unsafe_allow_html=True)
                n,t,e=st.columns([2,1,1])
                j["n"]=n.text_input(f"n{ji}",j["n"],key=f"nj{ji}",label_visibility="collapsed")
                tj=j["t1"]+j["t2"]
                if ss.ac and j["p"] and j["ini"]:tj+=now-j["ini"]
                mj,sj=divmod(int(tj),60)
                t.write(f"{mj:02d}:{sj:02d}")
                if e.button("🔴" if j["p"] else "🟢",key=f"bt{ji}"):
                    if not j["p"] and sum(1 for x in ss.js if x["p"])<5:
                        j["p"],j["e"]=True,j["e"]+1
                        if ss.ac:j["ini"]=now
                    elif j["p"]:
                        if ss.ac and j["ini"]:
                            if ss.pt=="T1":j["t1"]+=now-j["ini"]
                            else:j["t2"]+=now-j["ini"]
                        j["p"],j["ini"]=False,None
                    st.rerun()
                s1,s2,s3,s4=st.columns(4)
                if s1.button(f"T{j['t']}",key=f"tj{ji}"):j["t"]+=1;st.rerun()
                if s2.button(f"P{j['per']}",key=f"pj{ji}"):j["per"]+=1;st.rerun()
                if s3.button(f"R{j['rec']}",key=f"rj{ji}"):j["rec"]+=1;st.rerun()
                if s4.button(f"G{j['g']}",key=f"gj{ji}"):j["g"]+=1;ss.ml+=1;st.rerun()
                st.markdown("</div>",unsafe_allow_html=True)
st.divider()
if st.button("CSV"):
    d=[{"N":round((x["t1"]+x["t2"])/60,1),"G":x["g"],"T":x["t"]} for x in ss.js]
    st.download_button("FIN",pd.DataFrame(d).to_csv().encode('utf-8'),f"LUD.csv","text/csv",key="dfin")
