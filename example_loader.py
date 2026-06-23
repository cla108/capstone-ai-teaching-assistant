import os


def load_human_examples(examples_dir="examples", max_examples=3):
    """
    Loads human-written lesson examples from the examples folder.

    These examples are used only as a style and structure guide.
    They are not used as factual textbook content.
    """

    examples = []

    if not os.path.exists(examples_dir):
        return ""

    files = sorted([
        file for file in os.listdir(examples_dir)
        if file.endswith(".txt")
    ])

    for file in files[:max_examples]:
        file_path = os.path.join(examples_dir, file)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if content:
            examples.append(
                f"""
HUMAN EXAMPLE: {file}

{content}
"""
            )

    return "\n\n".join(examples)
