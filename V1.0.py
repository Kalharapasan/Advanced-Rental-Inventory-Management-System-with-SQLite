import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import sqlite3
import random
import datetime
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

class DatabaseManager:
    def __init__(self, db_name="rental_inventory.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Create rentals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rentals (
                rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                receipt_ref TEXT UNIQUE,
                product_type TEXT,
                product_code TEXT,
                no_days INTEGER,
                cost_per_day REAL,
                account_open TEXT,
                app_date DATE,
                next_credit_review DATE,
                last_credit_review INTEGER,
                date_rev DATE,
                credit_limit TEXT,
                credit_check TEXT,
                sett_due_day INTEGER,
                payment_due TEXT,
                discount REAL,
                deposit TEXT,
                pay_due_day TEXT,
                payment_method TEXT,
                check_credit INTEGER,
                term_agreed INTEGER,
                account_on_hold INTEGER,
                restrict_mailing INTEGER,
                tax REAL,
                subtotal REAL,
                total REAL,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        ''')
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_type TEXT NOT NULL,
                product_code TEXT UNIQUE,
                cost_per_day REAL,
                available_quantity INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Available'
            )
        ''')
        
        # Insert default products if they don't exist
        default_products = [
            ('Car', 'CAR452', 12.00, 5),
            ('Van', 'VAN775', 19.00, 3),
            ('Minibus', 'MIN334', 12.00, 2),
            ('Truck', 'TRK7483', 15.00, 2)
        ]
        
        for product in default_products:
            cursor.execute('''
                INSERT OR IGNORE INTO products (product_type, product_code, cost_per_day, available_quantity)
                VALUES (?, ?, ?, ?)
            ''', product)
        
        conn.commit()
        conn.close()
    
    def save_rental(self, rental_data):
        """Save rental data to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rentals (
                customer_id, receipt_ref, product_type, product_code, no_days, cost_per_day,
                account_open, app_date, next_credit_review, last_credit_review, date_rev,
                credit_limit, credit_check, sett_due_day, payment_due, discount, deposit,
                pay_due_day, payment_method, check_credit, term_agreed, account_on_hold,
                restrict_mailing, tax, subtotal, total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rental_data)
        
        conn.commit()
        conn.close()
    
    def get_all_rentals(self):
        """Get all rental records"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rentals ORDER BY created_date DESC')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_rentals(self, search_term):
        """Search rentals by receipt reference or product type"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM rentals 
            WHERE receipt_ref LIKE ? OR product_type LIKE ?
            ORDER BY created_date DESC
        ''', (f'%{search_term}%', f'%{search_term}%'))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_customers(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id, customer_name, phone, email, address FROM customers ORDER BY created_date DESC")
        customers = cursor.fetchall()
        conn.close()
        return customers
    
    def add_customer(self, name, phone, email, address):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO customers (customer_name, phone, email, address) VALUES (?, ?, ?, ?)", (name, phone, email, address))
        conn.commit()
        conn.close()
    
    def update_customer(self, customer_id, name, phone, email, address):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE customers SET customer_name=?, phone=?, email=?, address=? WHERE customer_id=?", (name, phone, email, address, customer_id))
        conn.commit()
        conn.close()
    
    def delete_customer(self, customer_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE customer_id=?", (customer_id,))
        conn.commit()
        conn.close()

class AdvancedRentalInventory:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Rental Inventory Management System")
        self.root.geometry("1600x900")
        self.root.configure(background='#2c3e50')
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Configure style
        self.configure_styles()
        
        # Initialize variables
        self.init_variables()
        
        # Create main interface
        self.create_main_interface()
        
        # Create notebook (tabs)
        self.create_notebook()
    
    def configure_styles(self):
        """Configure modern UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'), background='#2c3e50', foreground='white')
        style.configure('Heading.TLabel', font=('Arial', 16, 'bold'), background='#34495e', foreground='white')
        style.configure('Modern.TFrame', background='#34495e', relief='raised', borderwidth=2)
        style.configure('Card.TFrame', background='#ecf0f1', relief='raised', borderwidth=1)
    
    def init_variables(self):
        """Initialize all tkinter variables"""
        self.AcctOpen = StringVar()
        self.AppDate = StringVar()
        self.NextCreditReview = StringVar()
        self.LastCreditReview = StringVar()
        self.DateRev = StringVar()
        self.ProdCode = StringVar()
        self.ProdType = StringVar()
        self.NoDays = StringVar()
        self.CostPDay = StringVar()
        self.CreLimit = StringVar()
        self.CreCheck = StringVar()
        self.SettDueDay = StringVar()
        self.PaymentD = StringVar()
        self.Discount = StringVar()
        self.Deposit = StringVar()
        self.PayDueDay = StringVar()
        self.PaymentM = StringVar()
        
        self.var1 = IntVar()
        self.var2 = IntVar()
        self.var3 = IntVar()
        self.var4 = IntVar()
        self.Tax = StringVar()
        self.SubTotal = StringVar()
        self.Total = StringVar()
        self.Receipt_Ref = StringVar()
        
        # New variables for customer management
        self.customer_name = StringVar()
        self.customer_phone = StringVar()
        self.customer_email = StringVar()
        self.customer_address = StringVar()
    
    def create_main_interface(self):
        """Create the main interface layout"""
        # Main title
        title_frame = Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill=X, padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = Label(title_frame, text="Advanced Rental Inventory Management System", 
                           font=('Arial', 24, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(expand=True)
    
    def create_notebook(self):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.rental_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.analytics_tab = ttk.Frame(self.notebook)
        self.customer_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.rental_tab, text="New Rental")
        self.notebook.add(self.history_tab, text="Rental History")
        self.notebook.add(self.analytics_tab, text="Analytics")
        self.notebook.add(self.customer_tab, text="Customer Management")
        
        # Setup each tab
        self.setup_rental_tab()
        self.setup_history_tab()
        self.setup_analytics_tab()
        self.setup_customer_tab()
    
    def setup_rental_tab(self):
        """Setup the main rental tab with original functionality"""
        # Main container
        main_container = Frame(self.rental_tab, bg='#2c3e50')
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Left and Right frames
        left_frame = Frame(main_container, bg='#34495e', relief=RIDGE, bd=3)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        right_frame = Frame(main_container, bg='#34495e', relief=RIDGE, bd=3)
        right_frame.pack(side=RIGHT, fill=BOTH, padx=(5, 0))
        
        # Setup left frame sections
        self.setup_left_frame(left_frame)
        self.setup_right_frame(right_frame)
    
    def setup_left_frame(self, parent):
        """Setup left frame with product selection and details"""
        # Product Selection Frame
        product_frame = ttk.LabelFrame(parent, text="Product Selection", padding=10)
        product_frame.pack(fill=X, padx=10, pady=5)
        
        # Row 1: Product Type and Days
        Label(product_frame, text="Product Type:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=W, padx=5)
        self.cboProdType = ttk.Combobox(product_frame, textvariable=self.ProdType, state='readonly', 
                                       font=('Arial', 12), width=15)
        self.cboProdType.bind("<<ComboboxSelected>>", self.product_selected)
        self.cboProdType['values'] = ('Select', 'Car', 'Van', 'Minibus', 'Truck')
        self.cboProdType.current(0)
        self.cboProdType.grid(row=0, column=1, padx=5, pady=2)
        
        Label(product_frame, text="No of Days:", font=('Arial', 12, 'bold')).grid(row=0, column=2, sticky=W, padx=5)
        self.cboNoDays = ttk.Combobox(product_frame, textvariable=self.NoDays, state='readonly',
                                     font=('Arial', 12), width=15)
        self.cboNoDays.bind("<<ComboboxSelected>>", self.days_selected)
        self.cboNoDays['values'] = ('Select', '0', '1-30', '31-90', '91-270', '271-365')
        self.cboNoDays.current(0)
        self.cboNoDays.grid(row=0, column=3, padx=5, pady=2)
        
        # Row 2: Product Code and Cost
        Label(product_frame, text="Product Code:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=W, padx=5)
        Entry(product_frame, textvariable=self.ProdCode, font=('Arial', 12), width=18, state='readonly').grid(row=1, column=1, padx=5, pady=2)
        
        Label(product_frame, text="Cost Per Day:", font=('Arial', 12, 'bold')).grid(row=1, column=2, sticky=W, padx=5)
        Entry(product_frame, textvariable=self.CostPDay, font=('Arial', 12), width=18, state='readonly').grid(row=1, column=3, padx=5, pady=2)
        
        # Credit and Payment Frame
        credit_frame = ttk.LabelFrame(parent, text="Credit & Payment Details", padding=10)
        credit_frame.pack(fill=X, padx=10, pady=5)
        
        # Row 1
        Label(credit_frame, text="Credit Limit:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=W, padx=5)
        self.cboCreLimit = ttk.Combobox(credit_frame, textvariable=self.CreLimit, state='readonly', 
                                       font=('Arial', 12), width=15)
        self.cboCreLimit['values'] = ('Select', '£150', '£200', '£250', '£300')
        self.cboCreLimit.current(0)
        self.cboCreLimit.grid(row=0, column=1, padx=5, pady=2)
        
        Label(credit_frame, text="Credit Check:", font=('Arial', 12, 'bold')).grid(row=0, column=2, sticky=W, padx=5)
        self.cboCreCheck = ttk.Combobox(credit_frame, textvariable=self.CreCheck, state='readonly',
                                       font=('Arial', 12), width=15)
        self.cboCreCheck['values'] = ('Select', 'Yes', 'No')
        self.cboCreCheck.current(0)
        self.cboCreCheck.grid(row=0, column=3, padx=5, pady=2)
        
        # Row 2
        Label(credit_frame, text="Settlement Due:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=W, padx=5)
        Entry(credit_frame, textvariable=self.SettDueDay, font=('Arial', 12), width=18, state='readonly').grid(row=1, column=1, padx=5, pady=2)
        
        Label(credit_frame, text="Payment Due:", font=('Arial', 12, 'bold')).grid(row=1, column=2, sticky=W, padx=5)
        self.cboPaymentD = ttk.Combobox(credit_frame, textvariable=self.PaymentD, state='readonly', 
                                       font=('Arial', 12), width=15)
        self.cboPaymentD['values'] = ('Select', 'Yes', 'No')
        self.cboPaymentD.current(0)
        self.cboPaymentD.grid(row=1, column=3, padx=5, pady=2)
        
        # Row 3
        Label(credit_frame, text="Discount:", font=('Arial', 12, 'bold')).grid(row=2, column=0, sticky=W, padx=5)
        self.cboDiscount = ttk.Combobox(credit_frame, textvariable=self.Discount, state='readonly', 
                                       font=('Arial', 12), width=15)
        self.cboDiscount['values'] = ('Select', '0%', '5%', '10%', '15%', '20%')
        self.cboDiscount.current(0)
        self.cboDiscount.grid(row=2, column=1, padx=5, pady=2)
        
        Label(credit_frame, text="Deposit:", font=('Arial', 12, 'bold')).grid(row=2, column=2, sticky=W, padx=5)
        self.cboDeposit = ttk.Combobox(credit_frame, textvariable=self.Deposit, state='readonly', 
                                      font=('Arial', 12), width=15)
        self.cboDeposit['values'] = ('Select', 'Yes', 'No')
        self.cboDeposit.current(0)
        self.cboDeposit.grid(row=2, column=3, padx=5, pady=2)
        
        # Row 4
        Label(credit_frame, text="Pay Due Day:", font=('Arial', 12, 'bold')).grid(row=3, column=0, sticky=W, padx=5)
        Entry(credit_frame, textvariable=self.PayDueDay, font=('Arial', 12), width=18, state='readonly').grid(row=3, column=1, padx=5, pady=2)
        
        Label(credit_frame, text="Payment Method:", font=('Arial', 12, 'bold')).grid(row=3, column=2, sticky=W, padx=5)
        self.cboPaymentM = ttk.Combobox(credit_frame, textvariable=self.PaymentM, state='readonly',
                                       font=('Arial', 12), width=15)
        self.cboPaymentM['values'] = ('Select', 'Cash', 'Visa Card', 'Master Card', 'Debit Card')
        self.cboPaymentM.current(0)
        self.cboPaymentM.grid(row=3, column=3, padx=5, pady=2)
        
        # Checkboxes and Info Frame
        check_info_frame = Frame(parent, bg='#34495e')
        check_info_frame.pack(fill=X, padx=10, pady=5)
        
        # Left side - Checkboxes
        check_frame = ttk.LabelFrame(check_info_frame, text="Customer Checks", padding=10)
        check_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        self.chkCheckCredit = Checkbutton(check_frame, text="Check Credit", variable=self.var1, 
                                         font=('Arial', 12), command=self.check_credit)
        self.chkCheckCredit.pack(anchor=W, pady=2)
        
        self.chkTermAgreed = Checkbutton(check_frame, text="Term Agreed", variable=self.var2, 
                                        font=('Arial', 12), command=self.term_agreed)
        self.chkTermAgreed.pack(anchor=W, pady=2)
        
        self.chkAccountOnHold = Checkbutton(check_frame, text="Account On Hold", variable=self.var3, 
                                           font=('Arial', 12), command=self.account_on_hold)
        self.chkAccountOnHold.pack(anchor=W, pady=2)
        
        self.chkRestrictMailing = Checkbutton(check_frame, text="Restrict Mailing", variable=self.var4, 
                                             font=('Arial', 12), command=self.restricted_mails)
        self.chkRestrictMailing.pack(anchor=W, pady=2)
        
        # Right side - Info displays
        info_frame = ttk.LabelFrame(check_info_frame, text="Status Information", padding=10)
        info_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        self.txtInfo0 = Text(info_frame, height=2, width=50, font=('Arial', 9), wrap=WORD)
        self.txtInfo0.pack(pady=2)
        
        self.txtInfo1 = Text(info_frame, height=2, width=50, font=('Arial', 9), wrap=WORD)
        self.txtInfo1.pack(pady=2)
        
        self.txtInfo2 = Text(info_frame, height=2, width=50, font=('Arial', 9), wrap=WORD)
        self.txtInfo2.pack(pady=2)
        
        self.txtInfo3 = Text(info_frame, height=2, width=50, font=('Arial', 9), wrap=WORD)
        self.txtInfo3.pack(pady=2)
        
        # Buttons Frame
        button_frame = Frame(parent, bg='#34495e')
        button_frame.pack(fill=X, padx=10, pady=10)
        
        self.btnTotal = Button(button_frame, text="Calculate Total", font=('Arial', 14, 'bold'), 
                              bg='#27ae60', fg='white', padx=20, pady=10, command=self.calculate_total)
        self.btnTotal.pack(side=LEFT, padx=5)
        
        self.btnSave = Button(button_frame, text="Save Rental", font=('Arial', 14, 'bold'), 
                             bg='#3498db', fg='white', padx=20, pady=10, command=self.save_rental)
        self.btnSave.pack(side=LEFT, padx=5)
        
        self.btnReset = Button(button_frame, text="Reset", font=('Arial', 14, 'bold'), 
                              bg='#f39c12', fg='white', padx=20, pady=10, command=self.reset_form)
        self.btnReset.pack(side=LEFT, padx=5)
        
        self.btnExit = Button(button_frame, text="Exit", font=('Arial', 14, 'bold'), 
                             bg='#e74c3c', fg='white', padx=20, pady=10, command=self.exit_app)
        self.btnExit.pack(side=RIGHT, padx=5)
    
    def setup_right_frame(self, parent):
        """Setup right frame with account info and receipt"""
        # Account Info Frame
        account_frame = ttk.LabelFrame(parent, text="Account Information", padding=10)
        account_frame.pack(fill=X, padx=10, pady=5)
        
        Label(account_frame, text="Account Opened:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=W, padx=5)
        self.cboAcctOpen = ttk.Combobox(account_frame, textvariable=self.AcctOpen, state='readonly',
                                       font=('Arial', 12), width=20)
        self.cboAcctOpen['values'] = ('Select an option', 'Yes', 'No')
        self.cboAcctOpen.current(0)
        self.cboAcctOpen.grid(row=0, column=1, padx=5, pady=2)
        
        Label(account_frame, text="Next Credit Review:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=W, padx=5)
        Entry(account_frame, textvariable=self.NextCreditReview, font=('Arial', 12), width=23, state='readonly').grid(row=1, column=1, padx=5, pady=2)
        
        Label(account_frame, text="Last Credit Review:", font=('Arial', 12, 'bold')).grid(row=2, column=0, sticky=W, padx=5)
        Entry(account_frame, textvariable=self.LastCreditReview, font=('Arial', 12), width=23, state='readonly').grid(row=2, column=1, padx=5, pady=2)
        
        Label(account_frame, text="Date Review:", font=('Arial', 12, 'bold')).grid(row=3, column=0, sticky=W, padx=5)
        Entry(account_frame, textvariable=self.DateRev, font=('Arial', 12), width=23, state='readonly').grid(row=3, column=1, padx=5, pady=2)
        
        # Receipt Frame
        receipt_frame = ttk.LabelFrame(parent, text="Receipt", padding=10)
        receipt_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        self.txtReceipt = Text(receipt_frame, font=('Arial', 10), wrap=WORD)
        receipt_scroll = Scrollbar(receipt_frame, orient=VERTICAL, command=self.txtReceipt.yview)
        self.txtReceipt.configure(yscrollcommand=receipt_scroll.set)
        
        self.txtReceipt.pack(side=LEFT, fill=BOTH, expand=True)
        receipt_scroll.pack(side=RIGHT, fill=Y)
        
        # Total Frame
        total_frame = ttk.LabelFrame(parent, text="Billing Summary", padding=10)
        total_frame.pack(fill=X, padx=10, pady=5)
        
        Label(total_frame, text="Tax:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=W, padx=5)
        Entry(total_frame, textvariable=self.Tax, font=('Arial', 12), width=25, state='readonly').grid(row=0, column=1, padx=5, pady=2)
        
        Label(total_frame, text="Subtotal:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=W, padx=5)
        Entry(total_frame, textvariable=self.SubTotal, font=('Arial', 12), width=25, state='readonly').grid(row=1, column=1, padx=5, pady=2)
        
        Label(total_frame, text="Total:", font=('Arial', 12, 'bold')).grid(row=2, column=0, sticky=W, padx=5)
        Entry(total_frame, textvariable=self.Total, font=('Arial', 12), width=25, state='readonly').grid(row=2, column=1, padx=5, pady=2)
    
    def setup_history_tab(self):
        """Setup rental history tab"""
        history_frame = Frame(self.history_tab, bg='#2c3e50')
        history_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Search Frame
        search_frame = ttk.LabelFrame(history_frame, text="Search Rentals", padding=10)
        search_frame.pack(fill=X, pady=(0, 10))
        
        Label(search_frame, text="Search:", font=('Arial', 12, 'bold')).pack(side=LEFT, padx=5)
        self.search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=self.search_var, font=('Arial', 12), width=30)
        search_entry.pack(side=LEFT, padx=5)
        
        Button(search_frame, text="Search", font=('Arial', 12), bg='#3498db', fg='white',
               command=self.search_rentals).pack(side=LEFT, padx=5)
        
        Button(search_frame, text="Show All", font=('Arial', 12), bg='#27ae60', fg='white',
               command=self.load_all_rentals).pack(side=LEFT, padx=5)
        
        Button(search_frame, text="Export to PDF", font=('Arial', 12), bg='#e74c3c', fg='white',
               command=self.export_to_pdf).pack(side=RIGHT, padx=5)
        
        # Treeview for displaying rental history
        tree_frame = Frame(history_frame, bg='#2c3e50')
        tree_frame.pack(fill=BOTH, expand=True)
        
        self.history_tree = ttk.Treeview(tree_frame, columns=('ID', 'Receipt', 'Product', 'Days', 'Total', 'Date'), show='headings')
        self.history_tree.heading('ID', text='ID')
        self.history_tree.heading('Receipt', text='Receipt Ref')
        self.history_tree.heading('Product', text='Product Type')
        self.history_tree.heading('Days', text='No. Days')
        self.history_tree.heading('Total', text='Total')
        self.history_tree.heading('Date', text='Date')
        
        # Configure column widths
        self.history_tree.column('ID', width=50)
        self.history_tree.column('Receipt', width=150)
        self.history_tree.column('Product', width=100)
        self.history_tree.column('Days', width=80)
        self.history_tree.column('Total', width=100)
        self.history_tree.column('Date', width=150)
        
        history_scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scroll.set)
        
        self.history_tree.pack(side=LEFT, fill=BOTH, expand=True)
        history_scroll.pack(side=RIGHT, fill=Y)
        
        # Load initial data
        self.load_all_rentals()
    
    def setup_analytics_tab(self):
        """Setup analytics tab with charts"""
        analytics_frame = Frame(self.analytics_tab, bg='#2c3e50')
        analytics_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), facecolor='#2c3e50')
        self.canvas = FigureCanvasTkAgg(self.fig, analytics_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
        # Button frame for analytics
        button_frame = Frame(analytics_frame, bg='#2c3e50')
        button_frame.pack(fill=X, pady=10)
        
        Button(button_frame, text="Product Distribution", font=('Arial', 12), bg='#3498db', fg='white',
               command=self.show_product_distribution).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Monthly Revenue", font=('Arial', 12), bg='#27ae60', fg='white',
               command=self.show_monthly_revenue).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Customer Statistics", font=('Arial', 12), bg='#f39c12', fg='white',
               command=self.show_customer_stats).pack(side=LEFT, padx=5)
        
        # Initialize with product distribution chart
        self.show_product_distribution()
    
    def setup_customer_tab(self):
        outer = ttk.LabelFrame(self.customer_tab, text="Customer Management", style="Card.TLabelframe", padding=10)
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
        for row in self.db_manager.get_customers():
            self.customer_tree.insert("", "end", values=row)
    
    def on_customer_select(self, _event=None):
        sel = self.customer_tree.selection()
        if not sel:
            self.customer_id_edit = None
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
        self.db_manager.add_customer(
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
        self.db_manager.update_customer(
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
        self.db_manager.delete_customer(self.customer_id_edit)
        messagebox.showinfo("Success", "Customer deleted.")
        self.clear_customer_form()
        self.load_customers_table()
    
    # Event handlers and methods for original functionality
    def product_selected(self, event):
        """Handle product type selection"""
        values = str(self.cboProdType.get())
        if values == "Car":
            self.ProdCode.set("CAR452")
            self.CostPDay.set("£12")
            self.CreCheck.set("No")
            self.SettDueDay.set("12")
            self.PaymentD.set("No")
            self.Deposit.set("No")
            self.PaymentM.set("Cash")
        elif values == "Van":
            self.ProdCode.set("VAN775")
            self.CostPDay.set("£19")
            self.CreCheck.set("No")
            self.SettDueDay.set("19")
            self.PaymentD.set("No")
            self.Deposit.set("No")
            self.PaymentM.set("Cash")
        elif values == "Minibus":
            self.ProdCode.set("MIN334")
            self.CostPDay.set("£12")
            self.CreCheck.set("No")
            self.SettDueDay.set("12")
            self.PaymentD.set("No")
            self.Deposit.set("No")
            self.PaymentM.set("Cash")
        elif values == "Truck":
            self.ProdCode.set("TRK7483")
            self.CostPDay.set("£15")
            self.CreCheck.set("No")
            self.SettDueDay.set("15")
            self.PaymentD.set("No")
            self.Deposit.set("No")
            self.PaymentM.set("Cash")
        
        # Calculate price if days are selected
        if self.LastCreditReview.get() and self.SettDueDay.get():
            try:
                n = float(self.LastCreditReview.get())
                s = float(self.SettDueDay.get())
                price = n * s
                TC = "£" + str('%.2f' % price)
                self.PayDueDay.set(TC)
            except ValueError:
                pass
    
    def days_selected(self, event):
        """Handle number of days selection"""
        values = str(self.cboNoDays.get())
        
        if values == "1-30":
            d1 = datetime.date.today()
            d2 = datetime.timedelta(days=30)
            d3 = d1 + d2
            self.AppDate.set(str(d1))
            self.NextCreditReview.set(str(d3))
            self.LastCreditReview.set("30")
            self.DateRev.set(str(d3))
            self.CreLimit.set("£150")
            self.Discount.set("5%")
            self.AcctOpen.set("Yes")
        elif values == "31-90":
            d1 = datetime.date.today()
            d2 = datetime.timedelta(days=90)
            d3 = d1 + d2
            self.AppDate.set(str(d1))
            self.NextCreditReview.set(str(d3))
            self.LastCreditReview.set("90")
            self.DateRev.set(str(d3))
            self.CreLimit.set("£200")
            self.Discount.set("10%")
            self.AcctOpen.set("Yes")
        elif values == "91-270":
            d1 = datetime.date.today()
            d2 = datetime.timedelta(days=270)
            d3 = d1 + d2
            self.AppDate.set(str(d1))
            self.NextCreditReview.set(str(d3))
            self.LastCreditReview.set("270")
            self.DateRev.set(str(d3))
            self.CreLimit.set("£250")
            self.Discount.set("15%")
            self.AcctOpen.set("Yes")
        elif values == "271-365":
            d1 = datetime.date.today()
            d2 = datetime.timedelta(days=365)
            d3 = d1 + d2
            self.AppDate.set(str(d1))
            self.NextCreditReview.set(str(d3))
            self.LastCreditReview.set("365")
            self.DateRev.set(str(d3))
            self.CreLimit.set("£300")
            self.Discount.set("20%")
            self.AcctOpen.set("Yes")
        elif values == "0":
            messagebox.showinfo("Zero Selected", "You chose zero")
            self.reset_form()
    
    def check_credit(self):
        """Handle check credit checkbox"""
        if self.var1.get() == 1:
            self.txtInfo0.delete("1.0", END)
            self.txtInfo0.insert(END, "Customer's Check Credit Approved")
        else:
            self.txtInfo0.delete("1.0", END)
    
    def term_agreed(self):
        """Handle term agreed checkbox"""
        if self.var2.get() == 1:
            self.txtInfo1.delete("1.0", END)
            self.txtInfo1.insert(END, "Term Agreed")
        else:
            self.txtInfo1.delete("1.0", END)
    
    def account_on_hold(self):
        """Handle account on hold checkbox"""
        if self.var3.get() == 1:
            self.txtInfo2.delete("1.0", END)
            self.txtInfo2.insert(END, "Customer's Account On Hold")
        else:
            self.txtInfo2.delete("1.0", END)
    
    def restricted_mails(self):
        """Handle restricted mails checkbox"""
        if self.var4.get() == 1:
            self.txtInfo3.delete("1.0", END)
            self.txtInfo3.insert(END, "Restricted Mails for Customer")
        else:
            self.txtInfo3.delete("1.0", END)
    
    def calculate_total(self):
        """Calculate total cost and generate receipt"""
        try:
            if not self.LastCreditReview.get() or not self.SettDueDay.get():
                messagebox.showerror("Error", "Please select product type and number of days")
                return
            
            n = float(self.LastCreditReview.get())
            s = float(self.SettDueDay.get())
            price = n * s
            
            # Apply discount
            discount_str = self.Discount.get().replace('%', '')
            if discount_str and discount_str != 'Select':
                discount_rate = float(discount_str) / 100
                price = price * (1 - discount_rate)
            
            ST = "£" + str('%.2f' % price)
            iTax = "£" + str('%.2f' % (price * 0.15))
            self.Tax.set(iTax)
            self.SubTotal.set(ST)
            TC = "£" + str('%.2f' % ((price * 0.15) + price))
            self.Total.set(TC)
            
            # Generate receipt
            self.txtReceipt.delete("1.0", END)
            x = random.randint(10908, 500876)
            randomRef = str(x)
            self.Receipt_Ref.set("BILL" + randomRef)
            
            self.txtReceipt.insert(END, 'Receipt Ref:\t\t' + self.Receipt_Ref.get() + '\t\t' + str(self.AppDate.get()) + "\n")
            self.txtReceipt.insert(END, 'Product Type:\t\t' + self.ProdType.get() + "\n")
            self.txtReceipt.insert(END, 'Product Code:\t\t' + self.ProdCode.get() + "\n")
            self.txtReceipt.insert(END, 'No of Days:\t\t' + self.NoDays.get() + "\n")
            self.txtReceipt.insert(END, 'Account Open:\t\t' + self.AcctOpen.get() + "\n")
            self.txtReceipt.insert(END, 'Next Credit Review:\t' + str(self.NextCreditReview.get()) + "\n")
            self.txtReceipt.insert(END, 'Last Credit Review:\t' + str(self.LastCreditReview.get()) + "\n")
            self.txtReceipt.insert(END, 'Discount:\t\t' + self.Discount.get() + "\n")
            self.txtReceipt.insert(END, '\nTax:\t\t\t' + self.Tax.get() + "\n")
            self.txtReceipt.insert(END, 'SubTotal:\t\t' + str(self.SubTotal.get()) + "\n")
            self.txtReceipt.insert(END, 'Total Cost:\t\t' + str(self.Total.get()) + "\n")
            self.txtReceipt.insert(END, '\n' + '='*50 + '\n')
            self.txtReceipt.insert(END, 'Thank you for your business!')
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values")
    
    def save_rental(self):
        """Save rental to database"""
        try:
            if not self.Total.get() or self.Total.get() == "":
                messagebox.showerror("Error", "Please calculate total first")
                return
            
            # Prepare rental data
            rental_data = (
                1,  # customer_id (default for now)
                self.Receipt_Ref.get(),
                self.ProdType.get(),
                self.ProdCode.get(),
                self.NoDays.get(),
                float(self.CostPDay.get().replace('£', '')) if self.CostPDay.get() else 0,
                self.AcctOpen.get(),
                self.AppDate.get(),
                self.NextCreditReview.get(),
                int(self.LastCreditReview.get()) if self.LastCreditReview.get() else 0,
                self.DateRev.get(),
                self.CreLimit.get(),
                self.CreCheck.get(),
                int(self.SettDueDay.get()) if self.SettDueDay.get() else 0,
                self.PaymentD.get(),
                float(self.Discount.get().replace('%', '')) if self.Discount.get() and self.Discount.get() != 'Select' else 0,
                self.Deposit.get(),
                self.PayDueDay.get(),
                self.PaymentM.get(),
                self.var1.get(),
                self.var2.get(),
                self.var3.get(),
                self.var4.get(),
                float(self.Tax.get().replace('£', '')) if self.Tax.get() else 0,
                float(self.SubTotal.get().replace('£', '')) if self.SubTotal.get() else 0,
                float(self.Total.get().replace('£', '')) if self.Total.get() else 0
            )
            
            self.db_manager.save_rental(rental_data)
            messagebox.showinfo("Success", "Rental saved successfully!")
            self.reset_form()
            self.load_all_rentals()  # Refresh history
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save rental: {str(e)}")
    
    def reset_form(self):
        """Reset all form fields"""
        # Clear text widgets
        self.txtInfo0.delete("1.0", END)
        self.txtInfo1.delete("1.0", END)
        self.txtInfo2.delete("1.0", END)
        self.txtInfo3.delete("1.0", END)
        self.txtReceipt.delete("1.0", END)
        
        # Reset variables
        self.AcctOpen.set("")
        self.AppDate.set("")
        self.NextCreditReview.set("")
        self.LastCreditReview.set("")
        self.DateRev.set("")
        self.ProdCode.set("")
        self.ProdType.set("")
        self.NoDays.set("")
        self.CostPDay.set("")
        self.CreLimit.set("")
        self.CreCheck.set("")
        self.SettDueDay.set("")
        self.PaymentD.set("")
        self.Discount.set("")
        self.Deposit.set("")
        self.PayDueDay.set("")
        self.PaymentM.set("")
        self.var1.set(0)
        self.var2.set(0)
        self.var3.set(0)
        self.var4.set(0)
        self.Tax.set("")
        self.SubTotal.set("")
        self.Total.set("")
        self.Receipt_Ref.set("")
        
        # Reset comboboxes
        self.cboProdType.current(0)
        self.cboNoDays.current(0)
        self.cboAcctOpen.current(0)
        self.cboCreLimit.current(0)
        self.cboCreCheck.current(0)
        self.cboPaymentD.current(0)
        self.cboDiscount.current(0)
        self.cboDeposit.current(0)
        self.cboPaymentM.current(0)
    
    def exit_app(self):
        """Exit application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
    
    # Database and analytics methods
    def load_all_rentals(self):
        """Load all rentals into history tree"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        rentals = self.db_manager.get_all_rentals()
        for rental in rentals:
            self.history_tree.insert('', 'end', values=(
                rental[0],  # rental_id
                rental[2],  # receipt_ref
                rental[3],  # product_type
                rental[5],  # no_days
                f"£{rental[25]:.2f}",  # total
                rental[26]  # created_date
            ))
    
    def search_rentals(self):
        """Search rentals"""
        search_term = self.search_var.get()
        if not search_term:
            self.load_all_rentals()
            return
        
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        rentals = self.db_manager.search_rentals(search_term)
        for rental in rentals:
            self.history_tree.insert('', 'end', values=(
                rental[0],  # rental_id
                rental[2],  # receipt_ref
                rental[3],  # product_type
                rental[5],  # no_days
                f"£{rental[25]:.2f}",  # total
                rental[26]  # created_date
            ))
    
    def export_to_pdf(self):
        """Export rental history to PDF"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Rental History"
            )
            
            if filename:
                c = canvas.Canvas(filename, pagesize=letter)
                width, height = letter
                
                # Title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height - 50, "Rental History Report")
                c.drawString(50, height - 70, f"Generated on: {datetime.date.today()}")
                
                # Headers
                c.setFont("Helvetica-Bold", 12)
                y_position = height - 120
                c.drawString(50, y_position, "Receipt Ref")
                c.drawString(150, y_position, "Product")
                c.drawString(250, y_position, "Days")
                c.drawString(350, y_position, "Total")
                c.drawString(450, y_position, "Date")
                
                # Data
                c.setFont("Helvetica", 10)
                rentals = self.db_manager.get_all_rentals()
                y_position -= 20
                
                for rental in rentals:
                    if y_position < 50:  # Start new page
                        c.showPage()
                        y_position = height - 50
                    
                    c.drawString(50, y_position, str(rental[2]))  # receipt_ref
                    c.drawString(150, y_position, str(rental[3]))  # product_type
                    c.drawString(250, y_position, str(rental[5]))  # no_days
                    c.drawString(350, y_position, f"£{rental[25]:.2f}")  # total
                    c.drawString(450, y_position, str(rental[26])[:10])  # date
                    y_position -= 15
                
                c.save()
                messagebox.showinfo("Success", f"Report exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
    
    def show_product_distribution(self):
        """Show product distribution chart"""
        try:
            self.fig.clear()
            
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT product_type, COUNT(*) as count, SUM(total) as revenue
                FROM rentals 
                GROUP BY product_type
            ''')
            data = cursor.fetchall()
            conn.close()
            
            if data:
                products = [row[0] for row in data]
                counts = [row[1] for row in data]
                revenues = [row[2] for row in data]
                
                # Create subplots
                ax1 = self.fig.add_subplot(221)
                ax2 = self.fig.add_subplot(222)
                ax3 = self.fig.add_subplot(212)
                
                # Pie chart for distribution
                ax1.pie(counts, labels=products, autopct='%1.1f%%', startangle=90)
                ax1.set_title('Product Distribution by Count', color='white')
                
                # Bar chart for revenue
                ax2.bar(products, revenues, color=['#3498db', '#e74c3c', '#27ae60', '#f39c12'])
                ax2.set_title('Revenue by Product Type', color='white')
                ax2.set_ylabel('Revenue (£)', color='white')
                
                # Line chart for trend (last 30 days)
                cursor = conn = sqlite3.connect(self.db_manager.db_name)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DATE(created_date) as date, COUNT(*) as count
                    FROM rentals 
                    WHERE created_date >= date('now', '-30 days')
                    GROUP BY DATE(created_date)
                    ORDER BY date
                ''')
                trend_data = cursor.fetchall()
                conn.close()
                
                if trend_data:
                    dates = [row[0] for row in trend_data]
                    daily_counts = [row[1] for row in trend_data]
                    ax3.plot(dates, daily_counts, marker='o', color='#3498db')
                    ax3.set_title('Daily Rentals (Last 30 Days)', color='white')
                    ax3.set_ylabel('Number of Rentals', color='white')
                    ax3.tick_params(axis='x', rotation=45)
            
            # Style the figure
            self.fig.patch.set_facecolor('#2c3e50')
            for ax in self.fig.get_axes():
                ax.set_facecolor('#34495e')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")
    
    def show_monthly_revenue(self):
        """Show monthly revenue chart"""
        try:
            self.fig.clear()
            
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT strftime('%Y-%m', created_date) as month, 
                       SUM(total) as revenue, COUNT(*) as count
                FROM rentals 
                GROUP BY strftime('%Y-%m', created_date)
                ORDER BY month
            ''')
            data = cursor.fetchall()
            conn.close()
            
            if data:
                months = [row[0] for row in data]
                revenues = [row[1] for row in data]
                counts = [row[2] for row in data]
                
                ax1 = self.fig.add_subplot(211)
                ax2 = self.fig.add_subplot(212)
                
                # Revenue chart
                ax1.bar(months, revenues, color='#27ae60')
                ax1.set_title('Monthly Revenue', color='white')
                ax1.set_ylabel('Revenue (£)', color='white')
                
                # Count chart
                ax2.bar(months, counts, color='#3498db')
                ax2.set_title('Monthly Rental Count', color='white')
                ax2.set_ylabel('Number of Rentals', color='white')
            
            # Style the figure
            self.fig.patch.set_facecolor('#2c3e50')
            for ax in self.fig.get_axes():
                ax.set_facecolor('#34495e')
                ax.tick_params(colors='white', axis='x', rotation=45)
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")
    
    def show_customer_stats(self):
        """Show customer statistics"""
        try:
            self.fig.clear()
            
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            
            # Get statistics
            cursor.execute('SELECT COUNT(*) FROM rentals')
            total_rentals = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(total) FROM rentals')
            total_revenue = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT AVG(total) FROM rentals')
            avg_rental = cursor.fetchone()[0] or 0
            
            # Payment method distribution
            cursor.execute('''
                SELECT payment_method, COUNT(*) as count
                FROM rentals 
                WHERE payment_method != 'Select'
                GROUP BY payment_method
            ''')
            payment_data = cursor.fetchall()
            
            conn.close()
            
            # Create text summary
            ax = self.fig.add_subplot(111)
            ax.axis('off')
            
            stats_text = f"""
            CUSTOMER STATISTICS SUMMARY
            
            Total Rentals: {total_rentals}
            Total Revenue: £{total_revenue:.2f}
            Average Rental Value: £{avg_rental:.2f}
            
            PAYMENT METHOD DISTRIBUTION:
            """
            
            if payment_data:
                for method, count in payment_data:
                    percentage = (count / total_rentals) * 100 if total_rentals > 0 else 0
                    stats_text += f"\n{method}: {count} ({percentage:.1f}%)"
            
            ax.text(0.1, 0.9, stats_text, transform=ax.transAxes, 
                   fontsize=14, verticalalignment='top', color='white',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='#34495e', alpha=0.8))
            
            # Style the figure
            self.fig.patch.set_facecolor('#2c3e50')
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate statistics: {str(e)}")
    
    def add_customer(self):
        """Add new customer"""
        try:
            if not self.customer_name.get():
                messagebox.showerror("Error", "Customer name is required")
                return
            
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customers (customer_name, phone, email, address)
                VALUES (?, ?, ?, ?)
            ''', (
                self.customer_name.get(),
                self.customer_phone.get(),
                self.customer_email.get(),
                self.customer_address.get()
            ))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Customer added successfully!")
            self.clear_customer_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
    
    def clear_customer_form(self):
        """Clear customer form"""
        self.customer_name.set("")
        self.customer_phone.set("")
        self.customer_email.set("")
        self.customer_address.set("")
    
    def update_customer(self):
        if not hasattr(self, 'customer_id') or not self.customer_id:
            messagebox.showerror("Error", "Select a customer first")
            return
        # Validate email
        email = self.customer_email.get()
        if email and ("@" not in email or "." not in email):
            messagebox.showerror("Error", "Enter a valid email address")
            return
        # Validate phone (simple check: must be digits and at least 7 chars)
        phone = self.customer_phone.get()
        if phone and (not phone.isdigit() or len(phone) < 7):
            messagebox.showerror("Error", "Enter a valid phone number")
            return
        # Check if any changes were made
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT customer_name, phone, email, address FROM customers WHERE customer_id=?", (self.customer_id,))
        old = cursor.fetchone()
        new = (self.customer_name.get(), self.customer_phone.get(), self.customer_email.get(), self.customer_address.get())
        if old == new:
            conn.close()
            messagebox.showinfo("Info", "No changes to update.")
            return
        cursor.execute("UPDATE customers SET customer_name=?, phone=?, email=?, address=? WHERE customer_id=?",
                       (self.customer_name.get(), self.customer_phone.get(),
                        self.customer_email.get(), self.customer_address.get(), self.customer_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer updated")
        self.clear_customer_form()
        self.load_all_customers()
    
    def setup_customer_tab(self):
        outer = ttk.LabelFrame(self.customer_tab, text="Customer Management", style="Card.TLabelframe", padding=10)
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
        for row in self.db_manager.get_customers():
            self.customer_tree.insert("", "end", values=row)

    def on_customer_select(self, _event=None):
        sel = self.customer_tree.selection()
        if not sel:
            self.customer_id_edit = None
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
        self.db_manager.add_customer(
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
        self.db_manager.update_customer(
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
        self.db_manager.delete_customer(self.customer_id_edit)
        messagebox.showinfo("Success", "Customer deleted.")
        self.clear_customer_form()
        self.load_customers_table()

if __name__ == '__main__':
    root = tk.Tk()
    app = AdvancedRentalInventory(root)
    root.mainloop()