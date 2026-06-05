import pandas as pd


def calculate_age(birthday, today):
    age = today.year - birthday.year
    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1
    return max(age, 0)


def project_sip(monthly_amount, years, annual_return, annual_step_up=0):
    monthly_rate = annual_return / 100 / 12
    step_up_rate = annual_step_up / 100
    months = int(years * 12)
    invested = 0
    value = 0
    rows = []

    for month in range(1, months + 1):
        current_year = (month - 1) // 12
        contribution = monthly_amount * ((1 + step_up_rate) ** current_year)
        value = (value + contribution) * (1 + monthly_rate)
        invested += contribution

        if month % 12 == 0:
            rows.append(
                {
                    "Year": month // 12,
                    "Invested": round(invested),
                    "Projected Value": round(value),
                    "Estimated Gains": round(value - invested),
                }
            )

    return value, invested, pd.DataFrame(rows)


def required_monthly_for_goal(goal_amount, years, annual_return):
    months = int(years * 12)
    if goal_amount <= 0 or months <= 0:
        return 0

    monthly_rate = annual_return / 100 / 12
    if monthly_rate == 0:
        return goal_amount / months

    factor = ((1 + monthly_rate) ** months - 1) / monthly_rate
    return goal_amount / (factor * (1 + monthly_rate))


def project_swp(corpus, monthly_withdrawal, years, annual_return, inflation=0):
    monthly_rate = annual_return / 100 / 12
    inflation_rate = inflation / 100
    months = int(years * 12)
    balance = corpus
    withdrawn = 0
    depleted_month = None
    rows = []

    for month in range(1, months + 1):
        current_year = (month - 1) // 12
        withdrawal = monthly_withdrawal * ((1 + inflation_rate) ** current_year)
        balance *= 1 + monthly_rate
        balance -= withdrawal
        withdrawn += withdrawal

        if balance <= 0 and depleted_month is None:
            depleted_month = month
            balance = 0

        if month % 12 == 0 or depleted_month == month:
            rows.append(
                {
                    "Year": round(month / 12, 2),
                    "Withdrawn": round(withdrawn),
                    "Remaining Corpus": round(balance),
                }
            )

        if depleted_month:
            break

    return balance, withdrawn, depleted_month, pd.DataFrame(rows)
