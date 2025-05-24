# This is assignment 10, making a wikipedia chatbot
# sample questions and answers:
# 1) "what is the polar radius of earth?" answer is 6356.752
# 2) 

# first, we need to install the "nltk" package, so I did this from the command line (and commented out in this code):
# pip install nltk
# second, we need to install wikipedia from command line (and commented out in this code):
# pip install wikipedia

# Now we can start the instructions on README.txt
# setup
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# start
import re, string, calendar
from wikipedia import WikipediaPage
import wikipedia
from bs4 import BeautifulSoup
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from match import match
from typing import List, Callable, Tuple, Any, Match

# the get_page_html is a function to get a wikipedia page in html
def get_page_html(title: str) -> str:
    """Gets html of a wikipedia page

    Args:
        title - title of the page

    Returns:
        html of the page
    """
    results = wikipedia.search(title)
    return WikipediaPage(results[0]).html()


# the get_first_infobox_text function gets the summary box of the Wikipedia page, if one exists
def get_first_infobox_text(html: str) -> str:
    """Gets first infobox html from a Wikipedia page (summary box)

    Args:
        html - the full html of the page

    Returns:
        html of just the first infobox
    """
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="infobox")

    if not results:
        raise LookupError("Page has no infobox")
    return results[0].text


# The clean_text function removes non-standard characters, extra spaces, and more
def clean_text(text: str) -> str:
    """Cleans given text removing non-ASCII characters and duplicate spaces & newlines

    Args:
        text - text to clean

    Returns:
        cleaned text
    """
    only_ascii = "".join([char if char in string.printable else " " for char in text])
    no_dup_spaces = re.sub(" +", " ", only_ascii)
    no_dup_newlines = re.sub("\n+", "\n", no_dup_spaces)
    return no_dup_newlines

# the get_match function uses "regex" to see if the Wikipedia page has the property you are searching for
def get_match(
    text: str,
    pattern: str,
    error_text: str = "Page doesn't appear to have the property you're expecting",
) -> Match:
    """Finds regex matches for a pattern

    Args:
        text - text to search within
        pattern - pattern to attempt to find within text
        error_text - text to display if pattern fails to match

    Returns:
        text that matches
    """
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    match = p.search(text)

    if not match:
        raise AttributeError(error_text)
    return match

# The get_polar_radius function gets the radius of a planet, based on Wikipedia info
# For example, "what is the polar radius of earth?" answer is 6356.752
def get_polar_radius(planet_name: str) -> str:
    """Gets the radius of the given planet

    Args:
        planet_name - name of the planet to get radius of

    Returns:
        radius of the given planet
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(planet_name)))
    pattern = r"(?:Polar radius.*?)(?: ?[\d]+ )?(?P<radius>[\d,.]+)(?:.*?)km"
    error_text = "Page infobox has no polar radius information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group("radius")

# The get_country_currency function gets the currency of a country, based on Wikipedia info
# For example, "what is the currency of of italy?" answer is rome
def get_country_currency(country_name: str) -> str:
    """Gets the currency of the given country

    Args:
        country_name - name of the country to get currency of

    Returns:
        currency of the given country
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"(?:Currency.*?)(?: ?[\d]+ )?(?P<currency>[\d,.]+)(?:.*?)"
 #   pattern = r"(?:Currency.*?)(?: ?[\d]+ )?(?P<currency>[\d,.]+)(?:.*?)"
 #   pattern = r"(?:Born\D*)(?P<birth>\d{4}-\d{2}-\d{2})"
 #   pattern = r"(?:Polar radius.*?)(?: ?[\d]+ )?(?P<radius>[\d,.]+)(?:.*?)km"
    error_text = "Page infobox has no country currency information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group("currency")

# The get_continent_population function gets the population of a continent, based on Wikipedia info
# For example, "what is the population of africa?" answer is 1393676444
def get_population(continent_name: str) -> str:
    """Gets the population of the given continent

    Args:
        continent_name - name of the continent to get population of

    Returns:
        population of the given continent
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(continent_name)))
    pattern = r"(?:Population.*?)(?: ?[\d]+ )?(?P<population>[\d,.]+)(?:.*?)"
    error_text = "Page infobox has no continent information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group("population")

# The get_animal_genus function gets the genus of an animal, based on Wikipedia info
# For example, "what is the genus of a dog?" answer is canis
def get_animal_genus(animal_name: str) -> str:
    """Gets the genus of the given animal

    Args:
        animal_name - name of the animal to get genus of

    Returns:
        genus of the given animal
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(animal_name)))
    pattern = r"(?:Genus.*?)(?: ?[\d]+ )?(?P<genus>[\d,.]+)(?:.*?)"
    error_text = "Page infobox has no animal genus information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group("genus")

# The get_birth_date function gives the birthdate of the person
# For example: "when was henry ford born", answer: 1863-07-30
def get_birth_date(name: str) -> str:
    """Gets birth date of the given person

    Args:
        name - name of the person

    Returns:
        birth date of the given person
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(name)))
    pattern = r"(?:Born\D*)(?P<birth>\d{4}-\d{2}-\d{2})"
    error_text = (
        "Page infobox has no birth information (at least none in xxxx-xx-xx format)"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("birth")

# below are a set of actions. Each takes a list argument and returns a list of answers
# according to the action and the argument. It is important that each function returns a
# list of the answer(s) and not just the answer itself.

def birth_date(matches: List[str]) -> List[str]:
    """Returns birth date of named person in matches

    Args:
        matches - match from pattern of person's name to find birth date of

    Returns:
        birth date of named person
    """
    return [get_birth_date(" ".join(matches))]


def polar_radius(matches: List[str]) -> List[str]:
    """Returns polar radius of planet in matches

    Args:
        matches - match from pattern of planet to find polar radius of

    Returns:
        polar radius of planet
    """
    return [get_polar_radius(matches[0])]

def population(matches: List[str]) -> List[str]:
    """Returns population of continent in matches

    Args:
        matches - match from pattern of continent to find population of

    Returns:
        population of planet
    """
    return [get_population(matches[0])]

def country_currency(matches: List[str]) -> List[str]:
    """Returns currency of country in matches

    Args:
        matches - match from pattern of country to find currency of

    Returns:
        currency of country
    """
    return [get_country_currency(matches[0])]

def animal_genus(matches: List[str]) -> List[str]:
    """Returns genus of an animal in matches

    Args:
        matches - match from pattern of animal to find genus of

    Returns:
        genus of animal
    """
    return [get_animal_genus(matches[0])]

# dummy argument is ignored and doesn't matter
def bye_action(dummy: List[str]) -> None:
    raise KeyboardInterrupt

# type aliases to make pa_list type more readable, could also have written:
# pa_list: List[Tuple[List[str], Callable[[List[str]], List[Any]]]] = [...]
Pattern = List[str]
Action = Callable[[List[str]], List[Any]]

# The pattern-action list for the natural language query system. It must be declared
# here, after all of the function definitions
pa_list: List[Tuple[Pattern, Action]] = [
    ("when was % born".split(), birth_date),
    ("what is the currency of %".split(), country_currency),
    ("what is the polar radius of %".split(), polar_radius),
    ("what is the population of %".split(), population),
    ("what is the genus of a %".split(), animal_genus),
    (["bye"], bye_action),
]

def search_pa_list(src: List[str]) -> List[str]:
    """Takes source, finds matching pattern and calls corresponding action. If it finds
    a match but has no answers it returns ["No answers"]. If it finds no match it
    returns ["I don't understand"].

    Args:
        source - a phrase represented as a list of words (strings)

    Returns:
        a list of answers. Will be ["I don't understand"] if it finds no matches and
        ["No answers"] if it finds a match but no answers
    """
    for pat, act in pa_list:
        mat = match(pat, src)
        if mat is not None:
            answer = act(mat)
            return answer if answer else ["No answers"]

    return ["I don't understand"]


def query_loop() -> None:
    """The simple query loop. The try/except structure is to catch Ctrl-C or Ctrl-D
    characters and exit gracefully"""
    print("Welcome to the Wikipedia database!\n")
    while True:
        try:
            print()
            query = input("Your query? ").replace("?", "").lower().split()
            answers = search_pa_list(query)
            for ans in answers:
                print(ans)

        except (KeyboardInterrupt, EOFError):
            break

    print("\nSo long!\n")

# uncomment the next line once you've implemented everything are ready to try it out
query_loop()
