import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from urllib.parse import urlparse

APP_TITLE = "StackBrowser Pro - DSA Mini Project"
HISTORY_FILE = "browser_history.json"


class BrowserTab:
    """State for one simulated browser tab."""
    def __init__(self, title="New Tab"):
        self.back_stack = []
        self.forward_stack = []
        self.current_page = None
        self.title = title


class StackBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1250x780")
        self.root.minsize(900, 600)

        self.dark_mode = False
        self.palette = {}
        self.tabs = {}  # notebook frame -> BrowserTab
        self.history = []
        self.bookmarks = []
        self._loading_history = False

        self._load_saved_data()
        self._build_ui()
        self._apply_theme()
        self.new_tab()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # --------------------------- Persistence ---------------------------
    def _load_saved_data(self):
        if not os.path.exists(HISTORY_FILE):
            return
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.history = data.get("history", [])
            self.bookmarks = data.get("bookmarks", [])
            self.dark_mode = bool(data.get("dark_mode", False))
        except (OSError, json.JSONDecodeError, TypeError):
            self.history = []
            self.bookmarks = []
            self.dark_mode = False

    def save_data(self, show_message=False):
        data = {
            "history": self.history,
            "bookmarks": self.bookmarks,
            "dark_mode": self.dark_mode,
            "saved_at": datetime.now().isoformat(timespec="seconds")
        }
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            self.status_var.set(f"History and bookmarks saved to {HISTORY_FILE}")
            if show_message:
                messagebox.showinfo("Saved", f"Data saved in:\n{os.path.abspath(HISTORY_FILE)}")
        except OSError as exc:
            messagebox.showerror("Save Error", f"Could not save data:\n{exc}")

    def on_close(self):
        self.save_data()
        self.root.destroy()

    # --------------------------- UI creation ---------------------------
    def _build_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.header = tk.Frame(self.root, padx=18, pady=12)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)

        self.title_label = tk.Label(
            self.header, text="◈ StackBrowser Pro",
            font=("Segoe UI", 20, "bold"), anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = tk.Label(
            self.header, text="SPPU • Second Year Computer Engineering • Stack Data Structure",
            font=("Segoe UI", 9)
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(3, 0))

        header_actions = tk.Frame(self.header)
        header_actions.grid(row=0, column=1, rowspan=2, sticky="e")
        self.theme_button = tk.Button(
            header_actions, text="🌙 Dark Mode", command=self.toggle_theme,
            padx=12, pady=7, relief="flat"
        )
        self.theme_button.pack(side="left", padx=4)
        self.save_button = tk.Button(
            header_actions, text="Save Data", command=lambda: self.save_data(True),
            padx=12, pady=7, relief="flat"
        )
        self.save_button.pack(side="left", padx=4)

        self.main = tk.Frame(self.root, padx=12, pady=8)
        self.main.grid(row=1, column=0, sticky="nsew")
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=3)
        self.main.grid_columnconfigure(1, weight=2)

        # Left: tabs and simulated page
        self.left_panel = tk.Frame(self.main)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        tab_actions = tk.Frame(self.left_panel, pady=4)
        tab_actions.grid(row=0, column=0, sticky="ew")
        self.new_tab_button = tk.Button(
            tab_actions, text="+ New Tab", command=self.new_tab,
            padx=10, pady=6, relief="flat"
        )
        self.new_tab_button.pack(side="left", padx=(0, 6))
        self.close_tab_button = tk.Button(
            tab_actions, text="Close Tab", command=self.close_tab,
            padx=10, pady=6, relief="flat"
        )
        self.close_tab_button.pack(side="left")

        self.notebook = ttk.Notebook(self.left_panel)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Right: dashboard and data panels
        self.sidebar = tk.Frame(self.main, padx=10, pady=8)
        self.sidebar.grid(row=0, column=1, sticky="nsew")
        self.sidebar.grid_rowconfigure(2, weight=1)
        self.sidebar.grid_rowconfigure(4, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.stats_frame = tk.Frame(self.sidebar)
        self.stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for col in range(3):
            self.stats_frame.grid_columnconfigure(col, weight=1)

        self.stat_visits = self._make_stat(self.stats_frame, "VISITS", "0", 0)
        self.stat_back = self._make_stat(self.stats_frame, "BACK STACK", "0", 1)
        self.stat_forward = self._make_stat(self.stats_frame, "FORWARD STACK", "0", 2)

        self.stack_heading = tk.Label(
            self.sidebar, text="STACK VISUALIZATION",
            font=("Segoe UI", 11, "bold"), anchor="w"
        )
        self.stack_heading.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        stack_area = tk.Frame(self.sidebar)
        stack_area.grid(row=2, column=0, sticky="nsew")
        stack_area.grid_columnconfigure(0, weight=1)
        stack_area.grid_columnconfigure(1, weight=1)
        stack_area.grid_rowconfigure(1, weight=1)

        self.back_stack_label = tk.Label(stack_area, text="Back Stack (bottom → top)",
                                         font=("Segoe UI", 9, "bold"))
        self.back_stack_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.forward_stack_label = tk.Label(stack_area, text="Forward Stack (bottom → top)",
                                            font=("Segoe UI", 9, "bold"))
        self.forward_stack_label.grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.back_list = tk.Listbox(stack_area, height=7, exportselection=False)
        self.back_list.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        self.forward_list = tk.Listbox(stack_area, height=7, exportselection=False)
        self.forward_list.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        self.data_notebook = ttk.Notebook(self.sidebar)
        self.data_notebook.grid(row=3, column=0, rowspan=2, sticky="nsew", pady=(12, 0))

        # History tab
        self.history_frame = tk.Frame(self.data_notebook, padx=6, pady=6)
        self.data_notebook.add(self.history_frame, text="History")
        self.history_frame.grid_rowconfigure(1, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)

        self.history_search = tk.Entry(self.history_frame)
        self.history_search.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.history_search.insert(0, "Search history...")
        self.history_search.bind("<FocusIn>", self._clear_history_placeholder)
        self.history_search.bind("<KeyRelease>", lambda event: self.refresh_history_tree())

        self.history_tree = ttk.Treeview(
            self.history_frame, columns=("time", "page"),
            show="headings", height=8
        )
        self.history_tree.heading("time", text="Time")
        self.history_tree.heading("page", text="Visited Page")
        self.history_tree.column("time", width=70, anchor="w")
        self.history_tree.column("page", width=170, anchor="w")
        self.history_tree.grid(row=1, column=0, sticky="nsew")
        self.history_tree.bind("<Double-1>", self.open_history_item)

        history_buttons = tk.Frame(self.history_frame)
        history_buttons.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        self.clear_history_button = tk.Button(
            history_buttons, text="Clear History", command=self.clear_history,
            relief="flat", padx=8, pady=5
        )
        self.clear_history_button.pack(side="left")

        # Bookmarks tab
        self.bookmarks_frame = tk.Frame(self.data_notebook, padx=6, pady=6)
        self.data_notebook.add(self.bookmarks_frame, text="Bookmarks")
        self.bookmarks_frame.grid_rowconfigure(0, weight=1)
        self.bookmarks_frame.grid_columnconfigure(0, weight=1)

        self.bookmarks_tree = ttk.Treeview(
            self.bookmarks_frame, columns=("page",), show="headings", height=9
        )
        self.bookmarks_tree.heading("page", text="Saved Websites")
        self.bookmarks_tree.column("page", width=230, anchor="w")
        self.bookmarks_tree.grid(row=0, column=0, sticky="nsew")
        self.bookmarks_tree.bind("<Double-1>", self.open_bookmark)

        bookmark_buttons = tk.Frame(self.bookmarks_frame)
        bookmark_buttons.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.add_bookmark_button = tk.Button(
            bookmark_buttons, text="☆ Bookmark Current", command=self.add_bookmark,
            relief="flat", padx=8, pady=5
        )
        self.add_bookmark_button.pack(side="left", padx=(0, 4))
        self.remove_bookmark_button = tk.Button(
            bookmark_buttons, text="Remove", command=self.remove_bookmark,
            relief="flat", padx=8, pady=5
        )
        self.remove_bookmark_button.pack(side="left")

        self.status_var = tk.StringVar(value="Ready")
        self.status = tk.Label(
            self.root, textvariable=self.status_var, anchor="w",
            padx=12, pady=7, font=("Segoe UI", 9)
        )
        self.status.grid(row=2, column=0, sticky="ew")

        self.refresh_history_tree()
        self.refresh_bookmarks_tree()

    def _make_stat(self, parent, title, value, col):
        card = tk.Frame(parent, padx=8, pady=8, relief="groove", bd=1)
        card.grid(row=0, column=col, sticky="ew", padx=3)
        tk.Label(card, text=title, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        value_label = tk.Label(card, text=value, font=("Segoe UI", 18, "bold"))
        value_label.pack(anchor="w", pady=(3, 0))
        return value_label

    def _create_tab_content(self, frame):
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        toolbar = tk.Frame(frame, padx=8, pady=8)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_columnconfigure(3, weight=1)

        back_btn = tk.Button(toolbar, text="←", width=3,
                             command=lambda f=frame: self.go_back(f), relief="flat")
        back_btn.grid(row=0, column=0, padx=(0, 4))
        forward_btn = tk.Button(toolbar, text="→", width=3,
                                command=lambda f=frame: self.go_forward(f), relief="flat")
        forward_btn.grid(row=0, column=1, padx=4)
        home_btn = tk.Button(toolbar, text="⌂", width=3,
                             command=lambda f=frame: self.navigate(f, "home://browser"), relief="flat")
        home_btn.grid(row=0, column=2, padx=4)

        url_entry = tk.Entry(toolbar, font=("Segoe UI", 10))
        url_entry.grid(row=0, column=3, sticky="ew", padx=6, ipady=5)
        url_entry.bind("<Return>", lambda event, f=frame: self.visit_from_entry(f))

        go_btn = tk.Button(toolbar, text="Go", command=lambda f=frame: self.visit_from_entry(f),
                           relief="flat", padx=12, pady=5)
        go_btn.grid(row=0, column=4, padx=(4, 0))

        page = tk.Frame(frame, padx=24, pady=22)
        page.grid(row=1, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)

        page_title = tk.Label(page, text="Welcome to StackBrowser",
                              font=("Segoe UI", 22, "bold"), anchor="w", justify="left")
        page_title.grid(row=0, column=0, sticky="ew", pady=(12, 8))

        page_url = tk.Label(page, text="", font=("Segoe UI", 10),
                            anchor="w", justify="left", wraplength=650)
        page_url.grid(row=1, column=0, sticky="ew", pady=4)

        page_text = tk.Label(
            page,
            text=("This is a browser navigation simulator for the SPPU Data Structures project.\n\n"
                  "Enter a website address and select Go. The app models navigation history; "
                  "it does not load real website content."),
            font=("Segoe UI", 12), anchor="nw", justify="left",
            wraplength=650
        )
        page_text.grid(row=2, column=0, sticky="new", pady=(14, 20))

        page_hint = tk.Label(
            page, text="DATA STRUCTURE  •  STACK (LIFO)",
            font=("Segoe UI", 10, "bold"), padx=12, pady=9
        )
        page_hint.grid(row=3, column=0, sticky="w", pady=8)

        self.tabs[frame].widgets = {
            "url": url_entry, "back": back_btn, "forward": forward_btn,
            "title": page_title, "page_url": page_url,
            "description": page_text, "hint": page_hint,
            "page": page, "toolbar": toolbar
        }

    # --------------------------- Tabs ---------------------------
    def new_tab(self):
        frame = tk.Frame(self.notebook)
        state = BrowserTab()
        self.tabs[frame] = state
        self._create_tab_content(frame)
        self.notebook.add(frame, text="New Tab")
        self.notebook.select(frame)
        self.navigate(frame, "home://browser")
        self._apply_theme()

    def close_tab(self):
        selected = self._selected_frame()
        if selected is None:
            return
        if len(self.tabs) == 1:
            messagebox.showinfo("Browser", "At least one tab must remain open.")
            return
        self.notebook.forget(selected)
        self.tabs.pop(selected, None)
        selected.destroy()
        self.refresh_stack_view()

    def on_tab_changed(self, event=None):
        self.refresh_stack_view()

    def _selected_frame(self):
        selected = self.notebook.select()
        if not selected:
            return None
        try:
            return self.root.nametowidget(selected)
        except KeyError:
            return None

    # --------------------------- Navigation and stacks ---------------------------
    def _normalize_url(self, raw):
        url = raw.strip()
        if not url:
            messagebox.showwarning("Address Required", "Enter a website address first.")
            return None
        if url.lower() in ("home", "home://browser"):
            return "home://browser"
        if "://" not in url:
            url = "https://" + url
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or "." not in parsed.netloc:
            messagebox.showerror("Invalid Address", "Enter a valid address, e.g. https://example.com")
            return None
        return url

    def visit_from_entry(self, frame):
        raw = self.tabs[frame].widgets["url"].get()
        url = self._normalize_url(raw)
        if url:
            self.navigate(frame, url)

    def navigate(self, frame, url, from_history=False):
        if frame not in self.tabs:
            return
        state = self.tabs[frame]
        if url == state.current_page:
            self.status_var.set("This page is already open in the selected tab.")
            return

        if state.current_page is not None:
            state.back_stack.append(state.current_page)
        state.forward_stack.clear()
        state.current_page = url

        if not from_history:
            self.history.append({
                "url": url,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.refresh_history_tree()
        self._render_tab(frame)
        self.refresh_stack_view()
        self._update_tab_title(frame)
        self.status_var.set(f"Opened {url}")

    def go_back(self, frame=None):
        frame = frame or self._selected_frame()
        if frame not in self.tabs:
            return
        state = self.tabs[frame]
        if not state.back_stack:
            self.status_var.set("Back Stack is empty: no previous page.")
            return
        if state.current_page is not None:
            state.forward_stack.append(state.current_page)
        state.current_page = state.back_stack.pop()
        self._render_tab(frame)
        self.refresh_stack_view()
        self._update_tab_title(frame)
        self.status_var.set("Back operation: popped the previous page from Back Stack.")

    def go_forward(self, frame=None):
        frame = frame or self._selected_frame()
        if frame not in self.tabs:
            return
        state = self.tabs[frame]
        if not state.forward_stack:
            self.status_var.set("Forward Stack is empty: no next page.")
            return
        if state.current_page is not None:
            state.back_stack.append(state.current_page)
        state.current_page = state.forward_stack.pop()
        self._render_tab(frame)
        self.refresh_stack_view()
        self._update_tab_title(frame)
        self.status_var.set("Forward operation: popped the next page from Forward Stack.")

    def _page_name(self, url):
        if url == "home://browser":
            return "Home"
        parsed = urlparse(url)
        return parsed.netloc or url

    def _render_tab(self, frame):
        state = self.tabs[frame]
        widgets = state.widgets
        url = state.current_page or "home://browser"
        widgets["url"].delete(0, tk.END)
        widgets["url"].insert(0, url)
        widgets["page_url"].config(text=url)

        if url == "home://browser":
            widgets["title"].config(text="Welcome to StackBrowser")
            widgets["description"].config(
                text=("This is a browser navigation simulator for the SPPU Data Structures project.\n\n"
                      "Enter a website address and select Go. Use Back and Forward to demonstrate "
                      "the stack operations. Actual website content is not loaded.")
            )
        else:
            widgets["title"].config(text=self._page_name(url))
            widgets["description"].config(
                text=("Simulated webpage\n\n"
                      f"Selected address: {url}\n\n"
                      "StackBrowser records this address to demonstrate navigation history. "
                      "It does not download or render the actual website.")
            )

        widgets["back"].config(state="normal" if state.back_stack else "disabled")
        widgets["forward"].config(state="normal" if state.forward_stack else "disabled")

    def _update_tab_title(self, frame):
        state = self.tabs[frame]
        name = self._page_name(state.current_page or "home://browser")
        index = self.notebook.index(frame)
        self.notebook.tab(frame, text=name[:18] or f"Tab {index + 1}")

    # --------------------------- Stack visualization ---------------------------
    def refresh_stack_view(self):
        frame = self._selected_frame()
        state = self.tabs.get(frame) if frame else None
        self.back_list.delete(0, tk.END)
        self.forward_list.delete(0, tk.END)
        if state:
            for url in state.back_stack:
                self.back_list.insert(tk.END, self._page_name(url))
            if state.back_stack:
                self.back_list.itemconfig(tk.END, foreground="#16803C")
            for url in state.forward_stack:
                self.forward_list.insert(tk.END, self._page_name(url))
            if state.forward_stack:
                self.forward_list.itemconfig(tk.END, foreground="#8B5CF6")

            self.stat_visits.config(text=str(len(self.history)))
            self.stat_back.config(text=str(len(state.back_stack)))
            self.stat_forward.config(text=str(len(state.forward_stack)))
        else:
            self.stat_visits.config(text=str(len(self.history)))
            self.stat_back.config(text="0")
            self.stat_forward.config(text="0")

    # --------------------------- History ---------------------------
    def _clear_history_placeholder(self, event=None):
        if self.history_search.get() == "Search history...":
            self.history_search.delete(0, tk.END)

    def refresh_history_tree(self):
        if not hasattr(self, "history_tree"):
            return
        query = self.history_search.get().strip().lower()
        if query == "search history...":
            query = ""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        # Newest entries appear first.
        for entry in reversed(self.history):
            url = entry.get("url", "")
            time_text = entry.get("time", "")
            if query and query not in url.lower() and query not in time_text.lower():
                continue
            self.history_tree.insert("", tk.END, values=(time_text[-8:], url), tags=(url,))

    def open_history_item(self, event=None):
        selection = self.history_tree.selection()
        if not selection:
            return
        url = self.history_tree.item(selection[0], "tags")
        if url:
            frame = self._selected_frame()
            self.navigate(frame, url[0], from_history=False)

    def clear_history(self):
        if not self.history:
            self.status_var.set("Browsing history is already empty.")
            return
        if messagebox.askyesno("Clear History", "Delete all saved browsing history?"):
            self.history.clear()
            self.refresh_history_tree()
            self.refresh_stack_view()
            self.save_data()
            self.status_var.set("Browsing history cleared. Navigation stacks remain unchanged.")

    # --------------------------- Bookmarks ---------------------------
    def add_bookmark(self):
        frame = self._selected_frame()
        if frame not in self.tabs:
            return
        url = self.tabs[frame].current_page
        if not url:
            self.status_var.set("No page to bookmark.")
            return
        if any(item.get("url") == url for item in self.bookmarks):
            self.status_var.set("This page is already bookmarked.")
            return
        self.bookmarks.append({
            "url": url,
            "title": self._page_name(url),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.refresh_bookmarks_tree()
        self.save_data()
        self.status_var.set(f"Bookmarked {url}")

    def refresh_bookmarks_tree(self):
        if not hasattr(self, "bookmarks_tree"):
            return
        for item in self.bookmarks_tree.get_children():
            self.bookmarks_tree.delete(item)
        for bookmark in self.bookmarks:
            self.bookmarks_tree.insert(
                "", tk.END,
                values=(bookmark.get("title") or bookmark.get("url", ""),),
                tags=(bookmark.get("url", ""),)
            )

    def open_bookmark(self, event=None):
        selection = self.bookmarks_tree.selection()
        if not selection:
            return
        tags = self.bookmarks_tree.item(selection[0], "tags")
        if tags:
            frame = self._selected_frame()
            self.navigate(frame, tags[0])

    def remove_bookmark(self):
        selection = self.bookmarks_tree.selection()
        if not selection:
            messagebox.showinfo("Bookmarks", "Select a bookmark to remove.")
            return
        tags = self.bookmarks_tree.item(selection[0], "tags")
        url = tags[0] if tags else None
        self.bookmarks = [item for item in self.bookmarks if item.get("url") != url]
        self.refresh_bookmarks_tree()
        self.save_data()
        self.status_var.set("Bookmark removed.")

    # --------------------------- Theme ---------------------------
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme()
        self.save_data()
        self.theme_button.config(text="☀ Light Mode" if self.dark_mode else "🌙 Dark Mode")
        self.status_var.set("Dark mode enabled." if self.dark_mode else "Light mode enabled.")

    def _apply_theme(self):
        if self.dark_mode:
            p = {
                "bg": "#111827", "panel": "#1F2937", "text": "#F9FAFB",
                "muted": "#CBD5E1", "entry": "#0F172A", "button": "#334155",
                "accent": "#2563EB", "select": "#1D4ED8", "border": "#475569"
            }
        else:
            p = {
                "bg": "#F3F6FB", "panel": "#FFFFFF", "text": "#172B4D",
                "muted": "#64748B", "entry": "#FFFFFF", "button": "#E8EEFC",
                "accent": "#2457D6", "select": "#DCE7FF", "border": "#CBD5E1"
            }
        self.palette = p
        self.root.configure(bg=p["bg"])

        style = ttk.Style()
        style.configure("TNotebook", background=p["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(10, 6), background=p["button"],
                        foreground=p["text"])
        style.map("TNotebook.Tab", background=[("selected", p["panel"])],
                  foreground=[("selected", p["text"])])
        style.configure("Treeview", background=p["panel"], fieldbackground=p["panel"],
                        foreground=p["text"], rowheight=25)
        style.configure("Treeview.Heading", background=p["button"], foreground=p["text"])
        style.map("Treeview", background=[("selected", p["select"])],
                  foreground=[("selected", "#FFFFFF")])

        # Update every standard Tk widget using its widget class.
        def paint(widget):
            cls = widget.winfo_class()
            try:
                if cls in ("Frame", "Labelframe"):
                    widget.configure(bg=p["panel"])
                elif cls == "Label":
                    widget.configure(bg=p["panel"], fg=p["text"])
                elif cls == "Button":
                    widget.configure(
                        bg=p["button"], fg=p["text"],
                        activebackground=p["accent"], activeforeground="#FFFFFF",
                        disabledforeground=p["muted"]
                    )
                elif cls == "Entry":
                    widget.configure(
                        bg=p["entry"], fg=p["text"], insertbackground=p["text"],
                        disabledbackground=p["panel"], disabledforeground=p["muted"]
                    )
                elif cls == "Listbox":
                    widget.configure(
                        bg=p["entry"], fg=p["text"],
                        selectbackground=p["select"], selectforeground="#FFFFFF"
                    )
            except tk.TclError:
                pass
            for child in widget.winfo_children():
                paint(child)

        paint(self.root)
        self.status.configure(bg=p["button"], fg=p["text"])
        self.title_label.configure(bg=p["panel"], fg=p["text"])
        self.subtitle_label.configure(bg=p["panel"], fg=p["muted"])
        self.theme_button.configure(text="☀ Light Mode" if self.dark_mode else "🌙 Dark Mode")

        # Highlight key labels/cards consistently after generic widget painting.
        for label in (self.stat_visits, self.stat_back, self.stat_forward):
            label.configure(fg=p["accent"], bg=p["panel"])
        for label in (self.stack_heading, self.back_stack_label, self.forward_stack_label):
            label.configure(bg=p["panel"], fg=p["text"])
        for frame in self.tabs:
            if frame in self.tabs:
                for widget in self.tabs[frame].widgets.values():
                    if isinstance(widget, tk.Widget):
                        try:
                            widget.configure(bg=p["panel"])
                        except tk.TclError:
                            pass
                self._render_tab(frame)
        self.refresh_stack_view()
        self.refresh_history_tree()
        self.refresh_bookmarks_tree()


def main():
    root = tk.Tk()
    StackBrowserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
