import matplotlib.pyplot as plt

from database import get_category_data, get_reason_data


def show_category_chart():

    data = get_category_data()

    if not data:
        return

    categories = [item[0] for item in data]
    quantities = [item[1] for item in data]

    plt.figure(figsize=(8, 5))

    plt.bar(categories, quantities)

    plt.title("Food Waste by Category")
    plt.xlabel("Food Category")
    plt.ylabel("Quantity Wasted")

    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.show()


def show_reason_chart():

    data = get_reason_data()

    if not data:
        return

    reasons = [item[0] for item in data]
    counts = [item[1] for item in data]

    plt.figure(figsize=(8, 5))

    plt.pie(
        counts,
        labels=reasons,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Reasons for Food Waste")

    plt.tight_layout()
    plt.show()