/* Owned first-stage UI. Answers stay in this tab; no provider or storage access. */
(function (root) {
  'use strict';
  const VERSION = 'yaparo-first-stage-v1';
  const SUPPORTED = new Set(['select', 'multiselect', 'text', 'textarea', 'number', 'date', 'time', 'url', 'tel', 'email']);
  function node(tag, text, className) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = String(text);
    if (className) element.className = className;
    return element;
  }
  function mount(container, handlers = {}) {
    const model = root.YaparoFirstStage;
    if (!container || !model) throw new Error('First-stage root and model are required');
    let current = {version: VERSION, intent: '', outcome: '', answers: {}};
    let editingPair = true;
    let riskDeclaration;
    let errors = {};
    let signature = '';
    let extrasOpen = false;
    const options = (intent = current.intent) => model.outcomes(intent) || [];
    const intents = () => model.intents() || [];
    const validIntent = value => typeof value === 'string' && intents().some(item => item.id === value);
    const validOutcome = (intent, value) => typeof value === 'string' && options(intent).some(item => item.id === value);
    const copy = value => structuredClone(value);
    function project() {
      if (!validIntent(current.intent)) current = {version: VERSION, intent: '', outcome: '', answers: {}};
      else if (!validOutcome(current.intent, current.outcome)) current = {version: VERSION, intent: current.intent, outcome: '', answers: {}};
      else {
        current.answers = model.prune(current.intent, current.outcome, current.answers);
        const risk = model.fields(current.intent, current.outcome, current.answers).find(field => field.id === 'risk');
        if (risk?.options?.some(option => option.value === current.answers.risk)) riskDeclaration = current.answers.risk;
      }
      return copy(current);
    }
    const notify = () => {if (typeof handlers.onChange === 'function') handlers.onChange(project());};
    container.classList.add('first-stage');
    container.replaceChildren();
    const form = node('form'); form.id = 'first-stage-form'; form.noValidate = true;
    const pair = node('div', undefined, 'fs-pair');
    const intentBlock = node('section', undefined, 'fs-question-block');
    const intentTitle = node('h2', 'Bu çalışmayla ne yapmak istiyorsun?'); intentTitle.id = 'first-stage-intent-title'; intentTitle.tabIndex = -1;
    const intentHelp = node('p', 'Bir amaç seç. Sonraki seçenekler yalnız bu çalışmaya uygun olacak.', 'fs-hint');
    const intentGrid = node('div', undefined, 'fs-choice-grid'); intentGrid.id = 'first-stage-intents'; intentGrid.setAttribute('role', 'radiogroup'); intentGrid.setAttribute('aria-labelledby', intentTitle.id);
    intentBlock.append(intentTitle, intentHelp, intentGrid);
    const outcomeBlock = node('section', undefined, 'fs-question-block'); outcomeBlock.id = 'first-stage-outcome-block';
    const outcomeTitle = node('h2', 'Gören kişi ne yapsın?'); outcomeTitle.id = 'first-stage-outcome-title'; outcomeTitle.tabIndex = -1;
    const outcomeHelp = node('p', 'Bu çalışmanın asıl sonucunu seç. Diğer ayrıntıları buna göre soracağız.', 'fs-hint');
    const outcomeGrid = node('div', undefined, 'fs-choice-grid'); outcomeGrid.id = 'first-stage-outcomes'; outcomeGrid.setAttribute('role', 'radiogroup'); outcomeGrid.setAttribute('aria-labelledby', outcomeTitle.id);
    outcomeBlock.append(outcomeTitle, outcomeHelp, outcomeGrid); pair.append(intentBlock, outcomeBlock);
    const summary = node('div', undefined, 'fs-selection-summary'); summary.id = 'first-stage-selection-summary';
    const summaryText = node('p'); summaryText.id = 'first-stage-selection-text';
    const change = node('button', 'Seçimleri değiştir', 'fs-change'); change.type = 'button'; change.id = 'first-stage-change'; summary.append(summaryText, change);
    const context = node('section', undefined, 'fs-context'); context.id = 'first-stage-context';
    const contextTitle = node('h2', 'Şimdi bu çalışmaya özel birkaç bilgi'); contextTitle.id = 'first-stage-context-title'; contextTitle.tabIndex = -1;
    const requiredHint = node('p', 'Yıldızlı alanlar gerekli. Yalnız seçtiğin yola ait bilgileri soruyoruz.', 'fs-hint');
    const errorBox = node('div', undefined, 'fs-error-summary'); errorBox.id = 'first-stage-errors'; errorBox.tabIndex = -1; errorBox.setAttribute('role', 'alert');
    const fields = node('div', undefined, 'fs-fields'); fields.id = 'first-stage-fields';
    const actions = node('div', undefined, 'fs-actions');
    const submit = node('button', 'Planını kur', 'fs-submit'); submit.id = 'first-stage-submit'; submit.type = 'submit';
    const note = node('p', 'Bilgiler yalnız bu yerel taslakta kullanılır. Gerçek AI üretimi veya reklam yayını başlamaz.', 'fs-hint');
    actions.append(note, submit);
    const status = node('p', '', 'fs-status'); status.id = 'first-stage-status'; status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
    context.append(contextTitle, requiredHint, fields, actions, status);
    form.append(errorBox, pair, summary, context); container.append(form);

    function choice(item, selected, kind, choose) {
      const button = node('button', item.label, 'fs-choice'); button.type = 'button';
      button.dataset[kind === 'intent' ? 'firstIntent' : 'firstOutcome'] = item.id;
      button.id = `first-stage-${kind}-${item.id}`;
      button.setAttribute('role', 'radio'); button.setAttribute('aria-checked', String(selected));
      button.tabIndex = selected ? 0 : -1;
      if (selected) button.classList.add('is-selected');
      button.addEventListener('click', () => choose(item.id));
      button.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        const buttons = [...button.parentElement.querySelectorAll(':scope > button')];
        const index = buttons.indexOf(button);
        const next = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 : (index + (['ArrowLeft', 'ArrowUp'].includes(event.key) ? -1 : 1) + buttons.length) % buttons.length;
        buttons[next].click();
      });
      return button;
    }
    function chooseIntent(value) {
      if (current.intent === value) return;
      project();
      current = {version: VERSION, intent: value, outcome: '', answers: {}};
      errors = {}; extrasOpen = false; editingPair = true; status.textContent = '';
      render(); notify();
      document.getElementById(`first-stage-intent-${value}`)?.focus({preventScroll: true});
    }
    function chooseOutcome(value) {
      if (current.outcome !== value) {
        project(); current.outcome = value; current.answers = riskDeclaration === undefined ? {} : {risk: riskDeclaration}; errors = {}; extrasOpen = false; status.textContent = '';
      }
      editingPair = false; render(); notify(); contextTitle.focus();
    }
    function renderPair() {
      intentGrid.replaceChildren(...intents().map(item => choice(item, item.id === current.intent, 'intent', chooseIntent)));
      if (!current.intent && intentGrid.firstElementChild) intentGrid.firstElementChild.tabIndex = 0;
      outcomeGrid.replaceChildren(...options().map(item => choice(item, item.id === current.outcome, 'outcome', chooseOutcome)));
      if (!current.outcome && outcomeGrid.firstElementChild) outcomeGrid.firstElementChild.tabIndex = 0;
      outcomeBlock.hidden = !current.intent;
      const ready = validOutcome(current.intent, current.outcome);
      pair.hidden = ready && !editingPair;
      summary.hidden = !ready || editingPair;
      summaryText.textContent = ready ? `${intents().find(item => item.id === current.intent).label} → ${options().find(item => item.id === current.outcome).label}` : '';
      context.hidden = !ready || editingPair;
    }
    function readControl(control, field) {
      if (field.type === 'multiselect') return [...control.querySelectorAll('input:checked')].map(input => input.value);
      if (field.type === 'number') return control.value === '' ? undefined : Number(control.value);
      return control.value;
    }
    function captureFocus() {
      const active = document.activeElement;
      if (!active || !fields.contains(active) || !active.id) return null;
      let start = null, end = null;
      try {start = active.selectionStart; end = active.selectionEnd;} catch { /* Numeric/date controls do not expose text selection. */ }
      return {id: active.id, start, end};
    }
    function restoreFocus(saved) {
      if (!saved) return;
      const target = document.getElementById(saved.id);
      if (!target || !fields.contains(target)) return;
      target.focus({preventScroll: true});
      if (saved.start !== null) {try {target.setSelectionRange(saved.start, saved.end);} catch { /* Non-text control. */ }}
    }
    function update(field, control) {
      const value = readControl(control, field);
      if (value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) delete current.answers[field.id];
      else current.answers[field.id] = value;
      if (field.id === 'risk' && value === '') riskDeclaration = undefined;
      project(); delete errors[field.id]; status.textContent = '';
      const active = model.fields(current.intent, current.outcome, current.answers);
      const nextSignature = JSON.stringify(active);
      if (nextSignature !== signature) renderFields(active);
      else paintErrors();
      notify();
    }
    function makeField(field) {
      const box = node('div', undefined, 'fs-field'); box.dataset.firstField = field.id;
      const id = `first-stage-${field.id}`;
      let control;
      const label = node(field.type === 'multiselect' ? 'legend' : 'label', `${field.label}${field.required ? ' *' : ''}`);
      if (field.type !== 'multiselect') label.htmlFor = id;
      if (field.type === 'multiselect') {
        control = node('fieldset', undefined, 'fs-multiselect'); control.id = id;
        control.append(label);
        for (const option of field.options || []) {
          const optionLabel = node('label', undefined, 'fs-check');
          const input = node('input'); input.type = 'checkbox'; input.value = option.value; input.name = `fs-${field.id}`; input.id = `${id}-${option.value}`;
          input.checked = Array.isArray(current.answers[field.id]) && current.answers[field.id].includes(option.value);
          optionLabel.append(input, node('span', option.label)); control.append(optionLabel);
          input.addEventListener('change', () => update(field, control));
        }
        box.append(control);
      } else if (field.type === 'select') {
        control = node('select'); control.id = id; control.name = `fs-${field.id}`;
        const blank = node('option', 'Seçimini yap'); blank.value = ''; control.append(blank);
        for (const option of field.options || []) {
          const item = node('option', option.label); item.value = option.value; control.append(item);
        }
        control.value = current.answers[field.id] ?? '';
        box.append(label, control); control.addEventListener('change', () => update(field, control));
      } else if (SUPPORTED.has(field.type)) {
        control = node(field.type === 'textarea' ? 'textarea' : 'input'); control.id = id; control.name = `fs-${field.id}`;
        if (control.tagName === 'INPUT') control.type = field.type;
        if (control.tagName === 'TEXTAREA') control.rows = 3;
        control.value = current.answers[field.id] ?? '';
        control.maxLength = field.maxLength || 2000;
        if (field.min !== undefined) control.min = String(field.min);
        if (field.max !== undefined) control.max = String(field.max);
        if (field.step !== undefined) control.step = String(field.step);
        if (field.type === 'number') control.inputMode = field.step === 1 ? 'numeric' : 'decimal';
        box.append(label, control); control.addEventListener('input', () => update(field, control));
      } else {
        box.append(label, node('p', 'Bu alan şu an doldurulamıyor. Devam etmeden önce tamamlanması gerekiyor.', 'fs-field-error'));
      }
      if (control) {
        control.dataset.firstAnswer = field.id;
        control.setAttribute('aria-required', String(Boolean(field.required)));
      }
      const described = [];
      if (field.help) {
        const help = node('p', field.help, 'fs-hint'); help.id = `${id}-help`; box.append(help); described.push(help.id);
      }
      const error = node('p', '', 'fs-field-error'); error.id = `${id}-error`; error.hidden = true; box.append(error); described.push(error.id);
      if (control) control.setAttribute('aria-describedby', described.join(' '));
      return box;
    }
    function renderFields(active) {
      const savedFocus = captureFocus();
      const oldExtras = fields.querySelector(':scope > details');
      if (oldExtras) extrasOpen = oldExtras.open;
      fields.replaceChildren();
      const required = active.filter(field => field.required || field.essential);
      const optional = active.filter(field => !field.required && !field.essential);
      const appendGroups = (target, list) => {
        const groups = [...new Set(list.map(field => field.group || 'Çalışmanın ayrıntıları'))];
        for (const group of groups) {
          const set = node('fieldset', undefined, 'fs-group'); set.append(node('legend', group));
          const grid = node('div', undefined, 'fs-field-grid');
          list.filter(field => (field.group || 'Çalışmanın ayrıntıları') === group).forEach(field => grid.append(makeField(field)));
          set.append(grid); target.append(set);
        }
      };
      appendGroups(fields, required);
      if (optional.length) {
        const extras = node('details', undefined, 'fs-extras'); extras.open = extrasOpen;
        extras.append(node('summary', 'Ek bilgiler · istersen şimdi ekle'));
        appendGroups(extras, optional); fields.append(extras);
      }
      signature = JSON.stringify(active); paintErrors(); restoreFocus(savedFocus);
    }
    function paintErrors() {
      const active = model.fields(current.intent, current.outcome, current.answers);
      const known = new Map(active.map(field => [field.id, field]));
      errorBox.replaceChildren();
      const entries = Object.entries(errors).filter(([id]) => ['_form', '_route'].includes(id) || known.has(id));
      errorBox.hidden = entries.length === 0;
      if (entries.length) {
        errorBox.append(node('strong', 'Birkaç bilgiyi kontrol edelim'));
        const list = node('ul');
        for (const [id, message] of entries) {
          const item = node('li');
          if (known.has(id)) {
            const jump = node('button', message, 'fs-error-link'); jump.type = 'button';
            jump.addEventListener('click', () => {
              const control = document.getElementById(`first-stage-${id}`);
              const extra = control?.closest('details'); if (extra) extra.open = true;
              if (control?.tagName === 'FIELDSET') control.querySelector('input')?.focus(); else control?.focus();
            }); item.append(jump);
          } else item.textContent = message;
          list.append(item);
        }
        errorBox.append(list);
      }
      for (const field of active) {
        const control = document.getElementById(`first-stage-${field.id}`);
        const error = document.getElementById(`first-stage-${field.id}-error`);
        if (error) {error.textContent = errors[field.id] || ''; error.hidden = !errors[field.id];}
        if (control) control.setAttribute('aria-invalid', String(Boolean(errors[field.id])));
      }
    }
    function render() {
      project(); renderPair();
      if (current.outcome) renderFields(model.fields(current.intent, current.outcome, current.answers));
      else {fields.replaceChildren(); signature = ''; errors = {}; errorBox.hidden = true;}
    }
    change.addEventListener('click', () => {editingPair = true; renderPair(); intentTitle.focus();});
    form.addEventListener('submit', event => {
      event.preventDefault(); project();
      const result = model.validate(current.intent, current.outcome, current.answers);
      current.answers = result.answers;
      const unsupported = model.fields(current.intent, current.outcome, current.answers).filter(field => !SUPPORTED.has(field.type));
      errors = {...result.errors};
      if (unsupported.length) errors._form = 'Gerekli alanlardan biri henüz kullanılamıyor. Bu taslakla devam edemiyoruz.';
      renderFields(model.fields(current.intent, current.outcome, current.answers));
      if (!result.valid || unsupported.length) {
        editingPair = false; renderPair(); paintErrors();
        const firstId = Object.keys(errors).find(id => document.getElementById(`first-stage-${id}`));
        const first = firstId && document.getElementById(`first-stage-${firstId}`);
        const extra = first?.closest('details'); if (extra) extra.open = true;
        if (first?.tagName === 'FIELDSET') first.querySelector('input')?.focus(); else if (first) first.focus(); else errorBox.focus();
        if (typeof handlers.onInvalid === 'function') handlers.onInvalid(copy(errors));
        return;
      }
      status.textContent = 'Bilgilerin kontrol edildi. Sonraki adımda planını kurabiliriz.';
      if (typeof handlers.onSubmit === 'function') handlers.onSubmit(project());
    });
    render();
    return {
      getSnapshot: () => project(),
      restore(snapshot, settings = {}) {
        riskDeclaration = undefined;
        const knownVersion = snapshot && typeof snapshot === 'object' && !Array.isArray(snapshot) && snapshot.version === VERSION;
        current = knownVersion ? {version: VERSION, intent: snapshot.intent, outcome: snapshot.outcome, answers: snapshot.answers && typeof snapshot.answers === 'object' && !Array.isArray(snapshot.answers) ? copy(snapshot.answers) : {}} : {version: VERSION, intent: '', outcome: '', answers: {}};
        errors = {}; status.textContent = ''; project(); editingPair = !current.outcome; extrasOpen = false; render();
        if (settings?.notify) notify();
      },
      reset() {current = {version: VERSION, intent: '', outcome: '', answers: {}}; riskDeclaration = undefined; editingPair = true; extrasOpen = false; errors = {}; status.textContent = ''; render(); notify();},
      showErrors(next) {errors = next && typeof next === 'object' && !Array.isArray(next) ? {...next} : {}; paintErrors();},
      refresh() {render();}
    };
  }
  root.YaparoFirstStageUI = {mount, version: VERSION};
})(typeof window !== 'undefined' ? window : globalThis);
