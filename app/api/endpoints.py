from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
from collections import defaultdict
from app.utils.file_handler import save_uploaded_file
from datetime import datetime

router = APIRouter()


@router.post("/analyze/")
async def analyze_file(
    file: UploadFile = File(...),
    top_n: int = Form(5),
    transaction_types: str = Form("All"),
    date_column: str = Form("Date"),
    status_column: str = Form("Status"),
    type_column: str = Form("Type"),
    sender_column: str = Form("From"),
    sender_name_column: str = Form("From name"),
    receiver_column: str = Form("To"),
    receiver_name_column: str = Form("To name"),
    fee_column: str = Form("From / Fee"),
    amount_column: str = Form("Amount"),
    balance_column: str = Form("Balance"),
    currency_column: str = Form("Currency")
):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        file_path = save_uploaded_file(file)
        df_dict = pd.read_excel(file_path, sheet_name=None)

        if not df_dict:
            raise HTTPException(
                status_code=400, detail="Uploaded file is empty or unreadable")

        senders = defaultdict(lambda: {
                              "total_sent": 0, "transactions": 0, "currency": None, "name": "Unknown Sender"})
        receivers = defaultdict(lambda: {
                                "total_received": 0, "transactions": 0, "currency": None, "name": "Unknown Receiver"})

        for sheet_name, df in df_dict.items():
            if df.empty:
                continue

            print(f"Processing sheet: {sheet_name}")  # Debugging

            print(f"Available columns: {df.columns.tolist()}")  # Debugging

            required_columns = {date_column, status_column, type_column,
                                sender_column, receiver_column, amount_column, currency_column}
            if not required_columns.issubset(df.columns):
                continue

            if transaction_types != "All":
                df = df[df[type_column].isin(transaction_types.split(","))]

            for _, row in df.iterrows():
                sender = row.get(sender_column)
                sender_name = row.get(sender_name_column)
                receiver = row.get(receiver_column)
                receiver_name = row.get(receiver_name_column)
                amount = row.get(amount_column, 0)
                currency = row.get(currency_column, "Unknown")

                # Ensure sender and receiver names are not NaN
                if pd.isna(sender_name) or sender_name is None:
                    sender_name = sender  # Default to ID if name is missing

                if pd.isna(receiver_name) or receiver_name is None:
                    receiver_name = receiver  # Default to ID if name is missing

                if pd.notna(sender) and pd.notna(amount):
                    senders[sender]["total_sent"] += amount
                    senders[sender]["transactions"] += 1
                    senders[sender]["currency"] = currency
                    # Store sender name correctly
                    senders[sender]["name"] = sender_name

                if pd.notna(receiver) and pd.notna(amount):
                    receivers[receiver]["total_received"] += amount
                    receivers[receiver]["transactions"] += 1
                    receivers[receiver]["currency"] = currency
                    # Store receiver name correctly
                    receivers[receiver]["name"] = receiver_name

        sorted_senders = sorted(
            senders.items(), key=lambda x: x[1]["total_sent"], reverse=True)[:top_n]
        sorted_receivers = sorted(
            receivers.items(), key=lambda x: x[1]["total_received"], reverse=True)[:top_n]

        result = {
            "top_senders": [
                {"From": sender, "From Name": data["name"], "total_sent": data["total_sent"],
                 "transactions": data["transactions"], "currency": data["currency"]}
                for sender, data in sorted_senders
            ],
            "top_receivers": [
                {"To": receiver, "To Name": data["name"], "total_received": data["total_received"],
                 "transactions": data["transactions"], "currency": data["currency"]}
                for receiver, data in sorted_receivers
            ]
        }

        if not result["top_senders"] and not result["top_receivers"]:
            raise HTTPException(
                status_code=400, detail="No analysis results found")

        return {"analysis_result": result}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing file: {str(e)}")
