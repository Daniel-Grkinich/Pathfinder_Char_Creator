import random, re
from Backend.utils.class_func.race_func import *
from Backend.utils.data import languages
def language_chooser(character):
    full_race_data_grab = full_race_data(character)
    language_text = full_race_data_grab.get(character.chosen_race, {}).get('Languages', [])        
    regex = ':(.*)'
    captured_content = regex_search(character,language_text, regex)
    language_list = language_splitter(character,captured_content)
    languages = random_language_chooser(character,language_list, character.int_mod)
    
    return languages

def regex_search(character, string, regex):
    print("this is your race" + character.chosen_race)
    # print(f'this is your string {string}')
    # print(f'this is your regex {regex}')
    pattern = rf"{regex}"
    match = re.search(pattern, string)
    if match:
        captured_content = match.group(1)
    else:
        captured_content = languages

    # print(f'this is your captured_content {captured_content}')
    return captured_content

def language_splitter(character, language_text):
    if isinstance(language_text,list):
        return language_text
    else:
        pre_language_list = language_text.split(",")
        language_list = []
        for lang in pre_language_list:
            # print("this is your pre lang transform " + lang)
            lang = lang.strip()
            lang = remove_word(character, lang, 'and')  # Remove 'and' before splitting
            capitalized_lang = capitalize_after_dash(lang)
            language_list.append(capitalized_lang)
            # print("this is your post lang transform " + capitalized_lang)

    return language_list

def capitalize_after_dash(lang):
    words = lang.split('-')
    capitalized_words = [word.capitalize() for word in words]
    return '-'.join(capitalized_words)

def random_language_chooser(character, language_list, number):
    k=min(number, len(language_list))
    if k < 0:
        k =0
    languages = random.sample(language_list, k)
    return languages

def remove_word(character, string, word_to_remove):
    new_string = string.replace(word_to_remove, '')
    new_string = new_string.replace('.', '').replace(' ', '')
    return new_string