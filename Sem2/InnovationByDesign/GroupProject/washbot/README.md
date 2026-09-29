# 🧺 LaundryBot

A shared-laundry helper for houses, dorms and condos. Each washer and dryer has a light **tag** stuck on with magnets. The tag's colour shows the machine's state, and it shows who is using it plus a QR code. Scanning the QR opens a **WhatsApp queue bot**.

| Colour | Meaning |
|---|---|
| 🟢 Green | Free — scan to start |
| 🔵 Blue | In use (shows who) |
| 🟠 Amber | Done — owner should collect their clothes |
| 🟣 Purple | Saved for the next person in the queue |

## What's in here

| Folder | What it is |
|---|---|
| [`bot/`](bot/) | The WhatsApp Cloud API bot (Node + Express). It also serves `GET /api/tags/:id` for the tags, and a **house tester** at `/dev` where you can play 3 housemates. |
| [`bot/device.html`](bot/device.html) | **Tag simulator** at `/device`: the real tag — 20×4 character LCD, printed QR sticker (real and scannable), RGB light bar, buzzer. It follows the bot live. |
| [`bot/admin.html`](bot/admin.html) | The **manager's records page** at `/admin`: who used which machine and when, time to collect, missed turns, busiest hours, CSV export. |
| [`site/pitch.html`](site/pitch.html) | **Pitch deck** (13 slides, also at `/pitch`): problem → how might we → solution → product → demo → scale → landlords as customers → business model. Arrow keys / swipe. |
| [`site/`](site/) | A simple step-by-step explainer page (`index.html`) showing how the tag, bot and phones work together. |

## Quick start

```bash
cd bot
npm install
npm run dev
```

Then open http://localhost:3000/dev and play the 3 housemates: Enric, Kain and Edmond.

To see the explainer page, open `site/index.html` in a browser.

To connect real WhatsApp, follow [`bot/README.md`](bot/README.md).

## How it works

```
 📱 Resident scans QR on tag ──► WhatsApp ──► Meta Cloud API ──► bot /webhook
                                                                    │ queue + timers
 🏷️ Tag (ESP32 + 20×4 LCD) ◄── GET /api/tags/W1 every ~15 s ───┘
```

- Each tag has a **vibration sensor**, so it knows when the machine is really running and when it has finished. If the sensor isn't used, a 30-minute timer is the fallback.
- **Forgot to scan?** If the machine shakes for 5 seconds and nobody has scanned, the tag turns red and **beeps**, and the whole house gets a 🚨 WhatsApp alert. Whoever owns the load replies **MINE** and the alarm stops. The Records page shows who forgot, plus any loads nobody claimed.
- When you join a queue, the bot tells you roughly **when you can load your clothes**.
- When the time is up, the tag turns amber and the owner gets a reminder. They reply **DONE**, and the next person in line gets 10 minutes to scan.

## Records for the building manager
Every load is saved with who, which machine, and when it was started, finished and collected. Missed turns are saved too. Open **http://localhost:3000/admin**, or `/admin?key=YOUR_ADMIN_KEY` when it's live, to see the stats, filter by date, machine or person, and export a CSV.

Privacy: this is personal data. The bot's help message tells residents their use is recorded. Put a short notice on the tags or in the house rules as well, and keep `HISTORY_DAYS` no longer than you need. Singapore's PDPA and the EU's GDPR both expect this.

## Tag hardware (per machine)
ESP32, a 20×4 character LCD (Fordata FDCC2004 or any HD44780 2004 with an I²C backpack), an RGB LED strip or light pipe for the colour, a vibration sensor (MPU-6050 or SW-420), a buzzer, a printed QR sticker, magnets and a 3D-printed case. It's USB powered.

## Next up
- ESP32 tag firmware: poll the API, print the 4 `lcd` lines, set the RGB bar to `color`, report vibration, and beep when `alarm` is true.
- Deploy the bot (for example to Render) so it runs 24/7.
