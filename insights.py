from database import get_reason_data, get_food_frequency


def get_insights():
    insights = []

    reasons = get_reason_data()
    foods = get_food_frequency()

    if not reasons and not foods:
        return [
            "🌱 Start adding food waste records to generate insights."
        ]

    # Reason-based suggestions
    for reason, count in reasons:

        if reason == "Excess preparation" and count >= 2:
            insights.append(
                "💡 Excess preparation is repeated. "
                "Try preparing smaller portions."
            )

        elif reason == "Leftover" and count >= 2:
            insights.append(
                "💡 Leftovers are occurring often. "
                "Try planning meals around leftover food."
            )

        elif reason == "Spoiled" and count >= 2:
            insights.append(
                "⚠ Spoiled food is being recorded repeatedly. "
                "Check storage and expiry dates."
            )

        elif reason == "Overcooked" and count >= 2:
            insights.append(
                "🍳 Overcooking is repeated. "
                "Try preparing smaller quantities."
            )

    # Repeated food detection
    for food, count, quantity in foods:

        if count >= 3:
            insights.append(
                f"⚠ Repeated waste detected: {food} "
                f"has been wasted {count} times."
            )

    if not insights:
        insights.append(
            "🌱 Good progress! No major repeated waste pattern detected."
        )

    return insights


def calculate_score():
    records = get_food_frequency()

    if not records:
        return 100

    total_quantity = sum(item[2] for item in records)

    # Simple project-level scoring system
    if total_quantity <= 2:
        score = 95
    elif total_quantity <= 5:
        score = 85
    elif total_quantity <= 10:
        score = 75
    elif total_quantity <= 20:
        score = 60
    else:
        score = 45

    return score