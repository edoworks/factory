import {spec} from './spec.mjs';
import {replay, scores, encode, decode} from './engine.mjs';
const key = 'factory.game.' + spec.id;
const screen = document.querySelector('#screen'), warning = document.querySelector('#warning');
document.title = spec.title; document.querySelector('#title').textContent = spec.title;
document.querySelector('#description').textContent = spec.description;
let events = [], state, blocked = false, persistedRaw = null, writing = false;
function el(tag, text, parent, attrs = {}) {
  const item = document.createElement(tag); if (text !== null) item.textContent = text;
  for (const [name, value] of Object.entries(attrs)) item.setAttribute(name, value);
  parent?.append(item); return item;
}
function button(text, parent, action, id) { const b = el('button', text, parent, {type:'button', ...(id ? {id} : {})}); b.onclick = action; return b; }
function submit(text, form) { el('button', text, form, {type:'submit'}); }
function label(text, form, id) { el('label', text, form, {for:id}); }
function alertError(error) { warning.textContent = error.message; }
async function serializedWrite(change, allowBlocked = false) {
  if (writing || (blocked && !allowBlocked)) return;
  writing = true;
  const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 3000);
  try {
    if (!navigator.locks?.request) throw new Error('This browser cannot safely coordinate saved matches. Web Locks are required.');
    await navigator.locks.request(key, {mode:'exclusive', signal:controller.signal}, () => {
      // All app writers, including reset, use this same origin-scoped lock.
      // The comparison is inside the lock; compare-then-write alone is not atomic.
      if (localStorage.getItem(key) !== persistedRaw) {
        blocked = true;
        warning.textContent = 'This match changed in another tab. Please reload; your stale changes were not saved.';
        render(); return;
      }
      change();
    });
  } catch (error) {
    blocked = true; warning.textContent = 'Cannot safely write this match. ' + error.message; render();
  } finally { clearTimeout(timeout); writing = false; }
}
function act(event) {
  return serializedWrite(() => {
    try {
      const next = [...events, structuredClone(event)]; replay(next); events = next;
      const encoded = encode(events);
      try { localStorage.setItem(key, encoded); persistedRaw = encoded; warning.textContent = ''; }
      catch { warning.textContent = 'Progress is in memory only: storage is unavailable. Keep this page open.'; }
      render();
    } catch (error) { alertError(error); }
  });
}
try { persistedRaw = localStorage.getItem(key); if (persistedRaw !== null) events = decode(persistedRaw); }
catch (error) { blocked = true; warning.textContent = 'Cannot safely restore this match. Saved data was not overwritten. ' + error.message; }

function selectQuestion(form, q, special) {
  label(q.text, form, 'answer-'+q.id); el('small', q.scope, form);
  const select = el('select', null, form, {id:'answer-'+q.id, name:'answer:'+q.id, required:''});
  el('option', 'Choose…', select, {value:''});
  for (const option of q.options) el('option', option.label, select, {value:option.id});
  el('option', special === 'skip' ? 'Skip — zero points' : 'Void — zero for everyone', select, {value:special});
}
function lockCard(player, stage) {
  screen.replaceChildren(); el('h2', state.players[player] + '’s private card', screen);
  const form = el('form', null, screen, {id:'picks'});
  for (const id of stage.questions) selectQuestion(form, spec.questions.find(q => q.id === id), 'skip');
  if (stage.boost) {
    label('Optional boost — double one correct call', form, 'control-boost');
    const boost = el('select', null, form, {id:'control-boost',name:'control:boost'}); el('option','No boost',boost,{value:''});
    for (const id of stage.questions) el('option',spec.questions.find(q => q.id === id).text,boost,{value:id});
  }
  el('p', 'Lock is irreversible for this match. Put the phone down after your call.', form, {class:'help'});
  submit('Lock and hide picks',form);
  form.onsubmit = event => { event.preventDefault(); const values = new FormData(form); act({type:'lock',player,picks:Object.fromEntries(stage.questions.map(id=>[id,values.get('answer:'+id)])),boost:values.get('control:boost') || null}); };
  button('Back to handoff',screen,render);
}
function host(stage) {
  const form = el('form',null,screen,{id:'results'});
  el('p','Host: record observed broadcast outcomes. This rehearsal has no live feed.',form);
  for (const id of stage.questions) selectQuestion(form,spec.questions.find(q=>q.id===id),'void');
  submit('Preview results',form);
  form.onsubmit = event => {
    event.preventDefault(); const data = new FormData(form);
    const outcomes = Object.fromEntries(stage.questions.map(id=>[id,data.get('answer:'+id)]));
    try { replay([...events,{type:'confirm',outcomes}]); } catch(error) { alertError(error); return; }
    screen.replaceChildren(); el('h2','Review before confirming',screen);
    const list = el('ul',null,screen);
    for (const id of stage.questions) { const q=spec.questions.find(q=>q.id===id); el('li',q.text+': '+(q.options.find(o=>o.id===outcomes[id])?.label || 'Void'),list); }
    el('p','Confirmation reveals and scores these calls. It cannot be undone within this match.',screen);
    button('Confirm outcomes',screen,()=>act({type:'confirm',outcomes}),'confirm');
    button('Change outcomes',screen,render,'edit-results');
  };
}
function render() {
  state = replay(events); screen.replaceChildren(); const recap=document.querySelector('#recap');recap.replaceChildren();
  if(blocked) {
    el('h2','Saved match needs attention',screen);
    el('p','Reload to read the latest saved match. Reset can discard only the saved version this tab read.',screen);
    button('Reload latest match',screen,()=>location.reload(),'reload');return;
  }
  if(!state.players.length) {
    el('h2','Gather your couch',screen);const form=el('form',null,screen,{id:'setup'});
    label('Player names — one per line (2–6)',form,'players');const names=el('textarea','Player 1\nPlayer 2',form,{id:'players',required:''});
    submit('Start rehearsal',form);form.onsubmit=e=>{e.preventDefault();act({type:'start',players:names.value.split('\n').map(p=>p.trim())});};return;
  }
  const stage=spec.stages[state.stage];el('h2',stage?.title || 'Final podium',screen);
  if(stage?.kind==='lock') {
    el('p','Pass the phone. Open only your own card. Picks stay hidden until their results are confirmed.',screen);
    state.players.forEach((name,player)=>{if(!state.locked.includes(player)) button('Open '+name+'’s card',screen,()=>lockCard(player,stage),'player-'+player);else el('p',name+' — locked',screen);});
  } else if(stage) host(stage);
  if(Object.keys(state.outcomes).length) {
    el('h2',stage?'Confirmed calls':'The recap',recap);
    for(const row of scores(state)) {
      const article=el('article',null,recap);el('strong',row.points+' prediction points',article,{class:'score'});el('h3','#'+row.rank+' '+row.name,article);
      const list=el('ul',null,article);
      for(const d of row.details) el('li',`${d.question} · Pick: ${d.pick} · Result: ${d.outcome} · +${d.points}`,list);
    }
  }
}
document.querySelector('#reset').onclick=()=>{
  screen.replaceChildren();el('h2','Discard this match?',screen);el('p','Only this generated app’s saved match will be erased.',screen);
  button('Confirm reset',screen,()=>serializedWrite(()=>{localStorage.removeItem(key);persistedRaw=null;events=[];blocked=false;warning.textContent='';render();},true),'confirm-reset');
  button('Keep match',screen,render);
};
render();
