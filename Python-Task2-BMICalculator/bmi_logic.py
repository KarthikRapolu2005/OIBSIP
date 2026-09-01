"""
bmi_logic.py
------------
Core BMI calculation, classification, and input validation logic.
Kept independent of GUI/DB code so it can be unit tested in isolation.
"""


class ValidationError(Exception):
    """Raised when user-supplied input fails validation."""
    pass


# Reasonable real-world bounds to catch typos/nonsense input
MIN_WEIGHT_KG = 1.0
MAX_WEIGHT_KG = 500.0
MIN_HEIGHT_M = 0.3
MAX_HEIGHT_M = 3.0


def validate_username(username: str) -> str:
    """Ensure username is non-empty after trimming whitespace."""
    if username is None:
        raise ValidationError("Username cannot be empty.")
    cleaned = username.strip()
    if not cleaned:
        raise ValidationError("Username cannot be empty.")
    if len(cleaned) > 50:
        raise ValidationError("Username is too long (max 50 characters).")
    return cleaned


def _parse_positive_float(value: str, field_name: str) -> float:
    """Parse a string into a positive float, raising ValidationError on failure."""
    if value is None or str(value).strip() == "":
        raise ValidationError(f"{field_name} cannot be empty.")
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a valid number.")

    if parsed != parsed:  # NaN check
        raise ValidationError(f"{field_name} must be a valid number.")

    if parsed <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")

    return parsed


def validate_weight(weight_str: str) -> float:
    """Validate and parse weight in kg."""
    weight = _parse_positive_float(weight_str, "Weight")
    if weight < MIN_WEIGHT_KG or weight > MAX_WEIGHT_KG:
        raise ValidationError(
            f"Weight must be between {MIN_WEIGHT_KG} and {MAX_WEIGHT_KG} kg."
        )
    return weight


def validate_height(height_str: str) -> float:
    """Validate and parse height in meters."""
    height = _parse_positive_float(height_str, "Height")
    if height < MIN_HEIGHT_M or height > MAX_HEIGHT_M:
        raise ValidationError(
            f"Height must be between {MIN_HEIGHT_M} and {MAX_HEIGHT_M} meters."
        )
    return height


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculate BMI = weight (kg) / height (m)^2.
    Assumes inputs have already been validated as positive numbers.
    """
    if height_m <= 0:
        raise ValidationError("Height must be greater than zero.")
    if weight_kg <= 0:
        raise ValidationError("Weight must be greater than zero.")

    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def classify_bmi(bmi: float) -> str:
    """Classify a BMI value into a standard category."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


# Colour mapping used by the GUI for colour-coded feedback
CATEGORY_COLOURS = {
    "Underweight": "#3B82F6",  # blue
    "Normal": "#22C55E",       # green
    "Overweight": "#F59E0B",   # amber
    "Obese": "#EF4444",        # red
}


def get_category_colour(category: str) -> str:
    """Return a hex colour code for a given BMI category."""
    return CATEGORY_COLOURS.get(category, "#6B7280")  # grey fallback


def compute_full_result(username: str, weight_str: str, height_str: str) -> dict:
    """
    Full pipeline: validate inputs, compute BMI, classify it.
    Returns a dict ready to be persisted / displayed.
    Raises ValidationError with a user-friendly message on bad input.
    """
    clean_username = validate_username(username)
    weight = validate_weight(weight_str)
    height = validate_height(height_str)
    bmi = calculate_bmi(weight, height)
    category = classify_bmi(bmi)

    return {
        "username": clean_username,
        "weight": weight,
        "height": height,
        "bmi": bmi,
        "category": category,
        "colour": get_category_colour(category),
    }
