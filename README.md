# Python Calendar with Event Management

## Description

This is a command-line Python application that displays a calendar for a specific month and year, and allows users to manage (add, edit, view, delete) text-based events for specific days and hours. Events are saved locally in a JSON file (`calendar_events.json`) for persistence across sessions. The application also supports displaying the calendar in multiple languages.

## Features

*   **Calendar Display:** Shows the calendar for a pre-set month and year (currently April 2025).
*   **Language Selection:** Users can choose to display the calendar in one of the following languages:
    *   English
    *   Spanish
    *   French
    *   German
    *   Chinese (Simplified)
    *(Note: Availability of these languages depends on the locales installed on your operating system.)*
*   **Event Management:**
    *   **Add Event:** Add a text-based event to a specific day and hour of the selected month.
    *   **Edit Event:** Modify an existing event.
    *   **View Events:** Display all scheduled events for the selected month, showing the day, hour, and event description.
    *   **Delete Event:** Remove an event from a specific day and hour.
*   **Event Persistence:** Events are automatically saved to `calendar_events.json` and loaded when the application starts.

## Requirements

*   Python 3.x
*   Operating system with support for the desired locales (for language selection).

## How to Run

1.  Ensure you have Python 3 installed.
2.  Save the script as `cal.py` (or the name you have chosen) in a directory.
3.  Open a terminal or command prompt.
4.  Navigate to the directory where you saved the script.
5.  Run the script using the command:
    ```bash
    python cal.py
    ```
6.  Follow the on-screen prompts to select a language and manage calendar events.

## File Structure

*   `cal.py`: The main Python script for the application.
*   `calendar_events.json`: This file is automatically created in the same directory as `cal.py` when you first save an event. It stores all your calendar events.

## Event Data Structure

Events are stored in `calendar_events.json` in a nested dictionary structure:

```json
{
    "YYYY": { // Year as a string
        "MM": { // Month as a string
            "DD": { // Day as a string
                "HH": "Event description text" // Hour as a string (0-23)
            }
        }
    }
}
```
For example:
```json
{
    "2025": {
        "4": {
            "15": {
                "10": "Doctor's Appointment",
                "14": "Team Meeting"
            },
            "20": {
                "9": "Grocery Shopping"
            }
        }
    }
}
```

## Future Enhancements (Potential)

*   Allow users to select the year and month for the calendar view.
*   Implement a more user-friendly interface (e.g., using a library like `curses` or a GUI framework like Tkinter or PyQt).
*   Add support for recurring events.
*   Implement event reminders or notifications.
*   Improve error handling and input validation.
