import calendar
import locale
import json
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import shutil
import threading
import time
try:
    from Plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Plyer not available. Desktop notifications will be disabled.")
    print("Install with: pip install plyer")

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
        
        # Theme system
        self.current_theme = "light"  # Default theme
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff",
                "button_bg": "#f0f0f0",
                "button_fg": "#000000",
                "button_active_bg": "#e1e1e1",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "header_bg": "#e8e8e8",
                "today_bg": "#87ceeb",
                "event_bg": "#fffacd",
                "frame_bg": "#f5f5f5",
                "text_bg": "#ffffff",
                "scrollbar_bg": "#f0f0f0"
            },
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff",
                "button_bg": "#404040",
                "button_fg": "#ffffff",
                "button_active_bg": "#505050",
                "entry_bg": "#404040",
                "entry_fg": "#ffffff",
                "header_bg": "#353535",
                "today_bg": "#4682b4",
                "event_bg": "#8b8000",
                "frame_bg": "#353535",
                "text_bg": "#404040",
                "scrollbar_bg": "#505050"
            }
        }
        
        # Notification system
        self.notification_settings = {
            "enabled": True,
            "desktop_notifications": PLYER_AVAILABLE,
            "advance_notice": [5, 15, 30],  # minutes before event
            "sound_enabled": True,
            "popup_enabled": True
        }
        self.notification_thread = None
        self.notification_running = False
        self.active_notifications = []  # Track shown notifications to avoid duplicates
        
        self.setup_ui()
        self.apply_theme()
        self.display_calendar()
        self.start_notification_system()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Top frame for navigation
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(pady=10)
        
        # Navigation buttons
        self.prev_btn = tk.Button(self.nav_frame, text="<< Previous", command=self.prev_month)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.month_year_label = tk.Label(self.nav_frame, font=("Arial", 16, "bold"))
        self.month_year_label.pack(side=tk.LEFT, padx=20)
        
        self.next_btn = tk.Button(self.nav_frame, text="Next >>", command=self.next_month)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.today_btn = tk.Button(self.nav_frame, text="Today", command=self.go_to_today)
        self.today_btn.pack(side=tk.LEFT, padx=5)
        
        # Theme toggle button
        self.theme_btn = tk.Button(self.nav_frame, text="🌙 Dark", command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
        # Calendar frame
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Bottom frame for actions
        self.action_frame = tk.Frame(self.root)
        self.action_frame.pack(pady=10)
        
        self.add_btn = tk.Button(self.action_frame, text="Add Event", command=self.add_event)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_btn = tk.Button(self.action_frame, text="View Events", command=self.view_events)
        self.view_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = tk.Button(self.action_frame, text="Delete Event", command=self.delete_event)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.upload_btn = tk.Button(self.action_frame, text="Upload File", command=self.upload_file)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = tk.Button(self.action_frame, text="Edit Event", command=self.edit_event)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.settings_btn = tk.Button(self.action_frame, text="Settings", command=self.show_settings)
        self.settings_btn.pack(side=tk.LEFT, padx=5)
    
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
        self.day_headers = []
        for i, day in enumerate(days):
            label = tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold"), 
                           bg=self.themes[self.current_theme]["header_bg"], 
                           fg=self.themes[self.current_theme]["fg"],
                           relief=tk.RAISED)
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            self.day_headers.append(label)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Display calendar days
        self.day_buttons = []
        for week_num, week in enumerate(cal, 1):
            week_buttons = []
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days not in current month
                    label = tk.Label(self.calendar_frame, text="", 
                                   bg=self.themes[self.current_theme]["bg"])
                    label.grid(row=week_num, column=day_num, sticky="nsew", padx=1, pady=1)
                    week_buttons.append(label)
                else:
                    # Check if this day has events
                    has_events = self.has_events_on_day(day)
                    
                    # Determine background color
                    today = datetime.now()
                    if (self.current_year == today.year and 
                        self.current_month == today.month and 
                        day == today.day):
                        bg_color = self.themes[self.current_theme]["today_bg"]
                    elif has_events:
                        bg_color = self.themes[self.current_theme]["event_bg"]
                    else:
                        bg_color = self.themes[self.current_theme]["button_bg"]
                    
                    # Create day button
                    btn = tk.Button(self.calendar_frame, text=str(day), 
                                  bg=bg_color, 
                                  fg=self.themes[self.current_theme]["button_fg"],
                                  activebackground=self.themes[self.current_theme]["button_active_bg"],
                                  relief=tk.RAISED,
                                  command=lambda d=day: self.day_clicked(d))
                    btn.grid(row=week_num, column=day_num, sticky="nsew", padx=1, pady=1)
                    week_buttons.append(btn)
            self.day_buttons.append(week_buttons)
        
        # Configure grid weights for responsive design
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.calendar_frame.rowconfigure(i, weight=1)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "light":
            self.current_theme = "dark"
            self.theme_btn.config(text="☀️ Light")
        else:
            self.current_theme = "light"
            self.theme_btn.config(text="🌙 Dark")
        
        self.apply_theme()
        self.display_calendar()
    
    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        theme = self.themes[self.current_theme]
        
        # Apply to root window
        self.root.config(bg=theme["bg"])
        
        # Apply to frames
        self.nav_frame.config(bg=theme["frame_bg"])
        self.calendar_frame.config(bg=theme["bg"])
        self.action_frame.config(bg=theme["frame_bg"])
        
        # Apply to navigation elements
        self.prev_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                           activebackground=theme["button_active_bg"])
        self.next_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                           activebackground=theme["button_active_bg"])
        self.today_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                            activebackground=theme["button_active_bg"])
        self.theme_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                            activebackground=theme["button_active_bg"])
        
        # Apply to month/year label
        self.month_year_label.config(bg=theme["frame_bg"], fg=theme["fg"])
        
        # Apply to action buttons
        self.add_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                          activebackground=theme["button_active_bg"])
        self.view_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                           activebackground=theme["button_active_bg"])
        self.delete_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                             activebackground=theme["button_active_bg"])
        self.upload_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                             activebackground=theme["button_active_bg"])
        self.edit_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                           activebackground=theme["button_active_bg"])
        self.settings_btn.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                                activebackground=theme["button_active_bg"])
    
    def apply_theme_to_window(self, window):
        """Apply current theme to a specific window"""
        theme = self.themes[self.current_theme]
        window.config(bg=theme["bg"])
        
        # Apply theme to all child widgets recursively
        def apply_to_children(widget):
            try:
                widget_class = widget.winfo_class()
                if widget_class == "Frame" or widget_class == "Toplevel":
                    widget.config(bg=theme["bg"])
                elif widget_class == "Label":
                    widget.config(bg=theme["bg"], fg=theme["fg"])
                elif widget_class == "Button":
                    widget.config(bg=theme["button_bg"], fg=theme["button_fg"], 
                                activebackground=theme["button_active_bg"])
                elif widget_class == "Text":
                    widget.config(bg=theme["text_bg"], fg=theme["fg"], 
                                insertbackground=theme["fg"])
                elif widget_class == "Entry":
                    widget.config(bg=theme["entry_bg"], fg=theme["entry_fg"], 
                                insertbackground=theme["fg"])
                elif widget_class == "Listbox":
                    widget.config(bg=theme["text_bg"], fg=theme["fg"])
                elif widget_class == "Scrollbar":
                    widget.config(bg=theme["scrollbar_bg"])
                elif widget_class == "LabelFrame":
                    widget.config(bg=theme["bg"], fg=theme["fg"])
                elif widget_class == "Radiobutton":
                    widget.config(bg=theme["bg"], fg=theme["fg"], 
                                selectcolor=theme["button_bg"])
                elif widget_class == "Checkbutton":
                    widget.config(bg=theme["bg"], fg=theme["fg"], 
                                selectcolor=theme["button_bg"])
            except:
                pass  # Skip widgets that don't support these options
            
            # Recursively apply to children
            for child in widget.winfo_children():
                apply_to_children(child)
        
        apply_to_children(window)
    
    def has_events_on_day(self, day):
        """Check if a specific day has events"""
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        day_str = str(day)
        
        return (year_str in self.events and 
                month_str in self.events[year_str] and 
                day_str in self.events[year_str][month_str])
    
    def day_clicked(self, day):
        """Handle day button click - show detailed day view"""
        year_str = str(self.current_year)
        month_str = str(self.current_month)
        day_str = str(day)
        
        # Create detailed day view window
        day_window = tk.Toplevel(self.root)
        day_window.title(f"{calendar.month_name[self.current_month]} {day}, {self.current_year}")
        day_window.geometry("600x700")
        
        # Main frame with scrollbar
        main_frame = tk.Frame(day_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = tk.Label(scrollable_frame, 
                             text=f"Schedule for {calendar.month_name[self.current_month]} {day}, {self.current_year}",
                             font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Get existing events for this day
        day_events = self.events.get(year_str, {}).get(month_str, {}).get(day_str, {})
        
        # Create hour slots (24 hours)
        for hour in range(24):
            hour_str = str(hour)
            hour_frame = tk.Frame(scrollable_frame, relief=tk.RIDGE, bd=1)
            hour_frame.pack(fill=tk.X, pady=2)
            
            # Hour label
            time_12hr = datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M %p")
            hour_label = tk.Label(hour_frame, text=f"{hour:02d}:00 ({time_12hr})", 
                                font=("Arial", 10, "bold"), width=12, anchor="w")
            hour_label.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Event content frame
            content_frame = tk.Frame(hour_frame)
            content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # Check if there's an event at this hour
            if hour_str in day_events:
                event = day_events[hour_str]
                
                # Event info frame
                event_info_frame = tk.Frame(content_frame)
                event_info_frame.pack(fill=tk.X, pady=2)
                
                # Display event text
                if isinstance(event, dict):
                    event_text = event.get('text', str(event))
                    event_label = tk.Label(event_info_frame, text=event_text, 
                                         font=("Arial", 10), anchor="w", 
                                         bg=self.themes[self.current_theme]["event_bg"])
                    event_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    
                    # Show additional info
                    info_parts = []
                    if event.get('recurring'):
                        info_parts.append(f"Recurring every {event.get('interval', 1)} days")
                    if event.get('file'):
                        info_parts.append(f"File: {event['file']['file_name']}")
                    
                    if info_parts:
                        info_label = tk.Label(event_info_frame, text=" | ".join(info_parts), 
                                            font=("Arial", 8), fg="gray")
                        info_label.pack(side=tk.LEFT, padx=(5, 0))
                else:
                    event_label = tk.Label(event_info_frame, text=str(event), 
                                         font=("Arial", 10), anchor="w",
                                         bg=self.themes[self.current_theme]["event_bg"])
                    event_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Action buttons for existing event
                button_frame = tk.Frame(content_frame)
                button_frame.pack(fill=tk.X, pady=2)
                
                edit_btn = tk.Button(button_frame, text="Edit", 
                                   command=lambda h=hour: self.edit_event_inline(day_window, year_str, month_str, day_str, str(h)),
                                   bg=self.themes[self.current_theme]["button_bg"],
                                   fg=self.themes[self.current_theme]["button_fg"])
                edit_btn.pack(side=tk.LEFT, padx=2)
                
                delete_btn = tk.Button(button_frame, text="Delete", 
                                     command=lambda h=hour: self.delete_event_inline(day_window, year_str, month_str, day_str, str(h)),
                                     bg=self.themes[self.current_theme]["button_bg"],
                                     fg=self.themes[self.current_theme]["button_fg"])
                delete_btn.pack(side=tk.LEFT, padx=2)
                
                upload_btn = tk.Button(button_frame, text="Upload File", 
                                     command=lambda h=hour: self.upload_file_inline(day_window, year_str, month_str, day_str, str(h)),
                                     bg=self.themes[self.current_theme]["button_bg"],
                                     fg=self.themes[self.current_theme]["button_fg"])
                upload_btn.pack(side=tk.LEFT, padx=2)
                
                # Show delete file button if file exists
                if isinstance(event, dict) and event.get('file'):
                    delete_file_btn = tk.Button(button_frame, text="Delete File", 
                                               command=lambda h=hour: self.delete_file_inline(day_window, year_str, month_str, day_str, str(h)),
                                               bg=self.themes[self.current_theme]["button_bg"],
                                               fg=self.themes[self.current_theme]["button_fg"])
                    delete_file_btn.pack(side=tk.LEFT, padx=2)
                
            else:
                # No event - show add button
                no_event_label = tk.Label(content_frame, text="No event scheduled", 
                                        font=("Arial", 10), fg="gray", anchor="w")
                no_event_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                add_btn = tk.Button(content_frame, text="Add Event", 
                                  command=lambda h=hour: self.add_event_inline(day_window, year_str, month_str, day_str, str(h)),
                                  bg=self.themes[self.current_theme]["button_bg"],
                                  fg=self.themes[self.current_theme]["button_fg"])
                add_btn.pack(side=tk.RIGHT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Apply theme to the window
        self.apply_theme_to_window(day_window)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def add_event_inline(self, parent_window, year_str, month_str, day_str, hour_str):
        """Add event inline from day view"""
        event_text = simpledialog.askstring("Add Event", 
                                           f"Enter event description for {hour_str}:00:")
        if not event_text:
            return
        
        # Ask if recurring
        is_recurring = messagebox.askyesno("Recurring Event", "Is this a recurring event?")
        
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
        
        # Refresh the day view
        parent_window.destroy()
        day = int(day_str)
        self.day_clicked(day)
        
        messagebox.showinfo("Success", "Event added successfully!")
    
    def edit_event_inline(self, parent_window, year_str, month_str, day_str, hour_str):
        """Edit event inline from day view"""
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
        event_text = simpledialog.askstring("Edit Event", 
                                           f"Current: {current_text}\nEnter new event description:", 
                                           initialvalue=current_text)
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
        
        # Refresh the day view
        parent_window.destroy()
        day = int(day_str)
        self.day_clicked(day)
        
        messagebox.showinfo("Success", "Event updated successfully!")
    
    def delete_event_inline(self, parent_window, year_str, month_str, day_str, hour_str):
        """Delete event inline from day view"""
        current_event = self.events.get(year_str, {}).get(month_str, {}).get(day_str, {}).get(hour_str)
        if not current_event:
            messagebox.showerror("Error", "No event found to delete.")
            return
        
        # Get event text for confirmation
        if isinstance(current_event, dict):
            event_text = current_event.get('text', str(current_event))
        else:
            event_text = str(current_event)
        
        confirm = messagebox.askyesno("Confirm Deletion", 
                                    f"Delete event '{event_text}' at {hour_str}:00?")
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
            
            # Refresh the day view
            parent_window.destroy()
            day = int(day_str)
            self.day_clicked(day)
            
            messagebox.showinfo("Success", "Event deleted successfully!")
    
    def upload_file_inline(self, parent_window, year_str, month_str, day_str, hour_str):
        """Upload file inline from day view"""
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
            self.display_calendar()
            
            # Refresh the day view
            parent_window.destroy()
            day = int(day_str)
            self.day_clicked(day)
            
            messagebox.showinfo("Success", f"File '{file_name}' uploaded successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error uploading file: {e}")
    
    def delete_file_inline(self, parent_window, year_str, month_str, day_str, hour_str):
        """Delete file inline from day view"""
        current_event = self.events.get(year_str, {}).get(month_str, {}).get(day_str, {}).get(hour_str)
        if not isinstance(current_event, dict) or "file" not in current_event:
            messagebox.showerror("Error", "No file found to delete.")
            return
        
        file_name = current_event["file"]["file_name"]
        confirm = messagebox.askyesno("Confirm File Deletion", 
                                    f"Delete file '{file_name}' from this event?")
        if confirm:
            try:
                # Remove file from filesystem
                file_path = current_event["file"]["file_path"]
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Remove file metadata from event
                del current_event["file"]
                
                # If event only had file metadata, convert back to simple text
                if len(current_event) == 1 and "text" in current_event:
                    current_event = current_event["text"]
                
                self.events[year_str][month_str][day_str][hour_str] = current_event
                save_all_events(self.events)
                self.display_calendar()
                
                # Refresh the day view
                parent_window.destroy()
                day = int(day_str)
                self.day_clicked(day)
                
                messagebox.showinfo("Success", f"File '{file_name}' deleted successfully!")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting file: {e}")
    
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
        
        # Apply theme to the window
        self.apply_theme_to_window(event_window)
    
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
        
        # Theme settings
        theme_frame = tk.LabelFrame(settings_window, text="Theme Settings", padx=10, pady=10)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(theme_frame, text="Select theme:").pack(anchor=tk.W)
        
        self.selected_theme = tk.StringVar(value=self.current_theme)
        
        light_radio = tk.Radiobutton(theme_frame, text="☀️ Light Theme", 
                                   variable=self.selected_theme, value="light",
                                   command=self.update_theme_from_settings)
        light_radio.pack(anchor=tk.W)
        
        dark_radio = tk.Radiobutton(theme_frame, text="🌙 Dark Theme", 
                                  variable=self.selected_theme, value="dark",
                                  command=self.update_theme_from_settings)
        dark_radio.pack(anchor=tk.W)
        
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
        
        # Notification settings
        notif_frame = tk.LabelFrame(settings_window, text="Notification Settings", padx=10, pady=10)
        notif_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(notif_frame, text="Configure Notifications", command=self.show_notification_settings).pack(fill=tk.X, pady=2)
        
        # Status label
        status_text = "Enabled" if self.notification_settings["enabled"] else "Disabled"
        tk.Label(notif_frame, text=f"Status: {status_text}", font=("Arial", 9), fg="gray").pack(pady=2)
        
        # Apply settings button
        tk.Button(settings_window, text="Apply Language Settings", command=lambda: self.apply_language_settings(settings_window)).pack(pady=10)
        
        # Apply theme to the settings window
        self.apply_theme_to_window(settings_window)
    
    def update_theme_from_settings(self):
        """Update theme when changed from settings"""
        new_theme = self.selected_theme.get()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            # Update theme button text
            if self.current_theme == "dark":
                self.theme_btn.config(text="☀️ Light")
            else:
                self.theme_btn.config(text="🌙 Dark")
            
            self.apply_theme()
            self.display_calendar()
    
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
    
    def start_notification_system(self):
        """Start the notification monitoring system"""
        if not self.notification_settings["enabled"]:
            return
        
        self.notification_running = True
        self.notification_thread = threading.Thread(target=self.notification_monitor, daemon=True)
        self.notification_thread.start()
        print("Notification system started")
    
    def stop_notification_system(self):
        """Stop the notification monitoring system"""
        self.notification_running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=1)
        print("Notification system stopped")
    
    def notification_monitor(self):
        """Background thread to monitor for upcoming events"""
        while self.notification_running:
            try:
                self.check_upcoming_events()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Notification error: {e}")
                time.sleep(60)
    
    def check_upcoming_events(self):
        """Check for upcoming events and send notifications"""
        if not self.notification_settings["enabled"]:
            return
        
        current_time = datetime.now()
        
        # Clear old notifications (older than 1 hour)
        self.active_notifications = [
            notif for notif in self.active_notifications 
            if (current_time - notif["time"]).total_seconds() < 3600
        ]
        
        # Check events for notification
        for year, months in self.events.items():
            for month, days in months.items():
                for day, hours in days.items():
                    for hour, event in hours.items():
                        try:
                            event_time = datetime(int(year), int(month), int(day), int(hour))
                            
                            # Check each advance notice period
                            for advance_minutes in self.notification_settings["advance_notice"]:
                                notification_time = event_time - timedelta(minutes=advance_minutes)
                                
                                # Check if we should notify now (within 1 minute window)
                                time_diff = abs((current_time - notification_time).total_seconds())
                                
                                if time_diff <= 60:  # Within 1 minute of notification time
                                    # Create unique notification ID
                                    notification_id = f"{year}-{month}-{day}-{hour}-{advance_minutes}"
                                    
                                    # Check if we already sent this notification
                                    if not any(notif["id"] == notification_id for notif in self.active_notifications):
                                        self.send_event_notification(event, event_time, advance_minutes)
                                        
                                        # Track this notification
                                        self.active_notifications.append({
                                            "id": notification_id,
                                            "time": current_time,
                                            "event_time": event_time,
                                            "advance_minutes": advance_minutes
                                        })
                        
                        except (ValueError, TypeError) as e:
                            print(f"Error processing event time: {e}")
                            continue
    
    def send_event_notification(self, event, event_time, advance_minutes):
        """Send notification for an upcoming event"""
        # Get event text
        if isinstance(event, dict):
            event_text = event.get('text', str(event))
        else:
            event_text = str(event)
        
        # Format notification message
        if advance_minutes == 0:
            title = "Event Starting Now!"
            message = f"{event_text}"
        else:
            title = f"Event in {advance_minutes} minutes"
            message = f"{event_text}\nScheduled for {event_time.strftime('%H:%M')}"
        
        # Send desktop notification if available and enabled
        if (self.notification_settings["desktop_notifications"] and 
            PLYER_AVAILABLE):
            try:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=10,
                    app_name="Calendar"
                )
            except Exception as e:
                print(f"Desktop notification error: {e}")
        
        # Send popup notification if enabled
        if self.notification_settings["popup_enabled"]:
            self.root.after(0, lambda: self.show_popup_notification(title, message, event_time))
        
        # Play sound if enabled (Windows system sound)
        if self.notification_settings["sound_enabled"]:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except ImportError:
                try:
                    # Alternative for non-Windows systems
                    print('\a')  # System bell
                except:
                    pass
        
        print(f"Notification sent: {title} - {message}")
    
    def show_popup_notification(self, title, message, event_time):
        """Show in-app popup notification"""
        # Create notification popup
        popup = tk.Toplevel(self.root)
        popup.title("Event Notification")
        popup.geometry("300x150")
        popup.attributes("-topmost", True)
        
        # Center the popup on screen
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Title label
        title_label = tk.Label(popup, text=title, font=("Arial", 12, "bold"))
        title_label.pack(pady=5)
        
        # Message label
        message_label = tk.Label(popup, text=message, font=("Arial", 10), wraplength=280)
        message_label.pack(pady=5, padx=10)
        
        # Time label
        time_label = tk.Label(popup, text=f"Event Time: {event_time.strftime('%H:%M')}", 
                            font=("Arial", 9), fg="gray")
        time_label.pack(pady=2)
        
        # Buttons frame
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        
        # Dismiss button
        dismiss_btn = tk.Button(button_frame, text="Dismiss", command=popup.destroy)
        dismiss_btn.pack(side=tk.LEFT, padx=5)
        
        # Snooze button
        snooze_btn = tk.Button(button_frame, text="Snooze (5 min)", 
                             command=lambda: self.snooze_notification(popup, event_time))
        snooze_btn.pack(side=tk.LEFT, padx=5)
        
        # Apply theme to popup
        self.apply_theme_to_window(popup)
        
        # Auto-close after 30 seconds
        popup.after(30000, popup.destroy)
    
    def snooze_notification(self, popup, event_time):
        """Snooze notification for 5 minutes"""
        popup.destroy()
        
        # Schedule another notification in 5 minutes
        snooze_time = datetime.now() + timedelta(minutes=5)
        
        def delayed_notification():
            time.sleep(300)  # 5 minutes
            if self.notification_running:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Snoozed Event Reminder",
                    f"Event at {event_time.strftime('%H:%M')} - Snoozed reminder"
                ))
        
        snooze_thread = threading.Thread(target=delayed_notification, daemon=True)
        snooze_thread.start()
    
    def show_notification_settings(self):
        """Show notification settings window"""
        notif_window = tk.Toplevel(self.root)
        notif_window.title("Notification Settings")
        notif_window.geometry("400x500")
        
        # Main settings frame
        main_frame = tk.Frame(notif_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enable/Disable notifications
        enable_frame = tk.LabelFrame(main_frame, text="General Settings", padx=10, pady=10)
        enable_frame.pack(fill=tk.X, pady=5)
        
        self.notif_enabled_var = tk.BooleanVar(value=self.notification_settings["enabled"])
        enable_check = tk.Checkbutton(enable_frame, text="Enable Notifications", 
                                    variable=self.notif_enabled_var)
        enable_check.pack(anchor=tk.W)
        
        self.desktop_notif_var = tk.BooleanVar(value=self.notification_settings["desktop_notifications"])
        desktop_check = tk.Checkbutton(enable_frame, text="Desktop Notifications", 
                                     variable=self.desktop_notif_var,
                                     state=tk.NORMAL if PLYER_AVAILABLE else tk.DISABLED)
        desktop_check.pack(anchor=tk.W)
        
        if not PLYER_AVAILABLE:
            tk.Label(enable_frame, text="(Install 'plyer' package for desktop notifications)", 
                   fg="gray", font=("Arial", 8)).pack(anchor=tk.W)
        
        self.popup_notif_var = tk.BooleanVar(value=self.notification_settings["popup_enabled"])
        popup_check = tk.Checkbutton(enable_frame, text="Popup Notifications", 
                                   variable=self.popup_notif_var)
        popup_check.pack(anchor=tk.W)
        
        self.sound_notif_var = tk.BooleanVar(value=self.notification_settings["sound_enabled"])
        sound_check = tk.Checkbutton(enable_frame, text="Sound Notifications", 
                                   variable=self.sound_notif_var)
        sound_check.pack(anchor=tk.W)
        
        # Advance notice settings
        advance_frame = tk.LabelFrame(main_frame, text="Advance Notice (minutes)", padx=10, pady=10)
        advance_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(advance_frame, text="Get notified before events:").pack(anchor=tk.W)
        
        self.advance_vars = {}
        for minutes in [5, 10, 15, 30, 60]:
            var = tk.BooleanVar(value=minutes in self.notification_settings["advance_notice"])
            self.advance_vars[minutes] = var
            check = tk.Checkbutton(advance_frame, text=f"{minutes} minutes before", variable=var)
            check.pack(anchor=tk.W)
        
        # Test notification button
        test_frame = tk.Frame(main_frame)
        test_frame.pack(fill=tk.X, pady=10)
        
        test_btn = tk.Button(test_frame, text="Test Notification", 
                           command=self.test_notification)
        test_btn.pack()
        
        # Save/Cancel buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_btn = tk.Button(button_frame, text="Save Settings", 
                           command=lambda: self.save_notification_settings(notif_window))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=notif_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Apply theme
        self.apply_theme_to_window(notif_window)
    
    def test_notification(self):
        """Send a test notification"""
        test_time = datetime.now() + timedelta(minutes=1)
        test_event = "Test Event - Notification System Working!"
        
        self.send_event_notification(test_event, test_time, 1)
        messagebox.showinfo("Test", "Test notification sent!")
    
    def save_notification_settings(self, window):
        """Save notification settings"""
        # Update settings
        self.notification_settings["enabled"] = self.notif_enabled_var.get()
        self.notification_settings["desktop_notifications"] = self.desktop_notif_var.get() and PLYER_AVAILABLE
        self.notification_settings["popup_enabled"] = self.popup_notif_var.get()
        self.notification_settings["sound_enabled"] = self.sound_notif_var.get()
        
        # Update advance notice settings
        self.notification_settings["advance_notice"] = [
            minutes for minutes, var in self.advance_vars.items() if var.get()
        ]
        
        # Restart notification system if settings changed
        if self.notification_settings["enabled"]:
            if not self.notification_running:
                self.start_notification_system()
        else:
            if self.notification_running:
                self.stop_notification_system()
        
        window.destroy()
        messagebox.showinfo("Settings Saved", "Notification settings have been updated!")
    
    def __del__(self):
        """Clean up when the application is closed"""
        if hasattr(self, 'notification_running'):
            self.stop_notification_system()

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



