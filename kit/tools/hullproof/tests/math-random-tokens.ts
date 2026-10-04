// ruleid: hullproof-math-random-token
const resetToken = Math.random().toString(36).slice(2);

// ruleid: hullproof-math-random-token
function makeInviteCode() {
  return Math.random().toString(36).slice(2, 10);
}

// ok: hullproof-math-random-token
const jitterMs = Math.random() * 200;

// ok: hullproof-math-random-token
const token = crypto.randomUUID();

// ok: hullproof-math-random-token
function pickColor() {
  return colors[Math.floor(Math.random() * colors.length)];
}
