// Laundry queue bot — WhatsApp Cloud API + status API for the ESP32 tags.
import express from 'express';
import crypto from 'node:crypto';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const {
  WA_TOKEN, WA_PHONE_NUMBER_ID, WA_VERIFY_TOKEN, WA_APP_SECRET,
  WA_ALERT_TEMPLATE = '', WA_TEMPLATE_LANG = 'en',
  BOT_NUMBER = '', TAG_KEY = '', ADMIN_KEY = '', HISTORY_DAYS = 365, TIMEZONE = 'Asia/Singapore', PORT = 3000,
} = process.env;
const DEV = process.env.DEV === '1';
const GRAPH = 'https://graph.facebook.com/v21.0';

/* ------------------------------------------------------------------ */
/* Config                                                              */
/* ------------------------------------------------------------------ */
const MACHINES = {
  W1: { label: 'Washer', minutes: 30 },
  D1: { label: 'Dryer',  minutes: 30 },
};
const RESERVE_MIN = 10;   // how long the next person has to scan
const COLLECT_MIN = 20;   // after "done", auto-free the machine if nobody replies DONE
const REMIND_MIN = 10;    // second nudge to collect clothes, this long after "done"
const GRACE_SEC = 5;      // seconds a machine may shake before the alarm goes off (unless someone scanned)
const ALARM_MIN = 5;      // the tag beeps this long, then goes quiet (it stays red)
const SOON_MIN = 5;       // "your turn is coming up" heads-up this long before the expected time
const OFFER_MIN = 15;     // a queue offer from STATUS can be accepted with YES for this long
const HANDOVER_MIN = 5;   // rough time between loads (collect clothes, next person loads)
const COLORS = { free: '#16a34a', inuse: '#2563eb', done: '#f59e0b', next: '#9333ea', unclaimed: '#dc2626' };

/* ------------------------------------------------------------------ */
/* State (saved to data.json so a restart doesn't lose the queue)      */
/* ------------------------------------------------------------------ */
const DATA_FILE = new URL('./data.json', import.meta.url);
let clockOffset = 0;                          // dev-only time travel
const now = () => Date.now() + clockOffset;

const blank = () => ({ state: 'free', user: null, until: 0, queue: [] });
let db = Object.fromEntries(Object.keys(MACHINES).map(id => [id, blank()]));
try { db = { ...db, ...JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')) }; } catch {}
const save = () => fs.writeFileSync(DATA_FILE, JSON.stringify(db, null, 2));

/* ------------------------------------------------------------------ */
/* Usage records — who used which machine, when (for the manager)      */
/* One JSON object per line in history.jsonl; old lines are pruned.    */
/* ------------------------------------------------------------------ */
const HISTORY_FILE = new URL('./history.jsonl', import.meta.url);
let history = [];
function loadHistory() {
  try {
    const cutoff = Date.now() - Number(HISTORY_DAYS) * 86_400_000;
    const lines = fs.readFileSync(HISTORY_FILE, 'utf8').split('\n').filter(Boolean);
    history = lines.map(l => JSON.parse(l)).filter(r => (r.at || r.startedAt) >= cutoff);
    if (history.length !== lines.length) fs.writeFileSync(HISTORY_FILE, history.map(r => JSON.stringify(r)).join('\n') + (history.length ? '\n' : ''));
  } catch { history = []; }
}
loadHistory();
function record(rec) {
  history.push(rec);
  fs.appendFileSync(HISTORY_FILE, JSON.stringify(rec) + '\n');
}

/* ------------------------------------------------------------------ */
/* Sending messages                                                    */
/* ------------------------------------------------------------------ */
const devLog = [];   // every message the bot sent (dev mode), read by the tester page
let devSeq = 0;
async function send(to, text) {
  if (DEV || !WA_TOKEN) {
    devLog.push({ seq: ++devSeq, to, text, at: now() });
    if (devLog.length > 500) devLog.shift();
    console.log(`→ ${to}: ${text}`);
    return;
  }
  const res = await fetch(`${GRAPH}/${WA_PHONE_NUMBER_ID}/messages`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${WA_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ messaging_product: 'whatsapp', to, type: 'text', text: { body: text } }),
  });
  if (!res.ok) console.error('WhatsApp send failed', res.status, await res.text());
}

/* ------------------------------------------------------------------ */
/* Residents & house alerts                                            */
/* Everyone who has messaged the bot gets house alerts (MUTE to stop). */
/* WhatsApp only allows free text within 24 h of someone's last        */
/* message; outside that we need an approved template.                 */
/* ------------------------------------------------------------------ */
const PEOPLE_FILE = new URL('./residents.json', import.meta.url);
let residents = {};   // phone → { name, lastSeen, muted }
try { residents = JSON.parse(fs.readFileSync(PEOPLE_FILE, 'utf8')); } catch {}
const saveResidents = () => fs.writeFileSync(PEOPLE_FILE, JSON.stringify(residents, null, 2));
function touchResident(user) {
  residents[user.phone] = { ...residents[user.phone], name: user.name, lastSeen: Date.now() };
  saveResidents();
}
async function sendTemplate(to, text) {
  const res = await fetch(`${GRAPH}/${WA_PHONE_NUMBER_ID}/messages`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${WA_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ messaging_product: 'whatsapp', to, type: 'template', template: {
      name: WA_ALERT_TEMPLATE, language: { code: WA_TEMPLATE_LANG },
      components: [{ type: 'body', parameters: [{ type: 'text', text: text.replace(/\s*\n+\s*/g, ' ') }] }] } }),
  });
  if (!res.ok) console.error('WhatsApp template send failed', res.status, await res.text());
}
async function alertHouse(text, exceptPhone) {
  for (const [phone, r] of Object.entries(residents)) {
    if (phone === exceptPhone || r.muted) continue;
    if (DEV || !WA_TOKEN || Date.now() - r.lastSeen < 23.5 * 3_600_000) await send(phone, text);
    else if (WA_ALERT_TEMPLATE) await sendTemplate(phone, text);
    else console.warn(`Alert not sent to ${r.name}: outside WhatsApp's 24 h window and WA_ALERT_TEMPLATE is not set`);
  }
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */
const time = ms => new Date(ms).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: TIMEZONE });
const label = id => MACHINES[id].label;                     // what people see: "Washer" / "Dryer" (IDs stay internal)
const the = id => `the ${MACHINES[id].label.toLowerCase()}`;   // mid-sentence: "the washer"
const The = id => `The ${MACHINES[id].label.toLowerCase()}`;   // sentence start
const word = id => MACHINES[id].label.toUpperCase();        // command word: START WASHER, MINE DRYER…
const firstName = name => (name || 'there').trim().split(/\s+/)[0].slice(0, 12);
const qrLink = id => `https://wa.me/${BOT_NUMBER}?text=${encodeURIComponent('START ' + word(id))}`;

function findMachine(word) {
  if (!word) return null;
  const w = word.toUpperCase();
  if (MACHINES[w]) return w;
  return Object.keys(MACHINES).find(id => MACHINES[id].label.toUpperCase().startsWith(w)) || null;
}

/* ------------------------------------------------------------------ */
/* Queue logic                                                         */
/* ------------------------------------------------------------------ */
/* Loads: a wash and the dry that follows share one load ID, so a load can be followed washer → dryer.
   residents[phone].wetLoad = { load, at } is set when someone takes a washed load out. */
const LINK_HOURS = 3;
function takeWetLoad(phone) {
  const r = residents[phone], w = r?.wetLoad;
  if (!w || now() - w.at > LINK_HOURS * 3_600_000) return null;
  delete r.wetLoad; saveResidents();
  return w;
}

async function occupy(id, user, startedAt = now(), forgotScan = false) {
  const m = db[id];
  m.queue = m.queue.filter(u => u.phone !== user.phone);
  const { joinedAt, ...who } = user;
  Object.assign(m, { state: 'inuse', user: who, until: startedAt + MACHINES[id].minutes * 60_000, alarmUntil: 0 });
  const ref = crypto.randomUUID().slice(0, 8);
  const wet = id === 'D1' ? takeWetLoad(who.phone) : null;         // drying the load they just washed?
  m.session = { type: 'wash', ref, load: wet ? wet.load : ref, machine: id, name: who.name, phone: who.phone,
                queuedAt: joinedAt || null, startedAt, finishedAt: null, collectedAt: null, outcome: null, forgotScan };
  save();
  const linked = wet ? `\n🔗 Drying your load from the washer (washed at ${time(wet.washedAt)}).` : '';
  await send(user.phone, forgotScan
    ? `✅ Thanks for owning up, ${user.name}! ${The(id)} is yours — it started at ${time(startedAt)}.\nI'll remind you at ${time(m.until)}. Next time, scan the tag before you start 🙏`
    : `✅ ${The(id)} is yours, ${user.name}! Start it now.${linked}\nI'll remind you at ${time(m.until)}.\n\nReply DONE once you've collected your clothes.${m.leftover && m.leftover.phone !== user.phone ? leftoverNote(id) : ''}`);
}

/* The tag felt the machine running for GRACE_SEC with nobody scanned in */
async function goUnclaimed(id) {
  const m = db[id];
  m.savedFor = m.state === 'next' ? m.user : null;           // it was reserved for someone
  Object.assign(m, { state: 'unclaimed', user: null, since: m.vibeSince, until: 0, alarmUntil: now() + ALARM_MIN * 60_000 });
  save();
  const saved = m.savedFor ? `\n(It was saved for ${m.savedFor.name}.)` : '';
  await alertHouse(`🚨 House alert: the ${MACHINES[id].label.toLowerCase()} started at ${time(m.since)} but nobody scanned the tag.\nIf it's your load, reply MINE ${word(id)} to claim it.${saved}`);
}

/* Someone replied MINE (or scanned) for an unclaimed load */
async function claim(user, id) {
  const m = db[id], saved = m.savedFor;
  m.savedFor = null;
  await occupy(id, user, m.since || now(), true);
  if (saved && saved.phone !== user.phone) {                 // they jumped the queue: keep the saved person first
    m.queue.unshift({ ...saved, joinedAt: now() });
    m.session.note = `started while it was saved for ${saved.name}`;
    save();
    await send(saved.phone, `Heads up ${saved.name}: ${user.name} started ${the(id)} while it was saved for you. You're still #1 — I'll message you when it's free.`);
  }
  await alertHouse(`✅ Mystery solved — the ${MACHINES[id].label.toLowerCase()} is ${user.name}'s load. Thanks!`, user.phone);
}

/* The machine stopped and nobody ever claimed the load */
async function unclaimedEnded(id) {
  const m = db[id], saved = m.savedFor;
  record({ type: 'unclaimed', outcome: 'unclaimed', machine: id, name: 'Unknown', phone: '', startedAt: m.since, finishedAt: now(), at: m.since });
  m.savedFor = null;
  await alertHouse(`🧺 The ${MACHINES[id].label.toLowerCase()} has finished — nobody claimed that load. Whoever it belongs to, please collect your clothes!`);
  if (saved) {
    Object.assign(m, { state: 'next', user: saved, until: now() + RESERVE_MIN * 60_000, alarmUntil: 0 });
    await send(saved.phone, `🟣 ${The(id)} is free again and still saved for you until ${time(m.until)}.`);
  } else {
    Object.assign(m, { state: 'free', user: null, until: 0, alarmUntil: 0 });
  }
  save();
}

/* Vibration report from the tag's sensor (the tag debounces short pauses) */
async function vibration(id, running) {
  const m = db[id];
  if (running && !m.running) {
    m.running = true; m.vibeSince = now();
    setTimeout(() => tick().catch(console.error), GRACE_SEC * 1000 + 100);   // check right when the grace period ends
    if (m.state === 'done') await release(id, 'collected');   // someone emptied it and started a new load
  } else if (!running && m.running) {
    m.running = false; m.vibeSince = null;
    if (m.state === 'inuse') m.until = Math.min(m.until, now()); // it really finished → "done" message on this tick
    if (m.state === 'unclaimed') await unclaimedEnded(id);
  }
  save();
  await tick();
}

async function release(id, outcome = 'collected', extra = {}) {
  const m = db[id], prev = m.user;
  if (m.session) {
    const t = now();
    record({ ...m.session, finishedAt: m.session.finishedAt || t, collectedAt: t, outcome, ...extra });
    if (id === 'W1' && residents[m.session.phone]) {
      residents[m.session.phone].wetLoad = { load: m.session.load || m.session.ref, at: t, washedAt: m.session.startedAt };
      saveResidents();
    }
    m.session = null;
  }
  // auto-freed → the owner's clothes are probably still inside
  if (outcome === 'auto-freed' && prev) m.leftover = { name: prev.name, phone: prev.phone, since: now() };
  else if (outcome !== 'turn') m.leftover = null;
  const next = m.queue.shift();
  if (next) {
    Object.assign(m, { state: 'next', user: next, until: now() + RESERVE_MIN * 60_000 });
    await send(next.phone, `🟣 Your turn, ${next.name}! ${The(id)} is saved for you until ${time(m.until)}.\nScan the tag on the machine to start.${leftoverNote(id)}`);
  } else {
    Object.assign(m, blank(), { session: null, leftover: m.leftover || null });
  }
  save();
}

function whoText(id) {
  const m = db[id], verb = id === 'D1' ? 'drying' : 'washing';
  return {
    free:  '🟢 empty and free',
    inuse: `🔵 ${m.user?.name}'s clothes are ${verb} — done at ${time(m.until)}`,
    done:  `🟠 ${m.user?.name}'s clothes are done and still inside`,
    next:  `🟣 empty, saved for ${m.user?.name} until ${time(m.until)}`,
    unclaimed: `🔴 running since ${time(m.since)}, but nobody has claimed it`,
  }[m.state];
}
/* When can queue position `pos` (1 = first in line) expect to load their clothes? */
function etaFor(id, pos) {
  const m = db[id], cycle = (MACHINES[id].minutes + HANDOVER_MIN) * 60_000;
  const free = {
    inuse:     m.until + HANDOVER_MIN * 60_000,
    done:      now() + HANDOVER_MIN * 60_000,
    next:      now() + cycle,                                  // the saved person will use it first
    unclaimed: (m.since || now()) + cycle,
  }[m.state] ?? now();
  return Math.max(now(), free) + (pos - 1) * cycle;
}
const leftoverNote = id => db[id].leftover
  ? `\n\n⚠️ Heads up: ${db[id].leftover.name}'s clothes may still be inside. If they are, please move them to the basket and reply MOVED.` : '';
const leftoverText = id => db[id].leftover && db[id].state !== 'done' ? `\n   ⚠️ ${db[id].leftover.name}'s clothes may still be inside` : '';
const waitingText = id => db[id].queue.length ? `\n   🙋 Waiting: ${db[id].queue.map((u, i) => `${u.name} (~${time(etaFor(id, i + 1))})`).join(', ')}` : '';

async function handleStart(user, id) {
  const m = db[id];
  if (m.user?.phone === user.phone && m.state !== 'next')
    return send(user.phone, `You already have ${the(id)} (until ${time(m.until)}).`);
  if (m.state === 'unclaimed') return claim(user, id);
  if (m.state === 'free' || (m.state === 'next' && m.user.phone === user.phone))
    return occupy(id, user, m.running ? m.vibeSince : now());   // scanned just after pressing Start: count from the real start

  // busy → join the queue
  let pos = m.queue.findIndex(u => u.phone === user.phone) + 1;
  if (!pos) { m.queue.push({ ...user, joinedAt: now() }); pos = m.queue.length; save(); }
  const ahead = m.queue.slice(0, pos - 1).map(u => u.name);
  const line = ahead.length ? ` (after ${ahead.join(', ')})` : '';
  return send(user.phone, `${The(id)} is busy: ${whoText(id).replace(/^\S+ /, '')}.\nYou're #${pos} in the queue${line}.\n⏰ You can expect to load your clothes around ${time(etaFor(id, pos))}. I'll message you when it's your turn. Reply LEAVE to leave the queue.`);
}

async function handleDone(user, arg) {
  const mine = Object.keys(db).filter(k => db[k].user?.phone === user.phone && db[k].state !== 'next');
  const id = findMachine(arg) && mine.includes(findMachine(arg)) ? findMachine(arg)
           : mine.find(k => db[k].state === 'done') || mine[0];
  if (!id) {
    const left = Object.keys(db).find(k => db[k].leftover?.phone === user.phone);
    if (left) { db[left].leftover = null; save(); return send(user.phone, `Thanks, ${user.name} — glad you got your clothes back 👍`); }
    return send(user.phone, `You're not using a machine right now.`);
  }
  const dryNext = id === 'W1' ? `\nWant to dry them? Reply START DRYER — ${db.D1.state === 'free' ? 'the dryer is free now 🟢' : `the dryer is busy, I'll queue you (~${time(etaFor('D1', db.D1.queue.length + 1))})`}.` : '';
  await send(user.phone, `Thanks, ${user.name}! 👍${dryNext}`);
  return release(id, 'collected');
}

/* ---------- Booking a spot from anywhere ---------- */
const VN = { W1: 'Máy giặt', D1: 'Máy sấy' };
function offerText(phone, vi) {                            // after STATUS: offer a place in line for busy machines
  const busy = Object.keys(MACHINES).filter(id => db[id].state !== 'free' && db[id].user?.phone !== phone && !db[id].queue.some(u => u.phone === phone));
  if (!busy.length || !residents[phone]) return '';
  residents[phone].offer = { ids: busy, at: now() }; saveResidents();
  const parts = busy.map(id => `${vi ? VN[id] : label(id)} ~${time(etaFor(id, db[id].queue.length + 1))}`).join(' · ');
  return vi
    ? `\n\n📅 Muốn giữ chỗ? ${parts}\nTrả lời CÓ${busy.length > 1 ? ' MÁY GIẶT hoặc CÓ MÁY SẤY' : ''} để xếp hàng.`
    : `\n\n📅 Want a spot? ${parts}\nReply YES${busy.length > 1 ? ' WASHER or YES DRYER' : ''} to join the queue.`;
}
async function handleQueue(user, id, vi) {
  const m = db[id], lower = MACHINES[id].label.toLowerCase();
  if (residents[user.phone]) { delete residents[user.phone].offer; saveResidents(); }
  if (m.state === 'free') return send(user.phone, vi ? `${VN[id]} đang trống — cứ xuống quét mã QR là dùng được 🏃` : `${The(id)} is free right now — just go and scan its tag 🏃`);
  if (m.user?.phone === user.phone && m.state !== 'next') return send(user.phone, `You already have ${the(id)} 🙂`);
  if (m.state === 'next' && m.user.phone === user.phone) return send(user.phone, `It's already your turn — go scan the ${lower} tag before ${time(m.until)}!`);
  let pos = m.queue.findIndex(u => u.phone === user.phone) + 1;
  if (!pos) { m.queue.push({ ...user, joinedAt: now(), remote: true }); pos = m.queue.length; save(); }
  const eta = time(etaFor(id, pos));
  return send(user.phone, vi
    ? `📅 Đã giữ chỗ! Bạn là #${pos} cho ${lower === 'washer' ? 'máy giặt' : 'máy sấy'}, dự kiến khoảng ${eta}.\nMình sẽ nhắc bạn trước 5 phút và khi tới lượt — lúc đó xuống quét mã QR để bắt đầu nhé.`
    : `📅 You're booked! #${pos} for the ${lower}, expected around ${eta}.\nI'll remind you ${SOON_MIN} min before and again when it's your turn — then go scan the tag to start. Reply LEAVE to cancel.`);
}
async function quoteQueue(user, id, vi) {                   // show the wait, ask to confirm
  const m = db[id], pos = m.queue.findIndex(u => u.phone === user.phone) + 1;
  if (m.state === 'free' || pos || (m.user?.phone === user.phone)) return handleQueue(user, id, vi);   // nothing to confirm
  residents[user.phone].offer = { ids: [id], at: now() }; saveResidents();
  const n = m.queue.length + 1, eta = time(etaFor(id, n)), who = whoText(id).replace(/^\S+ /, '');
  return send(user.phone, vi
    ? `📅 ${VN[id]} đang bận. Nếu xếp hàng bây giờ, bạn là #${n} và dự kiến được dùng khoảng ${eta}.\nĐồng ý? Nhấn XẾP HÀNG lần nữa (hoặc trả lời CÓ) để giữ chỗ.`
    : `📅 ${The(id)} is busy (${who}).\nIf you join now you'll be #${n} — expected around ${eta}.\nOK with that? Press QUEUE again (or reply YES) to book it.`);
}

async function handleYes(user, arg, vi) {
  const offer = residents[user.phone]?.offer;
  if (!offer || now() - offer.at > OFFER_MIN * 60_000) return send(user.phone, vi ? 'Có gì cần giúp nào? 🙂 Gửi "ai đang giặt đồ?" để xem máy nào trống.' : 'Yes to what? 🙂 Send STATUS to see what\'s free.');
  const pick = findMachine(arg);
  const id = pick && offer.ids.includes(pick) ? pick : offer.ids.length === 1 ? offer.ids[0] : null;
  if (!id) return send(user.phone, vi ? 'Máy nào? Trả lời CÓ MÁY GIẶT hoặc CÓ MÁY SẤY.' : 'Which one? Reply YES WASHER or YES DRYER.');
  return handleQueue(user, id, vi);
}

async function handleMoved(user, arg) {
  const pick = findMachine(arg);
  const ok = k => (db[k].leftover && db[k].leftover.phone !== user.phone) || (db[k].state === 'done' && db[k].user.phone !== user.phone);
  const options = Object.keys(db).filter(ok);
  const id = pick && options.includes(pick) ? pick : options.length === 1 ? options[0] : null;
  if (!options.length) {
    if (Object.keys(db).some(k => db[k].user?.phone === user.phone && db[k].state === 'done')) return handleDone(user, arg);
    return send(user.phone, `There are no forgotten clothes to move right now 👍`);
  }
  if (!id) return send(user.phone, `Which machine? Reply MOVED WASHER or MOVED DRYER.`);
  const m = db[id], machine = MACHINES[id].label.toLowerCase();
  let owner;
  if (m.state === 'done') {                                  // still in "collect" time: this ends their load
    owner = m.user;
    await release(id, 'moved', { movedBy: user.name });
  } else {                                                   // machine was already auto-freed
    owner = m.leftover;
    record({ type: 'moved', outcome: 'moved', machine: id, name: user.name, phone: user.phone, owner: owner.name, at: now() });
    m.leftover = null; save();
  }
  await send(owner.phone, `🧺 ${user.name} took your clothes out of the ${machine} so they could use it. Please pick them up from the basket.`);
  return send(user.phone, `Thanks, ${user.name}! I've told ${owner.name} their clothes are in the basket 🙏`);
}

async function handleLeave(user) {
  let left = false;
  for (const id of Object.keys(db)) {
    const m = db[id];
    const before = m.queue.length;
    m.queue = m.queue.filter(u => u.phone !== user.phone);
    if (m.queue.length !== before) left = true;
    if (m.state === 'next' && m.user.phone === user.phone) {
      left = true;
      record({ type: 'turn', outcome: 'gave-up', machine: id, name: m.user.name, phone: m.user.phone, at: now() });
      await release(id, 'turn');
    }
  }
  save();
  return send(user.phone, left ? `You've left the queue.` : `You're not in any queue.`);
}

/* Vietnamese version of STATUS (used when someone asks in Vietnamese) */
function statusTextVi() {
  const ids = Object.keys(MACHINES), vn = { W1: 'Máy giặt', D1: 'Máy sấy' };
  if (ids.every(id => db[id].state === 'free' && !db[id].leftover))
    return '✅ Cả máy giặt và máy sấy đều đang trống! Quét mã QR trên máy để dùng nhé.';
  return '🧺 Phòng giặt lúc này\n\n' + ids.map(id => {
    const m = db[id], verb = id === 'D1' ? 'đang sấy' : 'đang giặt';
    const line = {
      free:  '🟢 đang trống',
      inuse: `🔵 ${m.user?.name} ${verb} — xong lúc ${time(m.until)}`,
      done:  `🟠 đồ của ${m.user?.name} đã xong, vẫn còn trong máy`,
      next:  `🟣 đang trống, giữ cho ${m.user?.name} đến ${time(m.until)}`,
      unclaimed: `🔴 đang chạy từ ${time(m.since)} nhưng chưa ai nhận`,
    }[m.state];
    const left = m.leftover && m.state !== 'done' ? `\n   ⚠️ Có thể đồ của ${m.leftover.name} vẫn còn trong máy` : '';
    const wait = m.queue.length ? `\n   🙋 Đang chờ: ${m.queue.map((u, i) => `${u.name} (~${time(etaFor(id, i + 1))})`).join(', ')}` : '';
    return `${vn[id] || label(id)}: ${line}${left}${wait}`;
  }).join('\n\n');
}

function statusText() {
  const ids = Object.keys(MACHINES);
  if (ids.every(id => db[id].state === 'free' && !db[id].leftover))
    return `✅ Both the washer and dryer are free right now! Scan a tag (or send START WASHER / START DRYER) to use one.`;
  return '🧺 Laundry room right now\n\n' + ids.map(id => `${label(id)}: ${whoText(id)}${leftoverText(id)}${waitingText(id)}`).join('\n\n');
}

const HELP_VI = `Chào bạn! Mình là LaundryBot 🧺\n\n• Quét mã QR trên máy (hoặc gửi START WASHER / START DRYER)\n• "Ai đang giặt đồ?" — xem máy nào trống, đồ của ai trong máy\n• DONE — bạn đã lấy đồ ra\n• MOVED — bạn đã lấy đồ người khác ra giúp\n• MINE — nhận mẻ giặt bạn quên quét mã\n• LEAVE — rời hàng chờ\n\nℹ️ Việc dùng máy (tên và giờ) được ghi lại cho quản lý nhà.`;
const HELP = `Hi! I'm LaundryBot 🧺\n\n• Scan the QR on a machine's tag (or send START WASHER / START DRYER)\n• DONE — you've collected your clothes\n• STATUS — see what's free\n• QUEUE WASHER / QUEUE DRYER — book a spot from your room\n• LEAVE — leave the queue\n• MOVED — you took someone else's forgotten clothes out\n• MINE — claim a load you started without scanning\n• MUTE / UNMUTE — house alerts\n\nℹ️ Machine use (your name and times) is recorded for the building manager.`;

async function handleMessage(phone, name, text) {
  const user = { phone, name: firstName(name) };
  touchResident(user);
  text = text.replace(/@\S+/g, ' ').trim();                   // "@bot ai đang giặt đồ?" → "ai đang giặt đồ?"
  const plain = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[đĐ]/g, 'd').toLowerCase();
  const vi = /[àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]/i.test(text)
          || /\b(ai|dang|giat|may say|trong|khong|chua|chao|cua toi|cua minh)\b/.test(plain);
  const [cmd, arg] = text.toUpperCase().split(/\s+/);
  if (cmd === 'MINE' || cmd === 'ME') {
    const open = Object.keys(db).filter(k => db[k].state === 'unclaimed');
    const pick = findMachine(arg);
    const id = pick && open.includes(pick) ? pick : open.length === 1 ? open[0] : null;
    if (!open.length) return send(phone, `There's no unclaimed machine right now 👍`);
    if (!id) return send(phone, `Which one? Reply MINE WASHER or MINE DRYER.`);
    return claim(user, id);
  }
  if (cmd === 'MUTE' || cmd === 'UNMUTE') {
    residents[phone].muted = cmd === 'MUTE'; saveResidents();
    return send(phone, cmd === 'MUTE' ? `🔕 House alerts muted. Send UNMUTE to turn them back on.` : `🔔 House alerts are on.`);
  }
  if (['START', 'USE', 'JOIN'].includes(cmd)) {
    const id = findMachine(arg);
    if (!id) return send(phone, `Which machine? Send START WASHER or START DRYER — or just scan the tag.`);
    return handleStart(user, id);
  }
  const machineWord = plain.includes('may giat') || plain.includes('washer') ? 'W1' : plain.includes('may say') || plain.includes('dryer') ? 'D1' : null;
  if (cmd === 'QUEUE' || cmd === 'BOOK' || /xep hang|giu cho|dat cho/.test(plain)) {
    // 1st press: show the expected time · 2nd press (or YES): book it
    const offer = residents[phone]?.offer, fresh = offer && now() - offer.at < OFFER_MIN * 60_000;
    const open = Object.keys(MACHINES).filter(k => db[k].state !== 'free' && db[k].user?.phone !== phone && !db[k].queue.some(u => u.phone === phone));
    let id = findMachine(arg) || machineWord;
    if (!id && fresh && offer.ids.length === 1) id = offer.ids[0];
    if (id && fresh && offer.ids.includes(id)) return handleQueue(user, id, vi);
    if (!id && open.length === 1) id = open[0];
    if (id) return quoteQueue(user, id, vi);
    const mine = Object.keys(MACHINES).find(k => db[k].queue.some(u => u.phone === phone));
    if (!open.length && mine) return handleQueue(user, mine, vi);             // already booked → repeat their time
    if (!open.length) return send(phone, vi ? 'Cả hai máy đều trống — cứ xuống quét mã là dùng được 🏃' : 'Both machines are free — just go and scan a tag 🏃');
    residents[phone].offer = { ids: open, at: now() }; saveResidents();
    const parts = open.map(k => `${vi ? VN[k] : label(k)} ~${time(etaFor(k, db[k].queue.length + 1))}`).join(' · ');
    return send(phone, vi ? `📅 Thời gian dự kiến: ${parts}\nTrả lời XẾP HÀNG MÁY GIẶT hoặc XẾP HÀNG MÁY SẤY để giữ chỗ.`
                          : `📅 Expected times: ${parts}\nReply QUEUE WASHER or QUEUE DRYER to book.`);
  }
  if (/^(yes|y|ok|okay|sure|yep|co|duoc|dong y|oke)\b/.test(plain)) return handleYes(user, arg || machineWord, vi);
  if (cmd === 'DONE') return handleDone(user, arg);
  if (cmd === 'MOVED' || cmd === 'MOVE') return handleMoved(user, arg);
  if (cmd === 'LEAVE' || cmd === 'CANCEL') return handleLeave(user);
  if (cmd === 'STATUS') return send(phone, (vi ? statusTextVi() : statusText()) + offerText(phone, vi));

  // Plain-language questions (English + Vietnamese, with or without accents)
  if (/\b(ai|who|whos|status|tinh trang|trong|free|available|ranh|co ai|con may)\b/.test(plain) || /dang (giat|say)|using|washing|drying/.test(plain))
    return send(phone, (vi ? statusTextVi() : statusText()) + offerText(phone, vi));
  if (/da lay do|lay do (roi|xong)|lay xong|got my clothes|collected/.test(plain)) return handleDone(user);
  if (/\b(cua (toi|minh|em|anh|chi)|la (toi|minh|em)|mine|thats me|its me)\b/.test(plain)) return handleMessage(phone, name, 'MINE');
  return send(phone, vi ? HELP_VI : HELP);
}

/* ------------------------------------------------------------------ */
/* Timers: wash finished, reservation expired, clothes never collected */
/* ------------------------------------------------------------------ */
async function tick() {
  for (const id of Object.keys(db)) {
    const m = db[id];
    if (m.state === 'inuse' || m.state === 'done') m.queue.forEach((u, i) => {
      const eta = etaFor(id, i + 1);
      if (!u.soonSent && eta - now() <= SOON_MIN * 60_000) {
        u.soonSent = true; save();
        send(u.phone, `⏰ Heads up ${u.name}: your ${MACHINES[id].label.toLowerCase()} turn is coming up around ${time(eta)}. Get your laundry ready — I'll message you when it's free.`);
      }
    });
    if ((m.state === 'free' || m.state === 'next') && m.running && now() - m.vibeSince >= GRACE_SEC * 1000) {
      await goUnclaimed(id);
    } else if (m.state === 'inuse' && now() >= m.until && !m.running) {
      Object.assign(m, { state: 'done', until: now() + COLLECT_MIN * 60_000, doneAt: now(), reminded: false });
      if (m.session) m.session.finishedAt = now();
      save();
      const waiting = m.queue.length ? ` ${m.queue[0].name} is waiting.` : '';
      await send(m.user.phone, `🧺 Your ${MACHINES[id].label.toLowerCase()} is done, ${m.user.name}!${waiting}\nPlease collect your clothes and reply DONE.`);
    } else if (m.state === 'done' && now() >= m.until) {
      await send(m.user.phone, `I've marked ${the(id)} as free so the next person can use it. If your clothes are still inside, please get them soon — reply DONE when you have.`);
      await release(id, 'auto-freed');
    } else if (m.state === 'done' && !m.reminded && now() >= (m.doneAt || 0) + REMIND_MIN * 60_000) {
      m.reminded = true; save();
      const waiting = m.queue.length ? ` ${m.queue[0].name} is waiting for it.` : '';
      await send(m.user.phone, `⏰ Reminder, ${m.user.name}: your clothes are still in the ${MACHINES[id].label.toLowerCase()}.${waiting}\nPlease collect them and reply DONE — I'll free the machine at ${time(m.until)}.`);
    } else if (m.state === 'next' && now() >= m.until) {
      await send(m.user.phone, `⏰ Your turn for ${the(id)} expired. Scan the tag again to rejoin the queue.`);
      record({ type: 'turn', outcome: 'missed', machine: id, name: m.user.name, phone: m.user.phone, at: now() });
      await release(id, 'turn');
    }
  }
}
setInterval(() => tick().catch(console.error), 15_000);

/* ------------------------------------------------------------------ */
/* HTTP                                                                */
/* ------------------------------------------------------------------ */
const app = express();
app.use(express.json({ verify: (req, _res, buf) => { req.rawBody = buf; } }));

// Meta calls this once when you save the webhook URL
app.get('/webhook', (req, res) => {
  if (req.query['hub.mode'] === 'subscribe' && req.query['hub.verify_token'] === WA_VERIFY_TOKEN)
    return res.send(req.query['hub.challenge']);
  res.sendStatus(403);
});

// Incoming WhatsApp messages
const seen = new Set();
app.post('/webhook', (req, res) => {
  if (WA_APP_SECRET) {
    const expected = 'sha256=' + crypto.createHmac('sha256', WA_APP_SECRET).update(req.rawBody || '').digest('hex');
    const got = req.get('x-hub-signature-256') || '';
    if (got.length !== expected.length || !crypto.timingSafeEqual(Buffer.from(got), Buffer.from(expected)))
      return res.sendStatus(401);
  }
  res.sendStatus(200); // answer fast; Meta retries slow webhooks

  for (const entry of req.body.entry || []) for (const change of entry.changes || []) {
    const v = change.value || {};
    const names = Object.fromEntries((v.contacts || []).map(c => [c.wa_id, c.profile?.name]));
    for (const msg of v.messages || []) {
      if (seen.has(msg.id)) continue;           // ignore retries
      seen.add(msg.id); if (seen.size > 1000) seen.delete(seen.values().next().value);
      const text = msg.text?.body || msg.button?.text || msg.interactive?.button_reply?.title || '';
      handleMessage(msg.from, names[msg.from], text).catch(console.error);
    }
  }
});

/* The 4 lines × 20 characters for the tag's 20x4 character LCD (Fordata FDCC2004 / HD44780).
   Plain ASCII plus two built-in LCD characters: \u00ff = full block █, \u00a5 = middle dot ･ */
const pad = s => String(s).slice(0, 20).padEnd(20);
const lr = (l, r) => { r = String(r); return String(l).slice(0, 19 - r.length).padEnd(20 - r.length) + r; };
function lcdLines(id) {
  const m = db[id], name = MACHINES[id].label.toUpperCase(), q = m.queue;
  const mins = Math.max(0, Math.ceil((m.until - now()) / 60_000));
  const nextLine = q[0] ? `Next: ${q[0].name} ~${time(etaFor(id, 1))}` : 'Nobody waiting';
  const busy = id === 'D1' ? 'DRYING' : 'WASHING';
  const left = m.leftover ? m.leftover.name : null;
  const lines = {
    inuse: () => {
      const cells = 12, filled = Math.round(Math.min(1, 1 - mins / MACHINES[id].minutes) * cells);
      return [`${name}: IN USE`, lr(m.user.name, `done ${time(m.until)}`),
              '\u00ff'.repeat(filled) + '\u00a5'.repeat(cells - filled) + ` ${String(mins).padStart(2)} min`, nextLine];
    },
    done:      () => [`${name}: FINISHED`, `${m.user.name}, please take`, 'your clothes out', q[0] ? `Next: ${q[0].name}` : 'Nobody waiting'],
    next:      () => [`${name}: NEXT UP`, `${m.user.name}'s turn now!`, `Scan within ${mins} min`, q[0] ? `Then: ${q[0].name}` : 'Nobody else waiting'],
    unclaimed: () => [`!!WHO IS ${busy}?!!`, 'Started - no scan!', 'Yours? Scan the QR', 'or reply MINE'],
    free:      () => [`${name}: FREE`, m.running ? 'Running - scan now!' : 'Scan QR to use it',
                      left ? `${left}'s clothes` : 'Nobody waiting', left ? 'may still be inside' : ''],
  }[m.state] || (() => [`${name}: FREE`, 'Scan QR to use it', '', '']);
  return lines().map(pad);
}

// What each ESP32 tag should display — polled every ~15 s
app.get('/api/tags/:id', (req, res) => {
  if (TAG_KEY && (req.get('x-tag-key') || req.query.key) !== TAG_KEY) return res.sendStatus(401);
  const id = req.params.id.toUpperCase(), m = db[id];
  if (!m) return res.sendStatus(404);
  const mins = Math.max(0, Math.ceil((m.until - now()) / 60_000));
  const display = {
    free:  { status: 'FREE',    name: '',          sub: m.leftover ? `${m.leftover.name}'s clothes inside?` : 'Scan to start' },
    inuse: { status: 'IN USE',  name: m.user?.name, sub: m.queue[0] ? `Next: ${m.queue[0].name}` : `Done at ${time(m.until)}` },
    done:  { status: 'DONE',    name: m.user?.name, sub: 'Collect clothes' },
    next:  { status: 'NEXT UP', name: m.user?.name, sub: `Scan in ${mins} min` },
    unclaimed: { status: 'WHO?',  name: 'Scan me!',  sub: "If it's yours, scan or reply MINE" },
  }[m.state];
  res.json({ id, machine: MACHINES[id].label, minutes: MACHINES[id].minutes, state: m.state, color: COLORS[m.state], ...display,
             queue: m.queue.length, qr: qrLink(id), running: !!m.running, lcd: lcdLines(id),
             alarm: m.state === 'unclaimed' && now() < (m.alarmUntil || 0) });   // true → the tag's buzzer should sound
});

// The tag's vibration sensor reports when the machine starts/stops shaking
app.post('/api/tags/:id/vibration', async (req, res) => {
  if (TAG_KEY && (req.get('x-tag-key') || req.query.key) !== TAG_KEY) return res.sendStatus(401);
  const id = req.params.id.toUpperCase();
  if (!db[id]) return res.sendStatus(404);
  await vibration(id, !!req.body?.running);
  res.json({ ok: true, state: db[id].state });
});

app.get('/', (_req, res) => res.send('LaundryBot is running.'));
app.get('/pitch', (_req, res) => res.sendFile(fileURLToPath(new URL('../site/pitch.html', import.meta.url))));   // the pitch deck

/* ------------------------------------------------------------------ */
/* Records for the building manager — needs ADMIN_KEY (open in DEV)    */
/* ------------------------------------------------------------------ */
const isAdmin = req => {
  const key = req.get('x-admin-key') || req.query.key || '';
  if (!ADMIN_KEY) return DEV;
  return key.length === ADMIN_KEY.length && crypto.timingSafeEqual(Buffer.from(key), Buffer.from(ADMIN_KEY));
};
const dayStart = d => new Date(`${d}T00:00:00`).getTime();
function filterHistory(q) {
  const from = q.from ? dayStart(q.from) : 0, to = q.to ? dayStart(q.to) + 86_400_000 : Infinity;
  return history
    .filter(r => { const t = r.startedAt || r.at; return t >= from && t < to; })
    .filter(r => !q.machine || r.machine === q.machine)
    .filter(r => !q.name || r.name.toLowerCase() === String(q.name).toLowerCase())
    .sort((a, b) => (b.startedAt || b.at) - (a.startedAt || a.at));
}
app.get('/api/history', (req, res) => {
  if (!isAdmin(req)) return res.sendStatus(401);
  res.json({ timezone: TIMEZONE, machines: Object.fromEntries(Object.entries(MACHINES).map(([k, v]) => [k, v.label])), records: filterHistory(req.query) });
});
app.get('/api/history.csv', (req, res) => {
  if (!isAdmin(req)) return res.sendStatus(401);
  const d = ms => ms ? new Date(ms).toLocaleDateString('en-CA', { timeZone: TIMEZONE }) : '';
  const t = ms => ms ? time(ms) : '';
  const mins = (a, b) => a && b ? Math.round((b - a) / 60_000) : '';
  const cell = v => /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : v;
  const rows = [['date', 'load', 'machine', 'name', 'phone', 'type', 'outcome', 'queued', 'started', 'finished', 'collected', 'wait_min', 'collect_min']];
  for (const r of filterHistory(req.query)) rows.push([
    d(r.startedAt || r.at), r.load || r.ref || '', MACHINES[r.machine]?.label || r.machine, r.name, r.phone, r.type, r.outcome,
    t(r.queuedAt), t(r.startedAt || r.at), t(r.finishedAt), t(r.collectedAt), mins(r.queuedAt, r.startedAt), mins(r.finishedAt, r.collectedAt),
  ]);
  res.type('text/csv').attachment(`laundry-records-${d(now())}.csv`).send(rows.map(r => r.map(cell).join(',')).join('\n'));
});
app.get('/admin', (_req, res) => res.sendFile(fileURLToPath(new URL('./admin.html', import.meta.url))));

/* ------------------------------------------------------------------ */
/* Dev tester — only with DEV=1 (no WhatsApp account needed)           */
/* ------------------------------------------------------------------ */
if (DEV) {
  app.post('/dev/message', async (req, res) => {
    const { from, name, text } = req.body;
    await handleMessage(String(from), name, String(text || ''));
    res.json({ ok: true });
  });
  app.post('/dev/skip', async (req, res) => {       // fast-forward the clock
    clockOffset += (Number(req.body.minutes) || 0) * 60_000;
    await tick();
    res.json({ ok: true });
  });
  app.post('/dev/reset', (_req, res) => {
    db = Object.fromEntries(Object.keys(MACHINES).map(id => [id, blank()]));
    clockOffset = 0; devLog.length = 0; history = []; fs.rmSync(HISTORY_FILE, { force: true });
    save(); res.json({ ok: true, seq: devSeq });
  });
  app.post('/dev/residents', (req, res) => {
    residents = Object.fromEntries((req.body.people || []).map(p => [String(p.phone), { ...residents[p.phone], name: p.name, lastSeen: Date.now() }]));   // the tester's housemates only
    saveResidents(); res.json({ ok: true });
  });
  // queue state + bot messages newer than ?since=
  app.get('/dev/state', (req, res) => {
    const since = Number(req.query.since) || 0;
    const etas = Object.fromEntries(Object.keys(db).map(id => [id, db[id].queue.map((_, i) => time(etaFor(id, i + 1)))]));
    const offers = Object.fromEntries(Object.entries(residents).filter(([, r]) => r.offer && now() - r.offer.at < OFFER_MIN * 60_000).map(([ph, r]) => [ph, r.offer.ids]));
    res.json({ db, etas, offers, now: now(), clock: time(now()), messages: devLog.filter(m => m.seq > since) });
  });
  app.get('/dev', (_req, res) => res.sendFile(fileURLToPath(new URL('./dev.html', import.meta.url))));
  app.get('/device', (_req, res) => res.sendFile(fileURLToPath(new URL('./device.html', import.meta.url))));
}

app.listen(PORT, () => {
  console.log(`LaundryBot on http://localhost:${PORT}${DEV ? '  (DEV mode — tester at /dev)' : ''}`);
  if (!DEV && !WA_TOKEN) console.warn('WA_TOKEN is not set — replies will only be printed here.');
});
