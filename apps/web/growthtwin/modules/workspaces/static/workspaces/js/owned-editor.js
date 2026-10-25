"use strict";
(() => {
  const boot = JSON.parse(document.getElementById("editor-data").textContent);
  let revision = boot.revision;
  let saving = false;
  const SIZE = 800;
  const names = { hero: "Örnek görsel", logo: "Örnek logo", title: "Başlık", subtitle: "Açıklama" };
  const ids = Object.keys(names);
  const $ = (id) => document.getElementById(id);
  const clamp = (n, low, high) => Math.min(high, Math.max(low, n));
  const copy = (data) => JSON.parse(JSON.stringify(data));
  function seed(fixture) {
    const product = fixture === "product";
    return { schema_version: 1, fixture, width: SIZE, height: SIZE, layers: [
      { id: "hero", type: "image", asset: fixture + ":illustration:v1", x: 115, y: 310, scale: 1, angle: 0 },
      { id: "logo", type: "image", asset: fixture + ":logo:v1", x: 55, y: 40, scale: 1, angle: 0 },
      { id: "title", type: "text", text: product ? "Gününe küçük bir güzellik." : "Evin için özenli bir dokunuş.", color: "#244c3b", x: 55, y: 135, scale: 1, angle: 0 },
      { id: "subtitle", type: "text", text: product ? "Kurgusal seramik koleksiyonu · Ürün örneği" : "Kurgusal ev bakım hizmeti · Ankara örneği", color: "#596b59", x: 58, y: 250, scale: 1, angle: 0 }
    ] };
  }
  const exactKeys = (value, keys) => value && typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === keys.length && keys.every((key) => Object.hasOwn(value, key));
  const finiteIn = (value, low, high) => typeof value === "number" && Number.isFinite(value) && value >= low && value <= high;
  const usesPalette = value => value.schema_version === 3 || (value.schema_version === 4 && value.hero_source === "palette");
  function validate(value, fixture) {
    const styled = value && [2,3,4].includes(value.schema_version);
    const formatted = value && value.schema_version === 4;
    if (formatted && (!["square","portrait"].includes(value.format) || !["illustration","palette"].includes(value.hero_source) || value.format !== boot.scene.format || value.hero_source !== boot.scene.hero_source)) throw Error("invalid format");
    if (styled && (!exactKeys(value.style, ["background_color", "logo_color", "logo_icon_color", "wordmark_color", "font_family"]) || value.style.font_family !== "Arial" || !["background_color", "logo_color", "logo_icon_color", "wordmark_color"].every(key => typeof value.style[key] === "string" && /^#[0-9a-f]{6}$/i.test(value.style[key])))) throw Error("invalid style");
    if (!exactKeys(value, ["schema_version", "fixture", "width", "height", "layers", ...(styled ? ["style"] : []), ...(formatted ? ["format","hero_source"] : [])]) || ![1,2,3,4].includes(value.schema_version) || value.schema_version !== boot.scene.schema_version || value.fixture !== fixture || !["product", "service"].includes(fixture) || value.width !== SIZE || value.height !== (formatted && value.format === "portrait" ? 1000 : SIZE) || !Array.isArray(value.layers) || value.layers.length !== 4) throw Error("invalid scene");
    const expected = seed(fixture).layers;
    value.layers.forEach((layer, index) => {
      const reference = expected[index];
      if (index === 0 && usesPalette(value)) reference.asset = fixture + ":palette:v1";
      const fields = ["id", "type", "x", "y", "scale", "angle", ...(reference.type === "text" ? ["text", "color"] : ["asset"])];
      if (!exactKeys(layer, fields) || layer.id !== reference.id || layer.type !== reference.type || !finiteIn(layer.x, 0, 700) || !finiteIn(layer.y, 0, value.height - 100) || !finiteIn(layer.scale, 0.5, 1.5) || !finiteIn(layer.angle, -45, 45)) throw Error("invalid layer");
      if (layer.type === "image" && layer.asset !== reference.asset) throw Error("unknown asset");
      if (layer.type === "text" && (typeof layer.text !== "string" || layer.text.length > 100 || /[\u0000-\u0009\u000b-\u001f\u007f]/.test(layer.text) || typeof layer.color !== "string" || !/^#[0-9a-f]{6}$/i.test(layer.color))) throw Error("invalid text");
    });
    return copy(value);
  }
  function message(text, error = false) { $("status").textContent = text; $("status").classList.toggle("error", error); }
  function bitmap(fixture, kind) {
    const element = document.createElement("canvas");
    element.width = kind === "logo" ? 275 : 580;
    element.height = kind === "logo" ? 58 : 430;
    const ctx = element.getContext("2d");
    const product = fixture === "product";
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
  let paletteData;
  async function paletteSource() {
    if (!paletteData) paletteData = (async () => {
      if (typeof boot.palette_url !== "string" || !/^\/workspace\/brands\/[1-9][0-9]*\/materials\/[0-9a-f-]{36}\/image\/$/.test(boot.palette_url)) throw Error("invalid private source");
      const response = await fetch(boot.palette_url, { credentials: "same-origin", redirect: "error", cache: "no-store", signal: AbortSignal.timeout(10000) });
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
    return paletteData;
  }
  const canvas = new fabric.Canvas("design", { backgroundColor: "#f5eddf", selection: false, preserveObjectStacking: true });
  let scene; let selected = "title"; let objects = new Map(); let renderVersion = 0; let ready = false; let dirty = false;
  let gestureActive = false;
  let savedScene; let undoSteps = []; let redoSteps = [];
  const sameScene = (a,b) => JSON.stringify(a) === JSON.stringify(b);
  function localButtons() {
    $("undo").disabled = !ready || saving || gestureActive || undoSteps.length === 0;
    $("redo").disabled = !ready || saving || gestureActive || redoSteps.length === 0;
  }
  function remember(before) {
    if (sameScene(before,scene)) return false;
    undoSteps.push(before); if (undoSteps.length > 50) undoSteps.shift(); redoSteps = [];
    dirty = !sameScene(scene,savedScene); localButtons(); return true;
  }
  function localStep(redo) {
    if (!ready || saving || gestureActive) return;
    const source = redo ? redoSteps : undoSteps; const destination = redo ? undoSteps : redoSteps;
    if (!source.length) return;
    const target = validate(source[source.length - 1],scene.fixture);
    destination.push(copy(scene)); source.pop(); scene = target;
    for (const layer of scene.layers) {
      const object = objects.get(layer.id);
      object.set({left:layer.x,top:layer.y,scaleX:layer.scale,scaleY:layer.scale,angle:layer.angle,flipX:false,flipY:false});
      if (layer.type === "text") object.set({text:layer.text,fill:layer.color});
      object.setCoords();
    }
    dirty = !sameScene(scene,savedScene); choose(selected); localButtons();
    message(redo ? "Düzenleme yinelendi. Saklamak için taslağı kaydet." : "Son düzenleme geri alındı. Kayıt geçmişi değişmedi.");
  }
  $("undo").addEventListener("click",()=>localStep(false));
  $("redo").addEventListener("click",()=>localStep(true));
  document.addEventListener("keydown",event=>{
    if (event.defaultPrevented || event.altKey || event.isComposing || !(event.ctrlKey || event.metaKey)) return;
    if (event.target instanceof Element && event.target.closest("input,textarea,select,[contenteditable]")) return;
    const key = event.key.toLowerCase();
    if (key === "z" || (key === "y" && !event.shiftKey)) {
      event.preventDefault(); localStep(key === "y" || event.shiftKey);
    }
  });
  canvas.on("mouse:down",event=>{if (event.target) {gestureActive = true; localButtons();}});
  canvas.on("mouse:up",()=>{gestureActive = false; localButtons();});
  function controls() {
    const layer = scene.layers.find((item) => item.id === selected);
    $("selected-name").textContent = names[selected];
    $("text-fields").hidden = layer.type !== "text";
    if (layer.type === "text") { $("copy").value = layer.text; $("color").value = layer.color; }
    for (const key of ["x", "y", "scale", "angle"]) $(key).value = layer[key];
    $("y").max = scene.height - 100;
    $("scale-value").textContent = Math.round(layer.scale * 100) + "%";
    $("angle-value").textContent = Math.round(layer.angle) + "°";
    for (const button of $("layers").children) button.setAttribute("aria-pressed", String(button.dataset.layer === selected));
  }
  function choose(id) {
    if (!ready || saving) return;
    selected = id; canvas.setActiveObject(objects.get(id)); canvas.requestRenderAll(); controls();
  }
  ids.forEach((id) => { const button = document.createElement("button"); button.type = "button"; button.textContent = names[id]; button.dataset.layer = id; button.addEventListener("click", () => choose(id)); $("layers").append(button); });
  function resize() {
    const pixels = Math.floor($("canvas-shell").clientWidth);
    if (pixels <= 0 || !scene) return;
    canvas.setDimensions({ width: pixels, height: pixels * scene.height / scene.width }); canvas.setViewportTransform([pixels / SIZE, 0, 0, pixels / SIZE, 0, 0]); canvas.requestRenderAll();
  }
  new ResizeObserver(resize).observe($("canvas-shell"));
  async function render(loaded) {
    const version = ++renderVersion; ready = false; $("controls").disabled = true; $("save").disabled = true; $("download").disabled = true;
    gestureActive = false; scene = loaded.scene; $("canvas-shell").style.aspectRatio = scene.width + "/" + scene.height; savedScene = copy(scene); undoSteps = []; redoSteps = []; localButtons(); selected = "title"; dirty = false; canvas.discardActiveObject(); canvas.clear(); canvas.backgroundColor = scene.style?.background_color || "#f5eddf"; objects = new Map();
    try {
      const next = await Promise.all(scene.layers.map(async (layer) => {
        let object;
        if (layer.type === "image") {
          const palette = usesPalette(scene) && layer.id === "hero";
          object = await fabric.FabricImage.fromURL(palette ? await paletteSource() : bitmap(scene.fixture, layer.id === "logo" ? "logo" : "hero"));
          if (palette && (object.width !== 320 || object.height !== 200)) throw Error("invalid palette dimensions");
        }
        else object = new fabric.Textbox(layer.text, { fontFamily: scene.style?.font_family || "Arial", fontSize: layer.id === "title" ? 49 : 21, fontWeight: layer.id === "title" ? "bold" : "normal", width: layer.id === "title" ? 680 : 650, fill: layer.color, editable: false, splitByGrapheme: false });
        object.set({ left: layer.x, top: layer.y, scaleX: layer.scale, scaleY: layer.scale, angle: layer.angle, originX: "left", originY: "top", lockScalingFlip: true, lockSkewingX: true, lockSkewingY: true, borderColor: "#4b7651", cornerColor: "#4b7651", transparentCorners: false, cornerSize: 10 });
        object.setControlsVisibility({ ml: false, mr: false, mt: false, mb: false });
        object.on("selected", () => { selected = layer.id; controls(); });
        const layerId = layer.id;
        object.on("modified", () => {
          const layer = scene.layers.find(item=>item.id === layerId);
          if (!ready || saving) {
            object.set({left:layer.x,top:layer.y,scaleX:layer.scale,scaleY:layer.scale,angle:layer.angle,flipX:false,flipY:false}); object.setCoords(); canvas.requestRenderAll(); return;
          }
          const before = copy(scene);
          layer.x = clamp(Number.isFinite(object.left) ? object.left : layer.x, 0, 700);
          layer.y = clamp(Number.isFinite(object.top) ? object.top : layer.y, 0, scene.height - 100);
          layer.scale = clamp(Number.isFinite(object.scaleX) ? Math.abs(object.scaleX) : layer.scale, 0.5, 1.5);
          layer.angle = clamp(Number.isFinite(object.angle) ? ((object.angle + 180) % 360 + 360) % 360 - 180 : 0, -45, 45);
          object.set({ left: layer.x, top: layer.y, scaleX: layer.scale, scaleY: layer.scale, angle: layer.angle, flipX: false, flipY: false }); object.setCoords(); remember(before); controls(); canvas.requestRenderAll(); message("Düzenleme hazır. Saklamak için taslağı kaydet.");
        });
        return [layer.id, object];
      }));
      if (version !== renderVersion) { next.forEach(([, object]) => object.dispose()); return; }
      objects = new Map(next); next.forEach(([, object]) => canvas.add(object)); ready = true; resize(); $("controls").disabled = false; $("save").disabled = false; $("download").disabled = false; canvas.setActiveObject(objects.get("title")); controls(); localButtons(); message(loaded.message, loaded.error);
    } catch { if (version === renderVersion) message("Önizleme hazırlanamadı. Kayıtlı görsele veya oturuma erişilemiyor olabilir. Eksik görselle kaydetme ve indirme kapalı; sayfayı yeniden açın.", true); }
  }
  function update() {
    if (!ready || saving) return;
    const layer = scene.layers.find((item) => item.id === selected);
    const candidate = copy(scene); const changed = candidate.layers.find((item) => item.id === selected);
    for (const key of ["x", "y", "scale", "angle"]) changed[key] = Number($(key).value);
    if (changed.type === "text") { changed.text = $("copy").value; changed.color = $("color").value; }
    try { validate(candidate, scene.fixture); } catch { message("Alanları gösterilen sınırlar içinde doldurun.", true); return; }
    const before = copy(scene); Object.assign(layer, changed); remember(before);
    const object = objects.get(selected); object.set({ left: layer.x, top: layer.y, scaleX: layer.scale, scaleY: layer.scale, angle: layer.angle });
    if (layer.type === "text") object.set({ text: layer.text, fill: layer.color });
    object.setCoords(); canvas.requestRenderAll(); $("scale-value").textContent = Math.round(layer.scale * 100) + "%"; $("angle-value").textContent = Math.round(layer.angle) + "°"; message("Düzenleme hazır. Saklamak için taslağı kaydet.");
  }
  for (const id of ["copy", "color", "x", "y", "scale", "angle"]) $(id).addEventListener("input", update);
  $("save").addEventListener("click", async () => {
    if (!ready || saving) return;
    saving = true; localButtons(); $("restore").disabled = true; $("controls").disabled = true; $("save").disabled = true;
    canvas.selection = false; objects.forEach(object => object.set({ selectable: false, evented: false }));
    try {
      const submitted = validate(scene,scene.fixture);
      const response = await fetch(boot.save_url, { method: "POST", credentials: "same-origin", redirect: "error",
        headers: { "Content-Type": "application/json", "X-CSRFToken": document.querySelector("#csrf-form input").value },
        body: JSON.stringify({ revision, scene: submitted }) });
      if (!response.ok) throw Error("save denied");
      const result = await response.json();
      if (!Number.isInteger(result.revision) || result.revision < revision) throw Error("bad response");
      revision = result.revision; $("revision").textContent = revision; dirty = false; savedScene = copy(submitted); undoSteps = []; redoSteps = []; updateHistory(result.history);
      message("Çalışma hesabına kaydedildi. Yeniden açtığında bu düzenleme korunur.");
    } catch { message("Kayıt doğrulanamadı. Oturum veya çalışma değişmiş olabilir. Düzenlemen ekranda duruyor; yeniden yüklemeden önce PNG indirebilirsin. Otomatik tekrar yapılmadı.", true); }
    finally { saving = false; localButtons(); $("restore").disabled = !ready || $("history").options.length === 0; $("controls").disabled = !ready; $("save").disabled = !ready; canvas.selection = true; objects.forEach(object => object.set({ selectable: true, evented: true })); }
  });
  function updateHistory(rows) {
    $("history").replaceChildren();
    if (!Array.isArray(rows)) return;
    rows.forEach(row => {
      if (!Number.isInteger(row.revision) || row.revision >= revision) return;
      const option = document.createElement("option"); option.value = row.revision;
      option.textContent = "Kayıt " + row.revision + " · " + row.label; $("history").append(option);
    });
    $("restore").disabled = saving || $("history").options.length === 0;
  }
  $("restore").addEventListener("click", async () => {
    if (!ready || saving || !$("history").value) return;
    if (dirty && !window.confirm("Kaydedilmemiş düzenlemen değişecek. Önceki kayda dönülsün mü?")) return;
    saving = true; localButtons(); $("save").disabled = true; $("restore").disabled = true; $("controls").disabled = true;
    canvas.discardActiveObject(); objects.forEach(object => object.set({ selectable:false, evented:false }));
    try {
      const response = await fetch(boot.restore_url, { method:"POST", credentials:"same-origin", redirect:"error",
        headers:{"Content-Type":"application/json","X-CSRFToken":document.querySelector("#csrf-form input").value},
        body:JSON.stringify({revision, target_revision:Number($("history").value)}) });
      if (!response.ok) throw Error("restore refused");
      const result = await response.json();
      if (!Number.isInteger(result.revision) || result.revision < revision) throw Error("invalid response");
      const restored = validate(result.scene, scene.fixture);
      revision = result.revision; $("revision").textContent = revision;
      await render({scene:restored, message:"Önceki tasarım yeni kayıt olarak açıldı. Sonraki kayıtlar korunuyor."});
      updateHistory(result.history);
    } catch { message("Geri dönüş doğrulanamadı. Düzenlemen korunuyor; güncel kaydı kontrol et. Otomatik tekrar yapılmadı.", true); }
    finally { saving = false; localButtons(); $("save").disabled = !ready; $("controls").disabled = !ready; $("restore").disabled = !ready || $("history").options.length === 0; objects.forEach(object => object.set({ selectable:true, evented:true })); }
  });
  $("download").addEventListener("click", () => {
    if (!ready) return;
    try {
      const dimensions = {width:canvas.width,height:canvas.height}; const viewport = canvas.viewportTransform.slice();
      let data;
      try {
        canvas.setDimensions({width:scene.width,height:scene.height}); canvas.setViewportTransform([1,0,0,1,0,0]);
        data = canvas.toDataURL({format:"png",multiplier:1,enableRetinaScaling:false});
      } finally {canvas.setDimensions(dimensions); canvas.setViewportTransform(viewport); canvas.requestRenderAll();}
      const link = document.createElement("a"); link.href = data; link.download = "yaparo-sentetik-" + scene.fixture + ".png"; document.body.append(link); link.click(); link.remove(); message(scene.width + " × " + scene.height + " PNG hazırlandı. Bu bir sentetik tasarım çıktısıdır.");
    } catch { message("Görsel dışa aktarılamadı. Taslağı kaydedip tekrar deneyin.", true); }
  });
  window.addEventListener("beforeunload", event => { if (dirty || saving) { event.preventDefault(); event.returnValue = ""; } });
  updateHistory(boot.history);
  try { render({ scene: validate(boot.scene, boot.scene.fixture), message: "Kayıtlı çalışma açıldı. Düzenlemeyi saklamak için kaydet." }); }
  catch { message("Kayıtlı tasarım açılamadı; kayıt değiştirilmedi.", true); }
})();
