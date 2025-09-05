import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import random
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# --------------------------- Database ---------------------------

class DatabaseManager:
    def __init__(self, db_name="rental_inventory.db"):
        self.db_name = db_name
        self.init_database()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.connect()
        c = conn.cursor()

        # Customers
        c.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone         TEXT,
                email         TEXT,
                address       TEXT,
                created_date  DATE DEFAULT CURRENT_DATE
            )
        """)

        # Products
        c.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                product_type       TEXT NOT NULL,
                product_code       TEXT UNIQUE,
                cost_per_day       REAL NOT NULL,
                available_quantity INTEGER DEFAULT 1,
                status             TEXT DEFAULT 'Available'
            )
        """)

        # Rentals
        c.execute("""
            CREATE TABLE IF NOT EXISTS rentals (
                rental_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id   INTEGER,
                receipt_ref   TEXT UNIQUE,
                product_type  TEXT,
                product_code  TEXT,
                no_days       INTEGER,
                cost_per_day  REAL,
                tax           REAL,
                subtotal      REAL,
                total         REAL,
                created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)

        # Seed some products
        default_products = [
            ("Car",     "CAR452", 12.00, 5),
            ("Van",     "VAN775", 19.00, 3),
            ("Minibus", "MIN334", 12.00, 2),
            ("Truck",   "TRK7483", 15.00, 2)
        ]
        for pt, code, cpd, qty in default_products:
            c.execute(
                "INSERT OR IGNORE INTO products (product_type, product_code, cost_per_day, available_quantity) VALUES (?,?,?,?)",
                (pt, code, cpd, qty)
            )

        conn.commit()
        conn.close()

    # ---- customers
    def get_customers(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT customer_id, customer_name, phone, email, address FROM customers ORDER BY created_date DESC")
        rows = c.fetchall()
        conn.close()
        return rows

    def add_customer(self, name, phone, email, address):
        conn = self.connect()
        c = conn.cursor()
        c.execute("INSERT INTO customers (customer_name, phone, email, address) VALUES (?,?,?,?)",
                  (name, phone, email, address))
        conn.commit()
        conn.close()

    def update_customer(self, cid, name, phone, email, address):
        conn = self.connect()
        c = conn.cursor()
        c.execute("UPDATE customers SET customer_name=?, phone=?, email=?, address=? WHERE customer_id=?",
                  (name, phone, email, address, cid))
        conn.commit()
        conn.close()

    def delete_customer(self, cid):
        conn = self.connect()
        c = conn.cursor()
        c.execute("DELETE FROM customers WHERE customer_id=?", (cid,))
        conn.commit()
        conn.close()

    # ---- products
    def get_products(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT product_id, product_type, product_code, cost_per_day FROM products ORDER BY product_type, product_code")
        rows = c.fetchall()
        conn.close()
        return rows

    def get_cost_for_code(self, product_code):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT cost_per_day FROM products WHERE product_code=?", (product_code,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0.0

    # ---- rentals
    def save_rental(self, rental_tuple):
        conn = self.connect()
        c = conn.cursor()
        c.execute("""
            INSERT INTO rentals
            (customer_id, receipt_ref, product_type, product_code, no_days, cost_per_day, tax, subtotal, total)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, rental_tuple)
        conn.commit()
        conn.close()

    def get_all_rentals(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("""
            SELECT r.rental_id,
                   r.receipt_ref,
                   cu.customer_name,
                   r.product_type,
                   r.product_code,
                   r.no_days,
                   r.cost_per_day,
                   r.subtotal,
                   r.tax,
                   r.total,
                   r.created_date
            FROM rentals r
            LEFT JOIN customers cu ON cu.customer_id = r.customer_id
            ORDER BY r.created_date DESC
        """)
        rows = c.fetchall()
        conn.close()
        return rows

    def search_rentals(self, q):
        q = f"%{q}%"
        conn = self.connect()
        c = conn.cursor()
        c.execute("""
            SELECT r.rental_id,
                   r.receipt_ref,
                   cu.customer_name,
                   r.product_type,
                   r.product_code,
                   r.no_days,
                   r.cost_per_day,
                   r.subtotal,
                   r.tax,
                   r.total,
                   r.created_date
            FROM rentals r
            LEFT JOIN customers cu ON cu.customer_id = r.customer_id
            WHERE r.receipt_ref LIKE ? OR cu.customer_name LIKE ? OR r.product_type LIKE ? OR r.product_code LIKE ?
            ORDER BY r.created_date DESC
        """, (q, q, q, q))
        rows = c.fetchall()
        conn.close()
        return rows

    def rentals_by_product_type(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT product_type, COUNT(*), SUM(total) FROM rentals GROUP BY product_type")
        rows = c.fetchall()
        conn.close()
        return rows

# --------------------------- App ---------------------------

class AdvancedRentalInventory:
    TAX_RATE = 0.15  # 15% VAT (change as needed)

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Rental Inventory Management System")
        self.root.geometry("1200x750")
        self.root.configure(background="#2c3e50")

        # Initialize database
        self.db = DatabaseManager()

        # Configure style
        self.configure_styles()

        # Initialize variables
        self.init_variables()

        # Create main interface
        self.create_main_interface()

        # Create notebook (tabs)
        self.create_notebook()

    # ---- UI scaffolding
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Arial", 22, "bold"), background="#2c3e50", foreground="white")
        style.configure("Card.TLabelframe", background="#ecf0f1", foreground="#2c3e50")
        style.configure("Card.TLabelframe.Label", font=("Arial", 12, "bold"))
        style.configure("TButton", padding=6)

    def init_variables(self):
        # rental vars
        self.selected_customer_id = tk.StringVar()
        self.selected_product_type = tk.StringVar()
        self.selected_product_code = tk.StringVar()
        self.cost_per_day = tk.StringVar(value="0.00")
        self.no_days = tk.StringVar(value="1")
        self.subtotal = tk.StringVar(value="0.00")
        self.tax = tk.StringVar(value="0.00")
        self.total = tk.StringVar(value="0.00")
        self.receipt_ref = tk.StringVar(value=self._make_receipt())

        # customer form vars
        self.customer_id_edit = None
        self.customer_name = tk.StringVar()
        self.customer_phone = tk.StringVar()
        self.customer_email = tk.StringVar()
        self.customer_address = tk.StringVar()

    def create_main_interface(self):
        title = ttk.Label(self.root, text="Advanced Rental Inventory Management System", style="Title.TLabel")
        title.pack(fill=X, padx=10, pady=10)

    def create_notebook(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.tab_rental = ttk.Frame(self.nb)
        self.tab_history = ttk.Frame(self.nb)
        self.tab_analytics = ttk.Frame(self.nb)
        self.tab_customers = ttk.Frame(self.nb)

        self.nb.add(self.tab_rental, text="New Rental")
        self.nb.add(self.tab_history, text="Rental History")
        self.nb.add(self.tab_analytics, text="Analytics")
        self.nb.add(self.tab_customers, text="Customer Management")

        self.setup_rental_tab()
        self.setup_history_tab()
        self.setup_analytics_tab()
        self.setup_customer_tab()

    # -------------------- New Rental --------------------
    def setup_rental_tab(self):
        frame = ttk.LabelFrame(self.tab_rental, text="Create New Rental", style="Card.TLabelframe", padding=10)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # row 0: customer
        ttk.Label(frame, text="Customer:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.cmb_customer = ttk.Combobox(frame, textvariable=self.selected_customer_id, width=35, state="readonly")
        self.cmb_customer.grid(row=0, column=1, sticky=W, padx=5, pady=5)

        add_cus_btn = ttk.Button(frame, text="New Customer…", command=self._quick_add_customer)
        add_cus_btn.grid(row=0, column=2, sticky=W, padx=5, pady=5)

        # row 1: product type + code
        ttk.Label(frame, text="Product Type:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.cmb_ptype = ttk.Combobox(frame, textvariable=self.selected_product_type, width=20, state="readonly")
        self.cmb_ptype.grid(row=1, column=1, sticky=W, padx=5, pady=5)

        ttk.Label(frame, text="Product Code:").grid(row=1, column=2, sticky=E, padx=5, pady=5)
        self.cmb_pcode = ttk.Combobox(frame, textvariable=self.selected_product_code, width=20, state="readonly")
        self.cmb_pcode.grid(row=1, column=3, sticky=W, padx=5, pady=5)

        # row 2: pricing
        ttk.Label(frame, text="Cost / Day:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.ent_cost = ttk.Entry(frame, textvariable=self.cost_per_day, width=12, state="readonly")
        self.ent_cost.grid(row=2, column=1, sticky=W, padx=5, pady=5)

        ttk.Label(frame, text="No. Days:").grid(row=2, column=2, sticky=E, padx=5, pady=5)
        self.ent_days = ttk.Entry(frame, textvariable=self.no_days, width=10)
        self.ent_days.grid(row=2, column=3, sticky=W, padx=5, pady=5)

        # row 3: totals
        ttk.Label(frame, text="Subtotal:").grid(row=3, column=0, sticky=W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.subtotal, width=12, state="readonly").grid(row=3, column=1, sticky=W, padx=5, pady=5)

        ttk.Label(frame, text="Tax:").grid(row=3, column=2, sticky=E, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.tax, width=12, state="readonly").grid(row=3, column=3, sticky=W, padx=5, pady=5)

        ttk.Label(frame, text="Total:").grid(row=4, column=0, sticky=W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.total, width=12, state="readonly").grid(row=4, column=1, sticky=W, padx=5, pady=5)

        ttk.Label(frame, text="Receipt Ref:").grid(row=4, column=2, sticky=E, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.receipt_ref, width=18, state="readonly").grid(row=4, column=3, sticky=W, padx=5, pady=5)

        # row 5: actions
        ttk.Button(frame, text="Calculate", command=self.calculate_totals).grid(row=5, column=0, padx=5, pady=10, sticky=W)
        ttk.Button(frame, text="Save Rental", command=self.save_rental).grid(row=5, column=1, padx=5, pady=10, sticky=W)
        ttk.Button(frame, text="Clear", command=self.clear_rental_form).grid(row=5, column=2, padx=5, pady=10, sticky=W)

        # bindings + data
        self.cmb_ptype.bind("<<ComboboxSelected>>", lambda e: self._filter_codes_for_type())
        self.cmb_pcode.bind("<<ComboboxSelected>>", lambda e: self._update_cost_from_code())
        self.ent_days.bind("<KeyRelease>", lambda e: self.calculate_totals())

        self._refresh_customer_combo()
        self._refresh_product_combos()

    def calculate_totals(self):
        try:
            days = int(self.no_days.get() or "0")
        except ValueError:
            days = 0
        try:
            cpd = float(self.cost_per_day.get() or "0")
        except ValueError:
            cpd = 0.0

        sub = days * cpd
        tax_amt = sub * self.TAX_RATE
        total_amt = sub + tax_amt

        self.subtotal.set(f"{sub:.2f}")
        self.tax.set(f"{tax_amt:.2f}")
        self.total.set(f"{total_amt:.2f}")

    def save_rental(self):
        # validations
        if not self.selected_customer_id.get():
            messagebox.showerror("Error", "Please select a customer.")
            return
        if not self.selected_product_code.get():
            messagebox.showerror("Error", "Please select a product code.")
            return
        try:
            days = int(self.no_days.get())
            if days <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "No. Days must be a positive integer.")
            return

        self.calculate_totals()

        receipt = self.receipt_ref.get()
        rental_tuple = (
            int(self.selected_customer_id.get()),
            receipt,
            self.selected_product_type.get(),
            self.selected_product_code.get(),
            int(self.no_days.get()),
            float(self.cost_per_day.get()),
            float(self.tax.get()),
            float(self.subtotal.get()),
            float(self.total.get()),
        )
        try:
            self.db.save_rental(rental_tuple)
        except sqlite3.IntegrityError:
            # duplicate receipt? regenerate and retry once
            self.receipt_ref.set(self._make_receipt())
            rental_tuple = (
                rental_tuple[0], self.receipt_ref.get(), *rental_tuple[2:]
            )
            self.db.save_rental(rental_tuple)

        messagebox.showinfo("Success", "Rental saved.")
        self.clear_rental_form()
        self.load_rentals_table()
        self.draw_analytics()

    def clear_rental_form(self):
        self.receipt_ref.set(self._make_receipt())
        self.no_days.set("1")
        self.cost_per_day.set("0.00")
        self.subtotal.set("0.00")
        self.tax.set("0.00")
        self.total.set("0.00")
        self.selected_product_type.set("")
        self.selected_product_code.set("")

    # helpers
    def _make_receipt(self):
        return f"RC{datetime.datetime.now():%y%m%d}{random.randint(1000,9999)}"

    def _refresh_customer_combo(self):
        customers = self.db.get_customers()
        # store id->name mapping in combo's values as "id - name"
        items = [f"{cid}" for cid, *_ in customers]
        # but we want to show names; so use dict + custom formatting
        self._customer_lookup = {str(cid): name for cid, name, *_ in customers}
        display = [f"{cid} - {self._customer_lookup[str(cid)]}" for cid, *_ in customers]
        self.cmb_customer["values"] = display
        # set variable to id only when selecting via event
        def parse_selection(event):
            sel = self.cmb_customer.get()
            if " - " in sel:
                cid = sel.split(" - ", 1)[0].strip()
                self.selected_customer_id.set(cid)
        self.cmb_customer.bind("<<ComboboxSelected>>", parse_selection)

    def _refresh_product_combos(self):
        products = self.db.get_products()
        self._by_type = {}
        self._code_to_cost = {}
        for _, ptype, pcode, cpd in products:
            self._by_type.setdefault(ptype, []).append(pcode)
            self._code_to_cost[pcode] = cpd
        self.cmb_ptype["values"] = sorted(self._by_type.keys())
        self.cmb_pcode["values"] = []

    def _filter_codes_for_type(self):
        ptype = self.selected_product_type.get()
        codes = self._by_type.get(ptype, [])
        self.cmb_pcode["values"] = codes
        if codes:
            self.selected_product_code.set(codes[0])
            self._update_cost_from_code()
        else:
            self.selected_product_code.set("")
            self.cost_per_day.set("0.00")
            self.calculate_totals()

    def _update_cost_from_code(self):
        code = self.selected_product_code.get()
        cpd = self._code_to_cost.get(code, 0.0)
        self.cost_per_day.set(f"{cpd:.2f}")
        self.calculate_totals()

    def _quick_add_customer(self):
        top = tk.Toplevel(self.root)
        top.title("Add Customer")
        top.resizable(False, False)

        name = tk.StringVar()
        phone = tk.StringVar()
        email = tk.StringVar()
        address = tk.StringVar()

        ttk.Label(top, text="Name:").grid(row=0, column=0, sticky=E, padx=6, pady=6)
        ttk.Entry(top, textvariable=name, width=30).grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(top, text="Phone:").grid(row=1, column=0, sticky=E, padx=6, pady=6)
        ttk.Entry(top, textvariable=phone, width=30).grid(row=1, column=1, padx=6, pady=6)
        ttk.Label(top, text="Email:").grid(row=2, column=0, sticky=E, padx=6, pady=6)
        ttk.Entry(top, textvariable=email, width=30).grid(row=2, column=1, padx=6, pady=6)
        ttk.Label(top, text="Address:").grid(row=3, column=0, sticky=E, padx=6, pady=6)
        ttk.Entry(top, textvariable=address, width=30).grid(row=3, column=1, padx=6, pady=6)

        def do_add():
            if not name.get().strip():
                messagebox.showerror("Error", "Name is required.")
                return
            self.db.add_customer(name.get().strip(), phone.get().strip(), email.get().strip(), address.get().strip())
            messagebox.showinfo("Success", "Customer added.")
            top.destroy()
            self._refresh_customer_combo()
            self.load_customers_table()

        ttk.Button(top, text="Add", command=do_add).grid(row=4, column=0, columnspan=2, pady=10)

    # -------------------- Rental History --------------------
    def setup_history_tab(self):
        top = ttk.LabelFrame(self.tab_history, text="Rental History", style="Card.TLabelframe", padding=10)
        top.pack(fill=BOTH, expand=True, padx=10, pady=10)

        sframe = Frame(top)
        sframe.pack(fill=X, pady=(0, 8))
        ttk.Label(sframe, text="Search:").pack(side=LEFT, padx=5)
        self.hist_search = tk.StringVar()
        ent = ttk.Entry(sframe, textvariable=self.hist_search, width=30)
        ent.pack(side=LEFT, padx=5)
        ttk.Button(sframe, text="Go", command=self.search_rentals).pack(side=LEFT, padx=5)
        ttk.Button(sframe, text="Clear", command=lambda: (self.hist_search.set(""), self.load_rentals_table())).pack(side=LEFT, padx=5)

        cols = ("ID", "Receipt", "Customer", "Type", "Code", "Days", "Cost/Day", "Subtotal", "Tax", "Total", "Created")
        self.hist_tree = ttk.Treeview(top, columns=cols, show="headings")
        for c in cols:
            self.hist_tree.heading(c, text=c)
        self.hist_tree.column("ID", width=60)
        self.hist_tree.column("Receipt", width=120)
        self.hist_tree.column("Customer", width=160)
        self.hist_tree.column("Type", width=110)
        self.hist_tree.column("Code", width=100)
        self.hist_tree.column("Days", width=70)
        self.hist_tree.column("Cost/Day", width=90)
        self.hist_tree.column("Subtotal", width=90)
        self.hist_tree.column("Tax", width=80)
        self.hist_tree.column("Total", width=90)
        self.hist_tree.column("Created", width=150)

        vs = ttk.Scrollbar(top, orient=VERTICAL, command=self.hist_tree.yview)
        self.hist_tree.configure(yscrollcommand=vs.set)
        self.hist_tree.pack(side=LEFT, fill=BOTH, expand=True)
        vs.pack(side=RIGHT, fill=Y)

        self.load_rentals_table()

    def load_rentals_table(self):
        for i in self.hist_tree.get_children():
            self.hist_tree.delete(i)
        for row in self.db.get_all_rentals():
            self.hist_tree.insert("", "end", values=row)

    def search_rentals(self):
        q = self.hist_search.get().strip()
        rows = self.db.search_rentals(q) if q else self.db.get_all_rentals()
        for i in self.hist_tree.get_children():
            self.hist_tree.delete(i)
        for row in rows:
            self.hist_tree.insert("", "end", values=row)

    # -------------------- Analytics --------------------
    def setup_analytics_tab(self):
        container = ttk.LabelFrame(self.tab_analytics, text="Analytics", style="Card.TLabelframe", padding=10)
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        self.lbl_revenue = ttk.Label(container, text="Total Revenue: 0.00")
        self.lbl_revenue.pack(anchor=E, padx=4, pady=4)

        ttk.Button(container, text="Refresh", command=self.draw_analytics).pack(anchor=E, padx=4, pady=4)

        self.draw_analytics()

    def draw_analytics(self):
        data = self.db.rentals_by_product_type()
        self.ax.clear()
        if data:
            labels = [r[0] for r in data]
            counts = [r[1] for r in data]
            revenue = [r[2] or 0 for r in data]
            self.ax.bar(labels, counts)
            total_rev = sum(revenue)
            self.lbl_revenue.config(text=f"Total Revenue: {total_rev:.2f}")
        else:
            self.ax.text(0.5, 0.5, "No rentals yet", ha="center", va="center")
            self.lbl_revenue.config(text="Total Revenue: 0.00")
        self.ax.set_ylabel("Rentals")
        self.ax.set_title("Rentals by Product Type")
        self.canvas.draw_idle()

    # -------------------- Customer Management --------------------
    def setup_customer_tab(self):
        outer = ttk.LabelFrame(self.tab_customers, text="Customer Management", style="Card.TLabelframe", padding=10)
        outer.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # form
        form = Frame(outer)
        form.pack(fill=X, pady=(0, 10))

        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky=E, padx=5, pady=4)
        ttk.Entry(form, textvariable=self.customer_name, width=28).grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(form, text="Phone:").grid(row=0, column=2, sticky=E, padx=5, pady=4)
        ttk.Entry(form, textvariable=self.customer_phone, width=28).grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky=E, padx=5, pady=4)
        ttk.Entry(form, textvariable=self.customer_email, width=28).grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form, text="Address:").grid(row=1, column=2, sticky=E, padx=5, pady=4)
        ttk.Entry(form, textvariable=self.customer_address, width=28).grid(row=1, column=3, padx=5, pady=4)

        btns = Frame(form)
        btns.grid(row=2, column=0, columnspan=4, pady=6)
        ttk.Button(btns, text="Add", command=self.add_customer).pack(side=LEFT, padx=5)
        ttk.Button(btns, text="Update", command=self.update_customer).pack(side=LEFT, padx=5)
        ttk.Button(btns, text="Delete", command=self.delete_customer).pack(side=LEFT, padx=5)
        ttk.Button(btns, text="Clear", command=self.clear_customer_form).pack(side=LEFT, padx=5)

        # table
        cols = ("ID", "Name", "Phone", "Email", "Address")
        self.customer_tree = ttk.Treeview(outer, columns=cols, show="headings")
        for c in cols:
            self.customer_tree.heading(c, text=c)
        self.customer_tree.column("ID", width=60)
        self.customer_tree.column("Name", width=180)
        self.customer_tree.column("Phone", width=120)
        self.customer_tree.column("Email", width=200)
        self.customer_tree.column("Address", width=220)

        vs = ttk.Scrollbar(outer, orient=VERTICAL, command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=vs.set)
        self.customer_tree.pack(side=LEFT, fill=BOTH, expand=True)
        vs.pack(side=RIGHT, fill=Y)

        self.customer_tree.bind("<<TreeviewSelect>>", self.on_customer_select)

        self.load_customers_table()

    def load_customers_table(self):
        for i in self.customer_tree.get_children():
            self.customer_tree.delete(i)
        for row in self.db.get_customers():
            self.customer_tree.insert("", "end", values=row)
        self._refresh_customer_combo()  # keep rental tab combo in sync

    def on_customer_select(self, _event=None):
        sel = self.customer_tree.selection()
        if not sel:
            return
        vals = self.customer_tree.item(sel[0], "values")
        self.customer_id_edit = int(vals[0])
        self.customer_name.set(vals[1])
        self.customer_phone.set(vals[2])
        self.customer_email.set(vals[3])
        self.customer_address.set(vals[4])

    def clear_customer_form(self):
        self.customer_id_edit = None
        self.customer_name.set("")
        self.customer_phone.set("")
        self.customer_email.set("")
        self.customer_address.set("")

    def add_customer(self):
        name = self.customer_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Customer name is required.")
            return
        self.db.add_customer(
            name,
            self.customer_phone.get().strip(),
            self.customer_email.get().strip(),
            self.customer_address.get().strip(),
        )
        messagebox.showinfo("Success", "Customer added.")
        self.clear_customer_form()
        self.load_customers_table()

    def update_customer(self):
        if not self.customer_id_edit:
            messagebox.showerror("Error", "Select a customer to update.")
            return
        self.db.update_customer(
            self.customer_id_edit,
            self.customer_name.get().strip(),
            self.customer_phone.get().strip(),
            self.customer_email.get().strip(),
            self.customer_address.get().strip(),
        )
        messagebox.showinfo("Success", "Customer updated.")
        self.clear_customer_form()
        self.load_customers_table()

    def delete_customer(self):
        if not self.customer_id_edit:
            messagebox.showerror("Error", "Select a customer to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this customer?"):
            return
        self.db.delete_customer(self.customer_id_edit)
        messagebox.showinfo("Success", "Customer deleted.")
        self.clear_customer_form()
        self.load_customers_table()


# --------------------------- Runner ---------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedRentalInventory(root)
    root.mainloop()
