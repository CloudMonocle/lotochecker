"""Lambda Fucntion to get latest Loto numbers and compare with stored numbers."""

import json
import os

import boto3
import pandas as pd

loto_df = pd.read_csv(
    "https://www.national-lottery.co.uk/LOTO_RESULTs/lotto/draw-history/csv"
)
CHECK_JSON = "loto_numers.json"


if os.path.exists(CHECK_JSON):
    with open(CHECK_JSON, "r", encoding="utf-8") as f:
        arrays = json.load(f)
else:
    arrays = []

first_row = loto_df.head(1)
json_output = first_row.to_json(orient="records")  # 'records' gives a list of dicts

for lotot in json.loads(json_output):
    SNS_MSG = "!!!---Loto Numbers---!!!\n"
    SNS_MSG += f"Draw Date: {lotot.get('DrawDate')}\n"
    # build a compact string of the six balls
    LOTO_NUMBERS = ", ".join(str(lotot.get(f"Ball {i}")) for i in range(1, 7))
    SNS_MSG += f"Lotto Numbers: {LOTO_NUMBERS}\n"
    SNS_MSG += f"BonusBall: {lotot.get('Bonus Ball')}"
    if len(arrays) > 0:
        SNS_MSG = SNS_MSG + "\n---Any Matching numbers---"
    for lotorow in arrays:
        LOTO_BC = 0
        LOTO_BB = False
        for i in range(1, 7):  # Loop from 1 to 6
            if lotot.get(f"Ball {i}") in lotorow:
                LOTO_BC += 1
        if lotot.get("Bonus Ball") in lotorow:
            LOTO_BB = True
        if LOTO_BC > 1:
            SNS_MSG += "\n"
            LOTO_RESULT = ", ".join(str(n) for n in lotorow)
            SNS_MSG += (
                f"Numbers: {LOTO_RESULT} Matched:{LOTO_BC}  Bonus Ball: {LOTO_BB}"
            )

# send sns
if os.environ.get("SNS_TOPIC_ARN", None) is None:
    print("No sns ARN found")
else:
    sns = boto3.client(
        "sns",
        region_name=os.environ.get("AWS_REGION", boto3.session.Session().region_name),
    )
    sns.publish(
        TopicArn=os.environ.get("SNS_TOPIC_ARN"),
        Subject="Loto LOTO_RESULTs",
        Message=SNS_MSG,
        MessageAttributes={
            "discord_channel": {"DataType": "String", "StringValue": "daily-stuff"},
        },
    )

print(SNS_MSG)
