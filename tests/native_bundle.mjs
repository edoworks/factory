// Executes the existing engine tests against the exact packed native engine.
// This DOM double verifies startup/order only; native UI tests qualify rendering.
import {readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';
const root = path.resolve(process.argv[2]);
const {spec, fingerprint} = await import(pathToFileURL(path.join(root, 'spec.mjs')));
const nodes = new Map();
function element() {
  return {textContent:'', children:[], setAttribute(name,value){this[name]=value; if(name==='id') nodes.set('#'+value,this);},
    append(child){this.children.push(child);}, replaceChildren(){this.children=[];}};
}
const document = {title:'', createElement:element, querySelector(selector){if(!nodes.has(selector)) nodes.set(selector,element());return nodes.get(selector);}};
const bundle = await readFile(path.join(root,'native-app.js'),'utf8');
const engine = new Function('document','localStorage','return '+bundle)(document,{getItem(){return null;}});
assert.equal(document.title,spec.title,'App ran before spec or engine initialization');
assert.ok(nodes.has('#players'),'App startup did not create setup');
assert.equal(globalThis.specModule,undefined,'Module bindings leaked globally');
const imports = "import test from 'node:test';\nimport assert from 'node:assert/strict';\nimport {spec, fingerprint} from './spec.mjs';\nimport {replay, scores, encode, decode} from './engine.mjs';\n";
const suite = await readFile(path.join(root,'engine.test.mjs'),'utf8');
assert.ok(suite.startsWith(imports),'Engine test import contract changed');
new Function('test','assert','spec','fingerprint','replay','scores','encode','decode',suite.slice(imports.length))(
  test,assert,spec,fingerprint,engine.replay,engine.scores,engine.encode,engine.decode);
