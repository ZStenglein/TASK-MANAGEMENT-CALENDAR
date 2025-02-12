import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os


class TaskManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Task Management Calendar")
        self.root.geometry("800x600")
        # Initialize data storage
        self.current_user = None
        self.load_data()
        # Start with login page
        self.show_login_page()
    def load_data(self):
        """Load user and task data from JSON files"""
        try:
            with open('users.json', 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}
        try:
            with open('tasks.json', 'r') as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            self.tasks = {}
    def save_data(self):
        """Save user and task data to JSON files"""
        with open('users.json', 'w') as f:
            json.dump(self.users, f)
        with open('tasks.json', 'w') as f:
            json.dump(self.tasks, f)
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    def show_login_page(self):
        """Display the login page"""
        self.clear_window()
        # Create main frame
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Welcome text
        ttk.Label(frame, text="Welcome", font=('Helvetica', 24)).grid(row=0, column=0, pady=20)
        # Email input
        ttk.Label(frame, text="Email:").grid(row=1, column=0, pady=5, sticky=tk.W)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(frame, textvariable=email_var, width=40)
        email_entry.grid(row=2, column=0, pady=5)
        # Password input
        ttk.Label(frame, text="Password:").grid(row=3, column=0, pady=5, sticky=tk.W)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(frame, textvariable=password_var, show="*", width=40)
        password_entry.grid(row=4, column=0, pady=5)
        # Login button
        login_button = ttk.Button(
            frame, 
            text="LOGIN",
            command=lambda: self.login(email_var.get(), password_var.get())
        )
        login_button.grid(row=5, column=0, pady=20)
        # Sign up link
        signup_link = ttk.Button(
            frame, 
            text="Don't have an account? Sign Up",
            command=lambda: self.show_signup_page()
        )
        signup_link.grid(row=6, column=0, pady=10)
    def login(self, email, password):
        """Handle login process"""
        if email == "" or password == "":
            messagebox.showerror("Error", "Please fill in all fields")
            return
        # Check if user exists and password matches
        if email not in self.users:
            messagebox.showerror("Error", "User not found")
            return
        if self.users[email] != password:
            messagebox.showerror("Error", "Incorrect password")
            return
        self.current_user = email
        self.show_task_view()
    def signup(self, email, password):
        """Handle signup process"""
        if email == "" or password == "":
            messagebox.showerror("Error", "Please fill in all fields")
            return
        if not '@' in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return
        self.users[email] = password
        self.save_data()
        messagebox.showinfo("Success", "Account created successfully!")
        self.show_login_page()
    def show_task_view(self):
        """Display the task view page"""
        self.clear_window()
        # Create main container
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # Header frame
        header_frame = ttk.Frame(container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(header_frame, text="Task Board", font=('Helvetica', 16)).grid(row=0, column=0, padx=5)
        # Add task button
        add_task_btn = ttk.Button(
            header_frame,
            text="+ Add New Task",
            command=self.show_add_task_dialog
        )
        add_task_btn.grid(row=0, column=1, padx=5)
        # Filter frame
        filter_frame = ttk.Frame(container)
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(filter_frame, text="Show:").grid(row=0, column=0, padx=5)
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["All", "In Progress", "Completed", "Not Started"],
            state="readonly"
        )
        filter_combo.grid(row=0, column=1, padx=5)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.update_task_list())
        # Task list frame
        task_frame = ttk.Frame(container)
        task_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        # Configure columns
        columns = ('task', 'end_date', 'status', 'priority', 'progress', 'assignees')
        self.task_tree = ttk.Treeview(task_frame, columns=columns, show='headings')
        # Define headings
        self.task_tree.heading('task', text='Task')
        self.task_tree.heading('end_date', text='End Date')
        self.task_tree.heading('status', text='Status')
        self.task_tree.heading('priority', text='Priority')
        self.task_tree.heading('progress', text='Progress')
        self.task_tree.heading('assignees', text='Assignees')
        # Configure column widths
        self.task_tree.column('task', width=150)
        self.task_tree.column('end_date', width=100)
        self.task_tree.column('status', width=100)
        self.task_tree.column('priority', width=70)
        self.task_tree.column('progress', width=70)
        self.task_tree.column('assignees', width=150)
        # Add scrollbar
        scrollbar = ttk.Scrollbar(task_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        # Grid the tree and scrollbar
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        # Configure weights
        task_frame.columnconfigure(0, weight=1)
        task_frame.rowconfigure(0, weight=1)
        # Populate task list
        self.update_task_list()
    def update_task_list(self):
        """Update the task list based on the current filter"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        # Get tasks for current user
        user_tasks = self.tasks.get(self.current_user, [])
        # Apply filter
        filter_value = self.filter_var.get()
        if filter_value != "All":
            user_tasks = [task for task in user_tasks if task['status'] == filter_value]
        # Add tasks to tree
        for task in user_tasks:
            self.task_tree.insert('', tk.END, values=(
                task['name'],
                task['date'],
                task['status'],
                task['priority'],
                f"{task['progress']}%",
                ', '.join(task['assignees']) if task['assignees'] else '-'
            ))
    def show_add_task_dialog(self):
        """Show dialog for adding a new task"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Task")
        dialog.geometry("400x500")
        frame = ttk.Frame(dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Task name
        ttk.Label(frame, text="Task Name:").grid(row=0, column=0, pady=5, sticky=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=name_var, width=40).grid(row=1, column=0, pady=5)
        # End date
        ttk.Label(frame, text="End Date:").grid(row=2, column=0, pady=5, sticky=tk.W)
        date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=date_var, width=40).grid(row=3, column=0, pady=5)
        # Status
        ttk.Label(frame, text="Status:").grid(row=4, column=0, pady=5, sticky=tk.W)
        status_var = tk.StringVar(value="Not Started")
        status_combo = ttk.Combobox(
            frame,
            textvariable=status_var,
            values=["Not Started", "In Progress", "Completed"],
            state="readonly",
            width=37
        )
        status_combo.grid(row=5, column=0, pady=5)
        # Priority
        ttk.Label(frame, text="Priority:").grid(row=6, column=0, pady=5, sticky=tk.W)
        priority_var = tk.StringVar(value="1")
        ttk.Entry(frame, textvariable=priority_var, width=40).grid(row=7, column=0, pady=5)
        # Progress
        ttk.Label(frame, text="Progress:").grid(row=8, column=0, pady=5, sticky=tk.W)
        progress_var = tk.StringVar(value="0")
        ttk.Entry(frame, textvariable=progress_var, width=40).grid(row=9, column=0, pady=5)
        # Assignees
        ttk.Label(frame, text="Assignees (comma-separated):").grid(row=10, column=0, pady=5, sticky=tk.W)
        assignees_var = tk.StringVar()
        ttk.Entry(frame, textvariable=assignees_var, width=40).grid(row=11, column=0, pady=5)
        # Save button
        ttk.Button(
            frame,
            text="Save Task",
            command=lambda: self.save_task(
                name_var.get(),
                date_var.get(),
                status_var.get(),
                priority_var.get(),
                progress_var.get(),
                assignees_var.get(),
                dialog
            )
        ).grid(row=12, column=0, pady=20)
    def save_task(self, name, date, status, priority, progress, assignees, dialog):
        """Save a new task"""
        if not all([name, date, status, priority, progress]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        try:
            priority = int(priority)
            progress = float(progress)
            if not (0 <= progress <= 100):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid priority or progress value")
            return
        task = {
            'name': name,
            'date': date,
            'status': status,
            'priority': priority,
            'progress': progress,
            'assignees': [a.strip() for a in assignees.split(',') if a.strip()]
        }
        # Update progress to 100 if status is "Completed"
        if status == "Completed":
            task['progress'] = 100
        if self.current_user not in self.tasks:
            self.tasks[self.current_user] = []
        self.tasks[self.current_user].append(task)
        self.save_data()
        dialog.destroy()
        self.update_task_list()  # Update the task list view
    def show_signup_page(self):
        """Display the sign up page"""
        self.clear_window()
        # Create main frame
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Welcome text
        ttk.Label(frame, text="Sign Up", font=('Helvetica', 24)).grid(row=0, column=0, pady=20)
        # Email input
        ttk.Label(frame, text="Email:").grid(row=1, column=0, pady=5, sticky=tk.W)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(frame, textvariable=email_var, width=40)
        email_entry.grid(row=2, column=0, pady=5)
        # Password input
        ttk.Label(frame, text="Password:").grid(row=3, column=0, pady=5, sticky=tk.W)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(frame, textvariable=password_var, show="*", width=40)
        password_entry.grid(row=4, column=0, pady=5)
        # Sign up button
        signup_button = ttk.Button(
            frame,
            text="Sign Up",
            command=lambda: self.signup(email_var.get(), password_var.get())
        )
        signup_button.grid(row=5, column=0, pady=20)
        # Login link
        login_link = ttk.Label(
            frame,
            text="Already have an account? Log In",
            cursor="hand2",
            foreground="blue"
        )
        login_link.grid(row=6, column=0, pady=10)
        login_link.bind("<Button-1>", lambda e: self.show_login_page())
if __name__ == "__main__":
    app = TaskManager()
    app.root.mainloop()
