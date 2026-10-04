import vm from 'node:vm';
import _ from 'lodash';
import { evaluate } from 'mathjs';
import Handlebars from 'handlebars';
declare const input: string; declare const body: any; declare const name: string;

// ruleid: hullproof-eval-or-new-function
eval(userInput);

// ruleid: hullproof-eval-or-new-function
const fn = new Function("a", body);

// ruleid: hullproof-eval-or-new-function
setTimeout("doThing(" + x + ")", 100);

// ruleid: hullproof-eval-or-new-function
(0, eval)(input);

// ruleid: hullproof-eval-or-new-function
globalThis.eval(input);

// ruleid: hullproof-eval-or-new-function
new vm.Script(input).runInThisContext();

// ruleid: hullproof-eval-or-new-function
vm.compileFunction(input);

// ruleid: hullproof-eval-or-new-function
vm.runInContext(input, ctx);

// ruleid: hullproof-eval-or-new-function
Function(input)();

// ruleid: hullproof-eval-or-new-function
setTimeout(input as any, 0);

// ruleid: hullproof-eval-or-new-function
setTimeout(`run(${name})`, 0);

// ruleid: hullproof-eval-or-new-function
Reflect.construct(Function, [input]);

// ok: hullproof-eval-or-new-function
setTimeout(() => doThing(x), 100);

// ok: hullproof-eval-or-new-function
const parsed = JSON.parse(text);

// ok: hullproof-eval-or-new-function
eval("1 + 1");

// ok: hullproof-eval-or-new-function
const adder = new Function("a", "b", "return a + b");

// ok: hullproof-eval-or-new-function
setTimeout(tick, 100);

// ruleid: hullproof-eval-through-alias
const indirect = eval;
indirect(input);

function viaAlias() {
  // ruleid: hullproof-eval-through-alias
  const F = Function;
  return new F("return " + input)();
}

// ruleid: hullproof-eval-through-alias
(() => {}).constructor(input)();

// ok: hullproof-eval-through-alias
const notAlias = JSON.parse;

// ruleid: hullproof-expression-library-eval
_.template(input)({});

// ruleid: hullproof-expression-library-eval
Handlebars.compile(input);

// ruleid: hullproof-expression-library-eval
evaluate(input);

// ruleid: hullproof-expression-library-eval
math.evaluate(body.expr);

// ok: hullproof-expression-library-eval
_.template("Hello <%= name %>")({ name });

// ok: hullproof-expression-library-eval
Handlebars.compile("Hello {{name}}");

// ruleid: hullproof-dynamic-module-path
require(input);

// ruleid: hullproof-dynamic-module-path
import(input);

// ruleid: hullproof-dynamic-module-path
const plugin = require("./plugins/" + name);

// ok: hullproof-dynamic-module-path
require("node:fs");

// ok: hullproof-dynamic-module-path
import("./heavy-chart");

// ok: hullproof-dynamic-module-path
import(`./locales/${name}.json`);

// ok: hullproof-dynamic-module-path
require.resolve(name);

// ruleid: hullproof-eval-or-new-function
Function.prototype.constructor("return process")();
