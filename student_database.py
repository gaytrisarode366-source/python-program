import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "Student Database Management System"
TABLE_SIZE = 10
DATA_FILE = "student_data.json"

# Professional blue-and-white palette
NAVY = "#12345A"
BLUE = "#1D66C1"
BLUE_DARK = "#164F98"
PALE_BLUE = "#EAF3FF"
BG = "#F4F7FB"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
MUTED = "#64748B"
BORDER = "#DCE5F0"
GREEN = "#16805D"
RED = "139, 0, 0"
AMBER = "#B7791F"


class Student:
    def __init__(self, roll_no, name, branch, year, division, email, phone, marks):
        self.roll_no = int(roll_no)
        self.name = name.strip()
        self.branch = branch.strip()
        self.year = year.strip()
        self.division = division.strip().upper()
        self.email = email.strip()
        self.phone = phone.strip()
        self.marks = float(marks)

    def to_dict(self):
        return {
            "roll_no": self.roll_no,
            "name": self.name,
            "branch": self.branch,
            "year": self.year,
            "division": self.division,
            "email": self.email,
            "phone": self.phone,
            "marks": self.marks,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["roll_no"], data["name"], data["branch"], data["year"],
            data["division"], data["email"], data["phone"], data["marks"]
        )


class StudentHashTable:
    """Hash table using separate chaining for collision handling."""

    def __init__(self, size=TABLE_SIZE, filename=DATA_FILE):
        self.size = size
        self.filename = filename
        self.table = [[] for _ in range(size)]
        self.load()

    def hash_function(self, key):
        return int(key) % self.size

    def search(self, roll_no):
        try:
            roll_no = int(roll_no)
        except (ValueError, TypeError):
            return None
        for student in self.table[self.hash_function(roll_no)]:
            if student.roll_no == roll_no:
                return student
        return None

    def insert(self, student):
        if self.search(student.roll_no) is not None:
            return False
        self.table[self.hash_function(student.roll_no)].append(student)
        self.save()
        return True

    def update(self, roll_no, updated_student):
        roll_no = int(roll_no)
        bucket = self.table[self.hash_function(roll_no)]
        for index, student in enumerate(bucket):
            if student.roll_no == roll_no:
                bucket[index] = updated_student
                self.save()
                return True
        return False

    def delete(self, roll_no):
        roll_no = int(roll_no)
        bucket = self.table[self.hash_function(roll_no)]
        for index, student in enumerate(bucket):
            if student.roll_no == roll_no:
                del bucket[index]
                self.save()
                return True
        return False

    def all_students(self):
        return sorted(
            (student for bucket in self.table for student in bucket),
            key=lambda student: student.roll_no
        )

    def collision_count(self):
        # Counts extra records in occupied buckets (e.g. 3 records in one bucket = 2 collisions).
        return sum(max(0, len(bucket) - 1) for bucket in self.table)

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump([s.to_dict() for s in self.all_students()], file, indent=4)
        except OSError as error:
            messagebox.showwarning("Save warning", f"Could not save records:\n{error}")

    def load(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                records = json.load(file)
            if not isinstance(records, list):
                raise ValueError("Expected a list of student records.")
            for record in records:
                student = Student.from_dict(record)
                if self.search(student.roll_no) is None:
                    self.table[self.hash_function(student.roll_no)].append(student)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            messagebox.showwarning(
                "Data loading warning",
                f"Saved data could not be loaded:\n{error}\n\nA new empty table will be used."
            )


class StudentDatabaseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x850")
        self.minsize(1050, 700)
        self.configure(bg=BG)

        self.database = StudentHashTable()
        self.selected_roll = None
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self._configure_styles()
        self._build_layout()
        self.refresh_all()

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=WHITE, foreground=TEXT,
                        fieldbackground=WHITE, rowheight=30, borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=PALE_BLUE, foreground=NAVY,
                        font=("Segoe UI", 10, "bold"), relief="flat", padding=8)
        style.map("Treeview", background=[("selected", "#D7E9FF")],
                  foreground=[("selected", NAVY)])
        style.configure("TCombobox", padding=6)
        style.configure("Vertical.TScrollbar", background=PALE_BLUE)

    def _build_layout(self):
        # Header
        header = tk.Frame(self, bg=NAVY, height=82)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=NAVY)
        brand.pack(side="left", padx=24, pady=14)
        tk.Label(brand, text="STUDENT DATABASE", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(brand, text="DATA STRUCTURES  •  HASHING PROJECT",
                 bg=NAVY, fg="#C9DDF7", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(header, text="SPPU  |  COMPUTER ENGINEERING",
                 bg=NAVY, fg=WHITE, font=("Segoe UI", 10, "bold")).pack(side="right", padx=24)

        # Scrollable main content (header and footer stay fixed)
        content_container = tk.Frame(self, bg=BG)
        content_container.pack(fill="both", expand=True)

        content_canvas = tk.Canvas(content_container, bg=BG, highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(
            content_container, orient="vertical", command=content_canvas.yview
        )
        content_canvas.configure(yscrollcommand=content_scrollbar.set)

        content_scrollbar.pack(side="right", fill="y")
        content_canvas.pack(side="left", fill="both", expand=True)

        # Important: keep this frame as a canvas window, not pack()-managed.
        body = tk.Frame(content_canvas, bg=BG)
        body_window = content_canvas.create_window(
            (22, 18), window=body, anchor="nw"
        )

        def update_scroll_region(_event=None):
            content_canvas.configure(
                scrollregion=content_canvas.bbox("all")
            )

        def fit_body_width(event):
            content_canvas.itemconfigure(
                body_window, width=max(1, event.width - 44)
            )
            content_canvas.after_idle(update_scroll_region)

        body.bind("<Configure>", update_scroll_region)
        content_canvas.bind("<Configure>", fit_body_width)

        def scroll_content(event):
            if getattr(event, "delta", 0):
                amount = -1 * int(event.delta / 120)
                if amount == 0:
                    amount = -1 if event.delta > 0 else 1
                content_canvas.yview_scroll(amount, "units")
            elif getattr(event, "num", None) == 4:
                content_canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                content_canvas.yview_scroll(1, "units")
            return "break"

        content_canvas.bind_all("<MouseWheel>", scroll_content)
        content_canvas.bind_all("<Button-4>", scroll_content)
        content_canvas.bind_all("<Button-5>", scroll_content)

        # Dashboard cards
        cards = tk.Frame(body, bg=BG)
        cards.pack(fill="x", pady=(0, 16))
        self.stat_vars = {
            "students": tk.StringVar(value="0"),
            "buckets": tk.StringVar(value=str(TABLE_SIZE)),
            "collisions": tk.StringVar(value="0"),
            "load": tk.StringVar(value="0%"),
        }
        self._stat_card(cards, "TOTAL STUDENTS", self.stat_vars["students"], "Registered records", BLUE)
        self._stat_card(cards, "HASH TABLE SIZE", self.stat_vars["buckets"], "Buckets available", NAVY)
        self._stat_card(cards, "COLLISIONS", self.stat_vars["collisions"], "Extra records in buckets", AMBER)
        self._stat_card(cards, "TABLE LOAD", self.stat_vars["load"], "Occupied buckets / total", GREEN)

        # Two-column work area
        work = tk.Frame(body, bg=BG)
        work.pack(fill="both", expand=True)
        work.columnconfigure(0, weight=4)
        work.columnconfigure(1, weight=3)
        work.rowconfigure(0, weight=1)

        left = tk.Frame(work, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right = tk.Frame(work, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_student_panel(left)
        self._build_hash_panel(right)

        footer = tk.Frame(self, bg=WHITE, height=30, highlightbackground=BORDER, highlightthickness=1)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, textvariable=self.status_var, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=22, pady=6)

    def _stat_card(self, parent, title, value_var, subtitle, accent):
        card = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Frame(card, bg=accent, height=4).pack(fill="x")
        inner = tk.Frame(card, bg=WHITE)
        inner.pack(fill="both", padx=14, pady=10)
        tk.Label(inner, text=title, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(inner, textvariable=value_var, bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(3, 0))
        tk.Label(inner, text=subtitle, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(1, 0))

    def _section_title(self, parent, title, subtitle=None):
        frame = tk.Frame(parent, bg=WHITE)
        frame.pack(fill="x", padx=16, pady=(15, 10))
        tk.Label(frame, text=title, bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(frame, text=subtitle, bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))
        return frame

    def _button(self, parent, text, command, primary=False, color=None):
        bg = color or (BLUE if primary else PALE_BLUE)
        fg = WHITE if primary or color else BLUE_DARK
        button = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                           activebackground=BLUE_DARK if primary else "#D8E9FF",
                           activeforeground=WHITE if primary or color else BLUE_DARK,
                           relief="flat", bd=0, cursor="hand2",
                           font=("Segoe UI", 9, "bold"), padx=12, pady=8)
        return button

    def _build_student_panel(self, parent):
        self._section_title(parent, "Student Records", "Add, search, update and delete student details")

        search_area = tk.Frame(parent, bg=WHITE)
        search_area.pack(fill="x", padx=16, pady=(0, 12))
        tk.Label(search_area, text="Search by roll number or name", bg=WHITE,
                 fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        search_row = tk.Frame(search_area, bg=WHITE)
        search_row.pack(fill="x")
        search_entry = tk.Entry(search_row, textvariable=self.search_var, font=("Segoe UI", 10),
                                relief="solid", bd=1, highlightthickness=0)
        search_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 7))
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_student_table())
        self._button(search_row, "Search", self.search_student, primary=True).pack(side="left")
        self._button(search_row, "Clear", self.clear_search).pack(side="left", padx=(6, 0))

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="x", expand=False, padx=16, pady=(0, 8))
        table_frame.configure(height=142)
        table_frame.pack_propagate(False)
        columns = ("roll", "name", "branch", "division", "marks")
        self.student_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=4)
        headings = {"roll": "Roll No.", "name": "Student Name", "branch": "Branch",
                    "division": "Div.", "marks": "Marks"}
        widths = {"roll": 70, "name": 145, "branch": 125, "division": 48, "marks": 65}
        for col in columns:
            self.student_tree.heading(col, text=headings[col])
            self.student_tree.column(col, width=widths[col], anchor="w" if col in ("name", "branch") else "center")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=yscroll.set)
        self.student_tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)
        self.student_tree.bind("<Double-1>", self.on_student_select)

        # Form
        form_header = tk.Frame(parent, bg=PALE_BLUE)
        form_header.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(form_header, text="STUDENT INFORMATION", bg=PALE_BLUE, fg=NAVY,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=7)

        form = tk.Frame(parent, bg=WHITE)
        form.pack(fill="x", padx=16, pady=(0, 8))
        self.form_vars = {key: tk.StringVar() for key in
                          ("roll", "name", "branch", "year", "division", "email", "phone", "marks")}
        fields = [
            ("Roll Number *", "roll"), ("Full Name *", "name"),
            ("Branch *", "branch"), ("Academic Year *", "year"),
            ("Division *", "division"), ("Email *", "email"),
            ("Phone *", "phone"), ("Marks (0-100) *", "marks")
        ]
        for index, (label, key) in enumerate(fields):
            row, col = divmod(index, 2)
            cell = tk.Frame(form, bg=WHITE)
            cell.grid(row=row, column=col, sticky="ew", padx=(0, 10 if col == 0 else 0), pady=3)
            tk.Label(cell, text=label, bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 2))
            entry = tk.Entry(cell, textvariable=self.form_vars[key], font=("Segoe UI", 9),
                             relief="solid", bd=1)
            entry.pack(fill="x", ipady=3)
            if key == "roll":
                self.roll_entry = entry
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        actions = tk.Frame(parent, bg=WHITE)
        actions.pack(fill="x", padx=16, pady=(0, 10))
        self._button(actions, "＋ Add Student", self.add_student, primary=True).pack(side="left", padx=(0, 7))
        self._button(actions, "Update", self.update_student).pack(side="left", padx=(0, 7))
        self._button(actions, "Delete", self.delete_student, color="#FCE8EA").pack(side="left", padx=(0, 7))
        self._button(actions, "Clear Form", self.clear_form).pack(side="left")

    def _build_hash_panel(self, parent):
        self._section_title(parent, "Hash Table Visualizer",
                            "Division method with separate chaining for collisions")

        formula = tk.Frame(parent, bg=PALE_BLUE)
        formula.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(formula, text="HASH FUNCTION", bg=PALE_BLUE, fg=BLUE_DARK,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        tk.Label(formula, text="h(roll number) = roll number % 10",
                 bg=PALE_BLUE, fg=NAVY, font=("Consolas", 12, "bold")).pack(anchor="w", padx=12, pady=(0, 8))

        self.hash_canvas = tk.Canvas(parent, bg=WHITE, highlightthickness=0, height=320)
        self.hash_canvas.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.hash_canvas.bind("<Configure>", lambda _event: self.draw_hash_table())

        self.hash_info_var = tk.StringVar(value="Select a student or add a record to inspect its hash bucket.")
        tk.Label(parent, textvariable=self.hash_info_var, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9), wraplength=370, justify="left").pack(fill="x", padx=16, pady=(0, 8))

        legend = tk.Frame(parent, bg=WHITE)
        legend.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(legend, text="● Occupied bucket", fg=BLUE, bg=WHITE,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(legend, text="● Collision", fg=AMBER, bg=WHITE,
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(14, 0))
        self._button(parent, "Refresh Hash Table", self.refresh_all).pack(anchor="e", padx=16, pady=(0, 14))

    def _form_student(self):
        values = {key: var.get().strip() for key, var in self.form_vars.items()}
        required = ("roll", "name", "branch", "year", "division", "email", "phone", "marks")
        for key in required:
            if not values[key]:
                messagebox.showerror("Missing information", f"Please enter {key.replace('_', ' ').title()}.")
                return None
        try:
            roll = int(values["roll"])
            if roll <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid roll number", "Roll number must be a positive integer.")
            return None
        try:
            marks = float(values["marks"])
            if not 0 <= marks <= 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid marks", "Marks must be a number between 0 and 100.")
            return None
        if not values["phone"].isdigit() or len(values["phone"]) < 7:
            messagebox.showerror("Invalid phone", "Enter a phone number containing at least 7 digits.")
            return None
        if "@" not in values["email"] or "." not in values["email"].split("@")[-1]:
            messagebox.showerror("Invalid email", "Enter a valid email address.")
            return None
        return Student(roll, values["name"], values["branch"], values["year"],
                       values["division"], values["email"], values["phone"], marks)

    def add_student(self):
        student = self._form_student()
        if student is None:
            return
        if self.database.search(student.roll_no):
            messagebox.showerror("Duplicate roll number", "This roll number already exists. Use Update instead.")
            return
        self.database.insert(student)
        self.selected_roll = student.roll_no
        self.refresh_all()
        self.select_roll(student.roll_no)
        self.status_var.set(f"Added student {student.name} (Roll No. {student.roll_no}).")
        messagebox.showinfo("Success", "Student record added successfully.")

    def update_student(self):
        student = self._form_student()
        if student is None:
            return
        old_roll_text = self.form_vars["roll"].get().strip()
        if not old_roll_text or self.database.search(student.roll_no) is None:
            messagebox.showerror("Record not found", "Select an existing student record before updating.")
            return
        self.database.update(student.roll_no, student)
        self.selected_roll = student.roll_no
        self.refresh_all()
        self.select_roll(student.roll_no)
        self.status_var.set(f"Updated student record for {student.name}.")
        messagebox.showinfo("Success", "Student record updated successfully.")

    def delete_student(self):
        roll_text = self.form_vars["roll"].get().strip()
        if not roll_text:
            selection = self.student_tree.selection()
            if selection:
                roll_text = self.student_tree.item(selection[0], "values")[0]
        try:
            roll = int(roll_text)
        except ValueError:
            messagebox.showerror("Select a record", "Select a student or enter a valid roll number.")
            return
        student = self.database.search(roll)
        if student is None:
            messagebox.showerror("Record not found", "No student exists with that roll number.")
            return
        if not messagebox.askyesno("Confirm deletion", f"Delete {student.name} (Roll No. {roll})?"):
            return
        self.database.delete(roll)
        self.selected_roll = None
        self.clear_form()
        self.refresh_all()
        self.status_var.set(f"Deleted student record for Roll No. {roll}.")
        messagebox.showinfo("Deleted", "Student record deleted successfully.")

    def search_student(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showinfo("Search", "Enter a roll number or student name in the search box.")
            return
        if query.isdigit():
            student = self.database.search(int(query))
            if student:
                self.select_roll(student.roll_no)
                self.fill_form(student)
                self.hash_info_var.set(
                    f"Roll number {student.roll_no}: h({student.roll_no}) = "
                    f"{student.roll_no} % {self.database.size} = {self.database.hash_function(student.roll_no)}."
                )
                self.status_var.set(f"Found student: {student.name}.")
            else:
                messagebox.showinfo("Not found", f"No student found with roll number {query}.")
        else:
            matches = [s for s in self.database.all_students() if query.casefold() in s.name.casefold()]
            if not matches:
                messagebox.showinfo("Not found", f"No student name matches '{query}'.")
            elif len(matches) == 1:
                self.select_roll(matches[0].roll_no)
                self.fill_form(matches[0])
                self.status_var.set(f"Found student: {matches[0].name}.")
            else:
                self.refresh_student_table()
                messagebox.showinfo("Multiple matches", f"Found {len(matches)} students. Select the required record from the table.")

    def clear_search(self):
        self.search_var.set("")
        self.refresh_student_table()
        self.status_var.set("Search cleared.")

    def clear_form(self):
        for variable in self.form_vars.values():
            variable.set("")
        self.selected_roll = None
        self.student_tree.selection_remove(self.student_tree.selection())
        self.hash_info_var.set("Select a student or add a record to inspect its hash bucket.")
        self.roll_entry.focus_set()

    def fill_form(self, student):
        for key, value in {
            "roll": student.roll_no, "name": student.name, "branch": student.branch,
            "year": student.year, "division": student.division, "email": student.email,
            "phone": student.phone, "marks": f"{student.marks:g}"
        }.items():
            self.form_vars[key].set(str(value))
        self.selected_roll = student.roll_no

    def on_student_select(self, _event=None):
        selection = self.student_tree.selection()
        if not selection:
            return
        values = self.student_tree.item(selection[0], "values")
        student = self.database.search(values[0])
        if student:
            self.fill_form(student)
            index = self.database.hash_function(student.roll_no)
            bucket_size = len(self.database.table[index])
            self.hash_info_var.set(
                f"Selected {student.name}: h({student.roll_no}) = {student.roll_no} % "
                f"{self.database.size} = {index}. Bucket {index} contains {bucket_size} record(s)"
                + ("; collision present." if bucket_size > 1 else ".")
            )
            self.draw_hash_table()

    def select_roll(self, roll_no):
        for item in self.student_tree.get_children():
            values = self.student_tree.item(item, "values")
            if str(values[0]) == str(roll_no):
                self.student_tree.selection_set(item)
                self.student_tree.focus(item)
                self.student_tree.see(item)
                break
        student = self.database.search(roll_no)
        if student:
            self.fill_form(student)
            self.draw_hash_table()

    def refresh_student_table(self):
        if not hasattr(self, "student_tree"):
            return
        query = self.search_var.get().strip().casefold()
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for student in self.database.all_students():
            if query and query not in str(student.roll_no).casefold() and query not in student.name.casefold():
                continue
            self.student_tree.insert("", "end", values=(
                student.roll_no, student.name, student.branch, student.division, f"{student.marks:g}"
            ))

    def refresh_all(self):
        if not hasattr(self, "student_tree"):
            return
        students = self.database.all_students()
        self.stat_vars["students"].set(str(len(students)))
        self.stat_vars["buckets"].set(str(self.database.size))
        self.stat_vars["collisions"].set(str(self.database.collision_count()))
        occupied = sum(1 for bucket in self.database.table if bucket)
        self.stat_vars["load"].set(f"{occupied / self.database.size * 100:.0f}%")
        self.refresh_student_table()
        self.draw_hash_table()

    def draw_hash_table(self):
        if not hasattr(self, "hash_canvas"):
            return
        canvas = self.hash_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 300)
        row_height = 29
        top = 8
        label_w = 66
        right_pad = 8
        content_w = width - label_w - right_pad
        bucket_h = 22

        selected_index = None
        try:
            roll_text = self.form_vars["roll"].get().strip()
            if roll_text.isdigit():
                selected_index = self.database.hash_function(int(roll_text))
        except (ValueError, AttributeError):
            pass

        for index, bucket in enumerate(self.database.table):
            y = top + index * row_height
            is_collision = len(bucket) > 1
            is_occupied = len(bucket) > 0
            bg = "#FFF3D6" if is_collision else (PALE_BLUE if is_occupied else "#F8FAFC")
            outline = AMBER if is_collision else (BLUE if is_occupied else BORDER)
            if index == selected_index:
                outline = BLUE_DARK
            canvas.create_text(4, y + bucket_h / 2, text=f"Bucket {index}",
                               anchor="w", fill=NAVY, font=("Segoe UI", 8, "bold"))
            canvas.create_rectangle(label_w, y, width - right_pad, y + bucket_h,
                                    fill=bg, outline=outline, width=2 if index == selected_index else 1)
            if not bucket:
                canvas.create_text(label_w + 8, y + bucket_h / 2, text="EMPTY",
                                   anchor="w", fill="#94A3B8", font=("Segoe UI", 8, "italic"))
            else:
                
                x = label_w + 6
                for student in bucket:
                    label = f"{student.roll_no}: {student.name}"
                    pill_w = max(55, min(145, len(label) * 6 + 16))
                    if x + pill_w > width - right_pad - 3:
                        canvas.create_text(x, y + bucket_h / 2, text="…",
                                           anchor="w", fill=NAVY, font=("Segoe UI", 9, "bold"))
                        break
                    pill_color = "#F9D98C" if is_collision else "#D7E9FF"
                    canvas.create_rectangle(x, y + 3, x + pill_w, y + bucket_h - 3,
                                            fill=pill_color, outline="")
                    canvas.create_text(x + 7, y + bucket_h / 2, text=label,
                                       anchor="w", fill=NAVY, font=("Segoe UI", 8, "bold"))
                    x += pill_w + 4

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = StudentDatabaseApp()
    app.run()
