import {spec, fingerprint} from './spec.mjs';

const fail = message => { throw new Error(message); };
const exact = (value, fields) => {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      JSON.stringify(Object.keys(value).sort()) !== JSON.stringify([...fields].sort())) fail('Invalid event fields');
};
const question = id => spec.questions.find(q => q.id === id);
const choice = (q, value, special) => value === special || q.options.some(o => o.id === value);

// Replaying a bounded log validates every state transition; saved objects never become authority.
export function replay(events) {
  if (!Array.isArray(events) || events.length > 100) fail('Invalid event log');
  const state = {players: [], stage: 0, picks: [], boosts: [], locked: [], outcomes: {}};
  for (const input of events) {
    const event = structuredClone(input);
    if (!state.players.length) {
      exact(event, ['type', 'players']);
      if (event.type !== 'start' || !Array.isArray(event.players) || event.players.length < 2 || event.players.length > 6 ||
          event.players.some(p => typeof p !== 'string' || !p.trim() || p.length > 30) ||
          new Set(event.players.map(p => p.trim().toLowerCase())).size !== event.players.length) fail('Use 2–6 distinct player names');
      state.players = event.players.map(p => p.trim());
      state.picks = event.players.map(() => ({})); state.boosts = event.players.map(() => []);
      continue;
    }
    const stage = spec.stages[state.stage];
    if (!stage) fail('Match already finished');
    if (event.type === 'lock') {
      exact(event, ['type', 'player', 'picks', 'boost']);
      if (stage.kind !== 'lock' || !Number.isInteger(event.player) || event.player < 0 ||
          event.player >= state.players.length || state.locked.includes(event.player)) fail('Card cannot be changed');
      exact(event.picks, stage.questions);
      if (stage.questions.some(id => !choice(question(id), event.picks[id], 'skip'))) fail('Pick or explicitly skip every call');
      if (event.boost !== null && (!stage.boost || !stage.questions.includes(event.boost) || event.picks[event.boost] === 'skip')) fail('Invalid boost');
      Object.assign(state.picks[event.player], event.picks);
      if (event.boost !== null) state.boosts[event.player].push(event.boost);
      state.locked.push(event.player);
      if (state.locked.length === state.players.length) { state.stage++; state.locked = []; }
    } else if (event.type === 'confirm') {
      exact(event, ['type', 'outcomes']);
      if (stage.kind !== 'reveal') fail('All cards must be locked before results');
      exact(event.outcomes, stage.questions);
      if (stage.questions.some(id => !choice(question(id), event.outcomes[id], 'void'))) fail('Choose an outcome or void');
      Object.assign(state.outcomes, event.outcomes); state.stage++;
    } else fail('Unsupported action');
  }
  return state;
}

export function scores(state) {
  const rows = state.players.map((name, player) => {
    const details = spec.questions.filter(q => Object.hasOwn(state.outcomes, q.id)).map(q => {
      const pick = state.picks[player][q.id], outcome = state.outcomes[q.id];
      const points = pick !== 'skip' && outcome !== 'void' && pick === outcome ? q.points * (state.boosts[player].includes(q.id) ? 2 : 1) : 0;
      return {question: q.text, pick, outcome, points};
    });
    return {name, points: details.reduce((sum, d) => sum + d.points, 0), details};
  });
  return rows.map(row => ({...row, rank: 1 + rows.filter(other => other.points > row.points).length})).sort((a, b) => a.rank - b.rank);
}

export function encode(events) {
  replay(events);
  return JSON.stringify({schema: 1, fingerprint, events});
}

export function decode(text) {
  if (typeof text !== 'string' || text.length > 100000) fail('Invalid saved data');
  const saved = JSON.parse(text); exact(saved, ['schema', 'fingerprint', 'events']);
  if (saved.schema !== 1 || saved.fingerprint !== fingerprint) fail('Save belongs to different rules; it was not changed');
  replay(saved.events);
  return structuredClone(saved.events);
}
