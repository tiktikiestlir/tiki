import numpy as np, json, wave
from scipy.signal import butter, sosfilt
SR=48000; TL=json.load(open("timeline.json")); T=TL["T"]; N=int(SR*T)
rng=np.random.default_rng(5)
def hp(x,f): return sosfilt(butter(2,f,'hp',fs=SR,output='sos'),x)
def lp(x,f): return sosfilt(butter(2,f,'lp',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'bp',fs=SR,output='sos'),x)
def add(buf,sig,t,g=1.0):
    i=int(t*SR); 
    if i>=len(buf): return
    sig=sig[:len(buf)-i]; buf[i:i+len(sig)]+=sig*g
def tt(d): return np.arange(int(d*SR))/SR
def midi(n): return 440*2**((n-69)/12)
def marimba(f,d=0.6,v=1.0):
    t=tt(d); e=np.exp(-t*7)
    s=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*4*t)*np.exp(-t*30)+0.15*np.sin(2*np.pi*f*10*t)*np.exp(-t*60)
    a=np.minimum(1,t/0.002); return s*e*a*v
music=np.zeros(N)
bpm=110; beat=60/bpm; eighth=beat/2
chords=[[60,64,67,72],[55,59,62,67],[57,60,64,69],[53,57,60,65]]  # C G Am F
bass=[36,43,45,41]
t=0.0; k=0
while t<T:
    bar=int(t/(4*beat))%4; ch=chords[bar]
    pat=[0,2,1,3,2,1,3,2]
    n=ch[pat[k%8]]+ (12 if (k%16) in (5,13) else 0)
    add(music,marimba(midi(n),0.5,0.32 if k%2 else 0.42),t)
    if k%4==0: add(music,marimba(midi(bass[bar]),0.9,0.55)*1.0,t)
    if k%2==1: add(music,hp(rng.standard_normal(int(0.04*SR)),6000)*np.exp(-tt(0.04)*80)*0.12,t)
    t+=eighth; k+=1
# gaps: card silence-ish + duck under voice
env=np.ones(N)*0.62
c0,c1=TL["card"]
ts=np.arange(N)/SR
env[(ts>=c0)&(ts<TL["mito"])]=0.08
voice=np.zeros(N)
for i,l in enumerate(TL["lines"]):
    w=wave.open(f"line{i}.wav"); x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768.0
    add(voice,x,l["t"])
    s,e=l["t"],l["t"]+l["dur"]
    m=(ts>=s-0.05)&(ts<e); env[m]=np.minimum(env[m],0.30)
env=np.convolve(env,np.ones(2400)/2400,mode='same')
music*=env
sfx=np.zeros(N)
def crack(big=True):
    d=0.9 if big else 0.25; t=tt(d); n=rng.standard_normal(len(t))
    c=hp(n,1500)*np.exp(-t*(25 if big else 45))
    r=lp(n,180)*np.exp(-t*3.5)*(2.5 if big else 0.6)
    return (c*0.6+r*0.5)
for s in TL["strikes"]:
    big=s["kind"]!="rapid"
    add(sfx,crack(big),s["t"],0.55 if big else 0.32)
rapid=[s for s in TL["strikes"] if s["kind"]=="rapid"]
for j,s in enumerate(rapid):  # counter ticks rising
    add(sfx,marimba(midi(72+j%12+ (j//12)*12*0),0.25,0.35),s["t"]+0.01)
def boing(t0):
    t=tt(0.45); f=220+180*np.exp(-t*8)*np.cos(t*40)
    ph=2*np.pi*np.cumsum(f)/SR; add(sfx,np.sin(ph)*np.exp(-t*7)*0.35,t0)
boing(8.5)
for s in rapid[::4]: boing(s["t"]+0.03)
def whoosh(t0,d=0.7,g=0.25):
    t=tt(d); n=rng.standard_normal(len(t)); w=np.sin(np.pi*t/d)**2
    add(sfx,bp(n,400,2500)*w*g,t0-d*0.5)
for w in [2.6,6.4,11.95,17.4]: whoosh(w)
# blink plinks / eye open
add(sfx,marimba(midi(84),0.3,0.3),7.18)
# drumroll during card
t=tt(TL["mito"]-c0); roll=bp(rng.standard_normal(len(t)),150,900)*(0.5+0.5*np.sign(np.sin(2*np.pi*14*t)))*np.minimum(1,t/1.2)*0.45
add(sfx,roll,c0)
# stamp hit
t=tt(0.5); add(sfx,(np.sin(2*np.pi*(60+120*np.exp(-t*30))*t)*np.exp(-t*9)*0.9+hp(rng.standard_normal(len(t)),3000)*np.exp(-t*40)*0.3),TL["mito"])
add(sfx,marimba(midi(72),0.6,0.4)+0,TL["mito"]+0.02); add(sfx,marimba(midi(79),0.6,0.4),TL["mito"]+0.1); add(sfx,marimba(midi(84),0.8,0.45),TL["mito"]+0.18)
# guess card pop
t=tt(0.15); add(sfx,np.sin(2*np.pi*(500+900*t/0.15)*t)*np.exp(-t*20)*0.3,c0)
mix=voice*1.0+music*0.55+sfx*0.8
# soft edges for clean loop
f=int(0.03*SR); mix[:f]*=np.linspace(0,1,f); mix[-f:]*=np.linspace(1,0,f)
peak=np.max(np.abs(mix)); mix=mix/peak*0.89 if peak>0.89 else mix
st=np.stack([mix,mix],1)
w=wave.open("mix.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
print("peak",peak)
