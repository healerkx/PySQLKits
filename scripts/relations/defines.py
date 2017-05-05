
COLOR_RESET         = "\x1b[0m"
COLOR_RED           = "\x1b[31m"
COLOR_GREEN         = "\x1b[32m"
COLOR_YELLOW        = "\x1b[33m"
COLOR_BLUE          = "\x1b[34m"

COLOR_BOLD_WHITE    = "\x1b[1;37m"
COLOR_BOLD_RED      = "\x1b[1;31m"
COLOR_BOLD_GREEN    = "\x1b[1;32m"
COLOR_BOLD_YELLOW   = "\x1b[1;33m"
COLOR_BOLD_BLUE     = "\x1b[1;34m"


def color_text(text, color):
    return "%s%s%s" % (color, text, COLOR_RESET)

def green_text(text, bold=False):
    return color_text(text, COLOR_BOLD_GREEN if bold else COLOR_GREEN)

def red_text(text, bold=False):
    return color_text(text, COLOR_BOLD_RED if bold else COLOR_RED)

def yellow_text(text, bold=False):
    return color_text(text, COLOR_BOLD_YELLOW if bold else COLOR_YELLOW)

def blue_text(text, bold=False):
    return color_text(text, COLOR_BOLD_BLUE if bold else COLOR_BLUE)