# Serenity Mindspace 🧘

> A warm, professional mental wellness platform connecting users with AI support and licensed specialists. Built with pure HTML/CSS/Vanilla JS — no framework required.

![Version](https://img.shields.io/badge/version-2.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Pages](https://img.shields.io/badge/pages-18-blue.svg)

---

## 🚀 Quick Start

```bash
# Python (simplest)
cd serenity-mindspace
python3 -m http.server 8000
# Open: http://localhost:8000

# Node.js
npx serve .

# VS Code
# Right-click index.html → "Open with Live Server"
```

---

## 📁 Project Structure

```
serenity-mindspace/
│
├── index.html                  ← Landing page (hero, features, how-it-works)
├── login.html                  ← Auth: sign up / login, user & specialist toggle
├── assessment.html             ← 17-question wellness assessment (4 sections)
├── choose-support.html         ← Choose AI chat, text specialist, or video
├── ai-chat.html                ← AI chat (Claude API + fallback responses)
├── specialists.html            ← Specialist directory with live filters
├── specialist-profile.html     ← Full specialist profile + booking CTA
├── booking.html                ← 3-step booking (type → calendar → confirm)
├── chat-room.html              ← Text session with specialist
├── video-call.html             ← Video session (getUserMedia / WebRTC-ready)
├── dashboard.html              ← User dashboard (stats, bookings, mood tracker)
├── specialist-dashboard.html   ← Specialist dashboard (patients, earnings)
├── store.html                  ← Token store (3 tiers, ₹99 – ₹799)
│
├── about.html                  ← Company story, values, team
├── faq.html                    ← Searchable FAQ with category filters
├── contact.html                ← Contact form with topic routing
├── privacy.html                ← Full privacy policy (DPDPA 2023/DPDPA)
├── terms.html                  ← Terms of service
├── 404.html                    ← Custom 404 with countdown redirect
│
├── css/
│   ├── main.css                ← Design tokens, reset, typography, utilities
│   └── components.css          ← All component styles (nav, cards, chat, modals)
│
├── js/
│   └── utils.js                ← Shared utility library (51 functions):
│                                    Token management, auth helpers, dark mode,
│                                    smart scroll nav, live clock, crisis detection,
│                                    toast notifications, confirm modals, booking
│
├── schema.sql                  ← PostgreSQL schema (users, sessions, credentials,
│                                    admin review, token economy, audit log)
├── manifest.json               ← PWA manifest
└── README.md                   ← This file
```

---

## ✨ What's Working (v2.0)

### Core Features
- ✅ **Real AI Chat** — Calls Claude claude-sonnet-4-6 API with full multi-turn history, assessment context, and graceful offline fallback
- ✅ **Real Camera Access** — `getUserMedia()` in video-call; mic/camera toggles actually mute the media tracks; screen sharing via `getDisplayMedia()`
- ✅ **Persistent State** — Message count, chat history, bookings, and tokens all survive page refreshes
- ✅ **Smart Nav** — Hides on scroll down, reappears on scroll up (every page)
- ✅ **Dark Mode** — Toggle on every page; respects system preference; persists across sessions
- ✅ **Real Calendar** — Booking page generates a live calendar from the device's current date; no hardcoded dates
- ✅ **Live Clock** — Any element with `data-live-time="time|date|datetime|short"` auto-updates every second
- ✅ **Auth Flow** — Login/signup saves user name, routes back to originally requested page after auth
- ✅ **Booking → Dashboard** — Confirmed bookings actually appear in the user dashboard upcoming sessions list
- ✅ **No `alert()` Calls** — Every alert replaced with styled toast notifications; every `confirm()` replaced with modal
- ✅ **All Footer Links Work** — About, FAQ, Contact, Privacy, Terms are fully built pages

### New Pages (v2.0)
| Page | Description |
|---|---|
| `about.html` | Company story, mission, values, team, stats, CTA |
| `faq.html` | Searchable FAQ, category filter, 18 questions |
| `contact.html` | Working contact form with topic routing, live office clock |
| `privacy.html` | Full privacy policy with table of contents |
| `terms.html` | Full terms of service |
| `404.html` | Custom 404 with breathing animation, 30-second countdown redirect |

### Security & Quality
- ✅ SEO meta tags + Open Graph on all 19 pages
- ✅ PWA manifest.json
- ✅ `utils.js` loaded on every page (no more dead code)
- ✅ Zero duplicate `getTokens()`/`setTokens()` functions
- ✅ Crisis keyword detection in AI chat
- ✅ Auth guards on all protected pages
- ✅ Specialist-only guard on specialist dashboard

---

## 🛠️ utils.js Reference (51 functions)

```javascript
// Tokens
getTokens()           setTokens(n)          addTokens(n)
deductTokens(n)       updateAllTokenDisplays()

// AI Message count (persisted)
getMessageCount()     incrementMessageCount()
getFreeMessagesLeft() resetMessageCount()

// Auth
isLoggedIn()          getUserType()         getUserName()
login(type, name)     logout()
requireAuth()         requireSpecialist()

// Storage
saveAssessment(data)  getAssessment()
saveBooking(obj)      getBookings()         getUpcomingBookings()
saveChatHistory(id, msgs)  getChatHistory(id)

// Real datetime
getRealNow()          getRealDate()         getRealTime()
getRealDateTime()     getRealShortDate()
startLiveClock()      // auto-runs on DOMContentLoaded

// Dark mode
applyTheme(theme)     toggleDarkMode()      initTheme()

// Nav
initMobileMenu()      initHeaderScroll()    updateNavAuthState()

// UI
showToast(msg, type)  showConfirmModal(...)
showLoader(msg)       hideLoader()

// Crisis
detectCrisisKeywords(text)  showCrisisResources()

// Validation
validateEmail(e)      validatePassword(p)
sanitizeInput(s)      escapeHtml(s)

// Misc
spinLuckyVault()      canSpinVault()
showToast(...)        exportChatTranscript(msgs, filename)
formatDate(d)         formatTime(d)         getTimeAgo(d)
```

---

## 🗄️ Database Schema (schema.sql)

**Tables:**
| Table | Purpose |
|---|---|
| `users` | All account types (user / specialist / admin) |
| `oauth_accounts` | Google/Apple Sign-In |
| `email_verifications` | Email confirmation tokens |
| `password_resets` | Password reset tokens |
| `specialist_profiles` | Specialist bio, rates, specialisations |
| `specialist_credentials` | Uploaded documents (ID, degree, licence) |
| `specialist_verifications` | Admin approval/rejection status |
| `assessments` | Wellness assessment responses |
| `sessions` | Booked and completed sessions |
| `chat_messages` | AI and specialist chat messages |
| `token_transactions` | Full token ledger |
| `notifications` | In-app notifications |
| `vault_spins` | Lucky Vault rate limiting |
| `admin_audit_log` | Every admin action, immutable |
| `availability_slots` | Specialist calendar slots |

**Views:**
- `v_pending_credential_reviews` — credentials awaiting admin action
- `v_approved_specialists` — public specialist directory feed

---

## 🔌 API Integration Guide

### AI Chat (Claude API)
The AI chat in `ai-chat.html` calls the Anthropic Messages API directly from the browser. For production, proxy this through your backend to protect your API key:

```javascript
// Current (demo): direct browser call
fetch('https://api.anthropic.com/v1/messages', { ... })

// Production: proxy through your server
fetch('/api/ai/chat', {
  method: 'POST',
  body: JSON.stringify({ message, history, assessmentContext })
})
```

### Token Purchase (Razorpay)
```javascript
// server-side: create order
const order = await razorpay.orders.create({
  amount: amountInPaise,
  currency: 'INR',
  receipt: `token_${Date.now()}`
});

// client-side: open checkout
const rzp = new Razorpay({ key: KEY_ID, ...order,
  handler: (response) => verifyAndCreditTokens(response)
});
rzp.open();
```

### Video Calls (Agora or Daily.co)
Replace the `getUserMedia()` setup in `video-call.html` with your SDK:
```javascript
// Agora example
const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'h264' });
await client.join(APP_ID, channelName, token, uid);
const localTrack = await AgoraRTC.createCameraVideoTrack();
await client.publish(localTrack);
```

---

## 🔒 Admin Role

Admin users (`user_type = 'admin'`) can:
1. **Review specialist credentials** via `v_pending_credential_reviews`
2. **Approve / reject / suspend** specialists via `specialist_verifications`
3. **Adjust token balances** via `token_transactions`
4. **View audit log** of all admin actions

All admin actions are recorded in `admin_audit_log` with old/new values.

Default admin seed: `admin@serenitymindspace.com` / `ChangeMe123!`  
⚠️ **Change the admin password before any production deployment.**

---

## 🚀 Production Checklist

- [ ] Move AI API calls behind a server-side proxy
- [ ] Set up Firebase Auth or custom JWT backend
- [ ] Connect Razorpay / UPI for real payments
- [ ] Deploy schema.sql to PostgreSQL
- [ ] Set up file storage (AWS S3 / Firebase Storage) for credentials
- [ ] Enable HTTPS / SSL
- [ ] Add rate limiting on AI chat endpoint
- [ ] Configure SMTP for email verification
- [ ] Set environment variables (never commit API keys)
- [ ] Change default admin password

---

## 🇮🇳 India-Specific Details

### Regulatory Compliance
- **DPDPA 2023** — Digital Personal Data Protection Act (India) governs all user data handling
- **IT (Amendment) Act** — Additional compliance for digital health platforms
- **RCI** — Rehabilitation Council of India for psychologist licensing verification
- **NMC** — National Medical Commission for psychiatrist credential verification

### Payment Stack
- **Razorpay** — Primary payment gateway (INR, UPI, NetBanking, Cards)
- **UPI** — Instant payments via UPI IDs
- All prices displayed in **₹ (Indian Rupees)**

### Crisis Helplines (India)
| Service | Number | Availability |
|---|---|---|
| iCall (TISS) | 9152987821 | Mon–Sat 8am–10pm |
| Vandrevala Foundation | 1860-2662-345 | 24×7 |
| AASRA | 9820466567 | 24×7 |
| Snehi | 044-24640050 | Daily 8am–10pm |
| Emergency | 112 | 24×7 |

### Localisation
- Default locale: `en-IN`
- Default timezone: `Asia/Kolkata` (IST, UTC+5:30)
- ID verification: Aadhaar (government ID) + degree + RCI/NMC licence
- Date format: DD/MM/YYYY (en-IN locale)


## 📞 Crisis Resources

> This platform is a support tool, not an emergency service.

- **9152987821 (iCall) Suicide & Crisis Lifeline** — call or text 9152987821 (iCall) (24/7, free)
- **Crisis Text Line** — call iCall on 9152987821 or AASRA on 9820466567
- **Emergency Services** — call 112

---

*Made with 💚 for mental wellness · v2.0*
