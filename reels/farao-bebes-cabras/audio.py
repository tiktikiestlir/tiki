import numpy as np, json, wave
from scipy.signal import butter, sosfilt
SR=48000; TL=json.load(open("timeline.json")); T=TL["T"]; N=int(SR*T)
rng=np.random.default_rng(13)
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
def W(li,word): return next(w["t"] for w in TL["lines"][li]["words"] if norm(w["w"])==word)
# music: E phrygian dominant flavour, 110 bpm
music=np.zeros(N); beat=60/110; e8=beat/2
scale=[64,65,68,69,71,72,74,76]  # E F G# A B C D E
riff=[0,1,2,1,0,2,3,2, 4,3,2,1,2,1,0,0]
bass=[40,40,41,40]
t=0.0;k=0
while t<T:
    n=scale[riff[k%16]]
    add(music,marimba(midi(n),0.45,0.34 if k%2 else 0.42),t)
    if k%4==0: add(music,marimba(midi(bass[(k//8)%4]),0.9,0.6),t)
    if k%8==4: add(music,lp(rng.standard_normal(int(0.12*SR)),400)*np.exp(-tt(0.12)*30)*0.5,t)  # frame drum
    if k%2==1: add(music,hp(rng.standard_normal(int(0.04*SR)),6000)*np.exp(-tt(0.04)*80)*0.12,t)
    t+=e8;k+=1
ts=np.arange(N)/SR; env=np.ones(N)*0.62
c0,c1=TL["card"]; A=TL["answer"]; env[(ts>=c0)&(ts<A)]=0.08
voice=np.zeros(N)
for i,l in enumerate(TL["lines"]):
    w=wave.open(f"line{i}.wav"); x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768.0
    add(voice,x,l["t"]); m=(ts>=l["t"]-0.05)&(ts<l["t"]+l["dur"]); env[m]=np.minimum(env[m],0.30)
env=np.convolve(env,np.ones(2400)/2400,mode='same'); music*=env
sfx=np.zeros(N)
def whoosh(t0,d=0.5,g=0.22):
    t=tt(d); add(sfx,bp(rng.standard_normal(len(t)),400,2500)*np.sin(np.pi*t/d)**2*g,t0-d*0.5)
def pop(t0,f=900,g=0.22):
    t=tt(0.12); add(sfx,np.sin(2*np.pi*(f+f*t/0.12)*t)*np.exp(-t*30)*g,t0)
def mee(t0,g=0.35,d=0.6):
    t=tt(d); f=420+30*np.sin(2*np.pi*7*t)*np.minimum(1,t/0.1)
    ph=2*np.pi*np.cumsum(f)/SR; saw=2*((ph/(2*np.pi))%1)-1
    s=bp(saw,600,2600)*np.minimum(1,t/0.03)*np.exp(-t*2.5)*(1+0.6*np.sin(2*np.pi*22*t))
    add(sfx,s*g,t0)
def thud(t0,g=0.6):
    t=tt(0.3); add(sfx,(np.sin(2*np.pi*(70+80*np.exp(-t*25))*t)*np.exp(-t*12)+lp(rng.standard_normal(len(t)),500)*np.exp(-t*20)*0.5)*g,t0)
for c in [1.6,3.1,5.3,7.6,9.2,14.1,17.45]: whoosh(c)
tB=W(0,'bebês');tC=W(0,'cabras');tL=W(1,'primeira');tR=W(2,'Regra');tD=W(3,'Dois');tF=W(3,'falou');tP=W(5,'pão');tFr=W(6,'frígios');tE=W(6,'Egito')
for p in [0.25,tB,tC,tL,tL+0.25,tL+0.5,tR+0.2,6.75,tP+0.7,tFr+0.2,tE]: pop(p)
mee(tC+0.1,0.3); mee(6.7,0.4,0.7); thud(6.75,0.5)
pop(tR,500,0.3); thud(tR+0.05,0.35)       # sign plants into the ground
# time-skip: rising whoosh + clock ticks
t=tt(1.5); add(sfx,bp(rng.standard_normal(len(t)),300,3000)*np.minimum(1,t/1.2)*np.exp(-np.maximum(0,t-1.2)*10)*0.2,tD)
for k in range(10): add(sfx,marimba(midi(88+(k%2)*5),0.08,0.15),tD+k*0.14)
# kid talks: everyone freezes (tiny record scratch) + staff drop clack
t=tt(0.25); add(sfx,bp(rng.standard_normal(len(t)),800,3000)*np.exp(-t*12)*0.25,tF)
thud(tF+0.4,0.3)
# card pop + drumroll
pop(c0,600,0.3); t=tt(A-c0); add(sfx,bp(rng.standard_normal(len(t)),150,900)*(0.5+0.5*np.sign(np.sin(2*np.pi*14*t)))*np.minimum(1,t/1.0)*0.45,c0)
# answer hit + sparkle
t=tt(0.5); add(sfx,np.sin(2*np.pi*(60+120*np.exp(-t*30))*t)*np.exp(-t*9)*0.8,A)
for i,n in enumerate([76,80,83,88]): add(sfx,marimba(midi(n),0.6,0.4),A+0.03+i*0.08)
# bread: falling whistle then boing landing
t=tt(0.45); f=1800-1300*t/0.45; add(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*0.18*np.minimum(1,t/0.05),tP-0.4)
thud(tP+0.05,0.7); t=tt(0.5); fb=200+150*np.exp(-t*8)*np.cos(t*40); add(sfx,np.sin(2*np.pi*np.cumsum(fb)/SR)*np.exp(-t*6)*0.35,tP+0.08)
for k in range(5): add(sfx,lp(rng.standard_normal(int(0.05*SR)),2500)*np.exp(-tt(0.05)*60)*0.3,tP+0.9+k*0.13)  # goat nibbling
# podium fanfare for phrygians, sad trombone for Egypt
for i,n in enumerate([64,68,71,76]): add(sfx,marimba(midi(n),0.5,0.35),tFr-0.1+i*0.07)
for i,n in enumerate([58,57,56,55]):
    d=0.55 if i==3 else 0.3; t=tt(d); f=midi(n)*(1+0.012*np.sin(2*np.pi*6*t)*(i==3))
    ph=2*np.pi*np.cumsum(f)/SR; saw=2*((ph/(2*np.pi))%1)-1
    add(sfx,lp(saw,1400)*np.minimum(1,t/0.03)*np.exp(-t*(1.5 if i==3 else 3))*0.28,tE+0.25+i*0.3)
# CTA: goat bleat
mee(18.95,0.3,0.5)
mix=voice+music*0.55+sfx*0.8
f=int(0.03*SR); mix[:f]*=np.linspace(0,1,f); mix[-f:]*=np.linspace(1,0,f)
p=np.max(np.abs(mix)); mix=mix/p*0.89 if p>0.89 else mix
w=wave.open("mix.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix,mix],1)*32767).astype(np.int16).tobytes()); w.close()
