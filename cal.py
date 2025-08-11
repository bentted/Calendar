import calendar
import locale
import json
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import shutil

EVENTS_FILE = "calendar_events.json"

# Define GUI Calendar Class
class CalendarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar Application")
        self.root.geometry("800x600")
        
        # Initialize data
        self.events_file = EVENTS_FILE
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.events = load_all_events()
        
        self.setup_ui()
        self.display_calendar()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Top frame for navigation
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)
        
        # Navigation buttons
        tk.Button(nav_frame, text="<< Previous", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        
        self.month_year_label = tk.Label(nav_frame, font=("Arial", 16, "bold"))
        self.month_year_label.pack(side=tk.LEFT, padx=20)
        
        tk.Button(nav_frame, text="Next >>", command=self.next_month).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Today", command=self.go_to_today).pack(side=tk.LEFT, padx=5)
        
        # Calendar frame
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Bottom frame for actions
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="Add Event", command=self.add_event).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="View Events", command=self.view_events).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Delete Event", command=self.delete_event).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Upload File", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Edit Event", command=self.edit_event).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Settings", command=self.show_settings).pack(side=tk.LEFT, padx=5)
    
    def display_calendar(self):
        """Display the calendar for current month"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Update month/year label
        month_name = calendar.month_name[self.current_month]
        self.month_year_label.config(text=f"{month_name} {self.current_year}")
        
        # Days of week header
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day in enumerate(days):
            label = tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold"), 
                           bg="lightgray", relief=tk.RAISED)
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Display calendar days
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days not in current month
                    label = tk.Label(self.calendar_frame, text="", bg="white")
                    label.grid(row=week_num, column=day_num, sticky="nsew", padx=1, pady=1)
                else:
                    # Check if this day has events
                    has_events = self.has_events_on_day(day)
                    bg_color = "lightyellow" if has_events else "white"
                    
                    # Create day button
                    btn = tk.Button(self.calendar_frame, text=str(day), 
                                  bg=bg_color, relief=tk.RAISED,
                                  command=lambda d=day: self.day_clicked(d))
                    btn.grid(row=week_num, column=day_num, sticky="nsew", padx=1, pady=1)
                    
                    # Highlight today
                    today = datetime.now()
                    if (self.current_year == today.year and 
                        self.current_month == today.month and 
                        day == today.day):
                        btn.config(bg="lightblue")
        
        # Configure grid weights for responsive design
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.calendar_frame.rowconfigure(i, weight=1)
    
    def has_events_on_day(self, day):
        """Check if a specific day has events"""
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        day_str = str(day)
        
        return (year_str in self.events and 
                month_str in self.events[year_str] and 
                day_str in self.events[year_str][month_str])
    
    def day_clicked(self, day):
        """Handle day button click"""
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        day_str = str(day)
        
        # Show events for this day
        day_events = self.events.get(year_str, {}).get(month_str, {}).get(day_str, {})
        
        if day_events:
            events_text = f"Events for {calendar.month_name[self.current_month]} {day}, {self.current_year}:\n\n"
            for hour, event in sorted(day_events.items(), key=lambda x: int(x[0])):
                if isinstance(event, dict):
                    event_text = event.get('text', str(event))
                else:
                    event_text = str(event)
                events_text += f"{hour}:00 - {event_text}\n"
            messagebox.showinfo("Day Events", events_text)
        else:
            result = messagebox.askyesno("No Events", 
                                       f"No events for {calendar.month_name[self.current_month]} {day}. "
                                       "Would you like to add an event?")
            if result:
                self.add_event_for_day(day)
    
    def prev_month(self):
        """Go to previous month"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.display_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.display_calendar()
    
    def go_to_today(self):
        """Go to current month"""
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.display_calendar()
    
    def add_event(self):
        """Add new event"""
        day = simpledialog.askinteger("Add Event", 
                                    f"Enter day (1-{calendar.monthrange(self.current_year, self.current_month)[1]}):")
        if day is None:
            return
        
        max_day = calendar.monthrange(self.current_year, self.current_month)[1]
        if not (1 <= day <= max_day):
            messagebox.showerror("Error", f"Invalid day. Please enter a number between 1 and {max_day}.")
            return
        
        self.add_event_for_day(day)
    
    def add_event_for_day(self, day):
        """Add event for specific day"""
        hour = simpledialog.askinteger("Add Event", "Enter hour (0-23):")
        if hour is None:
            return
        
        if not (0 <= hour <= 23):
            messagebox.showerror("Error", "Invalid hour. Please enter a number between 0 and 23.")
            return
        
        event_text = simpledialog.askstring("Add Event", "Enter event description:")
        if not event_text:
            return
        
        # Ask if recurring
        is_recurring = messagebox.askyesno("Recurring Event", "Is this a recurring event?")
        
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        day_str = str(day)
        hour_str = str(hour)
        
        if is_recurring:
            interval = simpledialog.askinteger("Recurring Event", "Enter recurrence interval in days:")
            if interval is None or interval <= 0:
                return
            event_data = {"text": event_text, "recurring": True, "interval": interval}
        else:
            event_data = event_text
        
        # Save event
        self.events.setdefault(year_str, {}).setdefault(month_str, {}).setdefault(day_str, {})[hour_str] = event_data
        save_all_events(self.events)
        self.display_calendar()
        messagebox.showinfo("Success", "Event added successfully!")
    
    def view_events(self):
        """View all events for current month"""
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        
        month_events = self.events.get(year_str, {}).get(month_str, {})
        
        if not month_events:
            messagebox.showinfo("No Events", f"No events for {calendar.month_name[self.current_month]} {self.current_year}")
            return
        
        events_text = f"Events for {calendar.month_name[self.current_month]} {self.current_year}:\n\n"
        
        for day in sorted(month_events.keys(), key=int):
            events_text += f"Day {day}:\n"
            for hour in sorted(month_events[day].keys(), key=int):
                event = month_events[day][hour]
                if isinstance(event, dict):
                    event_text = event.get('text', str(event))
                    if event.get('recurring'):
                        event_text += " (Recurring)"
                else:
                    event_text = str(event)
                events_text += f"  {hour}:00 - {event_text}\n"
            events_text += "\n"
        
        # Create a new window for viewing events
        event_window = tk.Toplevel(self.root)
        event_window.title("Monthly Events")
        event_window.geometry("400x500")
        
        text_widget = tk.Text(event_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        text_widget.insert(tk.END, events_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = tk.Scrollbar(text_widget)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)
    
    def delete_event(self):
        """Delete an event"""
        day = simpledialog.askinteger("Delete Event", 
                                    f"Enter day (1-{calendar.monthrange(self.current_year, self.current_month)[1]}):")
        if day is None:
            return
        
        max_day = calendar.monthrange(self.current_year, self.current_month)[1]
        if not (1 <= day <= max_day):
            messagebox.showerror("Error", f"Invalid day. Please enter a number between 1 and {max_day}.")
            return
        
        hour = simpledialog.askinteger("Delete Event", "Enter hour (0-23):")
        if hour is None:
            return
        
        if not (0 <= hour <= 23):
            messagebox.showerror("Error", "Invalid hour. Please enter a number between 0 and 23.")
            return
        
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        day_str = str(day)
        hour_str = str(hour)
        
        if (year_str in self.events and 
            month_str in self.events[year_str] and 
            day_str in self.events[year_str][month_str] and 
            hour_str in self.events[year_str][month_str][day_str]):
            
            # Show current event before deletion
            event = self.events[year_str][month_str][day_str][hour_str]
            if isinstance(event, dict):
                event_text = event.get('text', str(event))
            else:
                event_text = str(event)
            
            confirm = messagebox.askyesno("Confirm Deletion", 
                                        f"Delete event '{event_text}' on day {day} at {hour}:00?")
            if confirm:
                del self.events[year_str][month_str][day_str][hour_str]
                
                # Clean up empty dictionaries
                if not self.events[year_str][month_str][day_str]:
                    del self.events[year_str][month_str][day_str]
                if not self.events[year_str][month_str]:
                    del self.events[year_str][month_str]
                if not self.events[year_str]:
                    del self.events[year_str]
                
                save_all_events(self.events)
                self.display_calendar()
                messagebox.showinfo("Success", "Event deleted successfully!")
        else:
            messagebox.showinfo("No Event", f"No event found for day {day} at {hour}:00")
    
    def upload_file(self):
        """Upload file for an event"""
        day = simpledialog.askinteger("Upload File", 
                                    f"Enter day (1-{calendar.monthrange(self.current_year, self.current_month)[1]}):")
        if day is None:
            return
        
        max_day = calendar.monthrange(self.current_year, self.current_month)[1]
        if not (1 <= day <= max_day):
            messagebox.showerror("Error", f"Invalid day. Please enter a number between 1 and {max_day}.")
            return
        
        hour = simpledialog.askinteger("Upload File", "Enter hour (0-23):")
        if hour is None:
            return
        
        if not (0 <= hour <= 23):
            messagebox.showerror("Error", "Invalid hour. Please enter a number between 0 and 23.")
            return
        
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        day_str = str(day)
        hour_str = str(hour)
        
        # Check if event exists
        current_event = self.events.get(year_str, {}).get(month_str, {}).get(day_str, {}).get(hour_str)
        if not current_event:
            messagebox.showerror("Error", "No event scheduled at this time. Please add an event first.")
            return
        
        # File dialog to select file
        file_path = filedialog.askopenfilename(title="Select file to upload")
        if not file_path:
            return
        
        file_name = os.path.basename(file_path)
        try:
            # Ensure the uploads directory exists
            uploads_dir = "uploads"
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Copy the file to the uploads directory
            destination_path = os.path.join(uploads_dir, file_name)
            shutil.copy2(file_path, destination_path)
            
            file_metadata = {"file_name": file_name, "file_path": destination_path}
            
            # Update event with file metadata
            if isinstance(current_event, dict):
                current_event["file"] = file_metadata
            else:
                current_event = {"text": current_event, "file": file_metadata}
            
            self.events.setdefault(year_str, {}).setdefault(month_str, {}).setdefault(day_str, {})[hour_str] = current_event
            save_all_events(self.events)
            messagebox.showinfo("Success", f"File '{file_name}' uploaded successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error uploading file: {e}")
    
    def edit_event(self):
        """Edit an existing event"""
        day = simpledialog.askinteger("Edit Event", 
                                    f"Enter day (1-{calendar.monthrange(self.current_year, self.current_month)[1]}):")
        if day is None:
            return
        
        max_day = calendar.monthrange(self.current_year, self.current_month)[1]
        if not (1 <= day <= max_day):
            messagebox.showerror("Error", f"Invalid day. Please enter a number between 1 and {max_day}.")
            return
        
        hour = simpledialog.askinteger("Edit Event", "Enter hour (0-23):")
        if hour is None:
            return
        
        if not (0 <= hour <= 23):
            messagebox.showerror("Error", "Invalid hour. Please enter a number between 0 and 23.")
            return
        
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        day_str = str(day)
        hour_str = str(hour)
        
        current_event = self.events.get(year_str, {}).get(month_str, {}).get(day_str, {}).get(hour_str)
        if not current_event:
            messagebox.showerror("Error", "No event found to edit.")
            return
        
        # Get current event text
        if isinstance(current_event, dict):
            current_text = current_event.get('text', str(current_event))
        else:
            current_text = str(current_event)
        
        # Ask for new event text
        event_text = simpledialog.askstring("Edit Event", f"Current: {current_text}\nEnter new event description:", initialvalue=current_text)
        if event_text is None:  # User cancelled
            return
        
        if not event_text:
            messagebox.showerror("Error", "Event text cannot be empty.")
            return
        
        # Ask if recurring
        is_recurring = messagebox.askyesno("Recurring Event", "Is this a recurring event?")
        
        if is_recurring:
            interval = simpledialog.askinteger("Recurring Event", "Enter recurrence interval in days:")
            if interval is None or interval <= 0:
                return
            event_data = {"text": event_text, "recurring": True, "interval": interval}
            # Preserve file metadata if it exists
            if isinstance(current_event, dict) and "file" in current_event:
                event_data["file"] = current_event["file"]
        else:
            if isinstance(current_event, dict) and "file" in current_event:
                event_data = {"text": event_text, "file": current_event["file"]}
            else:
                event_data = event_text
        
        # Save updated event
        self.events.setdefault(year_str, {}).setdefault(month_str, {}).setdefault(day_str, {})[hour_str] = event_data
        save_all_events(self.events)
        self.display_calendar()
        messagebox.showinfo("Success", "Event updated successfully!")
    
    def show_settings(self):
        """Show settings window with various options"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x500")
        
        # Language settings
        lang_frame = tk.LabelFrame(settings_window, text="Language Settings", padx=10, pady=10)
        lang_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(lang_frame, text="Select language for month names:").pack(anchor=tk.W)
        
        languages = ['English', 'Spanish', 'French', 'German', 'Chinese']
        self.selected_language = tk.StringVar(value='English')
        
        for lang in languages:
            tk.Radiobutton(lang_frame, text=lang, variable=self.selected_language, value=lang).pack(anchor=tk.W)
        
        # Calendar settings
        cal_frame = tk.LabelFrame(settings_window, text="Calendar Settings", padx=10, pady=10)
        cal_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(cal_frame, text="Go to Specific Month/Year", command=self.go_to_specific_date).pack(fill=tk.X, pady=2)
        tk.Button(cal_frame, text="Export Events", command=self.export_events).pack(fill=tk.X, pady=2)
        tk.Button(cal_frame, text="Import Events", command=self.import_events).pack(fill=tk.X, pady=2)
        
        # Event management
        event_frame = tk.LabelFrame(settings_window, text="Event Management", padx=10, pady=10)
        event_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(event_frame, text="View All Events", command=self.view_all_events).pack(fill=tk.X, pady=2)
        tk.Button(event_frame, text="Search Events", command=self.search_events).pack(fill=tk.X, pady=2)
        tk.Button(event_frame, text="Upcoming Events", command=self.show_upcoming_events).pack(fill=tk.X, pady=2)
        tk.Button(event_frame, text="Process Recurring Events", command=self.process_recurring_events).pack(fill=tk.X, pady=2)
        
        # File management
        file_frame = tk.LabelFrame(settings_window, text="File Management", padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(file_frame, text="View Uploaded Files", command=self.view_uploaded_files).pack(fill=tk.X, pady=2)
        tk.Button(file_frame, text="Clean Up Files", command=self.cleanup_files).pack(fill=tk.X, pady=2)
        
        # Apply settings button
        tk.Button(settings_window, text="Apply Language Settings", command=lambda: self.apply_language_settings(settings_window)).pack(pady=10)
    
    def go_to_specific_date(self):
        """Navigate to a specific month and year"""
        year = simpledialog.askinteger("Go to Date", f"Enter year (current: {self.current_year}):", 
                                     initialvalue=self.current_year, minvalue=1900, maxvalue=2100)
        if year is None:
            return
        
        month = simpledialog.askinteger("Go to Date", f"Enter month (1-12, current: {self.current_month}):", 
                                      initialvalue=self.current_month, minvalue=1, maxvalue=12)
        if month is None:
            return
        
        self.current_year = year
        self.current_month = month
        self.display_calendar()
    
    def export_events(self):
        """Export events to a file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Events",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.events, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Success", f"Events exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export events: {e}")
    
    def import_events(self):
        """Import events from a file"""
        file_path = filedialog.askopenfilename(
            title="Import Events",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_events = json.load(f)
                
                # Merge with existing events
                for year, months in imported_events.items():
                    for month, days in months.items():
                        for day, hours in days.items():
                            for hour, event in hours.items():
                                self.events.setdefault(year, {}).setdefault(month, {}).setdefault(day, {})[hour] = event
                
                save_all_events(self.events)
                self.display_calendar()
                messagebox.showinfo("Success", f"Events imported from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import events: {e}")
    
    def view_all_events(self):
        """View all events across all months"""
        if not self.events:
            messagebox.showinfo("No Events", "No events found in the calendar.")
            return
        
        events_window = tk.Toplevel(self.root)
        events_window.title("All Events")
        events_window.geometry("600x500")
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(events_window)
        text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Build events text
        events_text = "All Events:\n\n"
        for year in sorted(self.events.keys(), key=int):
            events_text += f"Year {year}:\n"
            for month in sorted(self.events[year].keys(), key=int):
                month_name = calendar.month_name[int(month)]
                events_text += f"  {month_name}:\n"
                for day in sorted(self.events[year][month].keys(), key=int):
                    events_text += f"    Day {day}:\n"
                    for hour in sorted(self.events[year][month][day].keys(), key=int):
                        event = self.events[year][month][day][hour]
                        if isinstance(event, dict):
                            event_text = event.get('text', str(event))
                            if event.get('recurring'):
                                event_text += " (Recurring)"
                            if event.get('file'):
                                event_text += f" [File: {event['file']['file_name']}]"
                        else:
                            event_text = str(event)
                        events_text += f"      {hour}:00 - {event_text}\n"
                events_text += "\n"
            events_text += "\n"
        
        text_widget.insert(tk.END, events_text)
        text_widget.config(state=tk.DISABLED)
    
    def search_events(self):
        """Search for events by text"""
        search_term = simpledialog.askstring("Search Events", "Enter search term:")
        if not search_term:
            return
        
        search_term = search_term.lower()
        found_events = []
        
        for year, months in self.events.items():
            for month, days in months.items():
                for day, hours in days.items():
                    for hour, event in hours.items():
                        event_text = ""
                        if isinstance(event, dict):
                            event_text = event.get('text', str(event)).lower()
                        else:
                            event_text = str(event).lower()
                        
                        if search_term in event_text:
                            month_name = calendar.month_name[int(month)]
                            found_events.append(f"{month_name} {day}, {year} at {hour}:00 - {event_text}")
        
        if found_events:
            result_text = f"Found {len(found_events)} events containing '{search_term}':\n\n"
            result_text += "\n".join(found_events)
        else:
            result_text = f"No events found containing '{search_term}'"
        
        # Show results in a new window
        result_window = tk.Toplevel(self.root)
        result_window.title("Search Results")
        result_window.geometry("500x400")
        
        text_widget = tk.Text(result_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        text_widget.insert(tk.END, result_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_upcoming_events(self):
        """Show upcoming events in the next 7 days"""
        today = datetime.now()
        upcoming_events = []
        
        for i in range(7):  # Next 7 days
            check_date = today + timedelta(days=i)
            year_str = str(check_date.year)
            month_str = str(check_date.month)
            day_str = str(check_date.day)
            
            day_events = self.events.get(year_str, {}).get(month_str, {}).get(day_str, {})
            for hour, event in day_events.items():
                event_text = ""
                if isinstance(event, dict):
                    event_text = event.get('text', str(event))
                else:
                    event_text = str(event)
                
                event_time = check_date.replace(hour=int(hour), minute=0, second=0, microsecond=0)
                upcoming_events.append((event_time, event_text))
        
        if upcoming_events:
            upcoming_events.sort(key=lambda x: x[0])
            result_text = "Upcoming Events (Next 7 Days):\n\n"
            for event_time, event_text in upcoming_events:
                result_text += f"{event_time.strftime('%A, %B %d, %Y at %H:%M')} - {event_text}\n"
        else:
            result_text = "No upcoming events in the next 7 days."
        
        messagebox.showinfo("Upcoming Events", result_text)
    
    def process_recurring_events(self):
        """Process and update recurring events"""
        self.events = handle_recurring_events(self.events)
        save_all_events(self.events)
        self.display_calendar()
        messagebox.showinfo("Success", "Recurring events processed and updated!")
    
    def view_uploaded_files(self):
        """View all uploaded files"""
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            messagebox.showinfo("No Files", "No uploads directory found.")
            return
        
        files = os.listdir(uploads_dir)
        if not files:
            messagebox.showinfo("No Files", "No uploaded files found.")
            return
        
        files_text = f"Uploaded Files ({len(files)} total):\n\n"
        for file in files:
            file_path = os.path.join(uploads_dir, file)
            file_size = os.path.getsize(file_path)
            files_text += f"• {file} ({file_size} bytes)\n"
        
        # Show in a new window
        files_window = tk.Toplevel(self.root)
        files_window.title("Uploaded Files")
        files_window.geometry("400x300")
        
        text_widget = tk.Text(files_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        text_widget.insert(tk.END, files_text)
        text_widget.config(state=tk.DISABLED)
    
    def cleanup_files(self):
        """Clean up unused uploaded files"""
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            messagebox.showinfo("No Files", "No uploads directory found.")
            return
        
        # Get all referenced files
        referenced_files = set()
        for year, months in self.events.items():
            for month, days in months.items():
                for day, hours in days.items():
                    for hour, event in hours.items():
                        if isinstance(event, dict) and "file" in event:
                            referenced_files.add(event["file"]["file_name"])
        
        # Get all uploaded files
        uploaded_files = set(os.listdir(uploads_dir))
        
        # Find unused files
        unused_files = uploaded_files - referenced_files
        
        if not unused_files:
            messagebox.showinfo("Cleanup", "No unused files found.")
            return
        
        if messagebox.askyesno("Cleanup Files", f"Found {len(unused_files)} unused files. Delete them?"):
            for file in unused_files:
                file_path = os.path.join(uploads_dir, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete {file}: {e}")
            
            messagebox.showinfo("Success", f"Deleted {len(unused_files)} unused files.")
    
    def apply_language_settings(self, settings_window):
        """Apply language settings and close settings window"""
        selected_lang = self.selected_language.get()
        
        # Define locale mappings
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
        
        # Try to set locale
        try:
            if selected_lang in windows_locales:
                locale.setlocale(locale.LC_ALL, windows_locales[selected_lang])
                messagebox.showinfo("Success", f"Language set to {selected_lang}")
            elif selected_lang in locales_to_try:
                locale.setlocale(locale.LC_ALL, locales_to_try[selected_lang])
                messagebox.showinfo("Success", f"Language set to {selected_lang}")
        except locale.Error:
            messagebox.showerror("Error", f"Could not set locale for {selected_lang}")
        
        self.display_calendar()
        settings_window.destroy()

def run_gui_calendar():
    """Start the GUI version of the calendar"""
    root = tk.Tk()
    app = CalendarGUI(root)
    root.mainloop()

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
    except IOError:
        print(f"Error: Could not save events to {EVENTS_FILE}")

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

if __name__ == "__main__":
    try:
        print("Starting Calendar Application...")
        
        # Test tkinter availability
        try:
            test_root = tk.Tk()
            test_root.withdraw()  # Hide the test window
            test_root.destroy()
            print("Tkinter is available.")
        except Exception as tk_error:
            print(f"Tkinter error: {tk_error}")
            input("Press Enter to exit...")
            exit()
        
        # Load and process events
        print("Loading events...")
        all_events = load_all_events()
        all_events = handle_recurring_events(all_events)
        save_all_events(all_events)
        
        # Check for upcoming events
        today = datetime.now()
        upcoming_count = 0
        for year, months in all_events.items():
            for month, days in months.items():
                for day, hours in days.items():
                    for hour, event in hours.items():
                        event_time = datetime(int(year), int(month), int(day), int(hour))
                        if today <= event_time <= today + timedelta(minutes=30):
                            event_text = event if isinstance(event, str) else event.get('text', str(event))
                            print(f"Upcoming Event: {event_text} at {event_time.strftime('%Y-%m-%d %H:%M')}")
                            upcoming_count += 1
        
        if upcoming_count == 0:
            print("No upcoming events in the next 30 minutes.")
        
        print("Starting GUI...")
        # Start GUI
        root = tk.Tk()
        app = CalendarGUI(root)
        print("GUI initialized successfully!")
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting calendar: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")



