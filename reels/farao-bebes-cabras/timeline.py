import json
tts=json.load(open("tts.json"))
T=19.6
starts=[0.05,3.12,5.4,7.62,9.95,11.76,14.1,17.45]
lines=[]
for s,l in zip(starts,tts):
    lines.append({"t":s,"text":l["text"],"dur":l["dur"],"words":[{"w":w["w"],"t":round(s+w["s"],3),"e":round(s+w["s"]+w["d"],3)} for w in l["words"]]})
json.dump({"T":T,"fps":30,"lines":lines,"card":[10.3,11.7],"answer":11.76},open("timeline.json","w"),ensure_ascii=False,indent=1)
for l in lines: print(l["t"],round(l["t"]/T*100,1),"%",[(w["w"],w["t"]) for w in l["words"]])
