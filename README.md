# Python Command-Line Calendar with Advanced Event Management

## Description

This Python application provides a versatile command-line calendar. Users can view the calendar for any month and year, manage their schedules with robust event handling (including recurring events and notifications), and view the calendar interface in multiple languages. All events are persistently stored in a local JSON file.

## Core Features

*   **Dynamic Date Navigation:**
    *   Users can input any year and month to display the corresponding calendar.
    *   Defaults to the current month and year if no input is provided.
*   **Multi-Language Calendar Display:**
    *   Offers a selection of languages (English, Spanish, French, German, Chinese) for the calendar interface (month names, day names).
    *   Utilizes system locales for accurate translation, with fallbacks for broader compatibility.
*   **Comprehensive Event Management:**
    *   **Add Events:** Schedule new events for a specific date and hour.
    *   **Edit Events:** Modify existing event details, including text and recurrence.
    *   **View Events:** Display a list of all events scheduled for the selected month, sorted by date and time.
    *   **Delete Events:** Remove events from the calendar.
*   **Recurring Events:**
    *   Mark events as recurring and specify an interval in days.
    *   The application automatically updates past recurring events to their next valid occurrence at startup.
*   **Upcoming Event Notifications:**
    *   At startup, the application checks for and notifies the user of any events scheduled within the next 30 minutes.
*   **Persistent Event Storage:**
    *   Events are saved in a `calendar_events.json` file in the same directory as the script.
    *   This ensures that all scheduled items are retained across sessions.
    *   Handles file creation if it doesn't exist and gracefully manages empty or improperly formatted JSON files.
*   **Command-Line Interface (CLI):**
    *   All interactions are managed through intuitive text-based prompts and responses in the console.

## Requirements

*   Python 3.x
*   Operating system with support for the desired locales (for full language selection functionality).

## How to Run

1.  Ensure you have Python 3 installed on your system.
2.  Save the script as `cal.py` in a directory of your choice.
3.  Open a terminal or command prompt.
4.  Navigate to the directory where you saved `cal.py`.
5.  Execute the script using the command:
    ```bash
    python cal.py
    ```
6.  Follow the on-screen prompts to:
    *   Select a year and month.
    *   Choose a display language for the calendar.
    *   Manage your events (add, edit, view, delete) for the selected month.

## File Structure

*   `cal.py`: The main Python script containing all the application logic.
*   `calendar_events.json`: This JSON file is automatically created/updated in the same directory as `cal.py`. It stores all user-defined events.

## Event Data Structure

Events are stored in `calendar_events.json` using a nested dictionary structure.

**Standard Event:**
```json
{
    "YYYY": { // Year as a string (e.g., "2023")
        "MM": {   // Month as a string (e.g., "12")
            "DD": {   // Day as a string (e.g., "25")
                "HH": "Your event description here" // Hour as a string (0-23)
            }
        }
    }
}
```

**Recurring Event:**
When an event is marked as recurring, its entry includes additional fields:
```json
{
    "YYYY": {
        "MM": {
            "DD": {
                "HH": {
                    "text": "Your recurring event description",
                    "recurring": true,
                    "interval": 7 // Interval in days
                }
            }
        }
    }
}
```
Example:
```json
{
    "2024": {
        "5": {
            "15": {
                "10": "Team Meeting"
            },
            "20": {
                "9": {
                    "text": "Weekly Review",
                    "recurring": true,
                    "interval": 7
                }
            }
        }
    }
}
```

## Potential Future Enhancements

*   More sophisticated date/time input parsing.
*   Search functionality for events.
*   Export/import calendar events in standard formats (e.g., iCalendar).
*   A graphical user interface (GUI) using libraries like Tkinter, PyQt, or Kivy.
*   Customizable notification lead times.
