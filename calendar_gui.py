from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from datetime import datetime
import calendar

class CalendarApp(App):
    def build(self):
        self.selected_year = datetime.now().year
        self.selected_month = datetime.now().month
        self.selected_day = None
        self.selected_hour = None

        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Year selection
        year_layout = BoxLayout(size_hint=(1, 0.1))
        year_layout.add_widget(Label(text="Select Year:"))
        self.year_spinner = Spinner(
            text=str(self.selected_year),
            values=[str(year) for year in range(1900, 2101)],
            size_hint=(0.3, 1)
        )
        self.year_spinner.bind(text=self.on_year_selected)
        year_layout.add_widget(self.year_spinner)
        main_layout.add_widget(year_layout)

        # Month grid
        self.month_grid = GridLayout(cols=3, size_hint=(1, 0.6))
        self.update_month_grid()
        main_layout.add_widget(self.month_grid)

        # Day and hour selection
        day_hour_layout = BoxLayout(size_hint=(1, 0.2))
        day_hour_layout.add_widget(Label(text="Select Day:"))
        self.day_spinner = Spinner(
            text="",
            values=[],
            size_hint=(0.2, 1)
        )
        self.day_spinner.bind(text=self.on_day_selected)
        day_hour_layout.add_widget(self.day_spinner)

        day_hour_layout.add_widget(Label(text="Select Hour:"))
        self.hour_spinner = Spinner(
            text="",
            values=[str(hour) for hour in range(24)],
            size_hint=(0.2, 1)
        )
        self.hour_spinner.bind(text=self.on_hour_selected)
        day_hour_layout.add_widget(self.hour_spinner)
        main_layout.add_widget(day_hour_layout)

        # Confirm button
        confirm_button = Button(text="Confirm Selection", size_hint=(1, 0.1))
        confirm_button.bind(on_press=self.confirm_selection)
        main_layout.add_widget(confirm_button)

        return main_layout

    def update_month_grid(self):
        self.month_grid.clear_widgets()
        for month in range(1, 13):
            month_button = Button(text=calendar.month_name[month], size_hint=(1, None), height=40)
            month_button.bind(on_press=lambda btn, m=month: self.on_month_selected(m))
            self.month_grid.add_widget(month_button)

    def on_year_selected(self, spinner, text):
        self.selected_year = int(text)
        self.update_day_spinner()

    def on_month_selected(self, month):
        self.selected_month = month
        self.update_day_spinner()

    def on_day_selected(self, spinner, text):
        if text:
            self.selected_day = int(text)

    def on_hour_selected(self, spinner, text):
        if text:
            self.selected_hour = int(text)

    def update_day_spinner(self):
        if self.selected_year and self.selected_month:
            days_in_month = calendar.monthrange(self.selected_year, self.selected_month)[1]
            self.day_spinner.values = [str(day) for day in range(1, days_in_month + 1)]
            self.day_spinner.text = ""

    def confirm_selection(self, instance):
        if self.selected_year and self.selected_month and self.selected_day is not None and self.selected_hour is not None:
            popup = Popup(
                title="Selection Confirmed",
                content=Label(
                    text=f"Year: {self.selected_year}, Month: {self.selected_month}, "
                         f"Day: {self.selected_day}, Hour: {self.selected_hour}:00"
                ),
                size_hint=(0.8, 0.4)
            )
            popup.open()
        else:
            popup = Popup(
                title="Incomplete Selection",
                content=Label(text="Please select year, month, day, and hour."),
                size_hint=(0.8, 0.4)
            )
            popup.open()

if __name__ == "__main__":
    CalendarApp().run()
