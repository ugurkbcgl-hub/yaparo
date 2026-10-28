(function (root) {
  'use strict';
  function matches(rule, values, depth = 0) {
    if (!rule || depth > 12) return false;
    const value = Object.hasOwn(values, rule.field) ? values[rule.field] : undefined;
    switch (rule.op) {
      case 'always': return true;
      case 'eq': return value !== undefined && value === rule.value;
      case 'in': return value !== undefined && Array.isArray(rule.value) && rule.value.includes(value);
      case 'all': return Array.isArray(rule.args) && rule.args.length > 0 && rule.args.every(r => matches(r, values, depth + 1));
      case 'any': return Array.isArray(rule.args) && rule.args.some(r => matches(r, values, depth + 1));
      case 'cross_border': return typeof values.business_country === 'string' && Array.isArray(values.target_countries) && values.target_countries.some(c => c !== values.business_country);
      default: return false;
    }
  }
  function resolve(catalog, intent, outcome, supplied = {}) {
    const route = catalog.routes.find(r => r.intent_id === intent && r.outcome_id === outcome);
    if (!route) return {route: null, modules: [], questions: [], answers: {}};
    let answers = Object.fromEntries(catalog.questions.filter(q => Object.hasOwn(supplied, q.field_id)).map(q => [q.field_id, supplied[q.field_id]]));
    let modules, questions;
    // Prune until hidden values can no longer activate dependent modules.
    for (let pass = 0; pass <= catalog.questions.length; pass++) {
      const context = {...answers, intent_id: intent, outcome_id: outcome};
      modules = new Set(route.module_ids);
      for (const rule of catalog.module_rules) if (matches(rule.when, context)) rule.add_modules.forEach(m => modules.add(m));
      questions = catalog.questions.filter(q => modules.has(q.module_id) && matches(q.visible_when, context));
      const active = new Set(questions.map(q => q.field_id));
      const next = Object.fromEntries(Object.entries(answers).filter(([key]) => active.has(key)));
      if (Object.keys(next).length === Object.keys(answers).length) break;
      answers = next;
    }
    return {route, modules: [...modules], questions, answers};
  }
  const supported = new Set(['text', 'select', 'multiselect', 'url', 'url_list', 'phone', 'number', 'integer', 'datetime', 'timezone']);
  function valid(question, value, catalog) {
    if (!supported.has(question.type)) return false;
    const rules = question.validation || {};
    if (question.type === 'select' || question.type === 'multiselect') {
      const allowed = catalog.options.filter(o => o.option_set_id === question.option_set_id).map(o => o.value);
      return question.type === 'select' ? allowed.includes(value) : Array.isArray(value) && value.length > 0 && value.every(v => allowed.includes(v));
    }
    if (question.type === 'number' || question.type === 'integer') {
      return typeof value === 'number' && Number.isFinite(value) && (question.type !== 'integer' || Number.isInteger(value)) && (rules.minimum === undefined || value >= rules.minimum) && (rules.maximum === undefined || value <= rules.maximum) && (rules.exclusiveMinimum === undefined || value > rules.exclusiveMinimum);
    }
    if (typeof value !== 'string' || !value.trim() || value.length > (rules.maxLength || 2000)) return false;
    if (question.type === 'url' || question.type === 'url_list') {
      const urls = question.type === 'url' ? [value] : value.split(/\s+/);
      return urls.every(raw => {try {const u = new URL(raw); return ['https:', 'http:'].includes(u.protocol) && !u.username && !u.password && Boolean(u.hostname);} catch {return false;}});
    }
    if (question.type === 'phone') return /^\+?[\d ()-]{7,24}$/.test(value) && value.replace(/\D/g, '').length >= 7;
    if (question.type === 'datetime') return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value) && !Number.isNaN(Date.parse(value));
    if (question.type === 'timezone') {try {new Intl.DateTimeFormat('tr', {timeZone: value});} catch {return false;}}
    return true;
  }
  function assess(catalog, state, phase = 'brief') {
    const phases = {brief: ['brief'], plan: ['brief', 'plan'], publish: ['brief', 'plan', 'creative', 'publish']};
    if (!phases[phase]) throw new Error('Unknown qualification phase');
    const required = state.questions.filter(q => phases[phase].includes(q.required_for));
    const missing = required.filter(q => !valid(q, state.answers[q.field_id], catalog));
    const invalid = state.questions.filter(q => Object.hasOwn(state.answers, q.field_id) && !valid(q, state.answers[q.field_id], catalog));
    return {ready: Boolean(state.route) && state.route.route_state === 'resolved' && !state.route.requires_goal_confirmation && missing.length === 0 && invalid.length === 0, missing, invalid, needsClarification: Boolean(state.route && (state.route.route_state !== 'resolved' || state.route.requires_goal_confirmation))};
  }
  function outcomes(catalog, intent) {
    return catalog.routes.filter(r => r.intent_id === intent).sort((a, b) => a.recommended_rank - b.recommended_rank).map(r => ({...catalog.outcomes.find(o => o.outcome_id === r.outcome_id), recommended: r.show_initial === true, route_state: r.route_state}));
  }
  const api = {matches, resolve, valid, assess, outcomes, supported: [...supported]};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.YaparoV2Flow = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
