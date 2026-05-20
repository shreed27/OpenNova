# Email Setup

For Gmail, create an app password rather than using your normal account password.

Add these values to `.env`:
```ini
EMAIL_ADDRESS=you@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_IMAP_SERVER=imap.gmail.com
```

Then run:
```bash
python3 main.py --doctor
```
