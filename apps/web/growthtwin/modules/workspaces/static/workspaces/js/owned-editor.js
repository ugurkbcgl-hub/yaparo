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
  function validate(value, fixture) {
    if (!exactKeys(value, ["schema_version", "fixture", "width", "height", "layers"]) || value.schema_version !== 1 || value.fixture !== fixture || !["product", "service"].includes(fixture) || value.width !== SIZE || value.height !== SIZE || !Array.isArray(value.layers) || value.layers.length !== 4) throw Error("invalid scene");
    const expected = seed(fixture).layers;
    value.layers.forEach((layer, index) => {
      const reference = expected[index];
      const fields = ["id", "type", "x", "y", "scale", "angle", ...(reference.type === "text" ? ["text", "color"] : ["asset"])];
      if (!exactKeys(layer, fields) || layer.id !== reference.id || layer.type !== reference.type || !finiteIn(layer.x, 0, 700) || !finiteIn(layer.y, 0, 700) || !finiteIn(layer.scale, 0.5, 1.5) || !finiteIn(layer.angle, -45, 45)) throw Error("invalid layer");
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
      ctx.fillStyle = "#244c3b"; ctx.beginPath(); ctx.arc(25, 28, 20, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#e2ecb5"; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(14, 29); ctx.lineTo(25, 17); ctx.lineTo(36, 29); ctx.moveTo(19, 27); ctx.lineTo(19, 37); ctx.lineTo(31, 37); ctx.lineTo(31, 27); ctx.stroke();
      ctx.font = "bold 19px Arial"; ctx.fillText(product ? "DURU / ÖRNEK" : "ÖZEN / ÖRNEK", 57, 35);
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
  const canvas = new fabric.Canvas("design", { backgroundColor: "#f5eddf", selection: false, preserveObjectStacking: true });
  let scene; let selected = "title"; let objects = new Map(); let renderVersion = 0; let ready = false; let dirty = false;
  function controls() {
    const layer = scene.layers.find((item) => item.id === selected);
    $("selected-name").textContent = names[selected];
    $("text-fields").hidden = layer.type !== "text";
    if (layer.type === "text") { $("copy").value = layer.text; $("color").value = layer.color; }
    for (const key of ["x", "y", "scale", "angle"]) $(key).value = layer[key];
    $("scale-value").textContent = Math.round(layer.scale * 100) + "%";
    $("angle-value").textContent = Math.round(layer.angle) + "°";
    for (const button of $("layers").children) button.setAttribute("aria-pressed", String(button.dataset.layer === selected));
  }
  function choose(id) {
    if (!ready) return;
    selected = id; canvas.setActiveObject(objects.get(id)); canvas.requestRenderAll(); controls();
  }
  ids.forEach((id) => { const button = document.createElement("button"); button.type = "button"; button.textContent = names[id]; button.dataset.layer = id; button.addEventListener("click", () => choose(id)); $("layers").append(button); });
  function resize() {
    const pixels = Math.floor($("canvas-shell").clientWidth);
    if (pixels <= 0) return;
    canvas.setDimensions({ width: pixels, height: pixels }); canvas.setViewportTransform([pixels / SIZE, 0, 0, pixels / SIZE, 0, 0]); canvas.requestRenderAll();
  }
  new ResizeObserver(resize).observe($("canvas-shell"));
  async function render(loaded) {
    const version = ++renderVersion; ready = false; $("controls").disabled = true; $("save").disabled = true; $("download").disabled = true;
    scene = loaded.scene; selected = "title"; dirty = false; canvas.discardActiveObject(); canvas.clear(); canvas.backgroundColor = "#f5eddf"; objects = new Map();
    try {
      const next = await Promise.all(scene.layers.map(async (layer) => {
        let object;
        if (layer.type === "image") object = await fabric.FabricImage.fromURL(bitmap(scene.fixture, layer.id === "logo" ? "logo" : "hero"));
        else object = new fabric.Textbox(layer.text, { fontFamily: "Arial", fontSize: layer.id === "title" ? 49 : 21, fontWeight: layer.id === "title" ? "bold" : "normal", width: layer.id === "title" ? 680 : 650, fill: layer.color, editable: false, splitByGrapheme: false });
        object.set({ left: layer.x, top: layer.y, scaleX: layer.scale, scaleY: layer.scale, angle: layer.angle, originX: "left", originY: "top", lockScalingFlip: true, lockSkewingX: true, lockSkewingY: true, borderColor: "#4b7651", cornerColor: "#4b7651", transparentCorners: false, cornerSize: 10 });
        object.setControlsVisibility({ ml: false, mr: false, mt: false, mb: false });
        object.on("selected", () => { selected = layer.id; controls(); });
        object.on("modified", () => {
          layer.x = clamp(Number.isFinite(object.left) ? object.left : layer.x, 0, 700);
          layer.y = clamp(Number.isFinite(object.top) ? object.top : layer.y, 0, 700);
          layer.scale = clamp(Number.isFinite(object.scaleX) ? Math.abs(object.scaleX) : layer.scale, 0.5, 1.5);
          layer.angle = clamp(Number.isFinite(object.angle) ? ((object.angle + 180) % 360 + 360) % 360 - 180 : 0, -45, 45);
          object.set({ left: layer.x, top: layer.y, scaleX: layer.scale, scaleY: layer.scale, angle: layer.angle, flipX: false, flipY: false }); object.setCoords(); dirty = true; controls(); canvas.requestRenderAll(); message("Düzenleme hazır. Saklamak için taslağı kaydet.");
        });
        return [layer.id, object];
      }));
      if (version !== renderVersion) { next.forEach(([, object]) => object.dispose()); return; }
      objects = new Map(next); next.forEach(([, object]) => canvas.add(object)); ready = true; resize(); $("controls").disabled = false; $("save").disabled = false; $("download").disabled = false; choose("title"); message(loaded.message, loaded.error);
    } catch { if (version === renderVersion) message("Önizleme hazırlanamadı. Sayfayı yeniden açmayı deneyin.", true); }
  }
  function update() {
    if (!ready) return;
    const layer = scene.layers.find((item) => item.id === selected);
    const candidate = copy(scene); const changed = candidate.layers.find((item) => item.id === selected);
    for (const key of ["x", "y", "scale", "angle"]) changed[key] = Number($(key).value);
    if (changed.type === "text") { changed.text = $("copy").value; changed.color = $("color").value; }
    try { validate(candidate, scene.fixture); } catch { message("Alanları gösterilen sınırlar içinde doldurun.", true); return; }
    Object.assign(layer, changed); dirty = true;
    const object = objects.get(selected); object.set({ left: layer.x, top: layer.y, scaleX: layer.scale, scaleY: layer.scale, angle: layer.angle });
    if (layer.type === "text") object.set({ text: layer.text, fill: layer.color });
    object.setCoords(); canvas.requestRenderAll(); $("scale-value").textContent = Math.round(layer.scale * 100) + "%"; $("angle-value").textContent = Math.round(layer.angle) + "°"; message("Düzenleme hazır. Saklamak için taslağı kaydet.");
  }
  for (const id of ["copy", "color", "x", "y", "scale", "angle"]) $(id).addEventListener("input", update);
  $("save").addEventListener("click", async () => {
    if (!ready || saving) return;
    saving = true; $("controls").disabled = true; $("save").disabled = true;
    canvas.selection = false; objects.forEach(object => object.set({ selectable: false, evented: false }));
    try {
      const response = await fetch(boot.save_url, { method: "POST", credentials: "same-origin", redirect: "error",
        headers: { "Content-Type": "application/json", "X-CSRFToken": document.querySelector("#csrf-form input").value },
        body: JSON.stringify({ revision, scene: validate(scene, scene.fixture) }) });
      if (!response.ok) throw Error("save denied");
      const result = await response.json();
      if (!Number.isInteger(result.revision) || result.revision < revision) throw Error("bad response");
      revision = result.revision; $("revision").textContent = revision; dirty = false;
      message("Çalışma hesabına kaydedildi. Yeniden açtığında bu düzenleme korunur.");
    } catch { message("Kayıt doğrulanamadı. Oturum veya çalışma değişmiş olabilir. Düzenlemen ekranda duruyor; yeniden yüklemeden önce PNG indirebilirsin. Otomatik tekrar yapılmadı.", true); }
    finally { saving = false; $("controls").disabled = false; $("save").disabled = false; canvas.selection = true; objects.forEach(object => object.set({ selectable: true, evented: true })); }
  });
  $("download").addEventListener("click", () => {
    if (!ready) return;
    try {
      const link = document.createElement("a"); link.href = canvas.toDataURL({ format: "png", multiplier: SIZE / canvas.width, enableRetinaScaling: false }); link.download = "yaparo-sentetik-" + scene.fixture + ".png"; document.body.append(link); link.click(); link.remove(); message("800 × 800 PNG hazırlandı. Bu bir sentetik tasarım çıktısıdır.");
    } catch { message("Görsel dışa aktarılamadı. Taslağı kaydedip tekrar deneyin.", true); }
  });
  window.addEventListener("beforeunload", event => { if (dirty || saving) { event.preventDefault(); event.returnValue = ""; } });
  try { render({ scene: validate(boot.scene, boot.scene.fixture), message: "Kayıtlı çalışma açıldı. Düzenlemeyi saklamak için kaydet." }); }
  catch { message("Kayıtlı tasarım açılamadı; kayıt değiştirilmedi.", true); }
})();
