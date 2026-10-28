/* Owned brief → existing authored plan demo. No inferred business/account evidence. */
(function () {
  'use strict';
  if (location.pathname === '/legacy.html') return;
  const $ = id => document.getElementById(id);
  const M = window.YaparoFirstStage, studio = window.YaparoStudio;
  const D = window.YaparoResearch, B = window.YaparoBriefFlow;
  const intentMap = {promote:'product_service_intro',sell:'sale_promotion',event:'event',lead:'lead_request',hire:'recruitment',fundraise:'fundraising',announce:'announcement',community:'membership',reputation:'reputation'};
  let ui, previousPair = '', pendingMode = '', examplePair = '', exampleNotice;
  const read = () => ui?.getSnapshot() || {version:'yaparo-first-stage-v1',intent:'',outcome:'',answers:{}};
  function node(tag, text) {const n = document.createElement(tag); if (text !== undefined) n.textContent = text; return n;}
  function options(select, rows, value = '') {
    select.replaceChildren(); const empty = node('option','Seç'); empty.value = ''; select.append(empty);
    for (const row of rows) {const o = node('option',row.label); o.value = row.value; select.append(o);}
    select.value = rows.some(r => r.value === value) ? value : '';
  }
  function sourceAction(s) {return window.YaparoOutcomeContract.resolve(s).legacyProjection?.action || '';}
  function usage() {return read().answers.delivery_mode || '';}
  function mode() {return ({paid:'paid',organic:'organic',hybrid:'both',content_only:'organic'})[usage()] || 'paid';}
  function sourceGoal(s) {return window.YaparoOutcomeContract.resolve(s).legacyProjection?.goal || '';}
  function declaredRisk() {const s = read(); return s.intent === 'fundraise' ? 'fundraising' : s.answers.risk || 'normal';}
  function syncSource() {
    const s = read(); options($('communication'),D.options.filter(o => o.questionId === 'S1_Q01'),intentMap[s.intent] || '');
    options($('action'),D.options.filter(o => o.questionId === 'S1_Q04'),sourceAction(s)); $('journey-mode').value = mode(); $('risk').value = declaredRisk();
    const expected = sourceGoal(s); if (expected) $('goal').value = expected;
  }
  function classification() {
    const s = read(), comm = intentMap[s.intent], action = sourceAction(s);
    const current = $('business').value, sector = $('sector').value;
    const allowed = new Set(B.businesses(comm,D,action).map(o => o.value));
    options($('business'),D.options.filter(o => o.questionId === 'S3_Q02' && allowed.has(o.value)),current);
    const sectors = B.sectors(comm,$('business').value,D,action);
    options($('sector'),sectors,sector);
    $('business').required = false; $('sector').required = false;
  }
  function roleValue(role) {
    const s = read(), field = M.fields(s.intent,s.outcome,s.answers).find(f => f.role === role && s.answers[f.id] !== undefined);
    if (!field) return '';
    const value = s.answers[field.id];
    return field.options?.find(o => o.value === value)?.label || (Array.isArray(value) ? value.join(', ') : String(value));
  }
  function brief() {
    const s = read(), answers = M.prune(s.intent,s.outcome,s.answers), summary = M.summary(s.intent,s.outcome,answers);
    const subject = roleValue('subject'), message = roleValue('message');
    const labels = summary.map(row => `${row.label}: ${row.value}`).join(' · ');
    return {mode:mode(),communication:intentMap[s.intent] || '',business:$('business').value,sector:$('sector').value,action:sourceAction(s),risk:declaredRisk(),
      description:[subject,message].filter(Boolean).join('. ') || labels,audience:roleValue('audience'),identity:roleValue('identity'),message,
      branch:{},custom:{},destination:null,brief_policy:'yaparo-first-stage-v1',
      firstStage:{version:'yaparo-first-stage-v1',intent:s.intent,outcome:s.outcome,answers},
      planContext:{version:'owned-plan-context-v1',business:$('business').value,sector:$('sector').value,source:'explicit_user_selection',verified:false},
      outcomeContract:contract(),firstStageSummary:summary};
  }
  function contract() {return window.YaparoOutcomeContract.resolve(read());}
  function cards(revision) {return window.YaparoOutcomeContract.buildConcepts(read(),{revision});}
  function alternative(card) {
    const current=contract(); if(!current.valid || card.outcomeSignature!==current.binding.signature)return {};
    const next = cards(card.revision+1)[card.kind]; if(!next)return {};
    return {title:next.title,message:next.message,cta:next.cta,theme:next.theme};
  }
  function validate() {const s = read(), result = M.validate(s.intent,s.outcome,s.answers); if (!result.valid) ui.showErrors(result.errors); return result.valid;}
  function planIssue() {
    if (!validate()) return 'İlk aşamadaki bilgileri tamamlayıp yeniden devam et.';
    if (usage() === 'unsure') return 'Önce bu çalışmayı reklamda mı, kendi hesabında mı kullanacağını seç.';
    if (!sourceAction(read()) || !sourceGoal(read())) return 'Seçtiğin sonuç kaydedildi. Bu sonucun kanal ve ölçüm eşleştirmesi henüz bağlı değil; bütçe önerilmeyecek.';
    if (!$('business').value || !$('sector').value) return 'Plan için çalışma biçimini ve ilgili alanı seç. İlk aşamadaki yanıtlarından bunları varsaymıyoruz.';
    if ($('sector').value === 'other') return 'Bu faaliyet alanının kanal eşleştirmesi henüz netleşmedi; bütçe önerilmeyecek.';
    return '';
  }
  function nextIssue() {
    if (!validate()) return 'İlk aşamadaki bilgileri tamamla.';
    if (usage() === 'unsure') return 'Devam etmeden önce kullanım yolunu seç.';
    if (!contract().valid) return 'Bu isteğin içerik eşleştirmesi doğrulanamadı.';
    if (['paid','hybrid'].includes(usage()) && (!sourceAction(read()) || !sourceGoal(read()))) return 'Seçtiğin sonuç korundu; ücretli kanal eşleştirmesi doğrulanmadan bütçe ile devam edilemez. Yalnız içerik veya kendi hesaplarında paylaşım yolunu ilk aşamadan seçebilirsin.';
    if (usage() === 'content_only' && !formats().length) return 'En az bir içerik biçimi seç.';
    return '';
  }
  function formats() {return [...formatBox.querySelectorAll('input:checked')].map(n=>n.value);}
  function productionOptions() {return {outcomeSignature:contract().binding.signature,contentOnly:usage()==='content_only',formats:formats()};}
  // Existing source classifiers move to the paid planning stage. Never prefill them.
  const context = node('section'); context.id = 'owned-plan-context'; context.className = 'production-requirements';
  context.append(node('h2','Plan için çalışma bağlamı'),node('p','Yalnız plan örneğini değerlendirmek için seç. Bu seçimler hesap veya belge doğrulaması değildir.'));
  const contextFields = node('div'); contextFields.className = 'field-pair';
  for (const id of ['business','sector']) {
    const control = $(id), box = control.parentElement;
    box.querySelector('label').textContent = id === 'business' ? 'Çalışma hangi biçimde sunuluyor?' : 'İlgili faaliyet alanı';
    for (const extra of box.querySelectorAll('.brief-custom')) extra.hidden = true;
    control.value = ''; contextFields.append(box);
  }
  context.append(contextFields); $('plan-controls').prepend(context);
  const modeBox = node('section'); modeBox.className = 'production-requirements'; modeBox.id = 'owned-mode-choice';
  const modeLabel = node('label','Bu çalışmayı nasıl kullanmak istiyorsun?'); modeLabel.htmlFor = 'owned-mode';
  const modeSelect = node('select'); modeSelect.id = 'owned-mode';
  options(modeSelect,[{value:'paid',label:'Ücretli reklam'},{value:'organic',label:'Kendi hesaplarımda paylaşım'},{value:'hybrid',label:'İkisi birlikte'},{value:'content_only',label:'Yalnız içerik hazırlama'}]);
  modeBox.append(modeLabel,modeSelect); $('plan-form').prepend(modeBox);
  const formatBox = node('section'); formatBox.className = 'production-requirements'; formatBox.id = 'owned-content-formats';
  formatBox.append(node('h2','Hangi içerik biçimini hazırlayalım?'),node('p','Kanal seçmeden yerel taslak hazırla. Görsel, hazırlanmış bir yerleşim örneğidir; AI üretimi değildir.'));
  for(const [value,label] of [['text','Metin'],['image','Görsel yerleşimi']]) {
    const row=node('label',label), control=node('input'); control.type='checkbox'; control.name='owned-format'; control.value=value; control.checked=true; row.className='check-label'; row.prepend(control); formatBox.append(row);
  }
  $('plan-form').prepend(formatBox);
  const outcomeNote = node('section'); outcomeNote.className='production-requirements'; outcomeNote.id='owned-outcome-summary'; $('plan-form').prepend(outcomeNote);
  const notice = node('p'); notice.id = 'owned-plan-note'; notice.className = 'inline-notice'; $('plan-form').prepend(notice);
  function configure() {
    const c=contract(); outcomeNote.replaceChildren(); if(c.valid){outcomeNote.append(node('h2',c.outcomeLabel),node('p','Başarı göstergesi: '+c.kpi.label+' · Henüz ölçüm bağlı değil.')); for(const requirement of c.requirements)outcomeNote.append(node('p',requirement.label));}
    const selected = usage(); modeBox.hidden = selected !== 'unsure';
    notice.textContent = selected === 'unsure' ? 'İlk aşamadaki isteğin hazır. Şimdi kullanım yolunu netleştirelim.' : selected === 'content_only' ? 'Yalnız içerik hazırlama seçildi. Reklam, paylaşım veya indirme izni verilmiş sayılmaz.' : 'İlk aşama bilgilerin korundu. Aşağıdaki sonuçlar hazırlanmış yerel plan örnekleridir.';
    $('goal').disabled = true;
    $('organic-controls').hidden = selected === 'paid' || selected === 'content_only' || selected === 'unsure';
    context.hidden = !['paid','hybrid'].includes(selected);
    formatBox.hidden = selected !== 'content_only';
  }
  function changed(snapshot) {
    const pair = `${snapshot.intent}/${snapshot.outcome}`;
    if(examplePair&&pair!==examplePair){exampleNotice.hidden=true;examplePair='';document.querySelectorAll('[data-scenario]').forEach(button=>button.setAttribute('aria-pressed','false'));}
    if (pair !== previousPair) {$('business').value = ''; $('sector').value = ''; pendingMode = ''; previousPair = pair;}
    syncSource(); classification(); studio.invalidateFirstStage();
  }
  function restore(b) {
    if(exampleNotice)exampleNotice.hidden=true;examplePair='';document.querySelectorAll('[data-scenario]').forEach(button=>button.setAttribute('aria-pressed','false'));
    ui.restore(b.firstStage); previousPair = `${b.firstStage.intent}/${b.firstStage.outcome}`;
    syncSource(); classification();
    $('business').value = b.planContext?.business || ''; classification(); $('sector').value = b.planContext?.sector || '';
    configure();
  }
  function loadExample(profile, description) {
    const key=Object.keys(window.YaparoSimulation.profiles).find(k=>window.YaparoSimulation.profiles[k]===profile);
    const preset=window.YaparoOwnedExamples.get(key),risk=read().answers.risk;
    let snapshot;
    if(preset&&!description)snapshot=preset.snapshot;
    else{
      const intent=preset?.snapshot.intent||'promote',outcome=preset?.snapshot.outcome||'understand',answers={};
      const subject=M.fields(intent,outcome,answers).find(f=>f.role==='subject'&&['text','textarea'].includes(f.type));
      if(subject&&description)answers[subject.id]=description;
      snapshot={version:'yaparo-first-stage-v1',intent,outcome,answers};
    }
    if(risk)snapshot.answers.risk=risk;
    studio.resetExample();$('business').value='';$('sector').value='';pendingMode='';previousPair='';
    ui.restore(snapshot);changed(read());examplePair=`${snapshot.intent}/${snapshot.outcome}`;
    exampleNotice.textContent=description?'Notun ilgili forma yerleştirildi. Hazır örneğin adresi, bağlantısı ve diğer bilgileri eklenmedi.':`${preset?.label||'Başlangıç'} örneği yüklendi. Bilgiler tamamen kurgusaldır; düzenleyebilir ve kullanım yolunu kendin seçebilirsin.`;
    if(risk&&risk!=='normal')exampleNotice.textContent+=' Önceki özel koşul beyanın korundu.';
    exampleNotice.hidden=false;
    document.querySelectorAll('[data-scenario]').forEach(button=>button.setAttribute('aria-pressed',String(!description&&button.dataset.scenario===key)));
    studio.go(0);
  }
  studio.attachFirstStage({snapshot:read,brief,label(id) {
    if (id === 'communication') return M.intents().find(i => i.id === read().intent)?.label || '';
    if (id === 'action') return M.outcomes(read().intent).find(o => o.id === read().outcome)?.label || '';
    if (id === 'journey-mode') return M.fields(read().intent,read().outcome,read().answers).find(f => f.id === 'delivery_mode')?.options.find(o => o.value === usage())?.label || '';
  },mode,validate,planIssue,nextIssue,configure,restore,loadExample,contract,cards,alternative,productionOptions,syncClassification:classification,unclassified:()=>!$('business').value||!$('sector').value||$('sector').value==='other',review:()=>[['İstenen sonuç',contract().outcomeLabel],['Ölçüm durumu','Gerçek ölçüm bağlantısı ve sonuç tahmini yok.'],...M.summary(read().intent,read().outcome,read().answers).map(row => [row.label,row.value])]});
  const legacy = $('brief-form'); legacy.hidden = true;
  for (const control of legacy.querySelectorAll('input,select,textarea,button')) control.disabled = true;
  const mount = $('first-stage-root'); mount.hidden = false;
  exampleNotice=node('p');exampleNotice.id='owned-example-status';exampleNotice.className='inline-notice';exampleNotice.setAttribute('role','status');exampleNotice.hidden=true;mount.before(exampleNotice);
  ui = window.YaparoFirstStageUI.mount(mount,{onChange:changed,onSubmit:() => {syncSource(); if (studio.acceptFirstStage()) configure();}});
  modeSelect.addEventListener('change',() => {
    if (!modeSelect.value) return; pendingMode = modeSelect.value;
    const s = read(); s.answers.delivery_mode = pendingMode; ui.restore(s); syncSource();
    studio.refreshFirstStageMode(); studio.refreshFirstStageClassification(); configure();
  });
  for (const id of ['business','sector']) $(id).addEventListener('change',() => {classification(); studio.refreshFirstStageClassification();});
  configure();
})();
