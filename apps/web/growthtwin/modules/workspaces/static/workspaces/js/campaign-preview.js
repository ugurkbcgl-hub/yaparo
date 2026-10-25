"use strict";
(() => {
  const boot = JSON.parse(document.getElementById("preview-data").textContent);
  const scene = boot.scene;
  const button = document.getElementById("download");
  const status = document.getElementById("status");
  const shell = document.getElementById("canvas-shell");
  const canvas = new fabric.StaticCanvas("design", {backgroundColor:scene.style?.background_color || "#f5eddf",enableRetinaScaling:false});
  let ready = false; let paletteData;
  const palette = () => paletteData ||= window.YaparoSceneRenderer.paletteSource(boot.palette_url);
  function resize() {
    const pixels = Math.floor(shell.clientWidth);
    if (pixels <= 0) return;
    canvas.setDimensions({width:pixels,height:pixels * scene.height / scene.width});
    canvas.setViewportTransform([pixels / scene.width,0,0,pixels / scene.width,0,0]);
    canvas.requestRenderAll();
  }
  shell.style.aspectRatio = scene.width + "/" + scene.height;
  new ResizeObserver(resize).observe(shell);
  button.addEventListener("click", () => {
    if (!ready) return;
    try {
      const data = window.YaparoSceneRenderer.png(canvas,scene);
      const link = document.createElement("a"); link.href = data;
      link.download = "yaparo-kampanya-secim-" + boot.selection_version + ".png";
      document.body.append(link);link.click();link.remove();
      status.textContent = scene.width + " × " + scene.height + " PNG, kampanyanın seçili kaydından hazırlandı.";
    } catch {status.textContent = "PNG hazırlanamadı. Seçili tasarımı yeniden açın.";}
  });
  (async () => {
    try {
      const objects = await Promise.all(scene.layers.map(layer => window.YaparoSceneRenderer.object(scene,layer,palette)));
      objects.forEach(object => {object.set({selectable:false,evented:false});canvas.add(object);});
      resize();ready = true;button.disabled = false;
      status.textContent = "Seçili tasarım hazır. Bu önizleme düzenlenemez.";
    } catch {status.textContent = "Önizleme hazırlanamadı. Eksik görselle indirme kapalı; kampanyadan seçimi yeniden kontrol edin.";status.classList.add("error");}
  })();
})();
