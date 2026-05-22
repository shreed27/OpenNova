import time
import urllib.parse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .driver import WhatsAppDriver


class WhatsAppClient:
    WEBAPP_URL = "https://web.whatsapp.com/"
    SEARCH_BOX_XPATHS = [
        '//div[@role="textbox"][@contenteditable="true"][@data-tab="3"]',
        '//div[@role="textbox"][@contenteditable="true"][@data-tab="10"]',
        '//div[@role="textbox"][@contenteditable="true"][@title]',
        '//div[@contenteditable="true"][@data-tab="3"]',
    ]
    CHAT_TITLE_XPATH = '//div[@role="grid"]//span[@title] | //div[@role="listitem"]//span[@title]'
    COMPOSER_XPATHS = [
        '//footer//div[@role="textbox"][@contenteditable="true"]',
        '//div[@contenteditable="true"][@data-tab="10"]',
        '//div[@contenteditable="true"][@data-tab="6"]',
    ]

    def send_message(self, contact_name, message, phone_number=None):
        """
        Prefer an existing WhatsApp Web chat by display name.
        Fall back to a direct phone-number chat if one is available.
        """
        try:
            driver = WhatsAppDriver.get_driver()
            self._ensure_whatsapp_ready(driver)

            errors = []

            if contact_name:
                try:
                    self._open_chat_by_name(driver, contact_name)
                    self._send_message_in_open_chat(driver, message)
                    return f"Message sent to chat '{contact_name}'"
                except Exception as exc:
                    errors.append(f"chat lookup failed for '{contact_name}': {exc}")

            if phone_number:
                try:
                    self._open_chat_by_phone(driver, phone_number)
                    self._send_message_in_open_chat(driver, message)
                    return f"Message sent to {phone_number}"
                except Exception as exc:
                    errors.append(f"phone fallback failed for '{phone_number}': {exc}")

            if errors:
                return "Failed to send message: " + "; ".join(errors)

            return (
                "Failed to send message: no WhatsApp chat matched that name and "
                "no phone-number fallback is configured."
            )
        except Exception as exc:
            print(f"Error in send_message: {exc}")
            return f"Failed to send message: {exc}"

    def _ensure_whatsapp_ready(self, driver):
        current_url = ""
        try:
            current_url = driver.current_url
        except Exception:
            pass

        if "web.whatsapp.com" not in current_url:
            driver.get(self.WEBAPP_URL)

        try:
            self._find_first_visible(driver, self.SEARCH_BOX_XPATHS, timeout=20)
        except TimeoutException as exc:
            page_source = ""
            try:
                page_source = driver.page_source
            except Exception:
                pass

            login_markers = (
                "Scan this QR code",
                "Use WhatsApp on your computer",
                "Keep your phone connected",
            )
            if any(marker in page_source for marker in login_markers):
                raise RuntimeError(
                    "WhatsApp Web is not signed in. Open Safari, load web.whatsapp.com, "
                    "and scan the QR code once."
                ) from exc
            raise RuntimeError(
                "WhatsApp Web did not finish loading enough to search chats."
            ) from exc

    def _open_chat_by_name(self, driver, contact_name):
        search_box = self._find_first_visible(driver, self.SEARCH_BOX_XPATHS, timeout=20)
        self._replace_text(search_box, contact_name)
        time.sleep(1)

        candidates = self._collect_chat_titles(driver)
        lowered_name = contact_name.casefold()

        exact_matches = [title for title in candidates if title[0].casefold() == lowered_name]
        if exact_matches:
            self._click_chat_candidate(exact_matches[0][1])
            return

        partial_matches = [title for title in candidates if lowered_name in title[0].casefold()]
        if len(partial_matches) == 1:
            self._click_chat_candidate(partial_matches[0][1])
            return

        if len(partial_matches) > 1:
            labels = ", ".join(match[0] for match in partial_matches[:5])
            raise RuntimeError(
                f"multiple chats matched '{contact_name}': {labels}. Use a more specific display name."
            )

        raise RuntimeError(
            f"no existing WhatsApp Web chat matched '{contact_name}'."
        )

    def _open_chat_by_phone(self, driver, phone_number):
        driver.get(
            f"https://web.whatsapp.com/send?phone={urllib.parse.quote(phone_number)}"
        )
        self._find_first_visible(driver, self.COMPOSER_XPATHS, timeout=20)

    def _send_message_in_open_chat(self, driver, message):
        textbox = self._find_first_visible(driver, self.COMPOSER_XPATHS, timeout=20)
        textbox.click()
        textbox.send_keys(message)
        time.sleep(0.5)
        textbox.send_keys(Keys.ENTER)
        time.sleep(1)

    def _collect_chat_titles(self, driver):
        deadline = time.time() + 10
        last_titles = []
        while time.time() < deadline:
            titles = []
            for element in driver.find_elements(By.XPATH, self.CHAT_TITLE_XPATH):
                title = (element.get_attribute("title") or "").strip()
                if title:
                    titles.append((title, element))
            if titles:
                return titles
            last_titles = titles
            time.sleep(0.5)
        return last_titles

    def _click_chat_candidate(self, element):
        try:
            element.click()
            return
        except Exception:
            pass

        candidate = element
        for xpath in (
            './ancestor::div[@role="listitem"][1]',
            './ancestor::div[@tabindex="-1"][1]',
            './ancestor::div[@role="row"][1]',
        ):
            try:
                candidate = element.find_element(By.XPATH, xpath)
                candidate.click()
                return
            except Exception:
                continue

        raise RuntimeError("matched chat row was not clickable.")

    def _replace_text(self, element, value):
        element.click()
        element.send_keys(Keys.COMMAND, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(value)

    def _find_first_visible(self, driver, xpaths, timeout):
        deadline = time.time() + timeout
        while time.time() < deadline:
            for xpath in xpaths:
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    if element.is_displayed():
                        return element
                except Exception:
                    continue
            time.sleep(0.5)
        raise TimeoutException(f"Timed out waiting for WhatsApp element: {xpaths}")
