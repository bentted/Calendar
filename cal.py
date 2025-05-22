import calendar
import locale
import json
import os
from datetime import datetime, timedelta
import time

# Default to current month and year
now = datetime.now()
yy = now.year
mm = now.month

EVENTS_FILE = "calendar_events.json"

# Function to load all events
def load_all_events():
    if not os.path.exists(EVENTS_FILE):
        return {}
    try:
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

# Function to save all events
def save_all_events(data):
    try:
        with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    try:
    # Your code that may raise an IOError
    print(f"Error: Could not save events to {EVENTS_FILE}")
except IOError:
    print(f"Error: Could not save events to {EVENTS_FILE}")


# Define locales for common languages
locales_to_try = {
    'English': 'en_US.UTF-8',
    'Spanish': 'es_ES.UTF-8',
    'French': 'fr_FR.UTF-8',
    'German': 'de_DE.UTF-8',
    'Chinese': 'zh_CN.UTF-8'
}

windows_locales = {
    'English': 'English_United States.1252',
    'Spanish': 'Spanish_Spain.1252',
    'French': 'French_France.1252',
    'German': 'German_Germany.1252',
    'Chinese': 'Chinese_Simplified.936'
}

# Function to handle recurring events
def handle_recurring_events(events):
    today = datetime.now().date()
    recurring_events = []
    for year, months in events.items():
        for month, days in months.items():
            for day, hours in days.items():
                for hour, event in hours.items():
                    if isinstance(event, dict) and event.get("recurring"):
                        recurring_events.append((year, month, day, hour, event))
    for year, month, day, hour, event in recurring_events:
        event_date = datetime(int(year), int(month), int(day)).date()
        if event_date < today:
            next_date = event_date + timedelta(days=event["interval"])
            while next_date < today:
                next_date += timedelta(days=event["interval"])
            year_str, month_str, day_str = str(next_date.year), str(next_date.month), str(next_date.day)
            events.setdefault(year_str, {}).setdefault(month_str, {}).setdefault(day_str, {})[hour] = event
            del events[year][month][day][hour]
            if not events[year][month][day]:
                del events[year][month][day]
            if not events[year][month]:
                del events[year][month]
            if not events[year]:
                del events[year]
    return events

# Function to notify upcoming events
def notify_upcoming_events(events):
    today = datetime.now()
    for year, months in events.items():
        for month, days in months.items():
            for day, hours in days.items():
                for hour, event in hours.items():
                    event_time = datetime(int(year), int(month), int(day), int(hour))
                    if today <= event_time <= today + timedelta(minutes=30):
                        print(f"Upcoming Event: {event} at {event_time.strftime('%Y-%m-%d %H:%M')}")

# Function to select month and year
def select_month_and_year():
    global yy, mm
    while True:
        try:
            year_input = input("Enter year (or press Enter for current year): ")
            month_input = input("Enter month (1-12, or press Enter for current month): ")
            yy = int(year_input) if year_input else now.year
            mm = int(month_input) if month_input else now.month
            if 1 <= mm <= 12:
                break
            else:
                print("Invalid month. Please enter a number between 1 and 12.")
        except ValueError:
            print("Invalid input. Please enter valid numbers for year and month.")

# Load events and handle recurring events
all_events = load_all_events()
all_events = handle_recurring_events(all_events)
save_all_events(all_events)

# Notify about upcoming events
notify_upcoming_events(all_events)

# Allow user to select month and year
select_month_and_year()

print(f"Calendar for {calendar.month_name[mm]} {yy}\\n")

# Create a list of languages for the menu
language_options = list(windows_locales.keys())

print("Please select a language for the calendar:")
for i, lang_name in enumerate(language_options):
    print(f"{i + 1}. {lang_name}")

while True:
    try:
        choice = input(f"Enter a number (1-{len(language_options)}): ")
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(language_options):
            selected_lang_name = language_options[choice_index]
            loc_name = windows_locales[selected_lang_name]
            generic_loc_name = locales_to_try.get(selected_lang_name)
            
            print(f"\\nDisplaying calendar for {selected_lang_name}:\\n")
            calendar_displayed_successfully = False
            try:
                locale.setlocale(locale.LC_ALL, loc_name)
                print(f"--- {selected_lang_name} ({loc_name}) ---")
                print(calendar.month(yy, mm))
                calendar_displayed_successfully = True
            except locale.Error as e:
                print(f"Could not set Windows-specific locale for {selected_lang_name} ({loc_name}): {e}")
                if generic_loc_name and generic_loc_name != loc_name:
                    print(f"Trying generic locale: {generic_loc_name}")
                    try:
                        locale.setlocale(locale.LC_ALL, generic_loc_name)
                        print(f"--- {selected_lang_name} ({generic_loc_name}) ---")
                        print(calendar.month(yy, mm))
                        calendar_displayed_successfully = True
                    except locale.Error as e_generic:
                        print(f"Could not set generic locale for {selected_lang_name} ({generic_loc_name}) either: {e_generic}")
                        print(f"Skipping {selected_lang_name} as locale setup failed.")
                else:
                    print(f"No generic fallback locale defined or it's the same. Skipping {selected_lang_name}.")
            
            if calendar_displayed_successfully:
                all_events = load_all_events()
                year_str = str(yy)
                month_key_str = str(mm)

                while True: 
                    action = input(f"For {calendar.month_name[mm]} {year_str}, manage events or type 'done'? (add/edit/view/delete/done): ").lower()
                    
                    if action == 'done':
                        break
                    
                    if action == 'view':
                        month_events_data = all_events.get(year_str, {}).get(month_key_str, {})
                        if not month_events_data:
                            print(f"No events scheduled for {calendar.month_name[mm]} {year_str}.")
                        else:
                            print(f"\\nEvents for {calendar.month_name[mm]} {year_str}:")
                            for day_key in sorted(month_events_data.keys(), key=int):
                                day_data = month_events_data[day_key]
                                print(f"  Day {day_key}:")
                                for hour_key in sorted(day_data.keys(), key=int):
                                    event_detail = day_data[hour_key]
                                    print(f"    Hour {hour_key}:00 - {event_detail}")
                            print("") 
                        continue

                    if action in ['add', 'edit', 'delete']:
                        max_day = calendar.monthrange(yy, mm)[1]
                        while True:
                            try:
                                day_input = input(f"Enter the day of the month (1-{max_day}): ")
                                day = int(day_input)
                                if 1 <= day <= max_day:
                                    break
                                else:
                                    print(f"Invalid day. Please enter a number between 1 and {max_day}.")
                            except ValueError:
                                print("Invalid input. Please enter a number for the day.")
                        day_str = str(day)

                        while True:
                            try:
                                hour_input = input("Enter the hour (0-23, e.g., 9 for 9 AM, 14 for 2 PM): ")
                                hour = int(hour_input)
                                if 0 <= hour <= 23:
                                    break
                                else:
                                    print("Invalid hour. Please enter a number between 0 and 23.")
                            except ValueError:
                                print("Invalid input. Please enter a number for the hour.")
                        hour_str = str(hour)

                        current_event = all_events.get(year_str, {}).get(month_key_str, {}).get(day_str, {}).get(hour_str, "No event scheduled.")
                        
                        if action == 'delete':
                            if year_str in all_events and \
                               month_key_str in all_events.get(year_str, {}) and \
                               day_str in all_events.get(year_str, {}).get(month_key_str, {}) and \
                               hour_str in all_events.get(year_str, {}).get(month_key_str, {}).get(day_str, {}):
                                
                                del all_events[year_str][month_key_str][day_str][hour_str]
                                print("Event deleted.")
                                
                                if not all_events[year_str][month_key_str][day_str]:
                                    del all_events[year_str][month_key_str][day_str]
                                if not all_events[year_str][month_key_str]:
                                    del all_events[year_str][month_key_str]
                                if not all_events[year_str]:
                                    del all_events[year_str]
                                save_all_events(all_events)
                            else:
                                print(f"No event found for Day {day_str}, Hour {hour_str}:00 to delete.")
                        elif action in ['add', 'edit']:
                            if action == 'add':
                                print(f"Current event for Day {day_str}, Hour {hour_str}:00: {current_event}")
                                event_text = input(f"Enter event text for Day {day_str}, Hour {hour_str}:00: ")
                                if event_text:
                                    is_recurring = input("Is this a recurring event? (yes/no): ").lower() == 'yes'
                                    if is_recurring:
                                        while True:
                                            try:
                                                interval = int(input("Enter recurrence interval in days: "))
                                                break
                                            except ValueError:
                                                print("Invalid input. Please enter a number for the interval.")
                                        event_data = {"text": event_text, "recurring": True, "interval": interval}
                                    else:
                                        event_data = event_text
                                    year_events = all_events.setdefault(year_str, {})
                                    month_events = year_events.setdefault(month_key_str, {})
                                    day_events = month_events.setdefault(day_str, {})
                                    day_events[hour_str] = event_data
                                    print("Event saved.")
                                    save_all_events(all_events)
                                else:
                                    print("Event text cannot be empty. No event added.")
                            elif action == 'edit':
                                if current_event == "No event scheduled.":
                                    print("No event scheduled to edit.")
                                else:
                                    print(f"Current event for Day {day_str}, Hour {hour_str}:00: {current_event}")
                                    event_text = input(f"Enter new event text for Day {day_str}, Hour {hour_str}:00 (leave blank to keep current): ")
                                    if event_text:
                                        is_recurring = input("Is this a recurring event? (yes/no): ").lower() == 'yes'
                                        if is_recurring:
                                            while True:
                                                try:
                                                    interval = int(input("Enter recurrence interval in days: "))
                                                    break
                                                except ValueError:
                                                    print("Invalid input. Please enter a number for the interval.")
                                            event_data = {"text": event_text, "recurring": True, "interval": interval}
                                        else:
                                            event_data = event_text
                                        year_events = all_events.setdefault(year_str, {})
                                        month_events = year_events.setdefault(month_key_str, {})
                                        day_events = month_events.setdefault(day_str, {})
                                        day_events[hour_str] = event_data
                                        print("Event updated.")
                                        save_all_events(all_events)
                                    else:
                                        print("No changes made to the event.")
                        else:
                            print("Invalid action. Please type 'add', 'edit', 'view', 'delete', or 'done'.")



import locale

try:
    locale.setlocale(locale.LC_ALL, '')  # Empty string for default system locale
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C')  # Fallback to C locale
    except locale.Error:
        print("Could not reset to default locale.")
finally:
    print("Locale reset attempt completed.")



