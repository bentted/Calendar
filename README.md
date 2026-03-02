# Advanced Multi-Language Calendar Application

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Implementations](#implementations)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Data Structure](#data-structure)
- [Architecture](#architecture)
- [GUI Features](#gui-features)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project provides a comprehensive calendar application available in both Python (with GUI) and Rust (command-line) implementations. The application supports multi-language calendar display, advanced event management including recurring events, file attachments, notifications, and persistent data storage.

### Key Highlights
- **Multi-Language Support**: Display calendars in English, Spanish, French, German, and Chinese
- **Dual Implementation**: Full-featured Python GUI and efficient Rust CLI
- **Advanced Event Management**: Recurring events, file attachments, notifications
- **Persistent Storage**: JSON-based data persistence across sessions
- **Theme Support**: Light and dark themes (Python GUI)
- **Notification System**: Desktop notifications and upcoming event alerts

## Features

### Core Calendar Features
- **Dynamic Date Navigation**: Browse any month/year combination
- **Multi-Language Display**: Localized month names and day abbreviations
- **Event Management**: Add, edit, view, and delete events
- **Hourly Scheduling**: Schedule events for specific hours (0-23)
- **Visual Indicators**: Color-coded days with events and today highlighting

### Advanced Event Features
- **Recurring Events**: Set events to repeat at specified day intervals
- **Automatic Updates**: Past recurring events automatically move to next occurrence
- **File Attachments**: Upload and associate files with events
- **Event Categories**: Support for different event types and metadata
- **Bulk Operations**: View all events for a month at once

### Notification System
- **Upcoming Alerts**: Notifications for events within 30 minutes
- **Desktop Integration**: Native desktop notifications (Python with Plyer)
- **Configurable Timing**: Customizable advance notice periods
- **Sound Alerts**: Optional audio notifications

### User Interface
- **Python GUI**: Rich Tkinter-based graphical interface
  - Calendar grid with clickable days
  - Detailed day view with hourly slots
  - Theme switching (light/dark)
  - Responsive design
- **Rust CLI**: Efficient command-line interface
  - Text-based calendar display
  - Interactive menu system
  - Cross-platform compatibility

## Implementations

### Python Implementation (`cal.py`)
- **GUI Framework**: Tkinter with custom styling
- **Features**: Full GUI, themes, desktop notifications, file uploads
- **Dependencies**: Python 3.x, Plyer (optional), threading, shutil
- **Best For**: Desktop users who prefer graphical interfaces

### Rust Implementation
- **CLI Framework**: Standard library with external crates
- **Features**: Fast execution, memory safety, cross-platform
- **Dependencies**: chrono, serde, serde_json
- **Best For**: Server environments, CLI enthusiasts, embedded systems

## Prerequisites

### Python Version
- Python 3.7 or higher
- pip package manager

### Rust Version (for Rust implementation)
- Rust 1.60 or higher
- Cargo package manager

### System Requirements
- Windows, macOS, or Linux
- 50MB+ free disk space
- Network access for locale data (optional)

## Installation & Setup

### Python Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Calendar
   ```

2. **Install Python Dependencies**
   ```bash
   pip install plyer  # Optional, for desktop notifications
   ```

3. **Run the Application**
   ```bash
   python cal.py
   ```

### Rust Setup

1. **Install Rust** (if not already installed)
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Create Rust Project**
   ```bash
   cargo new calendar_rs
   cd calendar_rs
   ```

3. **Update Cargo.toml**
   ```toml
   [dependencies]
   chrono = "0.4"
   serde = { version = "1.0", features = ["derive"] }
   serde_json = "1.0"
   ```

4. **Copy Rust Source Code** to `src/main.rs`

5. **Build and Run**
   ```bash
   cargo build --release
   cargo run
   ```

## Usage Guide

### First-Time Setup

1. **Launch Application**: Run `python cal.py` or `cargo run`
2. **Select Date**: Choose year and month (defaults to current)
3. **Choose Language**: Select from 5 supported languages
4. **View Calendar**: See the calendar display in chosen language

### Managing Events

#### Adding Events
1. Click on a day (Python) or select "add" action (Rust)
2. Choose the hour (0-23)
3. Enter event description
4. Optionally mark as recurring with interval
5. Save the event

#### Editing Events
1. Navigate to day with existing event
2. Select "Edit" button or "edit" action
3. Modify text, recurrence, or file attachments
4. Save changes

#### Recurring Events
- **Setup**: Mark event as recurring and set interval in days
- **Automatic Updates**: Past recurring events move to next occurrence
- **Management**: Edit or delete recurring events independently

#### File Attachments
- **Upload**: Attach files to any event
- **Storage**: Files copied to `uploads/` directory
- **Management**: View attached file names in event details

### Navigation

#### Python GUI
- **Month Navigation**: Use "Previous" and "Next" buttons
- **Quick Jump**: Click "Today" to return to current date
- **Day Details**: Click any day number for hourly view
- **Theme Switch**: Toggle between light and dark themes

#### Rust CLI
- **Date Selection**: Enter year/month at startup
- **Event Actions**: Type commands (add/edit/view/delete/upload/done)
- **Navigation**: Text-based menu system

## Data Structure

### Event Storage Format

Events are stored in `calendar_events.json` using nested structure:

```json
{
  "YYYY": {
    "MM": {
      "DD": {
        "HH": "Simple event text"
      }
    }
  }
}
```

### Complex Events (with metadata)

```json
{
  "2024": {
    "12": {
      "25": {
        "10": {
          "text": "Christmas Meeting",
          "recurring": true,
          "interval": 365,
          "file": {
            "file_name": "agenda.pdf",
            "file_path": "uploads/agenda.pdf"
          }
        }
      }
    }
  }
}
```

### Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `text` | String | Event description |
| `recurring` | Boolean | Whether event repeats |
| `interval` | Integer | Days between recurrences |
| `file` | Object | File attachment metadata |
| `file_name` | String | Original filename |
| `file_path` | String | Local storage path |

## Architecture

### Python Architecture

```
cal.py
├── CalendarGUI Class
│   ├── __init__() - Initialize GUI and data
│   ├── setup_ui() - Create interface elements
│   ├── display_calendar() - Render calendar grid
│   ├── day_clicked() - Handle day selection
│   ├── theme_system - Light/dark theme management
│   └── event_management - CRUD operations
├── Event Storage Functions
│   ├── load_all_events() - Read from JSON
│   └── save_all_events() - Write to JSON
├── Notification System
│   ├── Desktop notifications (Plyer)
│   ├── Threading for background checks
│   └── Configurable alert timing
└── File Management
    ├── Upload handling
    ├── Storage organization
    └── Metadata tracking
```

### Rust Architecture

```
main.rs
├── Data Structures
│   ├── Events (HashMap tree)
│   ├── EventData (struct)
│   ├── FileMetadata (struct)
│   └── StoredEvent (enum)
├── Core Functions
│   ├── load_all_events() - JSON deserialization
│   ├── save_all_events() - JSON serialization
│   ├── handle_recurring_events() - Auto-update logic
│   └── notify_upcoming_events() - Alert system
├── Calendar Display
│   ├── print_calendar() - Text-based rendering
│   ├── get_localized_month_name() - I18n support
│   └── get_localized_day_abbreviations() - Day names
├── User Interface
│   ├── select_month_and_year() - Date input
│   ├── Event management loop
│   └── Input validation
└── File Operations
    ├── upload_file_for_event() - File handling
    ├── Directory management
    └── Error handling
```

## GUI Features

### Main Window Components

#### Navigation Bar
- **Previous/Next Buttons**: Month navigation
- **Month/Year Label**: Current date display
- **Today Button**: Quick return to current date
- **Theme Toggle**: Switch between light/dark modes

#### Calendar Grid
- **Day Buttons**: Clickable date cells
- **Color Coding**:
  - Blue: Today's date
  - Yellow: Days with events
  - Gray: Regular days
- **Responsive Layout**: Adapts to window resizing

#### Action Panel
- **Add Event**: Create new events
- **View Events**: List all month events
- **Delete Event**: Remove existing events
- **Upload File**: Attach files to events
- **Edit Event**: Modify existing events
- **Settings**: Configure notifications and preferences

### Day Detail Window

#### Hour Slots (0-23)
- **Time Display**: 24-hour and 12-hour formats
- **Event Cards**: Visual event representation
- **Action Buttons**: Edit, Delete, Upload per event
- **Add Buttons**: Create events for empty slots

#### Scrollable Interface
- **Vertical Scrolling**: Navigate through 24 hours
- **Mouse Wheel Support**: Smooth scrolling
- **Keyboard Navigation**: Arrow key support

### Theme System

#### Light Theme
- **Background**: Clean white/light gray
- **Text**: Dark colors for readability
- **Accents**: Blue highlights
- **Events**: Light yellow background

#### Dark Theme
- **Background**: Dark gray/black
- **Text**: Light colors
- **Accents**: Blue highlights
- **Events**: Dark yellow background

## API Reference

### Python Classes and Methods

#### CalendarGUI Class

```python
class CalendarGUI:
    def __init__(self, root: tk.Tk) -> None
    def setup_ui(self) -> None
    def display_calendar(self) -> None
    def day_clicked(self, day: int) -> None
    def toggle_theme(self) -> None
    def apply_theme(self) -> None
    def has_events_on_day(self, day: int) -> bool
    def add_event_inline(self, parent_window, year_str, month_str, day_str, hour_str) -> None
    def edit_event_inline(self, parent_window, year_str, month_str, day_str, hour_str) -> None
    def delete_event_inline(self, parent_window, year_str, month_str, day_str, hour_str) -> None
    def upload_file_inline(self, parent_window, year_str, month_str, day_str, hour_str) -> None
```

#### Utility Functions

```python
def load_all_events() -> Dict[str, Any]
def save_all_events(data: Dict[str, Any]) -> None
```

### Rust Functions

#### Core Functions

```rust
fn load_all_events() -> Events
fn save_all_events(data: &Events)
fn handle_recurring_events(events: &mut Events)
fn notify_upcoming_events(events: &Events)
fn select_month_and_year() -> (i32, u32)
```

#### Calendar Functions

```rust
fn print_calendar(year: i32, month: u32, lang: &str)
fn get_localized_month_name(month: u32, lang: &str) -> String
fn get_localized_day_abbreviations(lang: &str) -> Vec<String>
fn days_in_month(year: i32, month: u32) -> u32
```

#### File Functions

```rust
fn upload_file_for_event(year: &str, month: &str, day: &str, hour: &str) -> Option<FileMetadata>
```

### Data Types

#### Rust Structs

```rust
#[derive(Serialize, Deserialize, Debug, Clone)]
struct EventData {
    text: String,
    recurring: Option<bool>,
    interval: Option<i64>,
    file: Option<FileMetadata>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct FileMetadata {
    file_name: String,
    file_path: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(untagged)]
enum StoredEvent {
    Simple(String),
    Complex(EventData),
}
```

## Troubleshooting

### Common Issues

#### Python Issues

**Problem**: GUI doesn't start
- **Solution**: Ensure Python 3.7+ and tkinter are installed
- **Check**: `python -m tkinter` should open a test window

**Problem**: Desktop notifications don't work
- **Solution**: Install Plyer: `pip install plyer`
- **Alternative**: Notifications will be disabled gracefully

**Problem**: Events not saving
- **Solution**: Check file permissions in application directory
- **Verify**: `calendar_events.json` should be writable

#### Rust Issues

**Problem**: Compilation fails
- **Solution**: Update Rust: `rustup update`
- **Check**: Verify Cargo.toml dependencies

**Problem**: Calendar display is corrupted
- **Solution**: Ensure terminal supports UTF-8
- **Alternative**: Use English language option

**Problem**: File uploads fail
- **Solution**: Check filesystem permissions
- **Verify**: `uploads/` directory should be writable

### Performance Issues

#### Large Event Files
- **Symptom**: Slow startup or event loading
- **Solution**: Archive old events to separate files
- **Prevention**: Regular cleanup of unused events

#### Memory Usage
- **Python**: Monitor with Task Manager/Activity Monitor
- **Rust**: Typically lower memory usage
- **Solution**: Restart application periodically for long-term use

### Data Recovery

#### Corrupted JSON File
1. **Backup**: Copy `calendar_events.json` before fixing
2. **Validate**: Use JSON validator online
3. **Repair**: Fix syntax errors manually
4. **Restore**: Replace with backup if needed

#### Lost Events
1. **Check Backups**: Look for `.json.bak` files
2. **Recent Files**: Check system temporary directories
3. **Recovery Tools**: Use file recovery software if needed

## Contributing

### Development Setup

1. **Fork Repository**
2. **Create Feature Branch**: `git checkout -b feature-name`
3. **Make Changes**: Follow coding standards
4. **Test Thoroughly**: Both Python and Rust versions
5. **Submit Pull Request**: With detailed description

### Coding Standards

#### Python
- **PEP 8**: Follow Python style guide
- **Type Hints**: Use where appropriate
- **Documentation**: Docstrings for all functions
- **Testing**: Unit tests for core functionality

#### Rust
- **rustfmt**: Use standard formatting
- **clippy**: Address all warnings
- **Documentation**: /// comments for public functions
- **Testing**: Integration and unit tests

### Feature Requests

When requesting features:
1. **Check Issues**: Ensure not already requested
2. **Use Template**: Follow issue template
3. **Provide Context**: Explain use case
4. **Consider Impact**: Both Python and Rust versions

### Bug Reports

Include in bug reports:
1. **Environment**: OS, Python/Rust version
2. **Steps**: Reproduction steps
3. **Expected**: What should happen
4. **Actual**: What actually happens
5. **Files**: Relevant configuration/data files

## License

This project is released under the MIT License. See LICENSE file for details.

### Third-Party Dependencies

#### Python
- **Tkinter**: Python standard library (PSF License)
- **Plyer**: MIT License
- **Standard Libraries**: PSF License

#### Rust
- **chrono**: MIT/Apache-2.0
- **serde**: MIT/Apache-2.0
- **serde_json**: MIT/Apache-2.0

---

## Quick Start Checklist

- [ ] Install Python 3.7+ or Rust 1.60+
- [ ] Clone repository
- [ ] Install dependencies (`pip install plyer` for Python)
- [ ] Run application (`python cal.py` or `cargo run`)
- [ ] Select date and language
- [ ] Add your first event
- [ ] Explore features (themes, recurring events, file uploads)

For additional help, please check the troubleshooting section or open an issue on GitHub.