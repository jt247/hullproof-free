import Handlebars from 'handlebars';
declare const html: string; declare const nunjucks: any; declare const env: any;

// ruleid: hullproof-template-engine-escape-off
const marked = new Handlebars.SafeString(html);

// ruleid: hullproof-template-engine-escape-off
const tpl = Handlebars.compile(html, { noEscape: true });

// ruleid: hullproof-template-engine-escape-off
nunjucks.configure("views", { autoescape: false });

// ok: hullproof-template-engine-escape-off
const fixed = new Handlebars.SafeString("<b>ok</b>");

// ok: hullproof-template-engine-escape-off
nunjucks.configure("views", { autoescape: true });
