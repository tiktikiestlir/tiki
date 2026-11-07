import json
tts=json.load(open("tts.json"))
T=19.2
starts=[0.05,2.5,5.0,6.72,10.1,11.52,15.21,16.67]
lines=[]
for s,l in zip(starts,tts):
    lines.append({"t":s,"text":l["text"],"dur":l["dur"],"words":[{"w":w["w"],"t":round(s+w["s"],3),"e":round(s+w["s"]+w["d"],3)} for w in l["words"]]})
json.dump({"T":T,"fps":30,"lines":lines,"card":[10.1,11.5],"answer":11.52,"cut":8.3,"open":8.85,"close":17.55},open("timeline.json","w"),ensure_ascii=False,indent=1)
for l in lines:
    print(l["t"],round(l["t"]/T*100,1),"%",[ (w["w"],w["t"]) for w in l["words"]])
