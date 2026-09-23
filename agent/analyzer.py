import re


def analyze_chaos(text):

    text = text.strip()

    information = {
        "assignments": [],
        "presentations": [],
        "classes": []
    }


    # ==========================================
    # FIND ASSIGNMENTS
    # ==========================================

    assignment_pattern = re.compile(
        r"(?:I have|I also have|My)?\s*"
        r"([A-Za-z0-9 ]+assignment)"
        r".*?"
        r"(?:due|deadline)"
        r".*?"
        r"(\d{1,2})\s*(?:September|Sept)",
        re.IGNORECASE
    )

    assignment_matches = assignment_pattern.findall(text)

    for match in assignment_matches:

        title = match[0].strip()
        deadline = match[1]

        # Find estimated hours near this assignment
        start_position = text.lower().find(title.lower())

        nearby_text = text[
            start_position:start_position + 200
        ]

        hours_match = re.search(
            r"(\d+)\s*hours?",
            nearby_text,
            re.IGNORECASE
        )

        if hours_match:
            hours = int(hours_match.group(1))
        else:
            hours = 1

        information["assignments"].append({
            "title": title,
            "deadline": deadline,
            "hours": hours
        })


    # ==========================================
    # FIND PRESENTATIONS
    # ==========================================

    presentation_pattern = re.compile(
        r"(?:I have|I also have|My)?\s*"
        r"([A-Za-z0-9 ]+presentation)"
        r".*?"
        r"(?:on|due)"
        r".*?"
        r"(\d{1,2})\s*(?:September|Sept)",
        re.IGNORECASE
    )

    presentation_matches = presentation_pattern.findall(text)

    for match in presentation_matches:

        topic = match[0].strip()
        date = match[1]

        start_position = text.lower().find(topic.lower())

        nearby_text = text[
            start_position:start_position + 200
        ]

        hours_match = re.search(
            r"(\d+)\s*hours?",
            nearby_text,
            re.IGNORECASE
        )

        if hours_match:
            hours = int(hours_match.group(1))
        else:
            hours = 1

        information["presentations"].append({
            "topic": topic,
            "date": date,
            "hours": hours
        })


    # ==========================================
    # FIND CLASS TIMES
    # ==========================================

    class_pattern = re.compile(
        r"([A-Za-z ]+?)\s*class"
        r".*?"
        r"(\d{1,2})\s*"
        r"(?:AM|PM)"
        r"\s*(?:to|-)\s*"
        r"(\d{1,2})\s*"
        r"(AM|PM)",
        re.IGNORECASE
    )

    class_matches = class_pattern.findall(text)

    for match in class_matches:

        information["classes"].append({
            "subject": match[0].strip(),
            "start": match[1],
            "end": match[2],
            "period": match[3]
        })


    return information