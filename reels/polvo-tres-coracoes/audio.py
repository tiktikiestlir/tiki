import numpy as np, json, wave
from scipy.signal import butter, sosfilt
SR=48000; TL=json.load(open("timeline.json")); T=TL["T"]; N=int(SR*T)
rng=np.random.default_rng(9)
def hp(x,f): return sosfilt(butter(2,f,'hp',fs=SR,output='sos'),x)
def lp(x,f): return sosfilt(butter(2,f,'lp',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'bp',fs=SR,output='sos'),x)
def tt(d): return np.arange(int(d*SR))/SR
def add(buf,sig,t,g=1.0):
    i=int(t*SR)
    if i<0: sig=sig[-i:]; i=0
    if i>=len(buf): return
    sig=sig[:len(buf)-i]; buf[i:i+len(sig)]+=sig*g
def midi(n): return 440*2**((n-69)/12)
def marimba(f,d=0.6,v=1.0):
    t=tt(d); e=np.exp(-t*7)
    s=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*4*t)*np.exp(-t*30)+0.15*np.sin(2*np.pi*f*10*t)*np.exp(-t*60)
    return s*e*np.minimum(1,t/0.002)*v
norm=lambda w:''.join(c for c in w if c.isalnum())
def wt(li,word): return next(w["t"] for w in TL["lines"][li]["words"] if norm(w["w"])==word)
music=np.zeros(N); beat=60/110; eighth=beat/2
chords=[[57,60,64,69],[53,57,60,65],[48,52,55,60],[55,59,62,67]]  # Am F C G
bass=[45,41,36,43]
t=0.0;k=0
while t<T:
    bar=int(t/(4*beat))%4; ch=chords[bar]; pat=[0,2,1,3,2,1,3,2]
    add(music,marimba(midi(ch[pat[k%8]]+(12 if k%16 in(5,13) else 0)),0.5,0.32 if k%2 else 0.42),t)
    if k%4==0: add(music,marimba(midi(bass[bar]),0.9,0.55),t)
    if k%2==1: add(music,hp(rng.standard_normal(int(0.04*SR)),6000)*np.exp(-tt(0.04)*80)*0.12,t)
    t+=eighth;k+=1
ts=np.arange(N)/SR; env=np.ones(N)*0.62
c0,c1=TL["card"]; env[(ts>=c0)&(ts<TL["answer"])]=0.08
voice=np.zeros(N)
for i,l in enumerate(TL["lines"]):
    w=wave.open(f"line{i}.wav"); x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768.0
    add(voice,x,l["t"]); m=(ts>=l["t"]-0.05)&(ts<l["t"]+l["dur"]); env[m]=np.minimum(env[m],0.30)
env=np.convolve(env,np.ones(2400)/2400,mode='same'); music*=env
sfx=np.zeros(N)
def whoosh(t0,d=0.6,g=0.25):
    t=tt(d); add(sfx,bp(rng.standard_normal(len(t)),400,2500)*np.sin(np.pi*t/d)**2*g,t0-d*0.5)
def squish(t0,g=0.4):
    t=tt(0.35); f=180+260*np.exp(-t*9); ph=2*np.pi*np.cumsum(f)/SR
    add(sfx,(np.sin(ph)*0.6+lp(rng.standard_normal(len(t)),900)*0.5)*np.exp(-t*9)*g,t0)
def thump(t0,g=0.5):
    for dt,a in ((0,1),(0.16,0.7)):
        t=tt(0.18); add(sfx,np.sin(2*np.pi*(55+40*np.exp(-t*30))*t)*np.exp(-t*22)*a*g,t0+dt)
for w in [6.6,8.6,11.5,17.6]: whoosh(w)
# wire slice: rising filtered noise zip
t=tt(0.5); add(sfx,bp(rng.standard_normal(len(t)),2500,7000)*np.sin(np.pi*t/0.5)*0.3,TL["cut"])
squish(TL["open"],0.5); squish(TL["close"],0.45)
# jet swim
t=tt(0.7); add(sfx,lp(rng.standard_normal(len(t)),1200)*np.sin(np.pi*t/0.7)**2*0.5,TL["close"]+0.6)
# card pop + drumroll
t=tt(0.15); add(sfx,np.sin(2*np.pi*(500+900*t/0.15)*t)*np.exp(-t*20)*0.3,c0)
t=tt(TL["answer"]-c0); add(sfx,bp(rng.standard_normal(len(t)),150,900)*(0.5+0.5*np.sign(np.sin(2*np.pi*14*t)))*np.minimum(1,t/1.0)*0.45,c0)
# answer hit + three heart pops
A=TL["answer"]; t=tt(0.5)
add(sfx,np.sin(2*np.pi*(60+120*np.exp(-t*30))*t)*np.exp(-t*9)*0.8,A)
for i,n in enumerate([72,76,79]): add(sfx,marimba(midi(n),0.7,0.5),A+0.02+i*0.18)
# heartbeats until 'nada', then only small (branchial) beats
nada=wt(7,'nada'); tb=A+0.6
while tb<TL["close"]:
    thump(tb,0.45 if tb<nada else 0.2); tb+=1/1.6
# bubble plinks
for bt in [1.0,4.2,9.0,13.0,16.2,18.8]: add(sfx,marimba(midi(96),0.15,0.12),bt)
mix=voice+music*0.55+sfx*0.8
f=int(0.03*SR); mix[:f]*=np.linspace(0,1,f); mix[-f:]*=np.linspace(1,0,f)
p=np.max(np.abs(mix)); mix=mix/p*0.89 if p>0.89 else mix
w=wave.open("mix.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix,mix],1)*32767).astype(np.int16).tobytes()); w.close()
