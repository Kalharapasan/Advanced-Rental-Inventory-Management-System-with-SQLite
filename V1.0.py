from tkinter import *
import sqlite3
import tkinter as tk
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
        """Setup customer management tab"""
        customer_frame = Frame(self.customer_tab, bg='#2c3e50')
        customer_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Customer input frame
        input_frame = ttk.LabelFrame(customer_frame, text="Customer Information", padding=10)
        input_frame.pack(fill=X, pady=(0, 10))
        
        # Row 1
        Label(input_frame, text="Customer Name:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=W, padx=5)
        Entry(input_frame, textvariable=self.customer_name, font=('Arial', 12), width=25).grid(row=0, column=1, padx=5, pady=2)
        
        Label(input_frame, text="Phone:", font=('Arial', 12, 'bold')).grid(row=0, column=2, sticky=W, padx=5)
        Entry(input_frame, textvariable=self.customer_phone, font=('Arial', 12), width=25).grid(row=0, column=3, padx=5, pady=2)
        
        # Row 2
        Label(input_frame, text="Email:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=W, padx=5)
        Entry(input_frame, textvariable=self.customer_email, font=('Arial', 12), width=25).grid(row=1, column=1, padx=5, pady=2)
        
        Label(input_frame, text="Address:", font=('Arial', 12, 'bold')).grid(row=1, column=2, sticky=W, padx=5)
        Entry(input_frame, textvariable=self.customer_address, font=('Arial', 12), width=25).grid(row=1, column=3, padx=5, pady=2)
        
        # Buttons
        button_frame = Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        Button(button_frame, text="Add Customer", font=('Arial', 12), bg='#27ae60', fg='white',
               command=self.add_customer).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Clear", font=('Arial', 12), bg='#f39c12', fg='white',
               command=self.clear_customer_form).pack(side=LEFT, padx=5)