import pandas as pd
from app.services.analyzer import analyze_excel


def test_analyze_excel():
    data = {
        "Date": ['2023-01-01', '2023-01-02'],
        "Type": [" Payment", "Transfer"],
        "From": ["1234", "67890"],
        "To": ["67890", "12345"],
        "Amount": [500, 300]
    }

    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df['Date'])

    workbook = {"Sheet1": df}
    result = analyze_excel(workbook, top_n=5, transaction_types="All",
                           date_col="Date", status_col="Type", type_col="Type",
                           sender_col='From', sender_name_col="From",
                           receiver_col="To", receiver_name_col="To",
                           fee_col="From", amount_col="Amount", balance_col="Amount", currency_col="Amount"
                           )

    assert "Sheet1" in result
    assert len(result["Sheet1"]["top_senders"]) > 0
