# Balance Checker Reconciliation

This Python script reconciles a Balance Checker export with a Bitwave Balance Report and produces a structured Excel workbook for analysis.

## 🔧 Features

- Identifies asset symbols from Balance Checker rows.
- Joins enriched rows with Bitwave Balance Report by `walletId` and `value`.
- Calculates variances and adds `subsidiary` where applicable.
- Outputs a 3-sheet Excel file:
  - `Formatted Balance Checker`
  - `Original Balance Checker`
  - `Original Balance Report`

## 📂 Input Files

1. **Balance Checker CSV** — A raw export from a balance checking system.
2. **Bitwave Balance Report CSV** — A structured export from Bitwave.

## 📥 Installation

Make sure Python is installed. Then install the required libraries:

```bash
pip install pandas xlsxwriter
