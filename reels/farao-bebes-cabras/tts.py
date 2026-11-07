import asyncio, json, edge_tts, os, subprocess
LINES = [
 "Um faraó mandou criar dois bebês no meio das cabras.",
 "Pra descobrir a primeira língua do mundo.",
 "Regra: ninguém fala perto deles.",
 "Dois anos depois, um deles falou.",
 "Chuta: qual palavra?",
 "Bécos! Que é pão... em frígio.",
 "E concluiu: os frígios eram mais antigos que o Egito.",
 "Sabia? Comenta bécos.",
]
async def one(i, text):
    c = edge_tts.Communicate(text, "pt-BR-ThalitaMultilingualNeural", rate="+10%", proxy=os.environ["HTTPS_PROXY"], boundary="WordBoundary")
    words=[]; audio=b""
    async for ch in c.stream():
        if ch["type"]=="audio": audio+=ch["data"]
        elif ch["type"]=="WordBoundary":
            words.append({"w":ch["text"],"s":ch["offset"]/1e7,"d":ch["duration"]/1e7})
    open(f"line{i}.mp3","wb").write(audio)
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"line{i}.mp3","-ar","48000","-ac","1",f"line{i}.wav"])
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"line{i}.wav"]))
    return {"text":text,"words":words,"dur":dur}
async def main():
    out=[await one(i,t) for i,t in enumerate(LINES)]
    json.dump(out,open("tts.json","w"),ensure_ascii=False,indent=1)
    for o in out: print(round(o["dur"],2), round(o["words"][-1]["s"]+o["words"][-1]["d"],2), o["text"])
asyncio.run(main())
