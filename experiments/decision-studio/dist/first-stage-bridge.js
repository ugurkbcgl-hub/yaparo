/* Owned brief → existing authored plan demo. No inferred business/account evidence. */
(function () {
  'use strict';
  if (location.pathname === '/legacy.html') return;
  const $ = id => document.getElementById(id);
  const M = window.YaparoFirstStage, studio = window.YaparoStudio;
  const D = window.YaparoResearch, B = window.YaparoBriefFlow;
  const intentMap = {promote:'product_service_intro',sell:'sale_promotion',event:'event',lead:'lead_request',hire:'recruitment',fundraise:'fundraising',announce:'announcement',community:'membership',reputation:'reputation'};
  const actionMap = {remember:'remember',understand:'understand',traffic:'visit_website',visit:'visit_store',message:'message_whatsapp',call:'call',lead_form:'fill_form',book:'book_appointment',register:'register_event',apply:'apply_job',donate:'donate',follow:'follow_engage',subscribe:'join_membership',join:'join_membership',install:'download_app'};
  const goals = {remember:'awareness',understand:'awareness',traffic:'traffic',visit:'store_visits',message:'calls_messages',call:'calls_messages',lead_form:'lead_generation',book:'appointment',register:'event_registration',apply:'job_application',donate:'donation',follow:'engagement',subscribe:'lead_generation',join:'lead_generation',install:'app_install',purchase:'ecommerce_purchase'};
  let ui, previousPair = '', pendingMode = '';
  const read = () => ui?.getSnapshot() || {version:'yaparo-first-stage-v1',intent:'',outcome:'',answers:{}};
  function node(tag, text) {const n = document.createElement(tag); if (text !== undefined) n.textContent = text; return n;}
  function options(select, rows, value = '') {
    select.replaceChildren(); const empty = node('option','Seç'); empty.value = ''; select.append(empty);
    for (const row of rows) {const o = node('option',row.label); o.value = row.value; select.append(o);}
    select.value = rows.some(r => r.value === value) ? value : '';
  }
  function sourceAction(s) {
    if (s.outcome === 'purchase') return ({website:'buy_online',marketplace:'buy_marketplace'})[s.answers.action_checkout] || '';
    if (s.outcome === 'contact') return s.answers.action_contact === 'message' ? (s.answers.action_message_method === 'whatsapp' ? 'message_whatsapp' : '') : ({phone:'call',form:'fill_form'})[s.answers.action_contact] || '';
    if (s.outcome === 'message' && s.answers.action_message_method !== 'whatsapp') return '';
    if (s.outcome === 'lead_form' && s.answers.action_lead_method !== 'form') return '';
    if (s.outcome === 'book' && s.answers.action_booking !== 'page') return '';
    if (s.outcome === 'apply' && !['form','career'].includes(s.answers.action_apply_method)) return '';
    if (s.outcome === 'visit' && s.intent === 'event') return '';
    if (['subscribe','join','follow'].includes(s.outcome)) return '';
    return actionMap[s.outcome] || '';
  }
  function usage() {return read().answers.delivery_mode || '';}
  function mode() {return ({paid:'paid',organic:'organic',hybrid:'both',content_only:'organic'})[usage()] || 'paid';}
  function sourceGoal(s) {
    if (s.outcome === 'contact') return ({call:'calls_messages',message_whatsapp:'calls_messages',fill_form:'lead_generation'})[sourceAction(s)] || '';
    return goals[s.outcome] || '';
  }
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
      firstStageSummary:summary};
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
    if (usage() === 'unsure') return 'Devam etmeden önce kullanım yolunu seç.';
    if (usage() === 'content_only') return 'İçerik isteğin kaydedildi. Kanaldan bağımsız üretim ve format seçimi bu plan demosuna henüz bağlı değil; indirme veya yayın başlatılmadı.';
    if (!sourceAction(read()) || !sourceGoal(read())) return 'İlk aşaman tamamlandı. Seçtiğin sonucun içerik ve kanal eşleştirmesi hazırlanmayı bekliyor; farklı bir aksiyonla devam edilmeyecek.';
    return '';
  }
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
  const notice = node('p'); notice.id = 'owned-plan-note'; notice.className = 'inline-notice'; $('plan-form').prepend(notice);
  function configure() {
    const selected = usage(); modeBox.hidden = selected !== 'unsure';
    notice.textContent = selected === 'unsure' ? 'İlk aşamadaki isteğin hazır. Şimdi kullanım yolunu netleştirelim.' : selected === 'content_only' ? 'Yalnız içerik hazırlama seçildi. Reklam, paylaşım veya indirme izni verilmiş sayılmaz.' : 'İlk aşama bilgilerin korundu. Aşağıdaki sonuçlar hazırlanmış yerel plan örnekleridir.';
    $('goal').disabled = true;
    $('organic-controls').hidden = selected === 'paid' || selected === 'content_only' || selected === 'unsure';
    context.hidden = !['paid','hybrid'].includes(selected);
  }
  function changed(snapshot) {
    const pair = `${snapshot.intent}/${snapshot.outcome}`;
    if (pair !== previousPair) {$('business').value = ''; $('sector').value = ''; pendingMode = ''; previousPair = pair;}
    syncSource(); classification(); studio.invalidateFirstStage();
  }
  function restore(b) {
    ui.restore(b.firstStage); previousPair = `${b.firstStage.intent}/${b.firstStage.outcome}`;
    syncSource(); classification();
    $('business').value = b.planContext?.business || ''; classification(); $('sector').value = b.planContext?.sector || '';
    configure();
  }
  function loadExample(profile, description) {
    const intent = profile.communication === 'event' ? 'event' : profile.business === 'b2b_leadgen' || profile.theme === 'home' ? 'lead' : 'promote';
    const outcome = intent === 'event' ? 'register' : intent === 'lead' ? (profile.theme === 'home' ? 'call' : 'lead_form') : 'visit';
    const answers = {};
    for (const f of M.fields(intent,outcome,answers)) if (f.role === 'subject' && ['text','textarea'].includes(f.type)) answers[f.id] = description || `Sentetik örnek: ${profile.name}`;
    ui.restore({version:'yaparo-first-stage-v1',intent,outcome,answers}); changed(read()); $('step-0').hidden = false;
  }
  studio.attachFirstStage({snapshot:read,brief,label(id) {
    if (id === 'communication') return M.intents().find(i => i.id === read().intent)?.label || '';
    if (id === 'action') return M.outcomes(read().intent).find(o => o.id === read().outcome)?.label || '';
    if (id === 'journey-mode') return M.fields(read().intent,read().outcome,read().answers).find(f => f.id === 'delivery_mode')?.options.find(o => o.value === usage())?.label || '';
  },mode,validate,planIssue,nextIssue,configure,restore,loadExample,syncClassification:classification,unclassified:()=>!$('business').value||!$('sector').value||$('sector').value==='other',review:()=>M.summary(read().intent,read().outcome,read().answers).map(row => [row.label,row.value])});
  const legacy = $('brief-form'); legacy.hidden = true;
  for (const control of legacy.querySelectorAll('input,select,textarea,button')) control.disabled = true;
  const mount = $('first-stage-root'); mount.hidden = false;
  ui = window.YaparoFirstStageUI.mount(mount,{onChange:changed,onSubmit:() => {syncSource(); if (studio.acceptFirstStage()) configure();}});
  modeSelect.addEventListener('change',() => {
    if (!modeSelect.value) return; pendingMode = modeSelect.value;
    const s = read(); s.answers.delivery_mode = pendingMode; ui.restore(s); syncSource();
    studio.refreshFirstStageMode(); studio.refreshFirstStageClassification(); configure();
  });
  for (const id of ['business','sector']) $(id).addEventListener('change',() => {classification(); studio.refreshFirstStageClassification();});
  configure();
})();
