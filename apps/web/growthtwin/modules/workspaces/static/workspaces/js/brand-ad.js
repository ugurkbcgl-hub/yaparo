"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const boot = JSON.parse($("hosted-ad-boot").textContent);
  const form = $("ad-form"), canvas = $("ad-canvas"), ctx = canvas.getContext("2d");
  const fields = ["title", "body", "cta", "color"], limits = {title:60,body:100,cta:30};
  let photo, ready = false;
  const values = () => Object.fromEntries(fields.map(key => [key, form.elements[key].value]));
  function status(text, error=false) { $("ad-status").textContent = text; $("ad-status").classList.toggle("error", error); }
  function validate(value) {
    for (const key of Object.keys(limits)) {
      const text = value[key];
      if (!text.trim() || text.length > limits[key] || !text.isWellFormed() || /[\u0000-\u001f\u007f\u2028\u2029]/u.test(text)) throw Error("text");
    }
    if (!/^#[0-9a-f]{6}$/i.test(value.color)) throw Error("color");
  }
  function lines(text, width) {
    const result = []; let current = "";
    for (const word of text.trim().split(/ +/u)) {
      if (current && ctx.measureText(current+" "+word).width <= width) { current+=" "+word; continue; }
      if (current) { result.push(current); current=""; }
      for (const character of Array.from(word)) {
        if (current && ctx.measureText(current+character).width > width) { result.push(current); current=""; }
        if (ctx.measureText(character).width > width) throw Error("glyph");
        current+=character;
      }
    }
    if (current) result.push(current);
    return result;
  }
  function layout(value) {
    const width = 768 - 120;
    ctx.font = "bold 44px Arial"; const title = lines(value.title,width);
    ctx.font = "24px Arial"; const body = lines(value.body,width);
    ctx.font = "bold 24px Arial"; const cta = lines(value.cta,width-40);
    ctx.font = "bold 22px Arial"; const brand = lines(boot.brand_name,width);
    const start = 50 + brand.length*28 + 28;
    const end = start + title.length*52 + 18 + body.length*32 + 24 + cta.length*30 + 32;
    if (end > canvas.height / (canvas.width/768) * 0.52) throw Error("overflow");
    return {brand,start,title,body,cta,end};
  }
  function render() {
    $("ad-save").disabled = true; $("ad-export").disabled = true;
    if (!ready) return;
    try {
      const value = values(); validate(value); const boxes = layout(value);
      ctx.setTransform(1,0,0,1,0,0);
      ctx.clearRect(0,0,canvas.width,canvas.height);
      ctx.scale(canvas.width/768,canvas.width/768);
      const height = canvas.height/(canvas.width/768);
      const panel = boxes.end+26;
      if (boot.mode === "overlay") {
        ctx.drawImage(photo,0,0,768,height);
      } else {
        ctx.fillStyle = "#f5eddf"; ctx.fillRect(0,0,768,height);
        const ratio = Math.min(768/photo.width,(height-panel)/photo.height);
        const w = photo.width*ratio, h = photo.height*ratio;
        ctx.drawImage(photo,(768-w)/2,panel+(height-panel-h)/2,w,h);
      }
      ctx.fillStyle = "#f5eddf"; ctx.fillRect(0,0,768,panel);
      ctx.fillStyle = value.color; ctx.textBaseline = "top";
      ctx.font = "bold 22px Arial"; let brandY = 50;
      for (const line of boxes.brand) { ctx.fillText(line,60,brandY); brandY+=28; }
      ctx.fillStyle = boot.secondary_color; ctx.fillRect(60,brandY+6,648,4);
      ctx.fillStyle = value.color;
      let y = boxes.start; ctx.font = "bold 44px Arial";
      for (const line of boxes.title) { ctx.fillText(line,60,y); y+=52; }
      y+=18; ctx.font = "24px Arial";
      for (const line of boxes.body) { ctx.fillText(line,60,y); y+=32; }
      y+=24; ctx.fillStyle = value.color;
      ctx.fillRect(60,y,768-120,boxes.cta.length*30+32);
      const rgb = [1,3,5].map(i=>parseInt(value.color.slice(i,i+2),16)/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4);
      ctx.fillStyle = rgb[0]*0.2126+rgb[1]*0.7152+rgb[2]*0.0722 > 0.179 ? "#000000" : "#ffffff"; ctx.font = "bold 24px Arial";
      for (const line of boxes.cta) { ctx.fillText(line,80,y+16); y+=30; }
      const saved = fields.every(key => value[key] === boot.content[key]);
      $("ad-save").disabled = !!boot.read_only;
      $("ad-export").disabled = !saved || !boot.can_export;
      status(saved && boot.can_export ? "Kayıtlı taslak hazır. PNG indirebilirsin." : "Düzenleme ekranda. PNG indirmek için önce kaydet.");
    } catch {
      ctx.setTransform(1,0,0,1,0,0);
      ctx.clearRect(0,0,canvas.width,canvas.height);
      status("Metinler sınırı aşıyor veya bu düzene sığmıyor. Kısaltılmadı; alanları düzenle.",true);
    }
  }
  for (const key of fields) form.elements[key].addEventListener("input",render);
  form.addEventListener("submit",event => { if (boot.read_only || !ready || $("ad-save").disabled) event.preventDefault(); });
  $("ad-export").addEventListener("click",() => {
    if (!ready || $("ad-export").disabled) return;
    const link = document.createElement("a");
    link.download = "yaparo-brand-ad-"+boot.id+"-v"+boot.revision+".png";
    link.href = canvas.toDataURL("image/png"); link.click();
  });
  (async () => {
    try {
      const expected = "/workspace/brands/"+boot.brand_id+"/ads/"+boot.id+"/image/";
      if (boot.image_url !== expected || typeof boot.brand_name !== "string" || !boot.brand_name.trim() || boot.brand_name.length>240 || !boot.brand_name.isWellFormed() || !/^#[0-9a-f]{6}$/i.test(boot.secondary_color)) throw Error("url");
      const response = await fetch(boot.image_url,{credentials:"same-origin",redirect:"error",cache:"no-store",signal:AbortSignal.timeout(10000)});
      if (!response.ok || response.headers.get("Content-Type")?.split(";")[0] !== "image/png" || !response.body) throw Error("response");
      const reader = response.body.getReader(), chunks = []; let size = 0;
      try {
        while (true) { const {done,value} = await reader.read(); if (done) break; size+=value.byteLength; if (size>8388608) throw Error("size"); chunks.push(value); }
      } finally { await reader.cancel(); }
      const blob = new Blob(chunks,{type:"image/png"}), bytes = new Uint8Array(await blob.arrayBuffer());
      if (bytes.length < 24 || [137,80,78,71,13,10,26,10].some((v,i)=>bytes[i]!==v)) throw Error("png");
      const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))).map(v=>v.toString(16).padStart(2,"0")).join("");
      if (hash !== boot.sha256) throw Error("hash");
      photo = await createImageBitmap(blob);
      if (photo.width !== boot.source_width || photo.height !== boot.source_height || canvas.width !== boot.width || canvas.height !== boot.height || !["overlay","contain"].includes(boot.mode)) throw Error("dimensions");
      ready = true; render();
    } catch { status("Kaydedilmiş görsel doğrulanamadı. Kaydetme ve indirme kapalı; sayfayı yeniden aç.",true); }
  })();
})();
