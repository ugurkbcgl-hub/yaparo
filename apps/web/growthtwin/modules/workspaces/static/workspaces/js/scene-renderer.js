"use strict";
(() => {
  const usesPalette = value => value.schema_version === 3 || (value.schema_version === 4 && value.hero_source === "palette");
  function bitmap(scene, kind) {
    const element = document.createElement("canvas");
    element.width = kind === "logo" ? 275 : 580;
    element.height = kind === "logo" ? 58 : 430;
    const ctx = element.getContext("2d");
    const product = scene.fixture === "product";
    if (kind === "logo") {
      ctx.fillStyle = scene.style?.logo_color || "#244c3b"; ctx.beginPath(); ctx.arc(25, 28, 20, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = scene.style?.logo_icon_color || "#e2ecb5"; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(14, 29); ctx.lineTo(25, 17); ctx.lineTo(36, 29); ctx.moveTo(19, 27); ctx.lineTo(19, 37); ctx.lineTo(31, 37); ctx.lineTo(31, 27); ctx.stroke();
      ctx.fillStyle = scene.style?.wordmark_color || "#244c3b"; ctx.font = "bold 19px Arial"; ctx.fillText(product ? "DURU / ÖRNEK" : "ÖZEN / ÖRNEK", 57, 35);
    } else if (product) {
      ctx.fillStyle = "#e4d7bf"; ctx.beginPath(); ctx.ellipse(290, 340, 235, 50, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#b5c39b"; ctx.beginPath(); ctx.arc(290, 190, 171, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#9d593a"; ctx.beginPath(); ctx.roundRect(197, 150, 175, 180, [10, 10, 55, 55]); ctx.fill();
      ctx.strokeStyle = "#9d593a"; ctx.lineWidth = 25; ctx.beginPath(); ctx.ellipse(382, 221, 45, 52, 0, 0, Math.PI * 2); ctx.stroke();
      ctx.fillStyle = "#d39064"; ctx.beginPath(); ctx.ellipse(284, 151, 88, 24, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#75462e"; ctx.beginPath(); ctx.ellipse(284, 152, 72, 15, 0, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#f5ead2"; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(230, 191); ctx.lineTo(230, 280); ctx.stroke();
      ctx.fillStyle = "#244c3b"; ctx.font = "12px Arial"; ctx.fillText("SENTETİK TASARIM · FOTOĞRAF DEĞİLDİR", 160, 412);
    } else {
      ctx.fillStyle = "#d4e2c1"; ctx.beginPath(); ctx.arc(290, 200, 176, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#426951"; ctx.beginPath(); ctx.moveTo(115, 182); ctx.lineTo(287, 65); ctx.lineTo(462, 182); ctx.closePath(); ctx.fill();
      ctx.fillStyle = "#faf1dd"; ctx.fillRect(151, 182, 276, 165); ctx.fillStyle = "#b88053"; ctx.fillRect(260, 236, 60, 111);
      ctx.fillStyle = "#83a18a"; ctx.fillRect(178, 214, 49, 56); ctx.fillRect(350, 214, 49, 56);
      ctx.fillStyle = "#244c3b"; ctx.font = "12px Arial"; ctx.fillText("SENTETİK TASARIM · GERÇEK İŞLETME DEĞİLDİR", 140, 412);
    }
    return element.toDataURL("image/png");
  }
  async function paletteSource(url) {
    return (async () => {
      if (typeof url !== "string" || !/^(?:\/workspace\/brands\/[1-9][0-9]*\/materials\/[0-9a-f-]{36}\/image\/|\/workspace\/campaigns\/[1-9][0-9]*\/design\/[1-9][0-9]*\/image\/)$/.test(url)) throw Error("invalid private source");
      const response = await fetch(url, { credentials: "same-origin", redirect: "error", cache: "no-store", signal: AbortSignal.timeout(10000) });
      if (!response.ok || response.headers.get("Content-Type")?.split(";")[0] !== "image/png" || !response.body) throw Error("private image unavailable");
      const reader = response.body.getReader(); const chunks = []; let total = 0;
      try {
        while (true) {
          const {done,value} = await reader.read(); if (done) break;
          total += value.byteLength; if (total > 8388608) throw Error("image too large");
          chunks.push(value);
        }
      } finally { await reader.cancel(); }
      if (total < 8) throw Error("image missing");
      const blob = new Blob(chunks, {type:"image/png"});
      const signature = new Uint8Array(await blob.slice(0,8).arrayBuffer());
      if (![137,80,78,71,13,10,26,10].every((v,i)=>signature[i]===v)) throw Error("invalid PNG");
      return new Promise((resolve,reject)=>{const file = new FileReader(); file.onload=()=>resolve(file.result); file.onerror=reject; file.readAsDataURL(blob);});
    })();
  }

  async function object(scene, layer, palette) {
    let result;
    if (layer.type === "image") {
      const isPalette = usesPalette(scene) && layer.id === "hero";
      result = await fabric.FabricImage.fromURL(isPalette ? await palette() : bitmap(scene, layer.id === "logo" ? "logo" : "hero"));
      if (isPalette && (result.width !== 320 || result.height !== 200)) throw Error("invalid palette dimensions");
    } else result = new fabric.Textbox(layer.text, {fontFamily:scene.style?.font_family || "Arial",fontSize:layer.id === "title" ? 49 : 21,fontWeight:layer.id === "title" ? "bold" : "normal",width:layer.id === "title" ? 680 : 650,fill:layer.color,editable:false,splitByGrapheme:false});
    result.set({left:layer.x,top:layer.y,scaleX:layer.scale,scaleY:layer.scale,angle:layer.angle,originX:"left",originY:"top"});
    return result;
  }
  function png(canvas, scene) {
    const dimensions = {width:canvas.width,height:canvas.height}; const viewport = canvas.viewportTransform.slice();
    try {
      canvas.setDimensions({width:scene.width,height:scene.height}); canvas.setViewportTransform([1,0,0,1,0,0]);
      return canvas.toDataURL({format:"png",multiplier:1,enableRetinaScaling:false});
    } finally {canvas.setDimensions(dimensions);canvas.setViewportTransform(viewport);canvas.requestRenderAll();}
  }
  window.YaparoSceneRenderer = Object.freeze({object,paletteSource,png});
})();
