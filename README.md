# Tele-Budget Tracker

A modern, fully asynchronous Telegram Bot built with Python to track personal finances, visualize spending habits, and export professional reports.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![aiogram](https://img.shields.io/badge/aiogram-3.x-blueviolet)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-Async-red)
![Status](https://img.shields.io/badge/Status-Completed-success)

---

## 📺 Demo Preview

Click the link below to watch the bot in action:

### [▶️ Watch the Demo Video](https://drive.google.com/file/d/1s4y7uzBVnOjpfS1ly82_G_kn0-XYTeWd/view?usp=sharing)

*(Clicking the link above will open the full video demo)*

---

## Features

This bot goes beyond simple message handling by implementing complex data processing and file generation:

*   **Async Database Management:** Uses `SQLAlchemy` (Async) with SQLite for non-blocking database operations.
*   **Finite State Machine (FSM):** Guides users through multi-step conversations (e.g., Adding an expense -> Amount -> Category).
*   **Data Visualization:** Generates on-the-fly Pie Charts using `Matplotlib` to analyze spending categories.
*   **Dynamic PDF Receipts:** Uses `ReportLab` to draw pixel-perfect, thermal-printer style receipts.
*   **Excel Export:** Uses `Pandas` to generate downloadable `.xlsx` reports for external analysis.
*   **Interactive UI:** Utilizes Inline Keyboards and Callbacks for deleting items and navigation.

---

## Tech Stack

*   **Language:** Python 3.10+
*   **Framework:** [aiogram 3.x](https://docs.aiogram.dev/en/latest/) (Asynchronous)
*   **Database:** SQLAlchemy + aiosqlite
*   **Data Science:** Pandas, OpenPyXL
*   **Visualization:** Matplotlib
*   **PDF Generation:** ReportLab

---

## 📂 Project Structure

The project follows a modular architecture to ensure scalability:

```text
tele-budget-tracker/
├── bot.py                # Application Entry Point
├── .env                  # Environment Variables (Token)
├── requirements.txt      # Project Dependencies
├── data/
│   └── database.py       # DB Models & Connection Engine
├── handlers/
│   ├── common.py         # Start/Help logic
│   ├── expenses.py       # Add/Delete expense logic (FSM)
│   ├── statistics.py     # Chart generation
│   └── export.py         # PDF & Excel export logic
└── utils/
    ├── keyboards.py      # Reusable UI components
    └── pdf_generator.py  # Canvas drawing logic for receipts
```
## ⚡ Installation & Setup

Follow these steps to run the bot locally:

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/tele-budget-tracker.git
cd tele-budget-tracker
```
## 2. Set up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate
```
```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```
## 3. Install Dependencies
```bash
pip install -r requirements.txt
```
## 4. Configure Environment Variables
```bash
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u1234567
```
## 5. Run the Bot
```bash
python bot.py
```

## 📖 Usage Guide

1.  **Start:** Send `/start` to see the main menu.
2.  **Add Expense:** Click **💸 Add Expense**, enter the number, and pick a category.
3.  **View Stats:** Click **📊 Stats** to receive a generated pie chart.
4.  **Delete:** Click **🗑 Delete** to manage recent expenses via inline buttons.
5.  **Export:** Click **📥 Export** to download your data as a **PDF Receipt** or **Excel File**.

---

## 👨‍💻 Author

Built by **Tekleeyesus Munye** as part of a Python telegram bot Development Portfolio.

*   [GitHub Profile](https://github.com/tekle-eyesus)
*   [LinkedIn](https://www.linkedin.com/in/tekleeyesus-munye)
