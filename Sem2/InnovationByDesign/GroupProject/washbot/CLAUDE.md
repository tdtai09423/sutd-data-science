# LaundryBot — notes for Claude Code

Shared-laundry queue: light ESP32 tags on each machine + a WhatsApp Cloud API bot. No smart plugs. Each tag has a **vibration sensor** and a **buzzer**: wash end = shaking stops (30-min timer is the fallback), and shaking with nobody scanned sets off the alarm.

## Layout
- `bot/server.js` — the whole backend (Express). WhatsApp webhook (`GET/POST /webhook`, HMAC-checked with `WA_APP_SECRET`), queue logic, timers (`tick()` every 15 s), tag API `GET /api/tags/:id`. State lives in `bot/data.json` (gitignored).
- `bot/dev.html` — house tester at `/dev` (DEV), laid out like a sim game: an animated **laundry-room scene** on top (each housemate has a bedroom door; figures walk to the machine, scan the QR sticker with their phone, load clothes, press start, walk back; they go into their room to "chill" while waiting in line or while their load runs, and come out when it's their turn / their laundry is done / an alarm rings; MOVED carries clothes to the Lost & Found basket), a big readable copy of each tag's LCD above its machine, a "start without scan" button under each machine (simulates the vibration sensor), then **3 control panels** (Enric, Kain, Edmond) with chat + action buttons. Uses dev-only endpoints `/dev/message`, `/dev/skip`, `/dev/reset` (also wipes records), `/dev/residents`, `/dev/state`.
- `bot/device.html` — tag simulator at `/device` (DEV): 3D-printed tag with a **20×4 character LCD (Fordata FDCC2004 / HD44780)** drawn dot-for-dot, a **printed QR sticker** (the LCD can't show a QR; the QR per machine never changes), an **RGB light bar** for the colour, VIB light, buzzer, shake button. The LCD prints the `lcd` array (4 × 20 chars; `\u00ff` = █, `\u00a5` = ·) from `GET /api/tags/:id` — `lcdLines()` in server.js is the screen spec.
- `bot/admin.html` — the building manager's records page at `/admin`: who used which machine and when, stats, CSV export.
- `site/pitch.html` — 13-slide pitch deck (served at `/pitch`, also works as a plain file). Same visual style as the tester. Target customer is landlords / condo & dorm operators, not roommates.
- `site/index.html` — static 5-step explainer (plain SVG, no build).

## Run
- `cd bot && npm run dev` → http://localhost:3000/dev (no WhatsApp account needed; bot replies go to an in-memory log).
- `.claude/launch.json` has `bot` and `site` preview configs.

## Machine states
`free` → `inuse` (timer, or until shaking stops) → `done` (owner must reply DONE; auto-freed after 20 min) → `next` (first in queue has 10 min to scan) → `inuse` …
`free`/`next` + shaking for `GRACE_SEC` (5 s) with no scan → `unclaimed`: tag goes red and `alarm:true` (buzzer, for `ALARM_MIN`), every resident gets a 🚨 house alert. Someone replies **MINE** (or scans) → `inuse` with the real start time, `forgotScan:true` on the record; if it was saved for someone else they stay #1. Shaking stops with no claim → `unclaimed` record + "please collect" alert.
- Tag sensor: `POST /api/tags/:id/vibration {running}` (tag should debounce pauses of a few minutes). Tag reads `alarm` and `running` from `GET /api/tags/:id`.
- Residents (anyone who messaged the bot) are in `residents.json`; house alerts go to all except MUTE'd. Outside WhatsApp's 24 h window alerts need the `WA_ALERT_TEMPLATE` template.
- Queue replies include an expected load time (`etaFor`: remaining time + 5 min handover + one cycle per person ahead).
Machine IDs and durations (currently 30 min each) are in `MACHINES` at the top of `server.js`; the tester reads them from the tag API's `minutes` field.

## Usage records (a core requirement)
The building manager/company must be able to see **who used which machine, when**. Every finished load is appended to `bot/history.jsonl` (gitignored):
`{type:'wash', machine, name, phone, queuedAt, startedAt, finishedAt, collectedAt, outcome:'collected'|'auto-freed'}` plus `{type:'turn', outcome:'missed'|'gave-up', …, at}`.
- API: `GET /api/history` (filters `from`, `to`, `machine`, `name`) and `GET /api/history.csv` — need `ADMIN_KEY` (header `x-admin-key` or `?key=`); open without a key only in DEV.
- Records older than `HISTORY_DAYS` (default 365) are pruned on start. Residents are told in the bot's HELP text that use is recorded — keep that notice if you change the text.

## Forgotten clothes
`done` → reminder at `REMIND_MIN` (10) → auto-freed at `COLLECT_MIN` (20): `m.leftover = {name, phone}` (clothes probably still inside). The next person's messages and STATUS warn about it. `MOVED` (anyone else) clears it, tells the owner and records `{type:'moved', owner}`; `MOVED` during `done` ends the load as `outcome:'moved', movedBy`. The owner's `DONE` also clears their leftover.

## Loads & booking
- A wash and the dry that follows share `load` (records + CSV). When a washer load comes out, `residents[phone].wetLoad` is set; the owner's next dryer session within `LINK_HOURS` reuses that load ID, and the bot says "🔗 Drying your load from the washer". After DONE on the washer the bot suggests START DRYER.
- Booking from anywhere: `QUEUE [WASHER|DRYER]` → 1st time the bot quotes position + expected time and stores `residents[phone].offer`; a 2nd `QUEUE` (or YES / CÓ) within `OFFER_MIN` books it (`handleQueue`). STATUS also ends with an offer. `SOON_MIN` before someone's expected turn they get a "coming up" heads-up.
- Tester: every person starts with a **dirty basket**; their load is tracked client-side (`p.load`) so the dryer only ever takes that person's own wet clothes (collecting them from the washer / Lost & Found first). Clean clothes get put away → new dirty basket. Quick-reply chips appear under a chat for commands the bot suggests. 🎵 button plays generated muzak (Web Audio, no files).

## Language
Plain-language questions work (`@bot ai đang giặt đồ?`, "who's using the washer?"): mentions are stripped, text is accent-folded and keyword-matched. Vietnamese questions get Vietnamese replies (`statusTextVi`, `HELP_VI`). WhatsApp's Groups API only lets a business create its own ≤8-person group (invite link, Official Business Account), so "house alerts" DM each resident instead.

## Wording
Users never see machine IDs: it's "washer"/"dryer" and commands are `START WASHER`, `MINE DRYER`, `MOVED WASHER` (`findMachine` still accepts W1/D1). IDs are only in the tag API URLs.

## Conventions
- Node ≥ 20.12, ES modules, only dependency is express. Keep it dependency-light.
- User-facing bot text is short, friendly, emoji-light.
- Illustrations are inline SVG in code (no image assets).
