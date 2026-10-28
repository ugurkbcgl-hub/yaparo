(function () {
  'use strict';
  const catalog = window.YaparoV2Catalog, flow = window.YaparoV2Flow;
  let intent = '', outcome = '', answers = {}, opened = false;
  const $ = id => document.getElementById(id);
  function el(tag, text) {const node = document.createElement(tag); if (text) node.textContent = text; return node;}
  function choices(target, items, selected, key, action) {
    target.replaceChildren();
    items.forEach(item => {
      const button = el('button', item.label_tr);
      button.type = 'button'; button.dataset.value = item[key];
      button.setAttribute('aria-pressed', String(selected === item[key]));
      button.addEventListener('click', () => action(item[key])); target.append(button);
    });
  }
  function renderPair() {
    choices($('intents'), catalog.intents, intent, 'intent_id', value => {intent = value; outcome = ''; answers = {}; opened = false; render();});
    $('intent-section').hidden = opened;
    $('outcome-section').hidden = !intent || opened;
    $('selection').hidden = !opened;
    $('selection-text').textContent = opened ? catalog.intents.find(i => i.intent_id === intent).label_tr + ' → ' + catalog.outcomes.find(o => o.outcome_id === outcome).label_tr : '';
    const items = flow.outcomes(catalog, intent);
    choices($('outcomes'), items.filter(o => o.recommended), outcome, 'outcome_id', chooseOutcome);
    choices($('other-outcomes'), items.filter(o => !o.recommended), outcome, 'outcome_id', chooseOutcome);
    $('continue').hidden = !outcome || opened;
  }
  function chooseOutcome(value) {outcome = value; answers = {}; opened = false; render();}
  function state() {return flow.resolve(catalog, intent, outcome, answers);}
  function field(question) {
    const wrap = el('label'); wrap.className = 'field';
    wrap.append(el('span', question.label_tr + (question.required_for === 'brief' ? ' *' : '')));
    if (!flow.supported.includes(question.type)) {
      const note = el('div', 'Bu alan için özel seçim bileşeni hazırlanacak. Şimdilik doğrulanmış bir bilgi olarak kaydedilmez.');
      note.className = 'pending'; wrap.append(note); return wrap;
    }
    let control;
    if (['select', 'multiselect'].includes(question.type)) {
      control = el('select');
      if (question.type === 'multiselect') control.multiple = true;
      else {const option = el('option', 'Seç'); option.value = ''; control.append(option);}
      catalog.options.filter(o => o.option_set_id === question.option_set_id).forEach(o => {
        const option = el('option', o.label_tr); option.value = o.value;
        option.selected = Array.isArray(answers[question.field_id]) ? answers[question.field_id].includes(o.value) : answers[question.field_id] === o.value;
        control.append(option);
      });
    } else {
      control = el(question.type === 'text' && !['organization_name', 'subject'].includes(question.field_id) ? 'textarea' : 'input');
      if (control.tagName === 'INPUT') control.type = ({url: 'url', phone: 'tel', datetime: 'datetime-local', number: 'number', integer: 'number'})[question.type] || 'text';
      control.value = answers[question.field_id] ?? '';
      control.maxLength = question.validation.maxLength || 2000;
      if (question.type === 'timezone') control.placeholder = 'Örnek: Europe/Istanbul';
      if (question.type === 'url_list') control.placeholder = 'Her bağlantıyı boşlukla ayır';
    }
    control.name = question.field_id; control.id = 'v2-' + question.field_id;
    const update = () => {
      let value = control.multiple ? [...control.selectedOptions].map(o => o.value) : control.value;
      if (['number', 'integer'].includes(question.type) && value !== '') value = Number(value);
      if (value === '' || (Array.isArray(value) && !value.length)) delete answers[question.field_id];
      else answers[question.field_id] = value;
      answers = state().answers; $('result').replaceChildren();
    };
    control.addEventListener('input', update);
    control.addEventListener('change', () => {update(); if (['select', 'multiselect'].includes(question.type)) renderFields();});
    wrap.append(control);
    if (question.help_tr && question.field_id !== 'organization_name') wrap.append(el('small', question.help_tr));
    return wrap;
  }
  function renderFields() {
    const focused = document.activeElement?.id;
    const extrasOpen = $('fields').querySelector(':scope > details')?.open || false;
    const current = state(); answers = current.answers;
    $('fields').replaceChildren();
    const stage = current.questions.filter(q => q.stage === 1);
    const optional = el('details'); optional.open = extrasOpen; optional.append(el('summary', 'Ek ayrıntılar (isteğe bağlı)'));
    for (const module of catalog.modules) {
      const questions = stage.filter(q => q.module_id === module.module_id);
      for (const extra of [false, true]) {
        const group = questions.filter(q => (q.required_for === 'optional') === extra);
        if (!group.length) continue;
        const set = el('fieldset'); set.append(el('legend', module.title_tr)); group.forEach(q => set.append(field(q)));
        (extra ? optional : $('fields')).append(set);
      }
    }
    if (optional.children.length > 1) $('fields').append(optional);
    if (focused?.startsWith('v2-')) document.getElementById(focused)?.focus({preventScroll: true});
    $('route-note').textContent = flow.assess(catalog, current).needsClarification
      ? 'Bu iki seçim için hedefi netleştirmemiz gerekiyor. Ayrıntılarını yazabilirsin; henüz bütçe veya kanal dağılımına geçilmeyecek.'
      : 'Yıldızlı bilgiler başlangıç için gerekli. Bağlantı ve özel alanlar tamamlanmadan uygulamaya geçilmez.';
  }
  function render() {renderPair(); $('context').hidden = !opened; $('result').replaceChildren(); if (opened) renderFields();}
  $('continue').addEventListener('click', () => {opened = true; render(); $('context-title').focus();});
  $('change').addEventListener('click', () => {opened = false; render(); $('intent-title').scrollIntoView();});
  $('brief').addEventListener('submit', event => {
    event.preventDefault(); const current = state(), brief = flow.assess(catalog, current), plan = flow.assess(catalog, current, 'plan');
    const result = $('result'); result.replaceChildren();
    if (brief.needsClarification) result.append(el('p', 'Sonraki adım: amaç ve beklenen sonucu netleştir. Bu seçim bütçe önerisine dönüşmez.'));
    else if (!brief.ready) result.append(el('p', 'Başlangıç bilgilerini tamamlayalım.'));
    else result.append(el('p', 'Başlangıç bilgileri tamam. Sonraki adım, plan için gereken konum, bağlantı ve kullanım bilgilerini toplamak.'));
    const missing = brief.missing.length ? brief.missing : plan.missing;
    if (missing.length) {
      const details = el('details'); details.open = brief.missing.length > 0;
      details.append(el('summary', `${missing.length} bilgi henüz tamamlanmadı`)); const list = el('ul');
      missing.forEach(q => list.append(el('li', q.label_tr + (!flow.supported.includes(q.type) ? ' — özel bileşen gerekli' : '')))); details.append(list); result.append(details);
    }
    if (brief.invalid.length) result.append(el('p', 'Girilen bilgilerin biçimini kontrol et: ' + brief.invalid.map(q => q.label_tr).join(', ')));
    result.append(el('p', 'Bu önizleme plan oluşturmaz, bağlantıları sorgulamaz veya reklam yayımlamaz.'));
  });
  render();
})();
