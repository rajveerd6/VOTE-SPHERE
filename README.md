# 🗳️ VoteSphere

> A lightweight, secure, and anonymous online voting system for classrooms and small groups.

VoteSphere is a simple web-based voting portal built with **Flask**, **SQLite**, and **vanilla JavaScript**. It lets an admin set up candidates and voters, and lets each voter cast a single anonymous vote after verifying with their roll number. Live results are password-protected, and a full audit log is available only to the admin. Completely made from prompt engineering reducing time of build to just an hour or less.

---

## ✨ Features

### 👤 For Admins
- Secure admin login (single password)
- Add / remove **candidates**
- Add / remove **voters** (roll number, name, gender)
- Same password used for admin panel **and** viewing results
- View **public results** (vote counts, gender-wise breakdown — no identities)
- View **full audit log** (who voted for whom — admin only)
- Reset votes or perform a full database reset
- Change admin / result password anytime

### 🧑‍🤝‍🧑 For Voters
- Verify by **roll number** (supports `1` or `01` format)
- Cast **one vote** — anonymous
- Voice feedback:
  - Whisper "Please enter correct roll number" for invalid entries
  - Alarm sound for repeat voting attempts
- Bell sound on successful vote
- Automatically returns to the roll number page after voting (ready for the next voter)

### 🎨 UI / UX
- Modern dark theme with aurora glow + starfield background
- Glassmorphism cards and gradient buttons
- Smooth animations: page fade-in, button lift, card pop, shimmer text
- Fully responsive (mobile-friendly)

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python · Flask |
| Database | SQLite (built into Python) |
| Frontend | HTML · CSS · Vanilla JavaScript |
| Icons | Font Awesome 6 |
| Fonts | Poppins · Space Grotesk |

---
