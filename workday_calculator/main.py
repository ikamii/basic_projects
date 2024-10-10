import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from tkinter import font
import json
import os
from datetime import datetime

# File to save selected days
SAVE_FILE = "selected_days.json"

# Get today's date
currentdate = datetime.today()

# Load previously saved days if the file exists
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        selected_days = json.load(f)
else:
    selected_days = {}

def save_selected_days():
    """Save the selected days to a JSON file."""
    with open(SAVE_FILE, "w") as f:
        json.dump(selected_days, f)

def open_calendar():
    """Open the calendar window to allow the user to select days."""
    # Define custom font for the calendar (you can adjust the size as needed)
    calendar_font = font.Font(family="Arial", size=12)  # Bigger font for the calendar
    header_font = font.Font(family="Arial", size=16, weight="bold")  # Bigger font for headers

    # Calendar widget with custom fonts
    cal = Calendar(root, selectmode='day',
                   year=currentdate.year, month=currentdate.month, day=currentdate.day,
                   background='black', foreground='white',
                   selectbackground='black', selectforeground='lightgreen',
                   headersbackground='black', headersforeground='orange',
                   normalbackground='black', normalforeground='white',
                   font=calendar_font,  # Set calendar font
                   headersfont=header_font)  # Set header font
    cal.grid(row=1, column=1, padx=10, pady=10, sticky="n")

    # Create a tag for marking already selected days in red
    cal.tag_config('selected_day', background='black', foreground='red')

    # Mark previously selected days
    for selected_date, flag in selected_days.items():
        # Convert the string date to datetime.date object in dd.mm.yyyy format
        selected_date_obj = datetime.strptime(selected_date, "%d.%m.%Y").date()
        # Add the tag to the already selected day
        cal.calevent_create(selected_date_obj, 'Selected', tags='selected_day')

    def add_day(flag):
        selected_date_str = cal.get_date()

        # Convert the date from mm/dd/yy to datetime object (assuming 4-digit year conversion)
        selected_date_obj = datetime.strptime(selected_date_str, "%m/%d/%y").replace(year=datetime.now().year)

        # Reformat the date as dd.mm.yyyy
        selected_date = selected_date_obj.strftime("%d.%m.%Y")

        # Store the selected date with the flag (Full/Half)
        selected_days[selected_date] = flag
        day_listbox.insert(tk.END, f"{selected_date} - {flag}")

        # Mark the selected day in red in the calendar
        cal.calevent_create(selected_date_obj, 'Selected', tags='selected_day')

        # Save the updated selection in dd.mm.yyyy format
        save_selected_days()

        # Automatically calculate total days and remaining days
        calculate_work_days_from_selection()

    # Frame to hold the buttons
    button_frame = tk.Frame(root, bg="#333333")
    button_frame.grid(row=2, column=1, padx=10, pady=10, sticky="n")

    # Buttons to tag the selected day as "Full" or "Half"
    full_day_button = tk.Button(button_frame, text="Full Day", command=lambda: add_day("Full"))
    full_day_button.grid(row=0, column=0, padx=5)

    half_day_button = tk.Button(button_frame, text="Half Day", command=lambda: add_day("Half"))
    half_day_button.grid(row=0, column=1, padx=5)

def load_selected_days():
    """Load saved selected days into the listbox and calculate totals."""
    total_days = 0

    # Load saved selected days into the listbox and calculate the total days worked
    for day, flag in selected_days.items():
        day_listbox.insert(tk.END, f"{day} - {flag}")
        if flag == "Full":
            total_days += 1
        elif flag == "Half":
            total_days += 0.5

    # Preload total days worked and remaining days
    allowed_days = int(allowed_days_entry.get())  # Get allowed days from entry
    remaining_days = allowed_days - total_days

    # Update the result entry for total days worked
    result_entry.config(state="normal")
    result_entry.delete(0, tk.END)
    result_entry.insert(0, f"{total_days:.2f}")
    result_entry.config(state="readonly")

    # Update the result entry for remaining days
    remaining_entry.config(state="normal")
    remaining_entry.delete(0, tk.END)
    remaining_entry.insert(0, f"{remaining_days:.2f}")
    remaining_entry.config(state="readonly")

def calculate_work_days_from_selection():
    """Calculate total work days and remaining days based on the selection."""
    total_days = 0
    for day, flag in selected_days.items():
        if flag == "Full":
            total_days += 1
        elif flag == "Half":
            total_days += 0.5

    # Safeguard if user clears the allowed days entry
    try:
        allowed_days = int(allowed_days_entry.get())
    except ValueError:
        allowed_days = 0  # Default to 0 if the entry is empty or invalid

    remaining_days = allowed_days - total_days

    # Update the result entry for total days worked
    result_entry.config(state="normal")
    result_entry.delete(0, tk.END)
    result_entry.insert(0, f"{total_days:.2f}")
    result_entry.config(state="readonly")

    # Update the result entry for remaining days
    remaining_entry.config(state="normal")
    remaining_entry.delete(0, tk.END)
    remaining_entry.insert(0, f"{remaining_days:.2f}")
    remaining_entry.config(state="readonly")

def allowed_days_changed(event):
    """Trigger recalculation when allowed working days is changed."""
    calculate_work_days_from_selection()

# Create the main window
root = tk.Tk()
root.title("Workdays Calculator with Calendar")
root.geometry("650x400")  # Increase the window size to accommodate side-by-side layout
root.configure(bg="#333333")

# Create the allowed working days label and entry
# Create a frame to hold the "Allowed Working Days" label and entry
allowed_days_frame = tk.Frame(root, bg="#333333")
allowed_days_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")  # Align to the left

# Create the allowed working days label and place it inside the frame
allowed_days_label = tk.Label(allowed_days_frame, text="Allowed Working Days:", fg="white", bg="#333333")
allowed_days_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

# Create the allowed working days entry and place it inside the frame
allowed_days_entry = tk.Entry(allowed_days_frame, bg="black", fg="white", width=10)
allowed_days_entry.insert(0, "120")
allowed_days_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Bind changes in the allowed days entry to automatically recalculate
allowed_days_entry.bind("<KeyRelease>", allowed_days_changed)

# Create a listbox to show selected days and their flags
day_listbox = tk.Listbox(root, height=10, width=40)
day_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="n")

# Create a frame to align the result labels and entry boxes
result_frame = tk.Frame(root, bg="#333333")
result_frame.grid(row=3, column=0, padx=10, pady=5, sticky="w")  # Align to the left

# Create a label for the total days worked result
result_label = tk.Label(result_frame, text="Total Days Worked:", fg="white", bg="#333333")
result_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

# Create an entry box to display the total days worked (read-only)
result_entry = tk.Entry(result_frame, justify="center", width=10, fg="white", bg="black")
result_entry.grid(row=0, column=1, padx=25, pady=5, sticky="w")

# Create a label for the remaining days result
remaining_label = tk.Label(result_frame, text="Remaining Days:", fg="white", bg="#333333")
remaining_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

# Create an entry box to display the remaining days (read-only)
remaining_entry = tk.Entry(result_frame, justify="center", width=10, fg="white", bg="black")
remaining_entry.grid(row=1, column=1, padx=25, pady=5, sticky="w")

# Initially set result_entry and remaining_entry to readonly
result_entry.config(state="readonly")
remaining_entry.config(state="readonly")

# Load any previously saved selected days and preload calculations
load_selected_days()

# Open the calendar and mark previously selected days
open_calendar()

# Start the Tkinter event loop
root.mainloop()
