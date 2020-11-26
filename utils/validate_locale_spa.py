import re


def validate_label(label):
    """ Validate and normalize transcriptions. Returns a cleaned version of the label or None if it's invalid.  """
    if re.search(r"[0-9]", label) is not None:
        return None

    label = label.replace("-", " ")
    label = label.replace("–", " ")
    label = label.replace("—", " ")
    label = label.replace("_", " ")
    label = re.sub("[ ]{2,}", " ", label)
    label = label.replace(".", "")
    label = label.replace(",", "")
    label = label.replace(":", "")
    label = label.replace(";", "")
    label = label.replace("¿", "")
    label = label.replace("?", "")
    label = label.replace("¡", "")
    label = label.replace("!", "")
    label = label.replace("\"", "")
    label = label.replace("\'", "")
    label = label.replace("`", "")
    label = label.replace("´", "")
    label = label.replace("’", "")
    label = label.replace("“", "")
    label = label.replace("”", "")
    label = label.replace("(", "")
    label = label.replace(")", "")
    label = label.replace("<", "")
    label = label.replace(">", "")
    label = label.replace("[", "")
    label = label.replace("]", "")
    label = label.replace("{", "")
    label = label.replace("}", "")
    label = label.replace("&", "")
    label = label.replace("*", "")
    label = label.replace("%", "")
    label = label.replace("$", "")
    label = label.replace("@", "")
    label = label.replace("=", "")
    label = label.replace("#", "")
    label = label.replace("+", "")
    label = label.replace("^", "")
    label = label.replace("\\", "")
    label = label.replace("/", "")
    label = label.replace("|", "")
    label = label.replace("\t", "")
    label = label.replace("\x7f", "")
    label = label.strip()
    label = label.lower()

    return label if label else None
