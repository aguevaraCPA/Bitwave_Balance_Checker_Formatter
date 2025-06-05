import pandas as pd
import sys

def format_balance_checker(balance_checker_path, bitwave_report_path, output_path):
    # --- Step 1: Load Bitwave Balance Report and extract valid symbols ---
    balance_df = pd.read_csv(bitwave_report_path, dtype=str)
    valid_symbols = set(balance_df['ticker'].dropna().str.strip().str.upper().unique())

    # --- Step 2: Load and split Balance Checker lines ---
    with open(balance_checker_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    split_rows = [line.strip().split(",") for line in raw_lines]

    # --- Step 3: Reconstruct rows using the first valid asset symbol as pivot ---
    formatted_rows = []
    for row in split_rows[1:]:  # Skip header
        asset_index = next((i for i, val in enumerate(row) if val.strip().upper() in valid_symbols), -1)
        if asset_index > 0 and len(row) >= asset_index + 6:
            wallet_name = ",".join(row[:asset_index])
            asset_symbol = row[asset_index].strip().upper()
            rest = row[asset_index + 1:asset_index + 6]
            formatted_rows.append([wallet_name, asset_symbol] + rest)

    formatted_df = pd.DataFrame(formatted_rows, columns=[
        'wallet_name', 'asset_symbol', 'bitwave_balance_time', 'bitwave_balance',
        'thirdparty_balance', 'difference', 'thirdparty_balance_time'
    ])
    formatted_df.drop_duplicates(inplace=True)

    # --- Step 4: Clean and enrich Formatted Balance Checker ---
    formatted_df = formatted_df[formatted_df["wallet_name"].astype(str).str.strip() != ""]
    formatted_df["Wallet-Asset"] = formatted_df["wallet_name"].str.strip() + " - " + formatted_df["asset_symbol"].str.strip()
    balance_df["Wallet-Asset"] = balance_df["wallet"].str.strip() + " - " + balance_df["ticker"].str.strip()

    wallet_id_map = balance_df.set_index("Wallet-Asset")["walletId"].to_dict()
    balance_value_map = balance_df.set_index("Wallet-Asset")["value"].apply(pd.to_numeric, errors='coerce').to_dict()

    formatted_df["walletId"] = formatted_df["Wallet-Asset"].map(wallet_id_map)
    formatted_df["balance_report_balance"] = formatted_df["Wallet-Asset"].map(balance_value_map)
    formatted_df["thirdparty_balance"] = pd.to_numeric(formatted_df["thirdparty_balance"], errors='coerce')
    formatted_df["balance_report_var"] = formatted_df["thirdparty_balance"] - formatted_df["balance_report_balance"]

    # Add subsidiary from wallet name
    if "subsidiary" in balance_df.columns and "wallet" in balance_df.columns:
        subsidiary_map = balance_df.set_index(balance_df["wallet"].str.strip())["subsidiary"].to_dict()
        formatted_df["subsidiary"] = formatted_df["wallet_name"].str.strip().map(subsidiary_map)

    # --- Step 5: Prepare Original Balance Checker raw tab ---
    max_len = max(len(row) for row in split_rows)
    padded_rows = [row + [None] * (max_len - len(row)) for row in split_rows]
    raw_bc_df = pd.DataFrame(padded_rows)
    raw_bc_df.columns = [f"col_{i+1}" for i in range(raw_bc_df.shape[1])]

    # --- Step 6: Write to Excel ---
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        formatted_df.to_excel(writer, sheet_name="Formatted Balance Checker", index=False)
        raw_bc_df.to_excel(writer, sheet_name="Original Balance Checker", index=False, header=False)
        balance_df.to_excel(writer, sheet_name="Original Balance Report", index=False)

# Example usage:
# python format_balance_checker_final.py path/to/balance_checker.csv path/to/bitwave_report.csv path/to/output.xlsx
if __name__ == "__main__":
    bc_path = sys.argv[1]
    br_path = sys.argv[2]
    out_path = sys.argv[3]
    format_balance_checker(bc_path, br_path, out_path)
