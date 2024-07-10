import re
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, date



def update_date_fields(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        date_pattern = re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{2,4}),')

        for line in lines:
            match = date_pattern.match(line)
            if match:
                month = match.group(1)
                day = match.group(2)
                year = match.group(3)
                if len(year) == 2:  # If year is in 2-digit format, convert to 4-digit
                    year = '20' + year
                date_from_entry.delete(0, tk.END)
                date_from_entry.insert(0, f"{month.zfill(2)}/{day.zfill(2)}/{year}")
                date_format = '%m/%d/%Y'
                today = date.today().strftime(date_format)
                date_to_entry.delete(0, tk.END)
                date_to_entry.insert(0, today)
                break
        else:
            raise ValueError("Date format not recognized in the file.")
    except Exception as e:
        messagebox.showerror("Error", f"Error updating date fields: {e}")

def extract_member_messages(input_file, output_file, member_name, date_from, date_to, remove_datetime, remove_name):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    member_messages = []
    date_from = datetime.strptime(date_from, '%m/%d/%Y') if date_from else None
    date_to = datetime.strptime(date_to, '%m/%d/%Y') if date_to else None

    # Adjust the pattern to match the date format in your WhatsApp chat export
    member_message_pattern = re.compile(rf'^\d{{1,2}}/\d{{1,2}}/\d{{2,4}}, \d{{1,2}}:\d{{2}}[\u202F\u00A0]?(AM|PM)? - (.*?): (.*)')
    
    for line in lines:
        match = member_message_pattern.match(line)
        if match:
            message_date = datetime.strptime(match.group(0).split(',')[0], '%m/%d/%y')
            if (date_from and message_date < date_from) or (date_to and message_date > date_to):
                continue

            message = match.group(0)
            if remove_datetime:
                message = re.sub(r'^\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}[\u202F\u00A0]?(AM|PM)? - ', '', message)
            if remove_name:
                message = re.sub(rf'^{re.escape(member_name)}: ', '', message)
            
            if member_name and member_name in match.group(2):
                member_messages.append(message)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        for message in member_messages:
            file.write(message + '\n')
    messagebox.showinfo("Success", "Messages extracted successfully!")


def extract_members(input_file, output_file, member_type):
    try:
        left_pattern = re.compile(r'(.*?) left')
        joined_pattern = re.compile(r'(.*?) joined using this group\'s invite link')
        added_single_pattern = re.compile(r'(.*?) added (.*?)$')
        added_multiple_pattern = re.compile(r'(.*?) added (.*?) and (.*?)$')
        was_added_pattern = re.compile(r'(.*?) was added')
        were_added_pattern = re.compile(r'(.*?) and (.*?) were added')

        members = []

        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for line in lines:
            match = None
            if member_type == 'left':
                match = left_pattern.search(line)
            elif member_type == 'joined':
                match = joined_pattern.search(line)
            elif member_type == 'added' and 'added' in line:
                if ' and ' in line and ' were added' not in line:
                    match = added_multiple_pattern.search(line)
                elif ' and ' in line and ' were added' in line:
                    match = were_added_pattern.search(line)
                elif ' was added' in line:
                    match = was_added_pattern.search(line)
                else:
                    match = added_single_pattern.search(line)
                
            if match:
                try:
                    message_date = datetime.strptime(line.split(' - ')[0], '%m/%d/%y, %I:%M %p')
                except ValueError:
                    continue  # Skip if the line doesn't match expected datetime format
                
                if member_type == 'added':
                    if added_multiple_pattern.match(line):
                        person = match.group(1).strip()
                        number1 = match.group(2).strip()
                        number2 = match.group(3).strip()
                        members.append(f"{person} added {number1} and {number2}")
                    elif added_single_pattern.match(line):
                        person = match.group(1).strip()
                        number = match.group(2).strip()
                        members.append(f"{person} added {number}")
                    elif was_added_pattern.match(line):
                        person = match.group(1).strip()
                        members.append(f"{person} was added")
                    elif were_added_pattern.match(line):
                        number1 = match.group(1).strip()
                        number2 = match.group(2).strip()
                        members.append(f"{number1} and {number2} were added")
                else:
                    members.append(match.group(1).strip())

        with open(output_file, 'w', encoding='utf-8') as file:
            for member in members:
                # Clean the extracted member information
                member = member.replace('using this group\'s invite link', '').strip()
                file.write(member + '\n')

        messagebox.showinfo("Success", f"{member_type.capitalize()} members extracted successfully!")
    
    except Exception as e:
        messagebox.showerror("Error", f"Error extracting members: {e}")


def browse_file(entry):
    filename = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, filename)
    update_date_fields(filename)

def save_file(entry):
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def on_extract_messages():
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    member_name = member_name_entry.get()
    date_from = date_from_entry.get()
    date_to = date_to_entry.get()
    remove_datetime = remove_datetime_var.get()
    remove_name = remove_name_var.get()
    
    if not input_file or not output_file:
        messagebox.showerror("Error", "Please fill all required fields")
        return

    try:
        extract_member_messages(input_file, output_file, member_name, date_from, date_to, remove_datetime, remove_name)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_extract_members(member_type):
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    
    if not input_file or not output_file:
        messagebox.showerror("Error", "Please fill all required fields")
        return

    try:
        extract_members(input_file, output_file, member_type)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = tk.Tk()
root.title("WhatsApp Chat Extractor")

# Input file
tk.Label(root, text="Input File").grid(row=0, column=0, padx=10, pady=10)
input_file_entry = tk.Entry(root, width=50)
input_file_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=lambda: browse_file(input_file_entry)).grid(row=0, column=2, padx=10, pady=10)

# Output file
tk.Label(root, text="Output File").grid(row=1, column=0, padx=10, pady=10)
output_file_entry = tk.Entry(root, width=50)
output_file_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Save As", command=lambda: save_file(output_file_entry)).grid(row=1, column=2, padx=10, pady=10)

# Member name
tk.Label(root, text="Member Name").grid(row=2, column=0, padx=10, pady=10)
member_name_entry = tk.Entry(root, width=50)
member_name_entry.grid(row=2, column=1, padx=10, pady=10)

# Date from
tk.Label(root, text="Date From (MM/DD/YYYY)").grid(row=3, column=0, padx=10, pady=10)
date_from_entry = tk.Entry(root, width=50)
date_from_entry.grid(row=3, column=1, padx=10, pady=10)

# Date to
tk.Label(root, text="Date To (MM/DD/YYYY)").grid(row=4, column=0, padx=10, pady=10)
date_to_entry = tk.Entry(root, width=50)
date_to_entry.grid(row=4, column=1, padx=10, pady=10)

# Options to remove date/time and name
remove_datetime_var = tk.BooleanVar()
tk.Checkbutton(root, text="Remove Date/Time", variable=remove_datetime_var).grid(row=5, column=0, columnspan=2, padx=10, pady=10)
remove_name_var = tk.BooleanVar()
tk.Checkbutton(root, text="Remove Name", variable=remove_name_var).grid(row=5, column=1, columnspan=2, padx=10, pady=10)

# Buttons for extraction
tk.Button(root, text="Extract Messages", command=on_extract_messages).grid(row=6, column=0, columnspan=3, pady=10)
tk.Button(root, text="Extract Members Who Left", command=lambda: on_extract_members('left')).grid(row=7, column=0, columnspan=3, pady=10)
tk.Button(root, text="Extract Members Who Joined", command=lambda: on_extract_members('joined')).grid(row=8, column=0, columnspan=3, pady=10)
tk.Button(root, text="Extract Members Who Were Added", command=lambda: on_extract_members('added')).grid(row=9, column=0, columnspan=3, pady=10)

root.mainloop()
