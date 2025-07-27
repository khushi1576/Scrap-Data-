# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import pandas as pd
from scraper import scrape_yellowpages


class YellowPagesScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YellowPages Scraper")
        self.root.geometry("1000x600")

        self.setup_styles()
        self.create_widgets()

        self.scraping_thread = None
        self.is_scraping = False

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Search Input", padding=10)
        input_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Business Type:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_search_term = ttk.Entry(input_frame, width=40)
        self.entry_search_term.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(input_frame, text="Location:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_location = ttk.Entry(input_frame, width=40)
        self.entry_location.grid(row=1, column=1, padx=10, pady=5)

        self.start_button = ttk.Button(input_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.grid(row=2, column=0, pady=10)

        self.stop_button = ttk.Button(input_frame, text="Stop Scraping", command=self.stop_scraping, state="disabled")
        self.stop_button.grid(row=2, column=1, pady=10, sticky="w")

        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Status", padding=10)
        status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.status_text = ScrolledText(status_frame, height=4, wrap="word", font=("Consolas", 10))
        self.status_text.pack(fill="both", expand=True)

        # Data Frame
        data_frame = ttk.LabelFrame(self.root, text="Collected Data", padding=10)
        data_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        columns = ("No.", "Business Name", "Address", "Phone", "Website")
        self.data_table = ttk.Treeview(data_frame, columns=columns, show="headings")

        for col in columns:
            self.data_table.heading(col, text=col)
            self.data_table.column(col, anchor="center", width=150 if col != "No." else 50)

        self.data_table.pack(fill="both", expand=True)

    def log_status(self, message):
        self.status_text.insert("end", f"{message}\n")
        self.status_text.see("end")

    def start_scraping(self):
        search_term = self.entry_search_term.get().strip()
        location = self.entry_location.get().strip()

        if not search_term or not location:
            messagebox.showerror("Missing Input", "Please enter both search term and location.")
            return

        self.start_button.state(["disabled"])
        self.stop_button.state(["!disabled"])
        self.is_scraping = True
        self.log_status("🔍 Starting scraping...")

        for row in self.data_table.get_children():
            self.data_table.delete(row)

        self.scraping_thread = threading.Thread(target=self.scrape_yellowpages_thread, args=(search_term, location))
        self.scraping_thread.start()

    def stop_scraping(self):
        self.is_scraping = False
        self.log_status("🛑 Scraping stopped by user.")
        self.start_button.state(["!disabled"])
        self.stop_button.state(["disabled"])

    def scrape_yellowpages_thread(self, search_term, location):
        try:
            self.log_status("🔄 Scraping in progress...")
            filename = scrape_yellowpages(search_term, location)

            df = pd.read_csv(filename)
            for i, row in df.iterrows():
                self.data_table.insert("", "end", values=(
                    i + 1, row["Business Name"], row["Address"], row["Phone"], row["Website"]
                ))

            self.log_status(f"✅ Scraping complete. Data saved to {filename}")
        except Exception as e:
            self.log_status(f"❌ Scraping failed: {e}")
        finally:
            self.is_scraping = False
            self.start_button.state(["!disabled"])
            self.stop_button.state(["disabled"])
            self.log_status("✔️ Scraping session ended.")


if __name__ == "__main__":
    root = tk.Tk()
    app = YellowPagesScraperApp(root)
    root.mainloop()
