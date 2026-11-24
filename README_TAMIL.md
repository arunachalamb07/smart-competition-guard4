# SMART COMPETITION GUARD – VS Code Prototype

## இந்த Prototype என்ன செய்யும்?
- Judge website-ல் Team உருவாக்கலாம்.
- ஒவ்வொரு Team-க்கும் தனி Team Code கிடைக்கும்.
- Python laptop agent server-க்கு heartbeat அனுப்பும்.
- Chrome extension tab switching மற்றும் website domain events பதிவு செய்யும்.
- ChatGPT, Claude, Gemini, Copilot, Perplexity போன்ற configured AI domains திறந்தால் red alert உருவாகும்.
- Judge dashboard-ல் laptop status, alerts, event history பார்க்கலாம்.
- Judge `Review` அழுத்தி alert-ஐ review செய்ததாக mark செய்யலாம்.

**முக்கிய வரம்பு:** இது prototype மட்டுமே. AI பயன்படுத்தியதை 100% கண்டுபிடிக்காது. Listed domains-ஐ browser-ல் திறப்பதை மட்டுமே கண்டறியும். VPN, வேறு browser, mobile, second device அல்லது மறைக்கப்பட்ட வழிகளை கண்டறியாது. Alert என்பது விசாரணைக்கான signal; cheating proof அல்ல. Participants-க்கு monitoring பற்றி முன்கூட்டியே தெரிவிக்கவும். Passwords, keystrokes, screen, message content எதுவும் சேகரிக்கப்படாது.

## தேவையானவை
- Python 3.10 அல்லது அதற்கு மேல்
- VS Code
- Google Chrome (browser extension சோதனைக்கு)
- எல்லா devices-மும் ஒரே trusted Wi-Fi/LAN-ல் இருக்க வேண்டும்

## A. VS Code-ல் server run செய்வது
1. ZIP extract செய்து `smart_competition_guard` folder-ஐ VS Code-ல் Open Folder செய்யவும்.
2. VS Code Terminal திறக்கவும்.
3. Virtual environment உருவாக்கவும்:

### Windows
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python server.py
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

4. Browser-ல் `http://127.0.0.1:5000` திறக்கவும்.
5. Team Registration-ல் Team Name கொடுத்து Create Team அழுத்தவும்.
6. கிடைக்கும் Team Code-ஐ அந்த Team-ன் நான்கு laptops-க்கும் பகிரவும்.

## B. Laptop heartbeat agent run செய்வது
மற்றொரு VS Code terminal-ல்:

```bash
pip install requests
python agent.py --server http://127.0.0.1:5000 --team-code YOURCODE --laptop-name "Alpha Laptop 1"
```

இதை ஒவ்வொரு laptop-லும் தனித்தனி laptop name-உடன் run செய்யவும்.
உதாரணம்: `Alpha Laptop 2`, `Alpha Laptop 3`, `Alpha Laptop 4`.

## C. Chrome Extension install செய்வது
1. Chrome address bar-ல் `chrome://extensions` திறக்கவும்.
2. Developer mode ON செய்யவும்.
3. Load unpacked அழுத்தி இந்த project-இல் உள்ள `chrome_extension` folder தேர்வு செய்யவும்.
4. Extension icon-ஐ திறந்து Server URL, Team Code, Laptop Name கொடுக்கவும்.
5. Save & Enable Monitoring அழுத்தவும்.
6. அதே extension-ஐ ஒவ்வொரு participant laptop-லும் configure செய்யவும்.

Server laptop-ல் இயங்கினால், மற்ற laptops-ல் `127.0.0.1` பயன்படுத்தக் கூடாது. Server laptop-ன் LAN IP-ஐ பயன்படுத்தவும். உதாரணம்: `http://192.168.1.10:5000`. Windows Firewall-ல் private network-க்கு port 5000 அனுமதிக்க வேண்டியிருக்கலாம். Public internet-ல் port-ஐ திறக்க வேண்டாம்.

## D. Demo test
1. Judge dashboard-ல் `TEAM ALPHA` உருவாக்கவும்.
2. Team code copy செய்யவும்.
3. Laptop agent மற்றும் Chrome extension-ஐ configure செய்யவும்.
4. Dashboard-ல் laptop ONLINE ஆக வருகிறதா பார்க்கவும்.
5. Chrome-ல் tab மாற்றி பார்க்கவும் – TAB_SWITCH event வரும்.
6. `https://chatgpt.com` அல்லது configured AI domain திறக்கவும் – red alert வரும்.
7. Judge dashboard-ல் Review அழுத்தவும்.

## Troubleshooting
- `Invalid team code`: Dashboard-ல் காட்டிய Team Code சரியாக உள்ளதா பார்க்கவும்.
- `Server unreachable`: Server run ஆகிறதா, சரியான LAN IP-ஆ, இரு devices-மும் ஒரே Wi-Fi-லா பார்க்கவும்.
- Laptop OFFLINE: Agent process இயங்குகிறதா பார்க்கவும்; heartbeat 15 seconds-க்கு ஒருமுறை வரும்.
- Extension events வரவில்லை: Extension enabled-ஆ, சரியான server URL/code உள்ளதா பார்க்கவும்; `chrome://extensions`-ல் service worker errors பார்க்கவும்.
- Port 5000 busy: `server.py`-ன் கடைசி வரியில் port மாற்றி, எல்லா client URLs-லும் அதே port பயன்படுத்தவும்.

## Production-க்கு முன் செய்ய வேண்டியவை
- HTTPS, proper user authentication, role-based access control
- Secure team enrollment tokens; current demo codes are not strong authentication
- Database backups, retention policy, tamper-evident audit logs
- Participant consent and clear monitoring policy
- Admin actions audit trail
- Secure deployment and rate limiting
- Browser extension signing / managed installation
- False-positive review and appeal workflow


## Admin Password (முக்கியம்)
- Server start ஆகும்போது terminal-ல் `ADMIN PASSWORD: ...` என்று வரும். அதுவே login password.
- நிரந்தர password வேண்டுமென்றால், server-ஐ இயக்கும் முன் PowerShell-ல்:
  `$env:SMART_GUARD_ADMIN_PASSWORD="உங்கள்-password"`
- Dashboard login இல்லாமல் திறக்காது. Agent மற்றும் Chrome extension வழக்கம்போல் Team Code மூலம் இணையும்.
