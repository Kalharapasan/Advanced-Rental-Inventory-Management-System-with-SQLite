# rims_full_ui.py
# Advanced Rental Inventory Management System (Tkinter, SQLite, Matplotlib)
# UI is laid out to match the screenshots you shared.

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.constants import *
import sqlite3, random, datetime

# --------- Optional PDF export ----------
try:
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

# --------- Database Layer ----------
class DB:
    def __init__(self, name="rental_inventory.db"):
        self.name = name
        self.init()

    def conn(self):
        return sqlite3.connect(self.name)

    def init(self):
        c = self.conn()
        cur = c.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS customers(
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT, email TEXT, address TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS products(
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_type TEXT NOT NULL,
            product_code TEXT UNIQUE,
            cost_per_day REAL NOT NULL,
            available_quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Available'
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS rentals(
            rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_ref TEXT UNIQUE,
            product_type TEXT, product_code TEXT,
            no_days TEXT, cost_per_day REAL,
            credit_limit TEXT, credit_check TEXT,
            settlement_due TEXT, payment_due TEXT,
            discount TEXT, deposit TEXT, pay_due_day TEXT,
            payment_method TEXT,
            check_credit INTEGER, term_agreed INTEGER,
            account_on_hold INTEGER, restrict_mailing INTEGER,
            account_opened TEXT, next_credit_review TEXT,
            last_credit_review TEXT, date_review TEXT,
            tax REAL, subtotal REAL, total REAL,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        # seed products
        defaults = [
            ("Car", "CAR452", 12.00, 5),
            ("Van", "VAN775", 19.00, 3),
            ("Minibus", "MIN334", 12.00, 2),
            ("Truck", "TRK7483", 15.00, 2),
        ]
        for pt, code, cpd, qty in defaults:
            cur.execute("INSERT OR IGNORE INTO products(product_type,product_code,cost_per_day,available_quantity) VALUES(?,?,?,?)",
                        (pt, code, cpd, qty))
        c.commit(); c.close()

    # customers
    def customers(self):
        c = self.conn(); cur=c.cursor()
        cur.execute("SELECT customer_id, customer_name, phone, email, address FROM customers ORDER BY created_date DESC")
        r = cur.fetchall(); c.close(); return r

    def add_customer(self, n,p,e,a):
        c=self.conn(); cur=c.cursor()
        cur.execute("INSERT INTO customers(customer_name,phone,email,address) VALUES(?,?,?,?)",(n,p,e,a))
        c.commit(); c.close()

    def update_customer(self, cid,n,p,e,a):
        c=self.conn(); cur=c.cursor()
        cur.execute("UPDATE customers SET customer_name=?, phone=?, email=?, address=? WHERE customer_id=?",
                    (n,p,e,a,cid))
        c.commit(); c.close()

    def delete_customer(self, cid):
        c=self.conn(); cur=c.cursor()
        cur.execute("DELETE FROM customers WHERE customer_id=?", (cid,))
        c.commit(); c.close()

    # products
    def products(self):
        c=self.conn(); cur=c.cursor()
        cur.execute("SELECT product_type, product_code, cost_per_day FROM products ORDER BY product_type, product_code")
        r=cur.fetchall(); c.close(); return r

    def cost_for_code(self, code):
        c=self.conn(); cur=c.cursor()
        cur.execute("SELECT cost_per_day FROM products WHERE product_code=?", (code,))
        row=cur.fetchone(); c.close(); return row[0] if row else 0.0

    # rentals
    def add_rental(self, data_tuple):
        c=self.conn(); cur=c.cursor()
        cur.execute("""INSERT INTO rentals(
            receipt_ref, product_type, product_code, no_days, cost_per_day,
            credit_limit, credit_check, settlement_due, payment_due, discount,
            deposit, pay_due_day, payment_method, check_credit, term_agreed,
            account_on_hold, restrict_mailing, account_opened, next_credit_review,
            last_credit_review, date_review, tax, subtotal, total
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", data_tuple)
        c.commit(); c.close()

    def rentals(self, search=None):
        c=self.conn(); cur=c.cursor()
        if search:
            s=f"%{search}%"
            cur.execute("""SELECT rental_id, receipt_ref, product_type, no_days, total, created_date
                           FROM rentals
                           WHERE receipt_ref LIKE ? OR product_type LIKE ? OR product_code LIKE ?
                           ORDER BY created_date DESC""",(s,s,s))
        else:
            cur.execute("""SELECT rental_id, receipt_ref, product_type, no_days, total, created_date
                           FROM rentals ORDER BY created_date DESC""")
        rows=cur.fetchall(); c.close(); return rows

    def analytics(self):
        c=self.conn(); cur=c.cursor()
        cur.execute("SELECT product_type, COUNT(*), SUM(total) FROM rentals GROUP BY product_type")
        by_type = cur.fetchall()
        cur.execute("SELECT date(created_date), COUNT(*) FROM rentals WHERE created_date >= date('now','-30 day') GROUP BY date(created_date)")
        daily = cur.fetchall()
        c.close()
        return by_type, daily

# --------- App ----------
class App:
    TAX_RATE = 0.15

    def __init__(self, root):
        self.db = DB()
        self.root = root
        self.root.title("Advanced Rental Inventory Management System")
        self.root.geometry("1250x780")
        self.root.configure(bg="#2c3e50")

        self._style()
        self._vars()
        self._title()
        self._tabs()
        self._fill_combos()

    # ---------- UI scaffolding ----------
    def _style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), background="#2c3e50", foreground="white")
        s.configure("Panel.TLabelframe", background="#dcdcdc")
        s.configure("Panel.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        s.configure("Big.TButton", font=("Segoe UI", 11, "bold"))
        s.configure("Green.TButton", background="#27ae60", foreground="white")
        s.map("Green.TButton", background=[("active","#1f8c4d")])
        s.configure("Blue.TButton", background="#3498db", foreground="white")
        s.map("Blue.TButton", background=[("active","#2b7ab4")])
        s.configure("Orange.TButton", background="#f39c12", foreground="white")
        s.map("Orange.TButton", background=[("active","#c27e0e")])
        s.configure("Red.TButton", background="#e74c3c", foreground="white")
        s.map("Red.TButton", background=[("active","#bf3f33")])

    def _vars(self):
        # product / rental left
        self.v_prod_type = tk.StringVar(value="Select")
        self.v_prod_code = tk.StringVar()
        self.v_days = tk.StringVar(value="Select")
        self.v_cost = tk.StringVar(value="")
        # credit panel
        self.v_credit_limit = tk.StringVar(value="Select")
        self.v_credit_check = tk.StringVar(value="Select")
        self.v_settle_due = tk.StringVar()
        self.v_payment_due = tk.StringVar(value="Select")
        self.v_discount = tk.StringVar(value="Select")
        self.v_deposit = tk.StringVar(value="Select")
        self.v_pay_due_day = tk.StringVar()
        self.v_payment_method = tk.StringVar(value="Select")
        # checks
        self.v_check_credit = tk.IntVar()
        self.v_term_agreed = tk.IntVar()
        self.v_on_hold = tk.IntVar()
        self.v_restrict_mail = tk.IntVar()
        # account info (right)
        self.v_account_opened = tk.StringVar(value="Select an option")
        self.v_next_review = tk.StringVar()
        self.v_last_review = tk.StringVar()
        self.v_date_review = tk.StringVar()
        # totals
        self.v_subtotal = tk.StringVar(value="")
        self.v_tax = tk.StringVar(value="")
        self.v_total = tk.StringVar(value="")
        self.v_receipt = tk.StringVar(value=self._new_receipt())
        # receipt text
        self.txt_receipt = None

        # customers management
        self.cus_id = None
        self.cus_name = tk.StringVar()
        self.cus_phone = tk.StringVar()
        self.cus_email = tk.StringVar()
        self.cus_address = tk.StringVar()

    def _title(self):
        ttk.Label(self.root, text="Advanced Rental Inventory Management System",
                  style="Title.TLabel").pack(fill=X, padx=10, pady=8)

    def _tabs(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill=BOTH, expand=True, padx=8, pady=6)
        self.tab_rental = ttk.Frame(nb)
        self.tab_history = ttk.Frame(nb)
        self.tab_analytics = ttk.Frame(nb)
        self.tab_customers = ttk.Frame(nb)
        nb.add(self.tab_rental, text="New Rental")
        nb.add(self.tab_history, text="Rental History")
        nb.add(self.tab_analytics, text="Analytics")
        nb.add(self.tab_customers, text="Customer Management")

        self._build_rental_tab()
        self._build_history_tab()
        self._build_analytics_tab()
        self._build_customers_tab()

    # ---------- New Rental tab (layout like your screenshot) ----------
    def _build_rental_tab(self):
        left = tk.Frame(self.tab_rental, bg="#2c3e50")
        right = tk.Frame(self.tab_rental, bg="#2c3e50")
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,6))
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6,0))

        # Product Selection
        ps = ttk.Labelframe(left, text="Product Selection", padding=10, style="Panel.TLabelframe")
        ps.pack(fill=X, padx=8, pady=(8,6))
        self._form_row(ps, 0, "Product Type:", self._combo(ps, self.v_prod_type, width=22, values=[]))
        self._form_row(ps, 0, "No of Days:", self._combo(ps, self.v_days, width=22, values=["1-3","4-7","8-14","15-30","31-90"]))
        self._form_row(ps, 1, "Product Code:", self._entry(ps, self.v_prod_code, width=24))
        self._form_row(ps, 1, "Cost Per Day:", self._entry(ps, self.v_cost, width=24, state="readonly"))

        # Credit & Payment Details
        cr = ttk.Labelframe(left, text="Credit & Payment Details", padding=10, style="Panel.TLabelframe")
        cr.pack(fill=X, padx=8, pady=6)
        self._form_row(cr, 0, "Credit Limit:", self._combo(cr, self.v_credit_limit, values=["£500","£1000","£2000","£5000"]))
        self._form_row(cr, 0, "Credit Check:", self._combo(cr, self.v_credit_check, values=["Passed","Pending","Failed"]))
        self._form_row(cr, 1, "Settlement Due:", self._entry(cr, self.v_settle_due))
        self._form_row(cr, 1, "Payment Due:", self._combo(cr, self.v_payment_due, values=["Weekly","Monthly","Quarterly"]))
        self._form_row(cr, 2, "Discount:", self._combo(cr, self.v_discount, values=["0%","5%","10%","15%"]))
        self._form_row(cr, 2, "Deposit:", self._combo(cr, self.v_deposit, values=["£0","£50","£100","£200"]))
        self._form_row(cr, 3, "Pay Due Day:", self._entry(cr, self.v_pay_due_day))
        self._form_row(cr, 3, "Payment Method:", self._combo(cr, self.v_payment_method, values=["Cash","Card","Bank Transfer"]))

        # Checks + Status box
        row = tk.Frame(left, bg="#2c3e50"); row.pack(fill=X, padx=8, pady=(6,8))
        checks = ttk.Labelframe(row, text="Customer Checks", padding=10, style="Panel.TLabelframe")
        checks.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,6))
        ttk.Checkbutton(checks, text="Check Credit", variable=self.v_check_credit).pack(anchor=W, pady=4)
        ttk.Checkbutton(checks, text="Term Agreed", variable=self.v_term_agreed).pack(anchor=W, pady=4)
        ttk.Checkbutton(checks, text="Account On Hold", variable=self.v_on_hold).pack(anchor=W, pady=4)
        ttk.Checkbutton(checks, text="Restrict Mailing", variable=self.v_restrict_mail).pack(anchor=W, pady=4)

        status = ttk.Labelframe(row, text="Status Information", padding=10, style="Panel.TLabelframe")
        status.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6,0))
        ttk.Entry(status).pack(fill=X, pady=6)
        ttk.Entry(status).pack(fill=X, pady=6)
        ttk.Entry(status).pack(fill=X, pady=6)
        ttk.Entry(status).pack(fill=X, pady=6)

        # Buttons bottom (left side)
        btnbar = tk.Frame(left, bg="#2c3e50"); btnbar.pack(fill=X, padx=8, pady=(0,10))
        ttk.Button(btnbar, text="Calculate Total", style="Green.TButton", command=self.calculate, width=18).pack(side=LEFT, padx=6, pady=6)
        ttk.Button(btnbar, text="Save Rental", style="Blue.TButton", command=self.save_rental, width=16).pack(side=LEFT, padx=6, pady=6)
        ttk.Button(btnbar, text="Reset", style="Orange.TButton", command=self.reset_rental, width=12).pack(side=LEFT, padx=6, pady=6)
        ttk.Button(btnbar, text="Exit", style="Red.TButton", command=self.root.destroy, width=10).pack(side=LEFT, padx=6, pady=6)

        # Right side panels
        ai = ttk.Labelframe(right, text="Account Information", padding=10, style="Panel.TLabelframe")
        ai.pack(fill=X, padx=8, pady=(8,6))
        self._form_row(ai, 0, "Account Opened:", self._combo(ai, self.v_account_opened, values=["Open","Closed","Suspended"]))
        self._form_row(ai, 1, "Next Credit Review:", self._entry(ai, self.v_next_review))
        self._form_row(ai, 2, "Last Credit Review:", self._entry(ai, self.v_last_review))
        self._form_row(ai, 3, "Date Review:", self._entry(ai, self.v_date_review))

        rc = ttk.Labelframe(right, text="Receipt", padding=6, style="Panel.TLabelframe")
        rc.pack(fill=BOTH, expand=True, padx=8, pady=(6,8))
        self.txt_receipt = tk.Text(rc, height=20)
        self.txt_receipt.pack(fill=BOTH, expand=True)

        # bindings
        self.v_prod_code.trace_add("write", lambda *_: self._update_cost_from_code())
        self.v_prod_type.trace_add("write", lambda *_: self._filter_codes_by_type())

    def _form_row(self, parent, row, label, widget):
        # two columns per row (like screenshot)
        col = (0,1) if row % 1 == 0 else (0,1)
        r = row
        L = ttk.Label(parent, text=label, font=("Segoe UI", 10, "bold"))
        L.grid(row=r, column=(0 if label.endswith(":") else 0), sticky=W, padx=6, pady=4)
        widget.grid(row=r, column=1, sticky=W, padx=6, pady=4)

    def _entry(self, parent, var, width=24, state="normal"):
        return ttk.Entry(parent, textvariable=var, width=width, state=state)

    def _combo(self, parent, var, width=22, values=()):
        cb = ttk.Combobox(parent, textvariable=var, width=width, values=values, state="readonly")
        return cb

    # ---------- History tab ----------
    def _build_history_tab(self):
        top = ttk.Labelframe(self.tab_history, text="Search Rentals", padding=10, style="Panel.TLabelframe")
        top.pack(fill=BOTH, expand=True, padx=8, pady=8)

        sr = tk.Frame(top); sr.pack(fill=X, pady=(0,6))
        ttk.Label(sr, text="Search:", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=6)
        self.v_hist_q = tk.StringVar()
        ttk.Entry(sr, textvariable=self.v_hist_q, width=40).pack(side=LEFT, padx=6)
        ttk.Button(sr, text="Search", style="Blue.TButton", command=self.search_history).pack(side=LEFT, padx=4)
        ttk.Button(sr, text="Show All", style="Green.TButton", command=self.load_history).pack(side=LEFT, padx=4)
        ttk.Button(sr, text="Export to PDF", style="Red.TButton", command=self.export_pdf).pack(side=RIGHT)

        cols=("ID","Receipt Ref","Product Type","No. Days","Total","Date")
        self.tree_hist = ttk.Treeview(top, columns=cols, show="headings")
        for c in cols: self.tree_hist.heading(c, text=c)
        self.tree_hist.column("ID", width=60)
        self.tree_hist.column("Receipt Ref", width=140)
        self.tree_hist.column("Product Type", width=140)
        self.tree_hist.column("No. Days", width=110)
        self.tree_hist.column("Total", width=120)
        self.tree_hist.column("Date", width=160)
        vs = ttk.Scrollbar(top, orient=VERTICAL, command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=vs.set)
        self.tree_hist.pack(side=LEFT, fill=BOTH, expand=True)
        vs.pack(side=RIGHT, fill=Y)

        self.load_history()

    # ---------- Analytics tab ----------
    def _build_analytics_tab(self):
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        wrap = ttk.Labelframe(self.tab_analytics, text="", padding=10, style="Panel.TLabelframe")
        wrap.pack(fill=BOTH, expand=True, padx=8, pady=8)

        self.fig = Figure(figsize=(9,5))
        self.ax_pie = self.fig.add_subplot(2,2,1)
        self.ax_bar = self.fig.add_subplot(2,2,2)
        self.ax_line = self.fig.add_subplot(2,1,2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=wrap)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        ttk.Button(wrap, text="Refresh", style="Blue.TButton", command=self.refresh_analytics).pack(anchor=E, pady=6)
        self.refresh_analytics()

    # ---------- Customer Management tab ----------
    def _build_customers_tab(self):
        outer = ttk.Labelframe(self.tab_customers, text="Customer Information", padding=10, style="Panel.TLabelframe")
        outer.pack(fill=BOTH, expand=True, padx=8, pady=8)

        form = tk.Frame(outer); form.pack(fill=X, pady=(0,6))
        self._lbl_ent(form, 0, "Customer Name:", self.cus_name)
        self._lbl_ent(form, 0, "Phone:", self.cus_phone, col=2)
        self._lbl_ent(form, 1, "Email:", self.cus_email)
        self._lbl_ent(form, 1, "Address:", self.cus_address, col=2)

        btns = tk.Frame(outer); btns.pack(fill=X, pady=6)
        ttk.Button(btns, text="Add Customer", style="Green.TButton", command=self.cus_add).pack(side=LEFT, padx=4)
        ttk.Button(btns, text="Update", style="Blue.TButton", command=self.cus_update).pack(side=LEFT, padx=4)
        ttk.Button(btns, text="Delete", style="Red.TButton", command=self.cus_delete).pack(side=LEFT, padx=4)
        ttk.Button(btns, text="Clear", style="Orange.TButton", command=self.cus_clear).pack(side=LEFT, padx=4)

        cols=("ID","Name","Phone","Email","Address")
        self.tree_cus = ttk.Treeview(outer, columns=cols, show="headings", height=12)
        for c in cols: self.tree_cus.heading(c, text=c)
        self.tree_cus.column("ID", width=60)
        self.tree_cus.column("Name", width=180)
        self.tree_cus.column("Phone", width=120)
        self.tree_cus.column("Email", width=180)
        self.tree_cus.column("Address", width=220)
        vs = ttk.Scrollbar(outer, orient=VERTICAL, command=self.tree_cus.yview)
        self.tree_cus.configure(yscrollcommand=vs.set)
        self.tree_cus.pack(side=LEFT, fill=BOTH, expand=True)
        vs.pack(side=RIGHT, fill=Y)

        self.tree_cus.bind("<<TreeviewSelect>>", self._cus_select)
        self._reload_customers()

    def _lbl_ent(self, parent, row, text, var, col=0):
        ttk.Label(parent, text=text, font=("Segoe UI", 10, "bold")).grid(row=row, column=col*2, sticky=E, padx=6, pady=4)
        ttk.Entry(parent, textvariable=var, width=28).grid(row=row, column=col*2+1, padx=6, pady=4, sticky=W)

    # ---------- Data helpers ----------
    def _fill_combos(self):
        # product type list + code map
        self.products = self.db.products()
        self.codes_by_type = {}
        self.cost_by_code = {}
        for pt, code, cpd in self.products:
            self.codes_by_type.setdefault(pt, []).append(code)
            self.cost_by_code[code] = cpd
        # set product type combobox values
        for w in self.tab_rental.winfo_children():
            pass  # (we already set trace to update fields when value changes)
        # set default type if exists
        if self.codes_by_type:
            types = sorted(self.codes_by_type.keys())
            self._set_combo_values(self.v_prod_type, types)

    def _set_combo_values(self, var, values):
        # find the widget bound to this var (combobox) and set its values
        def find_cb(widget):
            if isinstance(widget, ttk.Combobox) and widget.cget("textvariable") == str(var):
                return widget
            for ch in widget.winfo_children():
                r = find_cb(ch)
                if r: return r
            return None
        cb = find_cb(self.tab_rental)
        if cb: cb["values"] = values

    def _filter_codes_by_type(self):
        t = self.v_prod_type.get()
        codes = self.codes_by_type.get(t, [])
        self.v_prod_code.set("")
        self.v_cost.set("")
        # update combobox for code
        self._set_combo_values(self.v_prod_code, codes)

    def _update_cost_from_code(self):
        code = self.v_prod_code.get().strip()
        if not code:
            self.v_cost.set(""); return
        cpd = self.cost_by_code.get(code) or self.db.cost_for_code(code)
        self.v_cost.set(f"£{cpd:.2f}")

    # ---------- Calculate / Save / Reset ----------
    def calculate(self):
        # days range -> an approximate numeric center
        ranges = {"1-3": 2, "4-7": 6, "8-14": 11, "15-30": 22, "31-90": 60}
        days = ranges.get(self.v_days.get(), 0)
        try:
            cpd = float(self.v_cost.get().replace("£","")) if self.v_cost.get() else 0.0
        except Exception:
            cpd = 0.0
        subtotal = days * cpd
        tax = subtotal * self.TAX_RATE
        total = subtotal + tax
        self.v_subtotal.set(f"£{subtotal:.2f}")
        self.v_tax.set(f"£{tax:.2f}")
        self.v_total.set(f"{total:.1f}")

        # build receipt text
        self.txt_receipt.delete("1.0", END)
        self.txt_receipt.insert(END, f"Receipt Ref : {self.v_receipt.get()}\n")
        self.txt_receipt.insert(END, f"Product Type : {self.v_prod_type.get()}\n")
        self.txt_receipt.insert(END, f"Product Code : {self.v_prod_code.get()}\n")
        self.txt_receipt.insert(END, f"No. of Days  : {self.v_days.get()} (~{days} days)\n")
        self.txt_receipt.insert(END, f"Cost / Day   : {self.v_cost.get()}\n")
        self.txt_receipt.insert(END, f"Subtotal     : {self.v_subtotal.get()}\n")
        self.txt_receipt.insert(END, f"Tax (15%)    : {self.v_tax.get()}\n")
        self.txt_receipt.insert(END, f"Total        : £{self.v_total.get()}\n")

    def save_rental(self):
        if not self.v_prod_type.get() or self.v_prod_type.get()=="Select":
            messagebox.showerror("Error","Select Product Type"); return
        if not self.v_prod_code.get():
            messagebox.showerror("Error","Enter/Select Product Code"); return
        if not self.v_days.get() or self.v_days.get()=="Select":
            messagebox.showerror("Error","Select No of Days"); return

        self.calculate()
        receipt = self.v_receipt.get()
        row = (receipt, self.v_prod_type.get(), self.v_prod_code.get(),
               self.v_days.get(), float(self.v_cost.get().replace("£","") or 0),
               self.v_credit_limit.get(), self.v_credit_check.get(),
               self.v_settle_due.get(), self.v_payment_due.get(),
               self.v_discount.get(), self.v_deposit.get(),
               self.v_pay_due_day.get(), self.v_payment_method.get(),
               self.v_check_credit.get(), self.v_term_agreed.get(),
               self.v_on_hold.get(), self.v_restrict_mail.get(),
               self.v_account_opened.get(), self.v_next_review.get(),
               self.v_last_review.get(), self.v_date_review.get(),
               float(self.v_tax.get().replace("£","") or 0),
               float(self.v_subtotal.get().replace("£","") or 0),
               float(self.v_total.get() or 0)
               )
        try:
            self.db.add_rental(row)
        except sqlite3.IntegrityError:
            # duplicate receipt -> regenerate and retry
            self.v_receipt.set(self._new_receipt())
            row = (self.v_receipt.get(),) + row[1:]
            self.db.add_rental(row)

        messagebox.showinfo("Saved","Rental saved.")
        self.reset_rental()
        self.load_history()
        self.refresh_analytics()

    def reset_rental(self):
        self.v_prod_type.set("Select"); self.v_days.set("Select")
        self.v_prod_code.set(""); self.v_cost.set("")
        self.v_credit_limit.set("Select"); self.v_credit_check.set("Select")
        self.v_settle_due.set(""); self.v_payment_due.set("Select")
        self.v_discount.set("Select"); self.v_deposit.set("Select")
        self.v_pay_due_day.set(""); self.v_payment_method.set("Select")
        self.v_check_credit.set(0); self.v_term_agreed.set(0)
        self.v_on_hold.set(0); self.v_restrict_mail.set(0)
        self.v_account_opened.set("Select an option")
        self.v_next_review.set(""); self.v_last_review.set(""); self.v_date_review.set("")
        self.v_subtotal.set(""); self.v_tax.set(""); self.v_total.set("")
        self.v_receipt.set(self._new_receipt())
        self.txt_receipt.delete("1.0", END)

    def _new_receipt(self):
        return f"BILL{random.randint(100000,999999)}"

    # ---------- History ----------
    def load_history(self):
        for i in self.tree_hist.get_children(): self.tree_hist.delete(i)
        for r in self.db.rentals():
            self.tree_hist.insert("", "end", values=r)

    def search_history(self):
        q = self.v_hist_q.get().strip()
        rows = self.db.rentals(q)
        for i in self.tree_hist.get_children(): self.tree_hist.delete(i)
        for r in rows: self.tree_hist.insert("", "end", values=r)

    def export_pdf(self):
        if not REPORTLAB_OK:
            messagebox.showwarning("PDF", "ReportLab not installed. Run: pip install reportlab")
            return
        rows = self.db.rentals(self.v_hist_q.get().strip() or None)
        if not rows:
            messagebox.showinfo("PDF", "No data to export."); return
        filename = f"rentals_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf"
        c = pdf_canvas.Canvas(filename, pagesize=A4)
        w, h = A4
        y = h - 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40,y, "Rental History"); y -= 24
        c.setFont("Helvetica", 10)
        headers = ["ID","Receipt","Product","No.Days","Total","Date"]
        c.drawString(40,y, " | ".join(headers)); y-=16
        for r in rows:
            line = f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | £{r[4]} | {r[5]}"
            if y < 60:
                c.showPage(); y=h-40
            c.drawString(40,y,line); y-=14
        c.save()
        messagebox.showinfo("PDF", f"Exported to {filename}")

    # ---------- Analytics ----------
    def refresh_analytics(self):
        (by_type, daily) = self.db.analytics()

        # pie: distribution by count
        self.ax_pie.clear()
        if by_type:
            labels = [r[0] for r in by_type]
            counts = [r[1] for r in by_type]
            self.ax_pie.pie(counts, labels=labels, autopct="%1.1f%%")
            self.ax_pie.set_title("Product Distribution by Count")
        else:
            self.ax_pie.text(0.5,0.5,"No data", ha="center")

        # bar: revenue by product type
        self.ax_bar.clear()
        if by_type:
            labels = [r[0] for r in by_type]
            revenue = [r[2] or 0 for r in by_type]
            self.ax_bar.bar(labels, revenue)
            self.ax_bar.set_title("Revenue by Product Type")
            self.ax_bar.set_ylabel("Revenue (£)")
        else:
            self.ax_bar.text(0.5,0.5,"No data", ha="center")

        # line: daily rentals last 30 days
        self.ax_line.clear()
        if daily:
            xs = [d[0] for d in daily]
            ys = [d[1] for d in daily]
            self.ax_line.plot(xs, ys, marker="o")
            self.ax_line.set_title("Daily Rentals (Last 30 Days)")
            self.ax_line.set_ylabel("Number of Rentals")
            self.ax_line.tick_params(axis='x', labelrotation=45)
        else:
            self.ax_line.text(0.5,0.5,"No data", ha="center")
        self.canvas.draw_idle()

    # ---------- Customers ----------
    def _reload_customers(self):
        for i in self.tree_cus.get_children(): self.tree_cus.delete(i)
        for r in self.db.customers():
            self.tree_cus.insert("", "end", values=r)

    def _cus_select(self, _e=None):
        sel = self.tree_cus.selection()
        if not sel: return
        vals = self.tree_cus.item(sel[0], "values")
        self.cus_id = vals[0]
        self.cus_name.set(vals[1]); self.cus_phone.set(vals[2])
        self.cus_email.set(vals[3]); self.cus_address.set(vals[4])

    def cus_clear(self):
        self.cus_id=None
        self.cus_name.set(""); self.cus_phone.set("")
        self.cus_email.set(""); self.cus_address.set("")

    def cus_add(self):
        if not self.cus_name.get().strip():
            messagebox.showerror("Error","Customer name is required."); return
        self.db.add_customer(self.cus_name.get().strip(), self.cus_phone.get().strip(),
                             self.cus_email.get().strip(), self.cus_address.get().strip())
        messagebox.showinfo("Success","Customer added.")
        self.cus_clear(); self._reload_customers()

    def cus_update(self):
        if not self.cus_id:
            messagebox.showerror("Error","Select a customer to update."); return
        self.db.update_customer(self.cus_id, self.cus_name.get().strip(),
                                self.cus_phone.get().strip(), self.cus_email.get().strip(),
                                self.cus_address.get().strip())
        messagebox.showinfo("Success","Customer updated.")
        self.cus_clear(); self._reload_customers()

    def cus_delete(self):
        if not self.cus_id:
            messagebox.showerror("Error","Select a customer to delete."); return
        if not messagebox.askyesno("Confirm","Delete this customer?"): return
        self.db.delete_customer(self.cus_id)
        messagebox.showinfo("Success","Customer deleted.")
        self.cus_clear(); self._reload_customers()

# ---------------- Run ----------------
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
