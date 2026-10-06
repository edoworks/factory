import test from 'node:test';
import assert from 'node:assert/strict';
import {spec, fingerprint} from './spec.mjs';
import {replay, scores, encode, decode} from './engine.mjs';
const start = () => [{type:'start',players:['Alex','Sam']}];
const q = id => spec.questions.find(q=>q.id===id);
const picks = stage => Object.fromEntries(stage.questions.map(id=>[id,q(id).options[0].id]));
function complete(mode='correct') {
  const events=start();
  for(const stage of spec.stages) {
    if(stage.kind==='lock') for(let player=0;player<2;player++) events.push({type:'lock',player,picks:mode==='skip'?Object.fromEntries(stage.questions.map(id=>[id,'skip'])):picks(stage),boost:stage.boost&&mode!=='skip'?stage.questions[0]:null});
    else events.push({type:'confirm',outcomes:mode==='void'?Object.fromEntries(stage.questions.map(id=>[id,'void'])):picks(stage)});
  }
  return events;
}
test('all correct calls and one boost per eligible stage score from the spec; ties share rank',()=>{
  const state=replay(complete());
  const expected=spec.questions.reduce((sum,q)=>sum+q.points,0)+spec.stages.filter(s=>s.boost).reduce((sum,s)=>sum+q(s.questions[0]).points,0);
  assert.deepEqual(scores(state).map(r=>[r.points,r.rank]),[[expected,1],[expected,1]]);
  assert.equal(state.stage,spec.stages.length);
});
test('explicit skips and voids produce zero',()=>{
  for(const mode of ['skip','void']) assert.ok(scores(replay(complete(mode))).every(r=>r.points===0));
});
test('misses earn zero even when boosted',()=>{
  const events=complete();
  for(const event of events) if(event.type==='confirm') for(const id of Object.keys(event.outcomes)) event.outcomes[id]=q(id).options[1].id;
  assert.ok(scores(replay(events)).every(r=>r.points===0));
});
test('host cannot confirm before every card is locked',()=>{
  const events=start(),stage=spec.stages[0];
  assert.throws(()=>replay([...events,{type:'confirm',outcomes:picks(stage)}]));
  events.push({type:'lock',player:0,picks:picks(stage),boost:null});
  assert.throws(()=>replay([...events,{type:'confirm',outcomes:picks(stage)}]));
});
test('locks are immutable and cannot omit picks or forge a player',()=>{
  const stage=spec.stages[0],event={type:'lock',player:0,picks:picks(stage),boost:null};
  assert.throws(()=>replay([...start(),event,event]));
  assert.throws(()=>replay([...start(),{...event,picks:{}}]));
  assert.throws(()=>replay([...start(),{...event,player:20}]));
  assert.throws(()=>replay([...start(),{...event,picks:{...event.picks,[stage.questions[0]]:'invalid'}}]));
});
test('skips cannot be boosted and non-boost phases reject boosts',()=>{
  const stage=spec.stages[0];
  assert.throws(()=>replay([...start(),{type:'lock',player:0,picks:{...picks(stage),[stage.questions[0]]:'skip'},boost:stage.questions[0]}]));
  const all=complete(),index=all.findIndex(e=>e.type==='lock'&&Object.keys(e.picks).some(id=>spec.stages.some(s=>!s.boost&&s.kind==='lock'&&s.questions.includes(id))));
  if(index!==-1) {all[index].boost=Object.keys(all[index].picks)[0];assert.throws(()=>replay(all));}
});
test('unrevealed calls do not appear in score details',()=>{
  const events=complete(),first=events.findIndex(e=>e.type==='confirm');
  const state=replay(events.slice(0,first+1));
  const visible=Object.keys(events[first].outcomes).length;
  assert.equal(scores(state)[0].details.length,visible);
});
test('reload round-trips while malformed, altered, incompatible saves fail closed',()=>{
  const events=complete();assert.deepEqual(decode(encode(events)),events);
  assert.throws(()=>decode('{broken'));
  assert.throws(()=>decode(JSON.stringify({schema:1,fingerprint:'other',events})));
  assert.throws(()=>decode(JSON.stringify({schema:1,fingerprint,events:[...events,{type:'confirm',outcomes:{}}]})));
  assert.throws(()=>decode(JSON.stringify({schema:1,fingerprint,events,untrusted:true})));
});
test('event replay does not mutate its inputs or retain their references',()=>{
  const events=complete(),before=structuredClone(events),state=replay(events);
  assert.deepEqual(events,before);events[0].players[0]='Poison';assert.equal(state.players[0],'Alex');
  state.picks[0].anything='changed';assert.equal(events[1].picks.anything,undefined);
});
test('malformed starts, duplicates and oversized logs reject',()=>{
  for(const players of [[],['One'],['Same','same'],['','Sam'],Array(7).fill('x')]) assert.throws(()=>replay([{type:'start',players}]));
  assert.throws(()=>replay(Array(101).fill({})));assert.throws(()=>replay([null]));
});
test('confirmed results cannot be amended',()=>{
  const all=complete();assert.throws(()=>replay([...all,{type:'confirm',outcomes:{}}]));
});
