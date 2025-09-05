# Advanced Rental Inventory Management System (Tkinter + SQLite)

**Demo / GUI App** — A single‑file Tkinter application for managing rental inventory, billing, and customer records. Uses an SQLite database. Tabs include: **New Rental**, **Rental History**, **Analytics**, **Customer Management**.

> ⚠️ `V1.1.py` is the latest version with improved UI, analytics refresh, PDF export (optional), and enhanced Customers CRUD.
> `V1.0.py` is the initial version with basic UI, charts, tkcalendar, and ReportLab integration.

---

## 🚀 Features

* **New Rental**: Select product type/code, date range, credit limit/status, payment details, discounts/deposits, optional checks (Check Credit, Term Agreed, On Hold, Restrict Mailing).
* **Auto Pricing**: Calculates **Subtotal/Tax/Total** (15% tax) based on date range and "Cost per day".
* **Receipt**: Text area with summary of rental and auto‑generated **Receipt Ref**.
* **Rental History**: Search/Show All, with **Export to PDF** (if ReportLab is installed).
* **Analytics**: Visualizations like product mix (Pie), revenue (Bar/Line) via Matplotlib.
* **Customer Management**: Full CRUD for customers (name, phone, email, address), table display, select to edit/update/delete.
* **SQLite DB**: Auto‑creates `rental_inventory.db` with seeded products (Car/Van/Minibus/Truck).

---

## 🛠️ Requirements

* Python 3.8+
* Built‑in: `tkinter`, `sqlite3`, `random`, `datetime`
* Third‑party:

  * `matplotlib`
  * `reportlab` *(optional – PDF export)*
  * `pandas` *(used in V1.0)*
  * `tkcalendar` *(used in V1.0)*

### Installation

```bash
# Windows/macOS/Linux
python -m pip install matplotlib reportlab pandas tkcalendar
```

> If you don’t need PDF export, `reportlab` is optional.

---

## 📦 Project Structure

```
project/
├── V1.1.py     # Latest GUI + Analytics + optional PDF export
├── V1.0.py     # Initial version (tkcalendar/Charts)
└── rental_inventory.db  # Auto‑created on first run
```

---

## ▶️ Run

```bash
# Run latest version
python V1.1.py

# Or run the initial version
python V1.0.py
```

On first run, `rental_inventory.db` is created and seeded with sample products (CAR452, VAN775, MIN334, TRK7483).

---

## 🗃️ Database (SQLite) — Quick Overview

**customers**

* `customer_id` (PK), `customer_name`, `phone`, `email`, `address`, `created_date`

**products**

* `product_id` (PK), `product_type`, `product_code` (Unique), `cost_per_day`, `available_quantity`, `status`

**rentals** *(Field names/count may vary slightly between V1.0 and V1.1)*

* Core: `receipt_ref`, `product_type`, `product_code`, `no_days` (values/range), `cost_per_day`, `credit_limit/check`, `payment_due/method`, `discount`, `deposit`, `tax`, `subtotal`, `total`, `created_date` ...

> **Note**: V1.1 rentals include extra fields for UI checks/account info (e.g., `check_credit`, `term_agreed`, `account_on_hold`, `restrict_mailing`, credit review dates).

---

## 🧭 Usage — High‑Level Flow

1. In **New Rental** tab → Select product type → Code/Cost auto‑fills → Choose date range.
2. Fill in credit/payment details (Discount, Deposit, Payment Method, etc.).
3. **Calculate Total** → Preview receipt → **Save Rental** to DB.
4. **Rental History** tab → Search/Export to PDF.
5. **Analytics** tab → Click Refresh (V1.1 has button).
6. **Customer Management** tab → Add/Update/Delete & select‑to‑edit.

---

## 📈 Analytics (Visualizations)

* **V1.1**: Single Matplotlib figure with subplots (Pie/Bar/Line) — product count & revenue, recent days trend.
* **V1.0**: Chart buttons (Product Distribution, Monthly Revenue, Customer Statistics) rendered via FigureCanvasTkAgg.

---

## 🧾 PDF Export

* **V1.1**: Uses ReportLab (if available). Export History → **PDF (A4/Letter depending on code)**.
* **V1.0**: Uses ReportLab `canvas` with `letter` page size.

> Without ReportLab, Export button may not function. Install: `pip install reportlab`.

---

## 🔁 Key Differences Between V1.0 and V1.1

* **UI & Style**: V1.1 uses modern ttk styles, 4‑tab layout, polished design.
* **DB Layer**: V1.1 has a dedicated `DB` class with product seed and cost lookup. V1.0 uses `DatabaseManager` class.
* **Calculations**: V1.1 applies `TAX_RATE = 0.15` and numeric day ranges. V1.0 multiplies days/settlement values + discount before tax/total.
* **Analytics**: V1.1 shows all charts in one figure with refresh. V1.0 uses multiple chart buttons.
* **Receipts**: Both auto‑generate references (`_new_receipt()` in V1.1, `BILLxxxxx` in V1.0).
* **Customers**: Both support CRUD. V1.1 adds row selection binding + reload helpers.

---

## 🧪 Troubleshooting

* **Tkinter not found**: On Linux, run `sudo apt install python3-tk`.
* **Matplotlib backend/TkAgg errors**: Ensure Tk is installed, and `pip install matplotlib`.
* **SQLite locked**: Avoid running multiple instances of the app with the same DB.
* **PDF export fails**: Check if ReportLab is installed (`pip show reportlab`).

---

## 🔒 License

Add a license of your choice (e.g., MIT/Apache‑2.0).

---

## 📷 Screenshots (Optional)

<img width="1366" height="768" alt="Screenshot (163)" src="https://github.com/user-attachments/assets/136ae047-2408-4100-a793-2650171b3284" />
<img width="1366" height="768" alt="Screenshot (162)" src="https://github.com/user-attachments/assets/3204245b-247f-49f6-b498-20e7ee6bbe00" />


---

## 🤝 Contributing

PRs are welcome — follow PEP8, use small commits, and write descriptive messages.


