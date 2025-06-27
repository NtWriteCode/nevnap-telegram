import os
import json
import telegram
import logging
import asyncio
from datetime import date, timedelta, datetime, time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def load_name_day_calendar():
    """Loads the name day calendar from the local JSON file."""
    try:
        with open("nevnapok.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("nevnapok.json not found.")
        return None
    except json.JSONDecodeError:
        logging.error("Error parsing name day calendar JSON.")
        return None

def get_name_days_from_calendar(calendar, month, day):
    """Gets the main and other name days for a specific date from the calendar."""
    try:
        month_str = str(month)
        day_str = str(day)
        day_data = calendar.get(month_str, {}).get(day_str, {})
        main_names = day_data.get("main", [])
        other_names = day_data.get("other", [])
        
        if not main_names and not other_names:
             raise KeyError

        return {"main": main_names, "other": other_names}
    except KeyError:
        logging.warning(f"No name day found for {month}-{day}")
        return {"main": ["Nincs névnap"], "other": []}


async def send_telegram_message(message):
    """Sends a message to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram bot token or chat ID is not set.")
        return

    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)  # type: ignore
        logging.info("Telegram message sent successfully.")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")

async def job(name_day_calendar):
    """The job to be run daily."""
    logging.info("Running daily name day job...")
    if not name_day_calendar:
        logging.error("Name day calendar is not loaded. Skipping job.")
        return

    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_data = get_name_days_from_calendar(name_day_calendar, today.month, today.day)
    tomorrow_data = get_name_days_from_calendar(name_day_calendar, tomorrow.month, tomorrow.day)

    # Format today's message part
    today_main_str = ", ".join(today_data["main"]) if today_data["main"] else "Nincs"
    today_msg = f"🇭🇺 Mai névnap: {today_main_str}"
    if today_data["other"]:
        today_other_str = ", ".join(today_data["other"])
        today_msg += f"\n(Továbbiak: {today_other_str})"

    # Format tomorrow's message part
    tomorrow_main_str = ", ".join(tomorrow_data["main"]) if tomorrow_data["main"] else "Nincs"
    tomorrow_msg = f"🇭🇺 Holnapi névnap: {tomorrow_main_str}"
    if tomorrow_data["other"]:
        tomorrow_other_str = ", ".join(tomorrow_data["other"])
        tomorrow_msg += f"\n(Továbbiak: {tomorrow_other_str})"

    message = f"{today_msg}\n\n{tomorrow_msg}"
    
    await send_telegram_message(message)

async def main():
    """The main entry point for the service."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables must be set.")
        return

    name_day_calendar = load_name_day_calendar()
    if not name_day_calendar:
        logging.error("Could not start due to missing name day calendar.")
        return

    logging.info("Service started.")

    # Run immediately on startup
    await job(name_day_calendar)

    while True:
        now = datetime.now()
        # Set the target time for 10:00 AM
        run_time = time(10, 0)
        
        # Calculate the next run time
        next_run_datetime = datetime.combine(now.date(), run_time)
        if now.time() >= run_time:
            # If it's already past 10:00 AM, schedule for tomorrow
            next_run_datetime += timedelta(days=1)

        wait_seconds = (next_run_datetime - now).total_seconds()
        
        logging.info(f"Next job scheduled for {next_run_datetime}. Waiting for {wait_seconds:.0f} seconds.")
        await asyncio.sleep(wait_seconds)
        
        await job(name_day_calendar)

if __name__ == "__main__":
    asyncio.run(main())
