import pandas as pd


def analyze_excel(workbook, top_n, transaction_types,
                  date_col, status_col, type_col,
                  sender_col, sender_name_col,
                  receiver_col, receiver_name_col,
                  fee_col, amount_col, balance_col, currency_col):

    analysis = {}
    selected_types = set(transaction_types.split(
        ",")) if transaction_types != "All" else None

    for sheet_name, df in workbook.items():
        required_columns = [date_col, type_col,
                            sender_col, receiver_col, amount_col]
        missing_columns = [
            col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {"error": f"Missing columns: {', '.join(missing_columns)} in sheet {sheet_name}"}

        # Convert data types
        df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

        # Remove NaN rows
        df = df.dropna(subset=[amount_col, date_col])

        # Filter transaction types
        if selected_types:
            df = df[df[type_col].isin(selected_types)]

        # Top Senders
        top_senders = df.groupby(sender_col).agg(
            total_sent=(amount_col, "sum"),
            transactions=(date_col, list)
        ).nlargest(top_n, "total_sent").reset_index()

        # Top Receivers
        top_receivers = df.groupby(receiver_col).agg(
            total_received=(amount_col, "sum"),
            transactions=(date_col, list)
        ).nlargest(top_n, "total_received").reset_index()

        analysis[sheet_name] = {
            "top_senders": top_senders.to_dict(orient="records"),
            "top_receivers": top_receivers.to_dict(orient="records")
        }

    return analysis
