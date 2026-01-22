"""
FORM AUTO-FILLER - ASYNC VERSION WITH STATUS UPDATES
====================================================
Parallel form automation with Google Sheets status updates

Author: AI Development Team
Version: 4.0.0 - ASYNC EDITION
Date: 2025-01-21
"""

import pandas as pd
from playwright.async_api import async_playwright
import asyncio
import time
from datetime import datetime
import json
import os
from typing import Dict, List, Tuple, Optional
import traceback
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# =========================
# CONFIGURATION MANAGEMENT
# =========================

class Config:
    """Centralized configuration management"""
    # Google Sheets Configuration
    GOOGLE_SHEETS_ID = "1ZuplfaKjpco06iYjlF_MgeDZkoOTaVrymP-4O4jZpPE"
    WEBSITE_SHEET_RANGE = "'Database'!A:A"            # Sheet 1: Website URLs (header + urls)
    DETAILS_SHEET_RANGE = "'Details to fill'!A:E"    # Sheet 2: Form details (header + row)
    STATUS_COLUMN_RANGE = "'Database'!B:B"           # Status column (Column B)
    CREDENTIALS_FILE = "form-automation-484413-7257a92cfa90.json"

    # Scopes required for Google Sheets API (READ + WRITE)
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # Parallel Processing
    MAX_PARALLEL_WORKERS = 3  # Number of parallel browser instances

    # Default Field Values
    DEFAULT_VALUES = {
        "name": "Interested Customer",
        "email": "contact.inquiry@example.com",
        "phone": "9876543210",
        "message": "Hello, I am interested in your services and would like to discuss further. Please contact me.",
        "country": "India",
    }

    # Smart Default Mappings
    SMART_DEFAULTS = {
        "job": "Business Owner",
        "company": "Private Business",
        "position": "Manager",
        "designation": "Director",
        "organization": "Self Employed",
        "profession": "Entrepreneur",
        "occupation": "Business",
        "country": "India",
        "city": "Delhi",
        "state": "Delhi",
        "address": "Delhi, India",
        "gender": "Male",
        "age": "30",
        "subject": "General Inquiry",
        "topic": "Business Inquiry",
        "department": "Sales",
        "website": "www.example.com",
        "title": "Mr",
    }

    # CAPTCHA Settings
    CAPTCHA_WAIT_TIME = 15
    CAPTCHA_CHECK_INTERVAL = 0.2
    CAPTCHA_RECHECK_ATTEMPTS = 5
    AUTO_CLICK_CAPTCHA = True

    # Performance Settings - OPTIMIZED
    ANIMATION_DELAY = 0.03
    PAGE_LOAD_TIMEOUT = 25000
    ELEMENT_TIMEOUT = 1200
    FIELD_FILL_DELAY = 4

    # Retry Settings
    MAX_RETRIES = 2
    RETRY_DELAY = 2

    # Browser Settings
    HEADLESS = True
    SLOW_MO = 50


# =========================
# GOOGLE SHEETS API CLIENT
# =========================

class GoogleSheetsClient:
    """Handle Google Sheets API with READ + WRITE capabilities"""

    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            print("🔐 Authenticating with Google Sheets API...")
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=Config.SCOPES
            )
            self.service = build('sheets', 'v4', credentials=creds)
            print("✅ Successfully authenticated with Google Sheets API (READ + WRITE)")
        except FileNotFoundError:
            print(f"❌ Credentials file not found: {self.credentials_file}")
            raise
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            raise

    def update_status(self, spreadsheet_id: str, row_number: int, status: str):
        """Update status in Google Sheet (Column B)"""
        try:
            # row_number here is expected to be zero-based index of the first data row (0 => row 2 in sheet)
            sheet_row = row_number + 2  # convert to sheet 1-indexed row (row 1 = header)
            range_name = f"Database!B{sheet_row}"
            body = {'values': [[status]]}
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            print(f"✅ Updated status in row {sheet_row}: {status}")
        except Exception as e:
            print(f"❌ Failed to update status: {str(e)}")

    def read_two_sheets(self, spreadsheet_id: str, websites_range: str, details_range: str) -> pd.DataFrame:
        """Read from two sheets and combine data"""
        try:
            # Read websites from Sheet 1
            print("\n📋 Reading Website URLs from Sheet 1...")
            websites_result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=websites_range
            ).execute()

            websites_values = websites_result.get('values', [])
            if not websites_values or len(websites_values) <= 1:
                print("❌ No website URLs found in Sheet 1")
                return pd.DataFrame()

            # Assume first row is header and subsequent rows are URLs
            websites = [row[0] for row in websites_values[1:] if row and len(row) > 0]
            print(f"✅ Found {len(websites)} website URLs")

            # Read details from Sheet 2
            print("\n📋 Reading Form Details from Sheet 2...")
            details_result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=details_range
            ).execute()

            details_values = details_result.get('values', [])
            if not details_values or len(details_values) <= 1:
                print("❌ No form details found in Sheet 2")
                return pd.DataFrame()

            details_df = pd.DataFrame(details_values[1:], columns=details_values[0])
            print(f"✅ Found form details with columns: {', '.join(details_df.columns)}")

            if len(details_df) == 0:
                print("❌ No data rows in details sheet")
                return pd.DataFrame()

            form_data = details_df.iloc[0].to_dict()

            combined_data = []
            for idx, website in enumerate(websites):
                row_data = {
                    'website': website,
                    'row_index': idx  # Store original row index for status updates (0-based for data rows)
                }
                row_data.update(form_data)
                combined_data.append(row_data)

            final_df = pd.DataFrame(combined_data)

            print(f"\n✅ Successfully combined data:")
            print(f"   Total websites to process: {len(final_df)}")

            return final_df

        except HttpError as error:
            print(f"❌ HTTP Error reading sheets: {error}")
            try:
                status_code = error.resp.status
            except:
                status_code = None
            if status_code == 403:
                print("🔒 Access denied (403). Make sure you shared the sheet with the service account email.")
                try:
                    with open(self.credentials_file, 'r') as f:
                        j = json.load(f)
                        client_email = j.get('client_email')
                        if client_email:
                            print("   Share with this email:", client_email)
                except Exception:
                    pass
            elif status_code == 400:
                print("400 Bad Request — likely the range or sheet name is invalid. Verify the tab names and that the range is correct.")
            raise
        except Exception as e:
            print(f"❌ Error reading multiple sheets: {str(e)}")
            raise


# =========================
# ASYNC CAPTCHA HANDLER
# =========================

class AsyncCaptchaHandler:
    """Async CAPTCHA detection and handling"""

    CAPTCHA_SELECTORS = [
        "iframe[src*='recaptcha']",
        "iframe[src*='google.com/recaptcha']",
        "div.g-recaptcha",
        ".g-recaptcha",
        "iframe[src*='hcaptcha']",
        "div.h-captcha",
        ".h-captcha",
        "div:has-text('I am not a robot')",
    ]

    @staticmethod
    async def detect(page) -> Tuple[bool, str]:
        """Detect if CAPTCHA is present"""
        for attempt in range(Config.CAPTCHA_RECHECK_ATTEMPTS):
            for selector in AsyncCaptchaHandler.CAPTCHA_SELECTORS:
                try:
                    elements = page.locator(selector)
                    if await elements.count() > 0:
                        for i in range(min(await elements.count(), 5)):
                            try:
                                elem = elements.nth(i)
                                if await elem.is_visible(timeout=300):
                                    box = await elem.bounding_box()
                                    if box and box['width'] > 10 and box['height'] > 10:
                                        return True, selector
                            except:
                                continue
                except:
                    continue
            if attempt < Config.CAPTCHA_RECHECK_ATTEMPTS - 1:
                await asyncio.sleep(0.2)
        return False, ""

    @staticmethod
    async def auto_click_captcha(page) -> bool:
        """Automatically click CAPTCHA checkbox if found"""
        if not Config.AUTO_CLICK_CAPTCHA:
            return False

        print("🤖 Attempting automatic CAPTCHA checkbox click...")

        checkbox_selectors = [
            "iframe[src*='recaptcha'][src*='anchor']",
            "iframe[title='reCAPTCHA']",
            "iframe[src*='hcaptcha'][src*='checkbox']",
        ]

        for selector in checkbox_selectors:
            try:
                iframe_elements = page.locator(selector)
                if await iframe_elements.count() > 0:
                    for i in range(await iframe_elements.count()):
                        try:
                            iframe = iframe_elements.nth(i)
                            if not await iframe.is_visible(timeout=1000):
                                continue
                            frame = await iframe.content_frame()
                            if frame:
                                checkbox_clicks = [
                                    "div.recaptcha-checkbox-border",
                                    ".recaptcha-checkbox",
                                    "#recaptcha-anchor",
                                    "div[role='checkbox']",
                                ]
                                for click_selector in checkbox_clicks:
                                    try:
                                        checkbox = frame.locator(click_selector)
                                        if await checkbox.count() > 0 and await checkbox.first.is_visible(timeout=500):
                                            await checkbox.first.click(timeout=2000)
                                            await asyncio.sleep(1)
                                            print("✅ CAPTCHA checkbox clicked successfully!")
                                            return True
                                    except:
                                        continue
                        except:
                            continue
            except:
                continue

        return False

    @staticmethod
    async def wait_for_solve(page, timeout: int = Config.CAPTCHA_WAIT_TIME) -> bool:
        """Wait for CAPTCHA solve with auto-click"""
        if Config.AUTO_CLICK_CAPTCHA:
            if await AsyncCaptchaHandler.auto_click_captcha(page):
                await asyncio.sleep(2)
                has_captcha, _ = await AsyncCaptchaHandler.detect(page)
                if not has_captcha:
                    print("\n✅ CAPTCHA AUTO-SOLVED! Continuing...\n")
                    return True
                else:
                    for wait_attempt in range(10):
                        await asyncio.sleep(1)
                        has_captcha_recheck, _ = await AsyncCaptchaHandler.detect(page)
                        if not has_captcha_recheck:
                            print("\n✅ CAPTCHA VERIFIED! Continuing...\n")
                            return True

        print("\n" + "="*90)
        print("🤖 CAPTCHA DETECTED - MANUAL INTERVENTION MAY BE REQUIRED")
        print(f"⏰ You have {timeout} seconds to solve")
        print("="*90 + "\n")

        start = time.time()
        while (time.time() - start) < timeout:
            has_captcha, _ = await AsyncCaptchaHandler.detect(page)
            if not has_captcha:
                await asyncio.sleep(0.5)
                has_captcha_recheck, _ = await AsyncCaptchaHandler.detect(page)
                if not has_captcha_recheck:
                    print("\n✅ CAPTCHA SOLVED! Continuing...\n")
                    await asyncio.sleep(1)
                    return True
            await asyncio.sleep(Config.CAPTCHA_CHECK_INTERVAL)

        print("\n⏱️ CAPTCHA timeout reached - Moving to next website\n")
        return False


# =========================
# ASYNC FIELD FILLER
# =========================

class AsyncFieldFiller:
    """Async field filling operations"""

    @staticmethod
    async def fill_text(element, value: str) -> bool:
        """Fill text input or textarea"""
        try:
            if not await element.is_visible(timeout=600):
                return False

            await element.scroll_into_view_if_needed(timeout=Config.ELEMENT_TIMEOUT)
            await asyncio.sleep(0.02)

            await element.click(timeout=Config.ELEMENT_TIMEOUT, force=True)
            await asyncio.sleep(0.01)

            await element.evaluate("el => el.value = ''")
            # select all then type
            try:
                await element.press("Control+a")
            except:
                pass
            await asyncio.sleep(0.01)

            await element.type(str(value), delay=Config.FIELD_FILL_DELAY)
            await asyncio.sleep(0.05)

            await element.evaluate("el => ['input', 'change', 'blur'].forEach(evt => el.dispatchEvent(new Event(evt, {bubbles: true})))")

            await asyncio.sleep(0.02)
            return True

        except:
            return False

    @staticmethod
    async def fill_dropdown(element, value: str) -> bool:
        """Fill dropdown"""
        try:
            await element.scroll_into_view_if_needed(timeout=Config.ELEMENT_TIMEOUT)
            await asyncio.sleep(0.1)

            options = await element.evaluate("""
                el => Array.from(el.options).map(opt => ({
                    text: opt.text.trim(),
                    value: opt.value,
                    index: opt.index
                }))
            """)

            if not options:
                return False

            value_lower = str(value).lower()

            # Try exact match
            for opt in options:
                if opt['text'].lower() == value_lower:
                    try:
                        await element.select_option(value=opt['value'])
                        await asyncio.sleep(0.1)
                        return True
                    except:
                        pass

            # Try contains match
            for opt in options:
                if value_lower in opt['text'].lower():
                    try:
                        await element.select_option(value=opt['value'])
                        await asyncio.sleep(0.1)
                        return True
                    except:
                        pass

            # Fallback: select first non-placeholder
            placeholders = ['select', 'choose', '--', 'please']
            for opt in options:
                if opt['text'] and not any(p in opt['text'].lower() for p in placeholders):
                    try:
                        await element.select_option(value=opt['value'])
                        await asyncio.sleep(0.1)
                        return True
                    except:
                        pass

            return False

        except:
            return False


# =========================
# ASYNC FORM PROCESSOR
# =========================

class AsyncFormProcessor:
    """Async form processing"""

    def __init__(self, page, row, website: str, sheets_client: GoogleSheetsClient, row_index: int):
        self.page = page
        self.row = row
        self.website = website
        self.sheets_client = sheets_client
        self.row_index = row_index
        self.filled_count = 0
        self.total_fields = 0

    def get_value(self, field_name: str) -> str:
        """Get value for field"""
        field_mapping = {
            'name': 'Name',
            'email': 'Email',
            'phone': 'Phone',
            'message': 'Message',
            'country': 'Country',
        }

        sheet_column = field_mapping.get(field_name.lower(), field_name)
        value = self.row.get(sheet_column, "")

        if pd.isna(value) or not str(value).strip():
            value = self.row.get(field_name, "")

        if not pd.isna(value) and str(value).strip():
            return str(value).strip()

        if field_name in Config.DEFAULT_VALUES:
            return Config.DEFAULT_VALUES[field_name]

        field_lower = field_name.lower()
        for key, default_val in Config.SMART_DEFAULTS.items():
            if key in field_lower or field_lower in key:
                return default_val

        return "N/A"

    async def process_all_fields(self) -> int:
        """Process all form fields"""
        try:
            input_count = await self.page.locator("input:visible:not([type='hidden']):not([type='submit']):not([type='button'])").count()
            textarea_count = await self.page.locator("textarea:visible").count()
            select_count = await self.page.locator("select:visible").count()

            self.total_fields = input_count + textarea_count + select_count

            if self.total_fields == 0:
                return 0

            print(f"   Found {input_count} inputs, {textarea_count} textareas, {select_count} dropdowns")

            # Fill inputs
            all_inputs = await self.page.locator("input:visible:not([type='hidden']):not([type='submit']):not([type='button'])").all()
            for inp in all_inputs:
                try:
                    field_type = await self.detect_field_type(inp)
                    value = self.get_value(field_type)
                    if await AsyncFieldFiller.fill_text(inp, value):
                        self.filled_count += 1
                        await asyncio.sleep(Config.ANIMATION_DELAY)
                except:
                    continue

            # Fill textareas
            all_textareas = await self.page.locator("textarea:visible").all()
            for ta in all_textareas:
                try:
                    value = self.get_value('message')
                    if await AsyncFieldFiller.fill_text(ta, value):
                        self.filled_count += 1
                        await asyncio.sleep(Config.ANIMATION_DELAY)
                except:
                    continue

            # Fill selects
            all_selects = await self.page.locator("select:visible").all()
            for sel in all_selects:
                try:
                    field_type = await self.detect_field_type(sel)
                    value = self.get_value(field_type)
                    if await AsyncFieldFiller.fill_dropdown(sel, value):
                        self.filled_count += 1
                        await asyncio.sleep(Config.ANIMATION_DELAY)
                except:
                    continue

        except Exception as e:
            print(f"   ❌ Field processing error: {str(e)[:60]}")

        return self.filled_count

    async def detect_field_type(self, element) -> str:
        """Detect field type"""
        try:
            info = await element.evaluate("""
                el => {
                    const labels = el.labels || [];
                    const label = labels[0]?.textContent || '';
                    return {
                        name: el.name || '',
                        id: el.id || '',
                        placeholder: el.placeholder || '',
                        type: el.type || '',
                        label: label
                    };
                }
            """)
            combined = ' '.join([
                info.get('name', ''),
                info.get('id', ''),
                info.get('placeholder', ''),
                info.get('label', '')
            ]).lower()

            if 'email' in combined or info.get('type') == 'email':
                return 'email'
            if 'phone' in combined or 'tel' in combined:
                return 'phone'
            if 'name' in combined:
                return 'name'
            if 'message' in combined or 'comment' in combined:
                return 'message'

            return info.get('name') or info.get('id') or 'unknown'

        except:
            return 'unknown'


# =========================
# ASYNC WORKER
# =========================

async def process_website_async(row, idx: int, total: int, sheets_client: GoogleSheetsClient, playwright_instance):
    """Async worker to process single website"""
    website = str(row.get("website","")).strip()
    row_index = int(row.get('row_index', idx))

    print(f"\n{'='*90}")
    print(f"🌐 [{idx+1}/{total}] {website}")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*90}\n")

    # Update status: PROCESSING
    try:
        sheets_client.update_status(Config.GOOGLE_SHEETS_ID, row_index, "PROCESSING")
    except Exception as e:
        print(f"   ⚠️ Could not update status before processing: {e}")

    browser = None
    try:
        # Launch browser
        browser = await playwright_instance.chromium.launch(
            headless=Config.HEADLESS,
            slow_mo=Config.SLOW_MO
        )

        context = await browser.new_context(
            viewport=None,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        page = await context.new_page()

        # Navigate (wrap in try to handle bad URLs/timeouts)
        try:
            await page.goto(website, wait_until="domcontentloaded", timeout=Config.PAGE_LOAD_TIMEOUT)
            print(f"   ✅ Website loaded")
        except Exception as nav_err:
            print(f"   ❌ Navigation error: {nav_err}")
            sheets_client.update_status(Config.GOOGLE_SHEETS_ID, row_index, "NAV_ERROR")
            return False

        await asyncio.sleep(0.5)

        # Check CAPTCHA
        has_captcha, _ = await AsyncCaptchaHandler.detect(page)
        if has_captcha:
            print(f"   🤖 CAPTCHA detected")
            if not await AsyncCaptchaHandler.wait_for_solve(page):
                try:
                    sheets_client.update_status(Config.GOOGLE_SHEETS_ID, row_index, "CAPTCHA_BLOCKED")
                except:
                    pass
                return False

        # Find contact link
        try:
            contact_found = False
            keywords = ["Contact Us", "Contact", "Get in Touch"]
            for keyword in keywords:
                try:
                    links = page.get_by_role("link", name=keyword, exact=False)
                    if await links.count() > 0:
                        await links.first.click()
                        contact_found = True
                        break
                except:
                    pass

            if contact_found:
                try:
                    await page.wait_for_load_state("domcontentloaded", timeout=10000)
                except:
                    pass
                print(f"   ✅ Contact page opened")
        except:
            pass

        await asyncio.sleep(0.5)

        # Process form
        processor = AsyncFormProcessor(page, row, website, sheets_client, row_index)
        filled = await processor.process_all_fields()

        if filled > 0:
            print(f"   ✅ Filled {filled}/{processor.total_fields} fields")

            # Submit
            try:
                submit_btns = page.locator("button[type='submit']:visible, input[type='submit']:visible")
                if await submit_btns.count() > 0:
                    submit_btn = submit_btns.first
                    await submit_btn.click(timeout=5000)
                    print(f"   ✅ Form submitted")
                    try:
                        sheets_client.update_status(Config.GOOGLE_SHEETS_ID, row_index, "SUCCESS")
                    except:
                        pass
                    await asyncio.sleep(1.5)
                    return True
                else:
                    try:
                        sheets_client.update_status(Config.GOOGLE_SHEETS_ID, row_index, "FILLED")
                    except:
                        pass
                    return True
            except Exception as submit_err:
                print(f"   ⚠️ Submit error: {submit_err}")
                try:
                    sheets_client.update_status(Config.GOOGLE_SHEETS_ID, row_index, "FILLED")
                except:
                    pass
                return True
        else:
            try:
                sheets_client.update_status(Config.GOOGLE_SHEETS_ID, row_index, "NO_FIELDS")
            except:
                pass
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:200]}")
        try:
            sheets_client.update_status(Config.GOOGLE_SHEETS_ID, row_index, "FAILED")
        except:
            pass
        return False

    finally:
        if browser:
            await browser.close()


# =========================
# MAIN ASYNC EXECUTOR
# =========================

async def main_async():
    """Main async execution"""
    print("="*90)
    print("🚀 FORM AUTO-FILLER - ASYNC PARALLEL EDITION v4.0")
    print(f"   ⚡ Max Parallel Workers: {Config.MAX_PARALLEL_WORKERS}")
    print("="*90)
    print()

    # Setup Google Sheets
    sheets_client = GoogleSheetsClient(Config.CREDENTIALS_FILE)

    # Load data
    df = sheets_client.read_two_sheets(
        Config.GOOGLE_SHEETS_ID,
        Config.WEBSITE_SHEET_RANGE,
        Config.DETAILS_SHEET_RANGE
    )

    if df.empty:
        print("❌ No data found")
        return

    print(f"\n✅ Loaded {len(df)} websites\n")

    # Initialize Playwright
    playwright_instance = await async_playwright().start()

    # Process websites in parallel batches
    tasks = []
    for idx, row in df.iterrows():
        task = process_website_async(row, idx, len(df), sheets_client, playwright_instance)
        tasks.append(task)

        # Process in batches
        if len(tasks) >= Config.MAX_PARALLEL_WORKERS or idx == len(df) - 1:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            tasks = []

            # Small delay between batches
            if idx < len(df) - 1:
                await asyncio.sleep(2)

    await playwright_instance.stop()

    print("\n" + "="*90)
    print("✅ ALL PROCESSING COMPLETE - CHECK GOOGLE SHEET STATUS COLUMN")
    print("="*90)


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\n⚠️ Execution interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        traceback.print_exc()
