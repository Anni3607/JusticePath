def classify_issue(user_text):

    text = user_text.lower()

    scores = {}

    for category, keywords in classification_rules.items():

        score = 0

        for keyword in keywords:

            if keyword in text:
                score += 1

        scores[category] = score

    best_category = max(
        scores,
        key=scores.get
    )

    if scores[best_category] == 0:
        return "Unknown"

    return best_category
