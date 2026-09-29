# Laundry queue bot (WhatsApp Cloud API)

Residents scan the QR on a machine's tag → WhatsApp opens with `START WASHER` → the bot gives them the machine or puts them in the queue. The ESP32 tags read `GET /api/tags/W1` to know what colour and name to show.

| Message | What happens |
|---|---|
| `START WASHER` / `START DRYER` (from the QR) | Take the machine if free, otherwise join the queue (with an expected load time) |
| `MOVED` | You took someone else's forgotten clothes out; they get told where their clothes are |
| `MINE` | Claim a load you started without scanning; stops the alarm |
| `DONE` | You've collected your clothes → next person gets a "your turn" message |
| `STATUS` | What's free right now |
| `LEAVE` | Leave the queue |

Timers: the washer and dryer are both 30 min for now. After that the tag turns amber and the owner gets a reminder. If nobody replies DONE within 20 min, the machine is freed automatically. The next person has 10 min to scan before their turn passes on. You can change these at the top of `server.js`.

## 1. Try it locally (no WhatsApp needed)

```bash
npm install
npm run dev
```

Open http://localhost:3000/dev. You can play the 3 housemates (Enric, Kain and Edmond), tap their action buttons or type messages, and skip time forward. The washer and dryer cards show what each tag displays and the clothes inside the machine. The button each person should press next glows green.

## 2. Connect real WhatsApp

1. Go to https://developers.facebook.com → **Create app** → type **Business** → add the **WhatsApp** product.
2. Go to **WhatsApp → API Setup**. Copy the **temporary access token** and the **Phone number ID**. Add your own phone under "To" so the test number can message you.
3. Copy `.env.example` to `.env` and fill it in. `BOT_NUMBER` is the test number, digits only.
4. Put the server on the internet over HTTPS:
   - quick test: `npm start`, then `ngrok http 3000`
   - to keep it running: deploy to Render, Railway or Fly.io, and add the same env variables there
5. Go to **WhatsApp → Configuration → Webhook**:
   - Callback URL: `https://YOUR-URL/webhook`
   - Verify token: the same `WA_VERIFY_TOKEN` as in `.env`
   - Click **Verify and save**, then subscribe to the **messages** field.
6. Send `STATUS` to the test number from your phone.

For real use (not only test numbers), add a real phone number and create a **permanent token** (System User in Business Settings). The temporary token expires after 24 hours.

## Records page (for the building manager)

`/admin` shows every load (who, which machine, started, finished, collected), plus missed turns, stats and a CSV export. Set `ADMIN_KEY` in `.env` and open `/admin?key=YOUR_KEY`, or type the key when the page asks. The raw data is in `history.jsonl`, one JSON record per line, kept for `HISTORY_DAYS` days.

## Tag API (for the ESP32)

`GET /api/tags/W1` (add header `x-tag-key: ...` if you set `TAG_KEY`)

```json
{ "id":"W1", "machine":"Washer", "state":"inuse", "color":"#2563eb",
  "status":"IN USE", "name":"Alex", "sub":"Next: Maya", "queue":1,
  "qr":"https://wa.me/15551234567?text=START%20W1" }
```

The tag draws `qr` as a QR code, fills the screen with `color`, and shows `status`, `name` and `sub`. Poll every 15–30 s.

## Notes
- The bot only messages people within 24 hours of their last message to it, which WhatsApp allows for free-form text. A wash never runs that long, so no message templates are needed.
- The queue is saved in `data.json`. That's fine for a few machines. Move it to a database if you run many buildings.
