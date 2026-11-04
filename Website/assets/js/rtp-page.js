/* RTP page (rtp-<id>.html): how one game's RTP is calculated, for operators, aggregators and test labs. The odds and the
   ladders are worked out here from the game's entry in data.js, the same way its game.js works them out. FIGURES holds what
   can't be: the return over every bet from $0.10 to $200, cent by cent, and 1,000,000 simulated rounds per cell, from a run
   of each game's own code (2026-11-04); they change only when a game's maths does. */
(() => {
'use strict';
const { $, esc, ICON, SITE, GAMES } = window.Brainer;
const main = $('#main');
const g = GAMES.find(x => x.id === document.body.dataset.game);

/* FIGURES:start */
const FIGURES = { 'space-crash': { rounds: 1000000, levels: [ { name: 'Easy', whole: 0.9648, from1: [ 0.958559, 0.97 ], allBets: [ 0.898182, 0.97 ], cap: { '10': null, '200': null }, measured: [ { after: 1, exact: 0.9696, rtp: 0.969552, se: 0.000197919 }, { after: 3, exact: 0.968, rtp: 0.968323, se: 0.000357458 }, { after: 5, exact: 0.968, rtp: 0.968011, se: 0.000484 } ] }, { name: 'Medium', whole: 0.9625, from1: [ 0.956893, 0.97 ], allBets: [ 0.91, 0.97 ], cap: { '10': { at: 22, reached: 0.000434783, ret: 0.434783 }, '200': { at: 18, reached: 0.0152174, ret: 0.76087 } }, measured: [ { after: 1, exact: 0.968, rtp: 0.967993, se: 0.000357458 }, { after: 3, exact: 0.964174, rtp: 0.964817, se: 0.000677332 }, { after: 5, exact: 0.966522, rtp: 0.967026, se: 0.000974963 } ] }, { name: 'Hard', whole: 0.966522, from1: [ 0.961345, 0.97 ], allBets: [ 0.914286, 0.97 ], cap: { '10': { at: 18, reached: 0.000395257, ret: 0.395257 }, '200': { at: 13, reached: 0.0149068, ret: 0.745342 } }, measured: [ { after: 1, exact: 0.968, rtp: 0.967883, se: 0.000484 }, { after: 3, exact: 0.966522, rtp: 0.966586, se: 0.000974963 }, { after: 5, exact: 0.968818, rtp: 0.970735, se: 0.00150926 } ] }, { name: 'Hardcore', whole: 0.966, from1: [ 0.961017, 0.969997 ], allBets: [ 0.923077, 0.97 ], cap: { '10': { at: 10, reached: 0.000918697, ret: 0.918697 }, '200': { at: 7, reached: 0.0133867, ret: 0.669336 } }, measured: [ { after: 1, exact: 0.966, rtp: 0.96632, se: 0.000788736 }, { after: 3, exact: 0.969348, rtp: 0.968593, se: 0.00195197 }, { after: 5, exact: 0.969913, rtp: 0.973092, se: 0.0039627 } ] } ] }, 'multi-charge': { rounds: 1000000, levels: [ { name: 'Easy', whole: 0.9648, from1: [ 0.958559, 0.97 ], allBets: [ 0.898182, 0.97 ], cap: { '10': null, '200': null }, measured: [ { after: 1, exact: 0.9696, rtp: 0.969615, se: 0.000197919 }, { after: 3, exact: 0.968, rtp: 0.968218, se: 0.000357458 }, { after: 5, exact: 0.968, rtp: 0.967983, se: 0.000484 } ] }, { name: 'Medium', whole: 0.9625, from1: [ 0.956893, 0.97 ], allBets: [ 0.91, 0.97 ], cap: { '10': { at: 22, reached: 0.000434783, ret: 0.434783 }, '200': { at: 18, reached: 0.0152174, ret: 0.76087 } }, measured: [ { after: 1, exact: 0.968, rtp: 0.968033, se: 0.000357458 }, { after: 3, exact: 0.964174, rtp: 0.964178, se: 0.000677332 }, { after: 5, exact: 0.966522, rtp: 0.966133, se: 0.000974963 } ] }, { name: 'Hard', whole: 0.966522, from1: [ 0.961345, 0.97 ], allBets: [ 0.914286, 0.97 ], cap: { '10': { at: 18, reached: 0.000395257, ret: 0.395257 }, '200': { at: 13, reached: 0.0149068, ret: 0.745342 } }, measured: [ { after: 1, exact: 0.968, rtp: 0.967414, se: 0.000484 }, { after: 3, exact: 0.966522, rtp: 0.964193, se: 0.000974963 }, { after: 5, exact: 0.968818, rtp: 0.966024, se: 0.00150926 } ] }, { name: 'Hardcore', whole: 0.966, from1: [ 0.961017, 0.969997 ], allBets: [ 0.923077, 0.97 ], cap: { '10': { at: 10, reached: 0.000918697, ret: 0.918697 }, '200': { at: 7, reached: 0.0133867, ret: 0.669336 } }, measured: [ { after: 1, exact: 0.966, rtp: 0.966156, se: 0.000788736 }, { after: 3, exact: 0.969348, rtp: 0.971361, se: 0.00195197 }, { after: 5, exact: 0.969913, rtp: 0.973933, se: 0.0039627 } ] } ] }, 'plane-crash': { rounds: 1000000, levels: [ { name: 'Easy', whole: 0.9648, from1: [ 0.958559, 0.97 ], allBets: [ 0.898182, 0.97 ], cap: { '10': null, '200': null }, measured: [ { after: 1, exact: 0.9696, rtp: 0.96935, se: 0.000197919 }, { after: 3, exact: 0.968, rtp: 0.968107, se: 0.000357458 }, { after: 5, exact: 0.968, rtp: 0.967695, se: 0.000484 } ] }, { name: 'Medium', whole: 0.9625, from1: [ 0.956893, 0.97 ], allBets: [ 0.91, 0.97 ], cap: { '10': { at: 22, reached: 0.000434783, ret: 0.434783 }, '200': { at: 18, reached: 0.0152174, ret: 0.76087 } }, measured: [ { after: 1, exact: 0.968, rtp: 0.967658, se: 0.000357458 }, { after: 3, exact: 0.964174, rtp: 0.963089, se: 0.000677332 }, { after: 5, exact: 0.966522, rtp: 0.964819, se: 0.000974963 } ] }, { name: 'Hard', whole: 0.966522, from1: [ 0.961345, 0.97 ], allBets: [ 0.914286, 0.97 ], cap: { '10': { at: 18, reached: 0.000395257, ret: 0.395257 }, '200': { at: 13, reached: 0.0149068, ret: 0.745342 } }, measured: [ { after: 1, exact: 0.968, rtp: 0.96754, se: 0.000484 }, { after: 3, exact: 0.966522, rtp: 0.965254, se: 0.000974963 }, { after: 5, exact: 0.968818, rtp: 0.965217, se: 0.00150926 } ] }, { name: 'Hardcore', whole: 0.966, from1: [ 0.961017, 0.969997 ], allBets: [ 0.923077, 0.97 ], cap: { '10': { at: 10, reached: 0.000918697, ret: 0.918697 }, '200': { at: 7, reached: 0.0133867, ret: 0.669336 } }, measured: [ { after: 1, exact: 0.966, rtp: 0.967831, se: 0.000788736 }, { after: 3, exact: 0.969348, rtp: 0.970082, se: 0.00195197 }, { after: 5, exact: 0.969913, rtp: 0.968064, se: 0.0039627 } ] } ] }, charge: { rounds: 1000000, levels: [ { name: 'Easy', whole: 0.9648, from1: [ 0.958559, 0.97 ], allBets: [ 0.898182, 0.97 ], cap: { '10': null, '200': null }, measured: [ { after: 1, exact: 0.9696, rtp: 0.969534, se: 0.000197919 }, { after: 3, exact: 0.968, rtp: 0.968059, se: 0.000357458 }, { after: 5, exact: 0.968, rtp: 0.967523, se: 0.000484 } ] }, { name: 'Medium', whole: 0.9625, from1: [ 0.956893, 0.97 ], allBets: [ 0.91, 0.97 ], cap: { '10': { at: 22, reached: 0.000434783, ret: 0.434783 }, '200': { at: 18, reached: 0.0152174, ret: 0.76087 } }, measured: [ { after: 1, exact: 0.968, rtp: 0.968078, se: 0.000357458 }, { after: 3, exact: 0.964174, rtp: 0.964064, se: 0.000677332 }, { after: 5, exact: 0.966522, rtp: 0.965757, se: 0.000974963 } ] }, { name: 'Hard', whole: 0.966522, from1: [ 0.961345, 0.97 ], allBets: [ 0.914286, 0.97 ], cap: { '10': { at: 18, reached: 0.000395257, ret: 0.395257 }, '200': { at: 13, reached: 0.0149068, ret: 0.745342 } }, measured: [ { after: 1, exact: 0.968, rtp: 0.967877, se: 0.000484 }, { after: 3, exact: 0.966522, rtp: 0.966326, se: 0.000974963 }, { after: 5, exact: 0.968818, rtp: 0.968504, se: 0.00150926 } ] }, { name: 'Hardcore', whole: 0.966, from1: [ 0.961017, 0.969997 ], allBets: [ 0.923077, 0.97 ], cap: { '10': { at: 10, reached: 0.000918697, ret: 0.918697 }, '200': { at: 7, reached: 0.0133867, ret: 0.669336 } }, measured: [ { after: 1, exact: 0.966, rtp: 0.965955, se: 0.000788736 }, { after: 3, exact: 0.969348, rtp: 0.968838, se: 0.00195197 }, { after: 5, exact: 0.969913, rtp: 0.965164, se: 0.0039627 } ] } ] }, 'fly-high': { rounds: 1000000, from1: 0.962063, allBets: 0.889908, at10c: [ 0.889908, 0.97 ], atOnce: 0.039648, measured: [ { at: 1.5, chance: 0.646667, hit: 0.647217, exact: 0.97, rtp: 0.970826, se: 0.000717008 }, { at: 2, chance: 0.485, hit: 0.485003, exact: 0.97, rtp: 0.970006, se: 0.00099955 }, { at: 10, chance: 0.097, hit: 0.096983, exact: 0.97, rtp: 0.96983, se: 0.00295958 }, { at: 100, chance: 0.0097, hit: 0.009847, exact: 0.97, rtp: 0.9847, se: 0.00980097 } ] } };
/* FIGURES:end */

const F = g && FIGURES[g.id];
if (!g || !F) {
  main.innerHTML = `<div class="wrap"><div class="page-head"><span class="sticker red">404</span><h1>Page not found</h1><p class="lead">That game has no RTP page.</p><div class="ctas"><a class="btn btn-ink btn-lg" href="games.html">See our games</a></div></div></div>`;
  return;
}

const pct = (v, d = 2) => `${(100 * v).toFixed(d)}%`;
const chance = v => v >= 0.001 ? pct(v) : `${+(100 * v).toPrecision(3)}%`;   // tiny chances keep three figures, not 0.00%
const fx = m => m.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '×';
const money = v => '$' + v.toLocaleString('en-US', { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 });
const range = ([lo, hi]) => `${pct(lo)}–${pct(hi)}`;
const table = (head, rows) => `<div class="tbl"><table><thead><tr>${head.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${r.map((c, i) => `<td${i ? ' class="num"' : ''}>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
const crumbs = `<nav class="crumbs" aria-label="Breadcrumb"><a href="games.html">Games</a><span aria-hidden="true">/</span><a href="game-${g.id}.html">${esc(g.title)}</a><span aria-hidden="true">/</span><span aria-current="page">RTP</span></nav>`;
const head = lead => `<div class="wrap">${crumbs}<div class="page-head"><span class="sticker">RTP up to ${g.rtp}%</span><h1>How ${esc(g.title)}’s RTP is calculated</h1><p class="lead">${lead}</p></div></div>`;
// how far the measured returns sit from the exact ones, in standard errors of the simulation
const within = ms => `${Math.max(...ms.map(m => Math.abs(m.rtp - m.exact) / m.se)).toFixed(1)} standard errors`;
const status = max => `<p class="note">${ICON.info}<span>Not yet tested by a lab: these figures are indicative until a lab certifies the maths. The demo’s Max Mode Test switch ${max}, to show the Brainer’s whole journey; those rounds are marked in the fairness sheet and left out of every figure here. In the demo the game in your browser plays the server’s part; in production the server makes the rolls. ${esc(SITE.legal)}</span></p>`;
const checkLinks = `<div class="ctas" style="margin-top:4px"><a class="btn btn-sun" href="fairness.html">How the check works</a><a class="btn" href="game-${g.id}.html">Play the demo</a></div>`;

// The words each step game uses. Message = the roll's message, as the game's fairness sheet and fairness.html name it.
const KIND = {
  'plane-crash': { step: 'step', steps: 'steps', Step: 'Step', pick: 'path', picks: 'paths', one: 'bomb', bad: 'bombs', Bad: 'Bombs', look: 'look bombed', msg: 'step' },
  'space-crash': { step: 'row', steps: 'rows', Step: 'Row', pick: 'drone', picks: 'drones', one: 'shield that holds', bad: 'shields that hold', Bad: 'Holding shields', look: 'turn red', msg: 'row' },
  'multi-charge': { step: 'charge', steps: 'charges', Step: 'Charge', pick: 'pillar', picks: 'pillars', one: 'overload', bad: 'overloads', Bad: 'Overloads', look: 'look overloaded', msg: 'charge' },
  charge: { step: 'charge', steps: 'charges', Step: 'Charge', pick: '', one: 'overload', bad: 'overloads', Bad: 'Overloads', msg: 'charge' }
};

// A step game's ladder, as game.js builds it: 25 slots hide b bad ones, so step n is safe with (25 − b − n + 1) ÷ (25 − n + 1),
// and after n safe steps the multiplier is the RTP divided by the chance of getting there, rounded down to the cent.
const ladderOf = l => { let cum = 1; return Array.from({ length: 25 - l.bombs }, (_, i) => { const s = (25 - l.bombs - i) / (25 - i); cum *= s; return { n: i + 1, s, cum, m: Math.floor(g.rtp / 100 / cum * 100 + 1e-7) / 100 }; }); };

function stepPage(k) {
  const L = g.levels.map(l => ({ l, rungs: ladderOf(l), f: F.levels.find(x => x.name === l.name) }));
  const pickBullets = k.pick ? `<ul class="rtp-points">
      <li><b>Every ${k.pick} is equally safe.</b> The ${k.pick} picked only shows the answer: on the same seeds, all five give the same result.</li>
      <li><b>The other four ${k.picks} are for show.</b> After each ${k.step}, one to three of them ${k.look} at random and the rest look safe, on a win and a loss alike. They come from separate rolls and never touch a result or a payout.</li>
      <li><b>No pattern or strategy changes the odds.</b> The player’s only real decision is when to cash out, and every cash-out point is priced at ${g.rtp}%.</li>
    </ul>` : '';
  const ladders = L.map(({ l, rungs }) => {
    const reach = rungs.findIndex(r => g.minBet * r.m >= g.maxWin) + 1;   // the first rung the max win ends a round on, even at the minimum bet
    return `<details${l.name === 'Medium' ? ' open' : ''}><summary>${esc(l.name)}: ${rungs.length} ${k.steps}, ${l.bombs} ${l.bombs === 1 ? k.one : k.bad} in 25</summary>
      ${table([k.Step, 'Safe chance', 'Chance to get here', 'Multiplier', 'Return'], rungs.map(r => [String(r.n), pct(r.s, 1), chance(r.cum), fx(r.m), pct(r.cum * r.m)]))}
      ${reach && reach < rungs.length ? `<p>The $${g.maxWin.toLocaleString('en-US')} max win ends every round by ${k.step} ${reach}, even at the $${g.minBet.toFixed(2)} minimum bet, so ${k.step}${rungs.length - reach > 1 ? `s ${reach + 1} to ${rungs.length} are` : ` ${rungs.length} is`} never offered.</p>` : ''}
    </details>`;
  }).join('');
  const capCell = (f, rungs, bet) => { const c = f.cap[bet]; return c ? `${k.Step} ${c.at}, in ${chance(c.reached)} of rounds` : `Never: the top pays ${money(Math.min(g.maxWin, Math.floor(bet * rungs.at(-1).m * 100) / 100))}`; };
  const caps200 = L.map(x => x.f.cap[200]).filter(Boolean).map(c => c.ret);
  const measured = L.flatMap(x => x.f.measured);
  return `${head(`Every player gets up to ${g.rtp}%. Each ${k.step} is one provably fair roll, and every point where a player can cash out is priced at ${g.rtp}% of its chance${k.pick ? `. The ${k.pick} the player picks never changes the odds` : ''}.`)}
  <div class="wrap"><div class="prose">
    <section id="roll"><h2>One roll decides each ${k.step}</h2>
      ${k.pick
        ? `<p>${esc(g.title)} draws one roll for each ${k.step} before the player picks: HMAC-SHA256(server seed, "client seed:nonce:${k.msg}"), read as a number from 0 to 1. A roll below that ${k.step}’s safe chance is a yes, and at or above it a no.</p>${pickBullets}`
        : `<p>Each charge is one roll of HMAC-SHA256(server seed, "client seed:nonce:charge"), read as a number from 0 to 1 and drawn before the round starts. A roll below that charge’s safe chance is a yes and the Brainer levels up; at or above it, the charge overloads and the bet is lost. The player’s only decision is when to cash out, and every cash-out point is priced at ${g.rtp}%.</p>`}
    </section>
    <section id="odds"><h2>The odds of each ${k.step}</h2>
      <p>A round has up to 25 ${k.steps} with 1, 3, 5 or 10 ${k.bad} among them, set by the difficulty. Each safe ${k.step} uses up one safe slot, so every next ${k.step} is a little riskier. With n the ${k.step} number and b the ${k.bad}:</p>
      <p class="formula">s<sub>n</sub> = (26 − n − b) ÷ (26 − n)<br>P<sub>n</sub> = s<sub>1</sub> × s<sub>2</sub> × … × s<sub>n</sub> = C(25 − n, b) ÷ C(25, b)</p>
      <p>s<sub>n</sub> is the chance that ${k.step} n is safe, P<sub>n</sub> the chance of getting through the first n ${k.steps}, and C(a, b) the number of ways to choose b of a.</p>
      ${table(['Difficulty', `${k.Bad} in 25`, k.Step === 'Step' ? 'Steps' : `${k.Step}s`, `${k.Step} 1 safe`, `Survive 5 ${k.steps}`, 'Top multiplier'], L.map(({ l, rungs }) => [esc(l.name), String(l.bombs), String(rungs.length), pct(rungs[0].s, 1), pct(rungs[4].cum), fx(rungs.at(-1).m)]))}
    </section>
    <section id="price"><h2>Every cash-out point is priced at ${g.rtp}%</h2>
      <p>After n safe ${k.steps}, the multiplier is ${g.rtp}% divided by the chance of getting there, rounded down to the cent. Cashing out there returns P<sub>n</sub> × M<sub>n</sub>, which is at most ${g.rtp}%:</p>
      <p class="formula">M<sub>n</sub> = ⌊${g.rtp} ÷ P<sub>n</sub>⌋ ÷ 100<br>return of cashing out after n = P<sub>n</sub> × M<sub>n</sub> ≤ ${(g.rtp / 100).toFixed(2)}</p>
      <p>The only thing a round tells the player is that the ${k.steps} so far were safe. So any way of playing, whether a fixed number of ${k.steps}, a random stop or a hunch, comes down to a choice of cash-out point, and a mix of points that each return at most ${g.rtp}% returns at most ${g.rtp}% too.</p>
      <p>The full ladder of each difficulty, before the max win and the payout’s rounding:</p>
      <div class="rules">${ladders}</div>
    </section>
    <section id="lower"><h2>What lowers the return below ${g.rtp}%</h2>
      <p>The RTP is “up to ${g.rtp}%” because two rules take a little off, always in the house’s favour:</p>
      <ul class="rtp-points">
        <li><b>Rounding down to the cent.</b> Both the multiplier and the payout round down, and a cent is a bigger share of a small payout. Returns at every cash-out point below the max win, over every bet in the range, cent by cent:</li>
      </ul>
      ${table(['Difficulty', 'Whole-dollar bets', 'Any bet from $1', 'Any bet from $0.10'], L.map(({ l, f }) => [esc(l.name), `${pct(f.whole)}–${pct(f.from1[1])}`, range(f.from1), range(f.allBets)]))}
      <ul class="rtp-points">
        <li><b>The $${g.maxWin.toLocaleString('en-US')} max win.</b> A round whose bet × multiplier reaches $${g.maxWin.toLocaleString('en-US')} pays $${g.maxWin.toLocaleString('en-US')} and ends there. Only deep ${k.steps} at big bets get that far. Where it starts:</li>
      </ul>
      ${table(['Difficulty', 'At a $10 bet', 'At a $200 bet'], L.map(({ l, rungs, f }) => [esc(l.name), capCell(f, rungs, 10), capCell(f, rungs, 200)]))}
      <p>A player who stops before the max win gets the returns in the first table. Only a player who always plays on to the max win gets less: at a $200 bet, that point returns ${pct(Math.min(...caps200))}–${pct(Math.max(...caps200))}.</p>
    </section>
    <section id="measured"><h2>Measured with the game’s own roll</h2>
      <p>Each cell is ${F.rounds.toLocaleString('en-US')} simulated rounds at a $1 bet, using the same roll as the game (checked identical to its code). The exact value from the formulas is in brackets.</p>
      ${table(['Difficulty', `Cash out after 1 ${k.step}`, 'After 3', 'After 5'], L.map(({ l, f }) => [esc(l.name), ...f.measured.map(m => `${pct(m.rtp)} (${pct(m.exact)})`)]))}
      <p>Every measured value is within ${within(measured)} of the exact one. The margin of error is widest on Hardcore, where wins are rarer and larger.</p>
    </section>
    <section id="check"><h2>How to check a round</h2>
      <ol class="list">
        <li>Before the round, the game shows the SHA-256 hash of its server seed, and the player can set their own client seed.</li>
        <li>${k.Step} n’s answer is HMAC-SHA256(server seed, "client seed:nonce:n"): its first 52 bits divided by 2<sup>52</sup> give the roll, compared with s<sub>n</sub>.</li>
        ${k.pick ? `<li>The show on the other ${k.picks} comes from "client seed:nonce:n:show:0" (how many, one to three) and "client seed:nonce:n:show:1" to "show:5" (which ones).</li>` : ''}
        <li>When the round ends, the server seed is revealed. The game’s fairness sheet re-hashes it and recomputes every ${k.step}.</li>
      </ol>
      ${checkLinks}
    </section>
    ${status(`makes every ${k.step} safe`)}
  </div></div>`;
}

function crashPage() {
  const xs = [1.01, 1.5, 2, 5, 10, 100, 1000, g.maxMult || 10000];
  return `${head(`Every player gets up to ${g.rtp}%. Each round is one provably fair roll that sets where the Brainer flies away, and every multiplier a player can cash out at is priced at ${g.rtp}% of its chance.`)}
  <div class="wrap"><div class="prose">
    <section id="roll"><h2>One roll decides where the round flies away</h2>
      <p>Each round is one roll u of HMAC-SHA256(server seed, "client seed:nonce"), read as a number from 0 to 1 and drawn before take-off. The round flies away at:</p>
      <p class="formula">point = ⌊${g.rtp} ÷ (1 − u)⌋ ÷ 100<br>kept between 1.00× and 10,000×</p>
      <p>About ${pct(1 - g.rtp / 100 / 1.01)} of rounds fly away at 1.00×, before anyone can cash out (measured: ${pct(F.atOnce)}).</p>
    </section>
    <section id="price"><h2>Every cash-out point is priced at ${g.rtp}%</h2>
      <p>A round reaches a multiplier x or more with this chance, so cashing out at x returns x times it:</p>
      <p class="formula">P(point ≥ x) = ${(g.rtp / 100).toFixed(2)} ÷ x<br>return of cashing out at x = x × ${(g.rtp / 100).toFixed(2)} ÷ x = ${(g.rtp / 100).toFixed(2)}</p>
      ${table(['Cash out at', 'Chance the round gets there', 'Return'], xs.map(x => [fx(x), chance(g.rtp / 100 / x), pct(g.rtp / 100)]))}
      <p>Cashing out by hand works the same as auto cash-out: whatever multiplier a bet is cashed at, the chance the round got there is ${(g.rtp / 100).toFixed(2)} ÷ that multiplier. Each of the two bets in a round is priced on its own, so playing two changes nothing.</p>
    </section>
    <section id="lower"><h2>What lowers the return below ${g.rtp}%</h2>
      <p>The RTP is “up to ${g.rtp}%” because the payout rounds down to the cent, always in the house’s favour:</p>
      <ul class="rtp-points">
        <li><b>Whole-dollar bets lose nothing:</b> bet × multiplier is already whole cents, so every cash-out point returns ${pct(g.rtp / 100)}.</li>
        <li><b>Any bet from $1</b> returns ${pct(F.from1)}–${pct(g.rtp / 100)}, and <b>the $${g.minBet.toFixed(2)} minimum bet</b> ${range(F.at10c)}, since a cent is a bigger share of a small payout.</li>
        <li><b>The $${g.maxWin.toLocaleString('en-US')} max win per bet</b> cashes a bet out by itself when it gets there, at ${fx(g.maxWin / 200)} on a $200 bet. That point is priced like any other, so it returns up to ${g.rtp}% too.</li>
      </ul>
    </section>
    <section id="measured"><h2>Measured with the game’s own roll</h2>
      <p>${F.rounds.toLocaleString('en-US')} simulated rounds with the same roll as the game (checked identical to its code), each read at four auto cash-out points:</p>
      ${table(['Cash out at', 'Chance (exact)', 'Rounds that got there', 'Return (exact ' + pct(g.rtp / 100) + ')'], F.measured.map(m => [fx(m.at), chance(m.chance), chance(m.hit), pct(m.rtp)]))}
      <p>Every measured return is within ${within(F.measured)} of the exact one; the margin of error grows with the multiplier, as wins get rarer and larger.</p>
    </section>
    <section id="check"><h2>How to check a round</h2>
      <ol class="list">
        <li>Before the round, the game shows the SHA-256 hash of its server seed, and the player can set their own client seed.</li>
        <li>The round’s roll is HMAC-SHA256(server seed, "client seed:nonce"): its first 52 bits divided by 2<sup>52</sup> give u, and the formula above gives the fly-away point.</li>
        <li>When the round ends, the server seed is revealed. The game re-hashes it and recomputes the point. The nonce counts every round, with or without a bet.</li>
      </ol>
      ${checkLinks}
    </section>
    ${status('flies every round to 10,000×')}
  </div></div>`;
}

main.innerHTML = KIND[g.id] ? stepPage(KIND[g.id]) : crashPage();
})();
