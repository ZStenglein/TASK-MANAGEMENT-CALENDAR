import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import re
from datetime import datetime

###############################################################################
# Utility: Data Persistence
###############################################################################
def load_data(filename="users_and_tasks.json"):
    """
    Loads user data (accounts and tasks) from a local JSON file.
    If the file doesn't exist or is empty, returns a default structure.
    """
    if not os.path.exists(filename):
        return {"users": []}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except:
        return {"users": []}

def save_data(data, filename="users_and_tasks.json"):
    """
    Saves user data (accounts and tasks) to a local JSON file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

###############################################################################
# Utility: Password & Email Validation
###############################################################################
def is_valid_email(email):
    """
    Basic check for a valid email format.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """
    Checks if the password meets complexity requirements:
    - Minimum 8 characters
    - Contains at least one letter
    - Contains at least one digit
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

###############################################################################
# Class: Task
###############################################################################
class Task:
    """
    A simple data class for tasks. 
    name        : str
    end_date    : str (e.g., '2025-12-31')
    status      : str (e.g., 'Not Started', 'In Progress', 'Completed')
    priority    : int
    progress    : int (0 to 100)
    assignees   : list of names
    """
    def __init__(self, name, end_date, status, priority, progress, assignees):
        self.name = name
        self.end_date = end_date
        self.status = status
        self.priority = priority
        self.progress = progress
        self.assignees = assignees

    def to_dict(self):
        return {
            "name": self.name,
            "end_date": self.end_date,
            "status": self.status,
            "priority": self.priority,
            "progress": self.progress,
            "assignees": self.assignees
        }

###############################################################################
# Class: MainApp
###############################################################################
class MainApp(tk.Tk):
    """
    Main application class.
    Handles switching between the Login/Signup frame and the TaskView frame.
    """
    def __init__(self):
        super().__init__()
        self.title("Task Management Calendar")
        self.geometry("700x500")
        self.resizable(False, False)

        # Load data from JSON
        self.data = load_data()

        # Active user index in self.data["users"]
        self.active_user_index = None

        self._show_login_frame()

    def _show_login_frame(self):
        """
        Clears the window and shows the login/register frame.
        """
        for widget in self.winfo_children():
            widget.destroy()
        login_frame = LoginFrame(self, self.data)
        login_frame.pack(expand=True, fill="both")

    def show_task_view(self, user_index):
        """
        Clears the window and shows the Task View frame for the specified user index.
        """
        self.active_user_index = user_index
        for widget in self.winfo_children():
            widget.destroy()
        task_view = TaskViewFrame(self, self.data, user_index)
        task_view.pack(expand=True, fill="both")

###############################################################################
# Frame: LoginFrame
###############################################################################
class LoginFrame(tk.Frame):
    """
    Frame for user login and signup.
    """
    def __init__(self, master, data):
        super().__init__(master)
        self.master = master
        self.data = data

        self.label_title = tk.Label(self, text="Login", font=("Arial", 16, "bold"))
        self.label_title.pack(pady=10)

        tk.Label(self, text="Email:").pack()
        self.entry_email = tk.Entry(self, width=30)
        self.entry_email.pack()

        tk.Label(self, text="Password:").pack()
        self.entry_password = tk.Entry(self, width=30, show="*")
        self.entry_password.pack()

        self.button_login = tk.Button(self, text="Login", command=self.login)
        self.button_login.pack(pady=10)

        self.button_signup = tk.Button(self, text="Sign Up", command=self.signup_popup)
        self.button_signup.pack()

    def login(self):
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()

        # Validate input
        if not email or not password:
            messagebox.showerror("Error", "Please fill in both fields.")
            return

        # Find user
        for i, user in enumerate(self.data["users"]):
            if user["email"].lower() == email.lower():
                # Check password (plain text for simplicity; ideally store a hash)
                if user["password"] == password:
                    # Successful login
                    messagebox.showinfo("Success", "Login successful!")
                    self.master.show_task_view(i)
                    return
                else:
                    messagebox.showerror("Error", "Incorrect password.")
                    return

        messagebox.showerror("Error", "Email not found.")

    def signup_popup(self):
        """
        Popup window to handle signup.
        """
        popup = tk.Toplevel(self)
        popup.title("Sign Up")
        popup.geometry("300x250")
        popup.resizable(False, False)

        tk.Label(popup, text="Email:").pack(pady=5)
        entry_new_email = tk.Entry(popup, width=30)
        entry_new_email.pack()

        tk.Label(popup, text="Password:").pack(pady=5)
        entry_new_password = tk.Entry(popup, width=30, show="*")
        entry_new_password.pack()

        def handle_signup():
            new_email = entry_new_email.get().strip()
            new_pass = entry_new_password.get().strip()

            # Validate
            if not is_valid_email(new_email):
                messagebox.showerror("Error", "Invalid email format.")
                return
            if not is_valid_password(new_pass):
                messagebox.showerror(
                    "Error",
                    "Password must be at least 8 characters,\ninclude one letter and one number."
                )
                return
            # Check if email already exists
            for user in self.data["users"]:
                if user["email"].lower() == new_email.lower():
                    messagebox.showerror("Error", "Email is already taken.")
                    return

            # Create new user
            new_user = {
                "email": new_email,
                "password": new_pass,
                "tasks": []
            }
            self.data["users"].append(new_user)
            save_data(self.data)
            messagebox.showinfo("Success", "Account created successfully!")
            popup.destroy()

        btn_create = tk.Button(popup, text="Create Account", command=handle_signup)
        btn_create.pack(pady=10)

###############################################################################
# Frame: TaskViewFrame
###############################################################################
class TaskViewFrame(tk.Frame):
    """
    Frame to view, create, edit, and filter tasks for the currently logged-in user.
    """
    def __init__(self, master, data, user_index):
        super().__init__(master)
        self.master = master
        self.data = data
        self.user_index = user_index

        # Title
        tk.Label(self, text="Task Management Calendar", font=("Arial", 16, "bold")).pack(pady=5)

        # Button: Add New Task
        btn_new_task = tk.Button(self, text="Add New Task", command=self.open_create_task_window)
        btn_new_task.pack()

        # Button: Filter
        btn_filter = tk.Button(self, text="Filter Tasks", command=self.open_filter_window)
        btn_filter.pack()

        # Treeview for tasks
        columns = ("name", "end_date", "status", "priority", "progress", "assignees")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100 if col != "name" else 150)

        self.tree.bind("<Double-1>", self.handle_tree_double_click)

        self.tree.pack(pady=10)

        # Populate the tree initially
        self.refresh_task_list()

        # Button: Logout
        btn_logout = tk.Button(self, text="Logout", command=self.logout)
        btn_logout.pack()

    def logout(self):
        self.master.active_user_index = None
        self.master._show_login_frame()

    def refresh_task_list(self, filtered_tasks=None):
        """
        Refreshes the Treeview with either all tasks or a filtered list.
        """
        self.tree.delete(*self.tree.get_children())

        if filtered_tasks is not None:
            tasks_to_show = filtered_tasks
        else:
            tasks_to_show = self.data["users"][self.user_index]["tasks"]

        # insertion sort by priority
        tasks_to_show = insertion_sort_by_priority(tasks_to_show)
        

        for idx, t in enumerate(tasks_to_show):
            assignees_str = ", ".join(t["assignees"]) if t["assignees"] else ""
            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    t["name"],
                    t["end_date"],
                    t["status"],
                    t["priority"],
                    f"{t['progress']}%",
                    assignees_str
                )
            )

    def open_create_task_window(self):
        CreateOrEditTaskWindow(self, mode="create")

    def handle_tree_double_click(self, event):
        """
        Double-click on a row to edit the task.
        """
        item_id = self.tree.focus()
        if not item_id:
            return

        CreateOrEditTaskWindow(self, mode="edit", task_index=int(item_id))

    def open_filter_window(self):
        FilterWindow(self)

###############################################################################
# Window: CreateOrEditTaskWindow
###############################################################################
class CreateOrEditTaskWindow(tk.Toplevel):
    """
    Popup window to create or edit a task.
    """
    def __init__(self, parent_frame, mode="create", task_index=None):
        super().__init__(parent_frame)
        self.parent_frame = parent_frame
        self.master_app = parent_frame.master
        self.data = parent_frame.data
        self.user_index = parent_frame.user_index
        self.mode = mode
        self.task_index = task_index

        self.title("Create Task" if mode == "create" else "Edit Task")
        self.geometry("400x450")
        self.resizable(False, False)

        # If editing, load existing task data
        self.existing_task = None
        if self.mode == "edit" and self.task_index is not None:
            self.existing_task = self.data["users"][self.user_index]["tasks"][self.task_index]

        # Task Name
        tk.Label(self, text="Task Name").pack(pady=5)
        self.entry_name = tk.Entry(self, width=30)
        self.entry_name.pack()
        if self.existing_task:
            self.entry_name.insert(0, self.existing_task["name"])

        # End Date
        tk.Label(self, text="End Date (YYYY-MM-DD)").pack(pady=5)
        self.entry_end_date = tk.Entry(self, width=30)
        self.entry_end_date.pack()
        if self.existing_task:
            self.entry_end_date.insert(0, self.existing_task["end_date"])

        # Status
        tk.Label(self, text="Status").pack(pady=5)
        self.status_var = tk.StringVar(value="Not Started")
        status_options = ["Not Started", "In Progress", "Completed"]
        self.dropdown_status = ttk.Combobox(self, textvariable=self.status_var, values=status_options, state="readonly")
        self.dropdown_status.pack()
        if self.existing_task:
            self.status_var.set(self.existing_task["status"])

        # Priority
        tk.Label(self, text="Priority (1 = Highest)").pack(pady=5)
        self.entry_priority = tk.Entry(self, width=30)
        self.entry_priority.pack()
        if self.existing_task:
            self.entry_priority.insert(0, str(self.existing_task["priority"]))

        # Progress
        tk.Label(self, text="Progress (0 - 100%)").pack(pady=5)
        self.entry_progress = tk.Entry(self, width=30)
        self.entry_progress.pack()
        if self.existing_task:
            self.entry_progress.insert(0, str(self.existing_task["progress"]))

        # Assignees
        tk.Label(self, text="Assignees (comma-separated, up to 5)").pack(pady=5)
        self.entry_assignees = tk.Entry(self, width=30)
        self.entry_assignees.pack()
        if self.existing_task:
            if self.existing_task["assignees"]:
                self.entry_assignees.insert(0, ", ".join(self.existing_task["assignees"]))

        # Button: Save
        btn_save = tk.Button(self, text="Save Task", command=self.save_task)
        btn_save.pack(pady=10)

    def save_task(self):
        """
        Validate fields, then save or update the task in the JSON structure.
        """
        name = self.entry_name.get().strip()
        end_date = self.entry_end_date.get().strip()
        status = self.status_var.get().strip()
        priority_str = self.entry_priority.get().strip()
        progress_str = self.entry_progress.get().strip()
        assignees_raw = self.entry_assignees.get().strip()

        # Validate required fields
        if not name:
            messagebox.showerror("Error", "Task name is required.")
            return
        if not end_date:
            messagebox.showerror("Error", "End date is required.")
            return
        # Validate date format
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
            # optional: also check if it's in the past, etc.
        except ValueError:
            messagebox.showerror("Error", "End date must be in YYYY-MM-DD format.")
            return
        # Validate priority
        try:
            priority = int(priority_str)
        except ValueError:
            messagebox.showerror("Error", "Priority must be an integer.")
            return
        # Validate progress
        try:
            progress = int(progress_str)
            if progress < 0 or progress > 100:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Progress must be an integer from 0 to 100.")
            return

        # Validate assignees
        assignees = []
        if assignees_raw:
            splitted = [a.strip() for a in assignees_raw.split(",") if a.strip()]
            if len(splitted) > 5:
                messagebox.showerror("Error", "You can add up to 5 assignees.")
                return
            # Optionally filter out special characters or duplicates
            # Example: ensure no duplicates
            unique_names = set()
            for s in splitted:
                if s in unique_names:
                    messagebox.showerror("Error", f"Duplicate assignee '{s}'.")
                    return
                unique_names.add(s)
            assignees = list(unique_names)

        new_task_data = {
            "name": name,
            "end_date": end_date,
            "status": status,
            "priority": priority,
            "progress": progress,
            "assignees": assignees
        }

        if self.mode == "create":
            # Append
            self.data["users"][self.user_index]["tasks"].append(new_task_data)
        else:
            # Edit
            self.data["users"][self.user_index]["tasks"][self.task_index] = new_task_data

        save_data(self.data)
        messagebox.showinfo("Success", "Task saved successfully.")
        self.parent_frame.refresh_task_list()
        self.destroy()

###############################################################################
# Window: FilterWindow
###############################################################################
class FilterWindow(tk.Toplevel):
    """
    Popup window to filter tasks by end date, status, priority, progress, or assignees.
    """
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.parent_frame = parent_frame
        self.master_app = parent_frame.master
        self.data = parent_frame.data
        self.user_index = parent_frame.user_index

        self.title("Filter Tasks")
        self.geometry("400x300")
        self.resizable(False, False)

        # Create fields for each filter type
        tk.Label(self, text="End Date Before (YYYY-MM-DD):").pack(pady=5)
        self.entry_end_date = tk.Entry(self, width=25)
        self.entry_end_date.pack()

        tk.Label(self, text="Status (exact match):").pack(pady=5)
        self.status_var = tk.StringVar()
        status_options = ["", "Not Started", "In Progress", "Completed"]
        self.dropdown_status = ttk.Combobox(self, textvariable=self.status_var, values=status_options)
        self.dropdown_status.pack()

        tk.Label(self, text="Max Priority (integer):").pack(pady=5)
        self.entry_priority = tk.Entry(self, width=25)
        self.entry_priority.pack()

        tk.Label(self, text="Progress >= (0-100):").pack(pady=5)
        self.entry_progress = tk.Entry(self, width=25)
        self.entry_progress.pack()

        tk.Label(self, text="Assignee Contains:").pack(pady=5)
        self.entry_assignee = tk.Entry(self, width=25)
        self.entry_assignee.pack()

        tk.Button(self, text="Apply Filter", command=self.apply_filter).pack(pady=5)
        tk.Button(self, text="Clear Filter", command=self.clear_filter).pack(pady=5)

    def apply_filter(self):
        tasks = self.data["users"][self.user_index]["tasks"]

        end_date_filter = self.entry_end_date.get().strip()
        status_filter = self.status_var.get().strip()
        priority_filter = self.entry_priority.get().strip()
        progress_filter = self.entry_progress.get().strip()
        # Grab assignee input and split on commas
        assignee_input = self.entry_assignee.get().strip().lower()
        assignee_tokens = [token.strip() for token in assignee_input.split(",") if token.strip()]

        filtered = []
        for t in tasks:
            # End Date
            if end_date_filter:
                try:
                    cutoff = datetime.strptime(end_date_filter, "%Y-%m-%d")
                    task_date = datetime.strptime(t["end_date"], "%Y-%m-%d")
                    if task_date > cutoff:
                        continue
                except ValueError:
                    # Invalid date input -> skip
                    continue

            # Status
            if status_filter and t["status"] != status_filter:
                continue

            # Priority
            if priority_filter:
                try:
                    max_priority = int(priority_filter)
                    if t["priority"] > max_priority:
                        continue
                except ValueError:
                    # Invalid priority -> skip
                    continue

            # Progress
            if progress_filter:
                try:
                    min_prog = int(progress_filter)
                    if t["progress"] < min_prog:
                        continue
                except ValueError:
                    continue

            # Assignee filter: check if *any* token is found among the assignees
            if assignee_tokens:
                # Convert each assignee to lowercase for substring checks
                lower_assignees = [a.lower() for a in t["assignees"]]
                # If *none* of the tokens appear in any assignee, skip
                # OR logic -> if at least one token matches, we keep it
                if not any(
                    any(tok in assignee for assignee in lower_assignees)
                    for tok in assignee_tokens
                ):
                    continue

            filtered.append(t)

        if not filtered:
            messagebox.showinfo("No Results", "No tasks match the selected criteria.")
        self.parent_frame.refresh_task_list(filtered)
        self.destroy()


###############################################################################
# Insertion Sort for tasks by priority
###############################################################################
def insertion_sort_by_priority(tasks):
    """
    An example of Insertion Sort that sorts tasks by ascending priority (smallest = highest).
    Returns a new sorted list.
    """
    arr = tasks[:]
    for i in range(1, len(arr)):
        key_task = arr[i]
        j = i - 1
        while j >= 0 and arr[j]["priority"] > key_task["priority"]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key_task
    return arr

###############################################################################
# Main Entry Point
###############################################################################
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
