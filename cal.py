import calendar
import locale
import json # New
import os   # New

yy = 2025
mm = 4

EVENTS_FILE = "calendar_events.json" # New

# New function
def load_all_events():
    if not os.path.exists(EVENTS_FILE):
        return {}
    try:
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            # Handle empty file case
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

# New function
def save_all_events(data):
    try:
        with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError:
        print(f"Error: Could not save events to {EVENTS_FILE}")

# Define a list of locales for common languages
# Format: (language_code, encoding)
# You might need to ensure these locales are supported on your system
# For Windows, locale names can be like 'Spanish_Spain', 'French_France', 'German_Germany', 'Chinese_Simplified'
# For Linux/macOS, they are usually like 'es_ES.UTF-8', 'fr_FR.UTF-8', 'de_DE.UTF-8', 'zh_CN.UTF-8'
# This is a generic list, actual names might vary.
locales_to_try = {
    'English': 'en_US.UTF-8',  # Default
    'Spanish': 'es_ES.UTF-8',
    'French': 'fr_FR.UTF-8',
    'German': 'de_DE.UTF-8',
    'Chinese': 'zh_CN.UTF-8'
}

# Windows-specific locale names (common examples)
windows_locales = {
    'English': 'English_United States.1252', # Or just 'en_US' or 'English'
    'Spanish': 'Spanish_Spain.1252', # Or 'es_ES' or 'Spanish'
    'French': 'French_France.1252', # Or 'fr_FR' or 'French'
    'German': 'German_Germany.1252', # Or 'de_DE' or 'German'
    'Chinese': 'Chinese_Simplified.936' # Or 'zh_CN' or 'Chinese (Simplified)'
}

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
            calendar_displayed_successfully = False # New flag
            try:
                locale.setlocale(locale.LC_ALL, loc_name)
                print(f"--- {selected_lang_name} ({loc_name}) ---")
                print(calendar.month(yy, mm))
                calendar_displayed_successfully = True # Set flag
            except locale.Error as e:
                print(f"Could not set Windows-specific locale for {selected_lang_name} ({loc_name}): {e}")
                if generic_loc_name and generic_loc_name != loc_name:
                    print(f"Trying generic locale: {generic_loc_name}")
                    try:
                        locale.setlocale(locale.LC_ALL, generic_loc_name)
                        print(f"--- {selected_lang_name} ({generic_loc_name}) ---")
                        print(calendar.month(yy, mm))
                        calendar_displayed_successfully = True # Set flag
                    except locale.Error as e_generic:
                        print(f"Could not set generic locale for {selected_lang_name} ({generic_loc_name}) either: {e_generic}")
                        print(f"Skipping {selected_lang_name} as locale setup failed.")
                else:
                    print(f"No generic fallback locale defined or it's the same. Skipping {selected_lang_name}.")
            
            if calendar_displayed_successfully: # New block: Event management
                all_events = load_all_events()
                year_str = str(yy)
                # mm is an int, used directly with calendar.month_name
                # For dictionary keys, ensure consistency if needed, but direct int mm is fine for calendar.month_name
                month_key_str = str(mm) # Use a string key for consistency in the JSON structure

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
                            print(f"Current event for Day {day_str}, Hour {hour_str}:00: {current_event}")
                            event_text_prompt = f"Enter event text for Day {day_str}, Hour {hour_str}:00 (leave blank to keep current if editing, or type new event): "
                            event_text = input(event_text_prompt)
                            if event_text: 
                                year_events = all_events.setdefault(year_str, {})
                                month_events = year_events.setdefault(month_key_str, {})
                                day_events = month_events.setdefault(day_str, {})
                                day_events[hour_str] = event_text
                                print("Event saved.")
                                save_all_events(all_events)
                            elif action == 'add' and not event_text:
                                print("Event text cannot be empty for a new event. No event added.")
                            else: # Blank input during 'edit'
                                print("No changes made to the event.")
                    else:
                        print("Invalid action. Please type 'add', 'edit', 'view', 'delete', or 'done'.")
            # End of new event management block
            break  # Exit the language selection while True loop
        else:
            print(f"Invalid choice. Please enter a number between 1 and {len(language_options)}.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        break # Exit on other unexpected errors

print("\\n")

# Reset to default locale (optional, but good practice)
try:
    locale.setlocale(locale.LC_ALL, '') # Empty string for default system locale
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C') # Fallback to C locale
    except locale.Error:
        print("Could not reset to default locale.")

