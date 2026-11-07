const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{
  const mode=process.argv[2]||'preview';
  const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  p.on('console',m=>console.log('PAGE',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto('http://localhost:8766/scene.html');
  await p.waitForFunction('window.READY===true',{timeout:120000});
  if(mode==='preview'){
    const ts=(process.argv[3]||'0,1.8,3.2,6.0,7.5,8.5,10.8,12.05,13.0,14.5,16.2,18.5,19.97').split(',').map(Number);
    for(const t of ts){const s=Date.now();await p.evaluate(t=>window.renderFrame(t),t);await p.screenshot({path:`pv_${t}.jpg`,type:'jpeg',quality:85});console.log(t,Date.now()-s,'ms');}
  } else {
    const fps=30,T=19.2,N=Math.round(fps*T);
    const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','video.mp4'],{stdio:['pipe','inherit','inherit']});
    const st=Date.now();
    for(let i=0;i<N;i++){await p.evaluate(t=>window.renderFrame(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:94});
      if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
      if(i%30===0)console.log('frame',i,((Date.now()-st)/1000).toFixed(0)+'s');}
    ff.stdin.end();await new Promise(r=>ff.on('close',r));
  }
  await b.close();
})();
