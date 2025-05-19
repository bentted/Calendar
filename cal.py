import calendar
import locale

yy = 2025
mm = 4

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
            try:
                locale.setlocale(locale.LC_ALL, loc_name)
                print(f"--- {selected_lang_name} ({loc_name}) ---")
                print(calendar.month(yy, mm))
            except locale.Error as e:
                print(f"Could not set Windows-specific locale for {selected_lang_name} ({loc_name}): {e}")
                if generic_loc_name and generic_loc_name != loc_name:
                    print(f"Trying generic locale: {generic_loc_name}")
                    try:
                        locale.setlocale(locale.LC_ALL, generic_loc_name)
                        print(f"--- {selected_lang_name} ({generic_loc_name}) ---")
                        print(calendar.month(yy, mm))
                    except locale.Error as e_generic:
                        print(f"Could not set generic locale for {selected_lang_name} ({generic_loc_name}) either: {e_generic}")
                        print(f"Skipping {selected_lang_name} as locale setup failed.")
                else:
                    print(f"No generic fallback locale defined or it's the same. Skipping {selected_lang_name}.")
            break  # Exit the loop after successful processing or attempt
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

