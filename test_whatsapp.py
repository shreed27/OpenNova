import time

import pytest

selenium = pytest.importorskip("selenium", reason="WhatsApp browser smoke test requires selenium")

from skills.whatsapp.whatsapp_client import WhatsAppClient


@pytest.mark.skip(reason="Manual WhatsApp QR smoke test; run directly when needed")
def test_manual_whatsapp_browser_login():
    print("Initializing WhatsApp Client...")
    client = WhatsAppClient()
    
    # We don't actually send a message in the test to avoid spamming random numbers.
    # Just opening it is enough to trigger the QR code scan.
    print("Browser opened. Please scan the QR code if handling for the first time.")
    print("Waiting 60 seconds for you to scan...")
    time.sleep(60)
    print("Test Complete. You can close the browser.")

if __name__ == "__main__":
    test_manual_whatsapp_browser_login()
