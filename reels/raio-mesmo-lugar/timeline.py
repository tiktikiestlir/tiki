import json
tts=json.load(open("tts.json"))
starts=[0.05,3.55,7.0,9.9,12.0,15.6,17.4]
T=20.0
lines=[]
for s,l in zip(starts,tts):
    lines.append({"t":s,"text":l["text"],"dur":l["dur"],"words":[{"w":w["w"],"t":round(s+w["s"],3),"e":round(s+w["s"]+w["d"],3)} for w in l["words"]]})
strikes=[{"t":1.75,"tgt":[-6,0,3],"kind":"ground"},
         {"t":3.15,"tgt":[3,0,7],"kind":"ground"},
         {"t":6.05,"tgt":[-3,0,-7],"kind":"ground"},
         {"t":8.45,"tgt":"tower","kind":"tower"}]
# 22 rapid hits 12.25..14.7, ease-in-out spacing
n=22
for i in range(n):
    u=i/(n-1)
    e=u*u*(3-2*u)
    strikes.append({"t":round(12.3+e*2.4,3),"tgt":"tower","kind":"rapid"})
json.dump({"T":T,"fps":30,"lines":lines,"strikes":strikes,"card":[10.45,11.9],"mito":12.0},open("timeline.json","w"),ensure_ascii=False,indent=1)
for l in lines: print(l["t"], round(l["t"]+l["dur"],2), round(l["t"]/T*100,1),"%", l["text"])
