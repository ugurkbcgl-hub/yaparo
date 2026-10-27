"use strict";

// Documented geo-type capabilities, NOT account/content/publishing eligibility.
// No live map, geocoder, device location, platform query or network request.
window.YaparoGeo = (() => {
  const byId = id => document.getElementById(id);
  const LIMITS = Object.freeze({minKm: 1, maxKm: 800, checked: "2026-10-27"});
  const CENTERS = Object.freeze({
    istanbul: {lat: 40.991, lon: 29.025, label: "Kadıköy örnek merkezi"},
    ankara: {lat: 39.9179, lon: 32.8627, label: "Çankaya örnek merkezi"},
    izmir: {lat: 38.4189, lon: 27.1287, label: "Konak örnek merkezi"}
  });
  const currency = n => new Intl.NumberFormat("tr-TR", {
    style: "currency", currency: "TRY", maximumFractionDigits: 0
  }).format(n);

  function read() {
    const mode = byId("geo-mode").value;
    if (mode === "country") return {mode, label: "Türkiye geneli"};
    if (mode === "area") {
      const name = byId("region").value.trim();
      return name.length >= 2 ? {mode, label: name} : null;
    }
    if (mode !== "radius") return null;
    const lat = Number(byId("latitude").value);
    const lon = Number(byId("longitude").value);
    const radius = Number(byId("radius-number").value);
    if (!Number.isFinite(lat) || !Number.isFinite(lon) ||
        lat < 35.5 || lat > 42.5 || lon < 25.5 || lon > 45 ||
        !Number.isInteger(radius) || radius < LIMITS.minKm || radius > LIMITS.maxKm) return null;
    return {
      mode, lat, lon, radiusKm: radius,
      label: `${lat.toFixed(5)}° K, ${lon.toFixed(5)}° D merkezli ${radius} km yarıçap`
    };
  }

  function channelStatus(geo) {
    return [
      {name: "Google Ads", eligible: Boolean(geo), share: geo ? 100 : 0,
        reason: geo ? "Seçilen coğrafi tür belgelerde destekleniyor. Hesap ve kampanya türü onayı bekliyor."
          : "Konum alanları geçersiz veya eksik; pay ayrılmadı."},
      {name: "Meta", eligible: false, share: 0,
        reason: "Seçilen konum hassasiyeti ve güncel hesap/kampanya sınırı doğrulanmadı. Pay ayrılmadı; destek yok demek değildir."},
      {name: "TikTok", eligible: false, share: 0,
        reason: geo?.mode === "radius"
          ? "Kesin yarıçap desteği doğrulanmadı. Entegrasyon/video Faz 2; pay ayrılmadı."
          : "Türkiye konum/hesap uygunluğu doğrulanmadı. Entegrasyon/video Faz 2; pay ayrılmadı."}
    ];
  }

  function draw(geo) {
    const circle = byId("geo-circle"), pin = byId("geo-pin");
    const visible = geo?.mode === "radius";
    circle.style.display = pin.style.display = visible ? "" : "none";
    if (!visible) return;
    const x = (geo.lon - 25.5) * 600 / 19.5;
    const y = (42.5 - geo.lat) * 260 / 7;
    // Local equirectangular approximation. Neither precise geodesy nor borders.
    const rx = geo.radiusKm * 600 / (19.5 * 111.32 * Math.cos(geo.lat * Math.PI / 180));
    const ry = geo.radiusKm * 260 / (7 * 111.32);
    for (const node of [circle, pin]) {
      node.setAttribute("cx", String(x)); node.setAttribute("cy", String(y));
    }
    circle.setAttribute("rx", String(rx)); circle.setAttribute("ry", String(ry));
  }

  function update() {
    const mode = byId("geo-mode").value, radiusMode = mode === "radius";
    byId("geo-area").hidden = mode !== "area";
    byId("geo-radius").hidden = !radiusMode;
    byId("region").disabled = mode !== "area";
    byId("region").required = mode === "area";
    for (const id of ["latitude", "longitude", "radius-number", "radius-range"]) {
      byId(id).disabled = !radiusMode;
      byId(id).required = radiusMode;
    }
    byId("geo-center").disabled = !radiusMode;
    const geo = read();
    const total = Number(byId("budget").value);
    const budgetValid = Number.isInteger(total) && total >= 100 && total <= 1000000;
    const valid = Boolean(geo) && budgetValid;
    byId("geo-status").textContent = geo
      ? `${geo.label} · Hedef alan genişletilmez. Gerçek platform uygunluğu henüz doğrulanmadı.`
      : "Konum geçersiz: bölge adını veya koordinatları ve 1–800 km tam sayı yarıçapı kontrol et. Alan kendiliğinden düzeltilmez.";
    byId("radius-label").textContent = radiusMode && geo ? `${geo.radiusKm} km` : "";
    if (radiusMode && geo) byId("radius-range").value = String(geo.radiusKm);
    const channels = channelStatus(valid ? geo : null);
    const container = byId("geo-channels");
    container.replaceChildren();
    for (const channel of channels) {
      const row = document.createElement("div");
      row.className = `geo-channel ${channel.eligible ? "geo-eligible" : "geo-excluded"}`;
      const heading = document.createElement("strong"); heading.textContent = channel.name;
      const share = document.createElement("span"); share.textContent = `%${channel.share}`;
      const reason = document.createElement("p"); reason.textContent = channel.reason;
      row.append(heading, share, reason); container.append(row);
    }
    byId("google").value = valid ? "100" : "0";
    byId("allocation-reason").textContent = valid
      ? "Önce konum seçimine uymayan veya desteği doğrulanmayan kanalları eledik. Tek belgelenmiş coğrafi aday Google Ads; örnek bütçenin tamamı ona ayrıldı. Bu bir başarı veya getiri tahmini değildir."
      : "Konum veya bütçe geçerli değil. Hiçbir kanala pay ayrılmadı; önce alanları düzelt.";
    byId("allocation-money").textContent = valid
      ? `Google Ads ${currency(total)} · Meta ${currency(0)} · TikTok ${currency(0)}`
      : "Dağıtılmayan bütçe · Geçerli konum ve bütçe bekleniyor";
    byId("geo-total").textContent = valid
      ? "Toplam %100 · Coğrafi aday önerisi, yatırım talimatı değil"
      : "Toplam %0 · Otomatik genişletme veya başka kanala aktarım yok";
    draw(geo);
    return geo;
  }

  byId("geo-mode").addEventListener("change", update);
  for (const id of ["latitude", "longitude"]) {
    byId(id).addEventListener("input", () => {
      byId("geo-center").value = "custom"; update();
    });
  }
  byId("region").addEventListener("input", update);
  byId("radius-number").addEventListener("input", update);
  byId("radius-range").addEventListener("input", () => {
    byId("radius-number").value = byId("radius-range").value; update();
  });
  byId("geo-center").addEventListener("change", () => {
    const center = CENTERS[byId("geo-center").value];
    if (center) {byId("latitude").value = center.lat; byId("longitude").value = center.lon;}
    update();
  });
  byId("geo-map").addEventListener("click", event => {
    if (byId("geo-mode").value !== "radius") return;
    const rect = byId("geo-map").getBoundingClientRect();
    byId("longitude").value = (25.5 + (event.clientX - rect.left) / rect.width * 19.5).toFixed(6);
    byId("latitude").value = (42.5 - (event.clientY - rect.top) / rect.height * 7).toFixed(6);
    byId("geo-center").value = "custom"; update();
    document.dispatchEvent(new Event("yaparo-geography-change"));
  });

  return Object.freeze({update, snapshot() {
    const geo = update();
    if (!geo || byId("google").value !== "100") return null;
    return {...geo, checked: LIMITS.checked, exclusions: channelStatus(geo)
      .filter(channel => !channel.eligible).map(channel => `${channel.name}: ${channel.reason}`).join(" · ")};
  }});
})();
