import pandas as pd


def basic_analysis(df, question):

    question_lower = question.lower()

    # Highest value question
    if "highest" in question_lower or "maximum" in question_lower:
        numeric_columns = df.select_dtypes(
            include="number"
        ).columns

        if len(numeric_columns) > 0:
            column = numeric_columns[0]

            row = df.loc[
                df[column].idxmax()
            ]

            return row.to_dict()


    # Average question
    if "average" in question_lower or "mean" in question_lower:
        numeric_columns = df.select_dtypes(
            include="number"
        ).columns

        if len(numeric_columns) > 0:
            column = numeric_columns[0]

            return {
                "average": float(
                    df[column].mean()
                )
            }


    # Row count
    if "how many" in question_lower or "count" in question_lower:
        return {
            "count": len(df)
        }


    return {
        "message": "Analysis requires more instructions"
    }
