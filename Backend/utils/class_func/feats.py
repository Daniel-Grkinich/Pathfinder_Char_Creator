import re, random
import pandas as pd
from math import ceil, floor


# Importing custom functions
from Backend.utils.class_func.generic_func import *
from Backend.utils.class_func.chooseable import *



def print_metamagic(character):
    data = pd.read_csv(f'data/feats.csv', sep='|', on_bad_lines='skip')
    Metamagic_feats = data[data['type']=='Metamagic']
    extraction_list = ['name']        
    # print(Metamagic_feats[extraction_list])

def feat_spell_searcher(character, class_1, chosen_set, types, info_column, info_column_2 = None):
    if chosen_set == None:
        return
    # print("this is your chosen_set", chosen_set)
    if character.c_class == class_1:
        data = pd.read_csv(f'data/{types}.csv', sep='|', on_bad_lines='skip')
    
        if info_column_2 is None:
            extraction_list = ['name', info_column]
        else:
            extraction_list = ['name', info_column, info_column_2]



        query_result = remove_mythic(character, types,data, chosen_set, extraction_list)

        result_dict = {}
        result_dict = remove_dots_dashes(character, result_dict, query_result, info_column)
        # print("this is your result dict", result_dict) 
        character.result_dict.update(result_dict)
        # print("this is your char result dict", character.result_dict)
        
        return character.result_dict         

def remove_mythic(character, types, data, chosen_set, extraction_list):
    
    if chosen_set == None:
        return None

    chosen_set_upper = {i.upper() for i in chosen_set}
    # print(f'This is your chosen set {chosen_set_upper}')

    if types == 'feats':
        query_result = data[(data['name'].str.upper().isin(chosen_set_upper)) & (data['type'] != 'Mythic')][extraction_list]
    else:
        query_result = data[(data['name'].str.upper().isin(chosen_set_upper)) & (data['mythic'] == 0)][extraction_list]  

    return query_result

def remove_dots_dashes(character, result_dict, query_result, info_column, info_column_2=None):
    replace_dash = lambda x: re.sub(r'[-]', ' ', str(x))            
    replace_dot = lambda x: re.sub(r'[.]', '', str(x))            

    if query_result is None:
        return

    for index, row in query_result.iterrows():
        feat_name = row['name']
        if pd.isna(row[info_column]):
            row[info_column] = ''
        feat_info = {f'{info_column}': replace_dash(row[f'{info_column}'])}
        feat_info = {f'{info_column}': replace_dot(row[f'{info_column}'])}
        
        if info_column_2 is not None:
            if pd.isna(row[info_column_2]):
                row[info_column_2] = ''
        feat_info = {f'{info_column}': replace_dash(row[f'{info_column}'])}
        feat_info = {f'{info_column}': replace_dot(row[f'{info_column}'])}

        result_dict[feat_name] = feat_info
    
    return result_dict



def bonus_searcher(character, choice, chosen_desc, types):
    bonus_list = []
    bonus = chosen_desc.get(choice,{}).get(f"bonus {types}", {})
    # print('bonus', bonus)
    # print('bonus list', bonus_list)
    character.json_list_grabber( bonus_list, ",", bonus)
    remove_parentheses(character, bonus_list)

    return bonus_list


def remove_parentheses(character, text_list):
    result_list = []
    for text in text_list:
        pattern = r'\([^)]*\)'
        result = re.sub(pattern, '', text)
        result_list.extend(result)
    
    return result_list       
        

def remove_duplicates_list(character,lst):
    seen = set()
    result = []
    for item in lst:
        # Convert lists to tuples for hashability
        item_tuple = tuple(item) if isinstance(item, list) else item
        if item_tuple not in seen:
            seen.add(item_tuple)
            result.append(item)
    return result

def build_selector(character):
    casting_level_str = character.classes[character.c_class]['casting level'].lower()
    specialty_set = {'cleric', 'druid'}
    type_chance = random.choices(range(1, 101))[0]
    feat_list = []

    if character.bab == 'H' or (character.bab == 'M' and casting_level_str not in ('low', 'mid', 'high')):
        add_martial_feats(character, feat_list)
    if character.bab == 'L' and casting_level_str != 'none':
        add_magical_feats(character, feat_list)
    if character.bab == 'M' and casting_level_str != 'none':
        if type_chance >= 50:
            add_martial_feats(character, feat_list)
        else:
            add_magical_feats(character, feat_list)
    if character.c_class in specialty_set:
        add_specialty_feats(character, feat_list)

    result_dict_pre = feat_spell_searcher(character, character.c_class, feat_list, "feats", "prerequisites", "description")
    result_dict = transform_result_dict(character, result_dict_pre)
    chosen_feats = get_feats_without_prerequisites(character, character.c_class, result_dict, character.feat_amounts)
    cleaned_chosen_feats = capitalize_feats(character, chosen_feats)
    return cleaned_chosen_feats


def add_martial_feats(character, feat_list):
    martial = character.feat_buckets['martial']
    universal = character.feat_buckets['universal']

    martial_choice = random.choice(list(martial.keys()))
    universal_choice = random.choice(list(universal.keys()))
    martial_choice_2 = random.choice(list((martial[martial_choice].keys())))
    list_2 = list(universal[universal_choice])
    list_1 = list(martial[martial_choice][martial_choice_2])
    feat_list.extend(list_1 + list_2)        

    if character.dex_mod >= character.str_mod +2:
        feat_list.append('weapon finesse')        

    character.feat_list = feat_list
    return character.feat_list

def add_magical_feats(character, feat_list):
    magical = character.feat_buckets['magical']
    universal = character.feat_buckets['universal']

    magical_choice = random.choice(list(magical.keys()))
    universal_choice = random.choice(list(universal.keys()))
    list_2 = list(universal[universal_choice])
    list_1 = list(magical[magical_choice])
    feat_list.extend(list_1 + list_2)    

def add_specialty_feats(character, feat_list):
    classes_choices = list(character.feat_buckets['classes'][character.c_class])
    feat_list.extend(classes_choices)       

def transform_result_dict(character, result_dict):
    for feat in list(result_dict.keys()):
        feat_info = result_dict[feat]
        prereq_set = set()
        prerequisites = str(feat_info.get('prerequisites', None))

        if prerequisites is not None:
            prereq_set.add(prerequisites.lower())
            result_dict[feat]['prerequisites'] = prerequisites.lower()
            new_feat = feat.lower()

            if prerequisites.lower() == 'nan':
                result_dict[feat]['prerequisites'] = ''
                new_feat = ''

            if new_feat != feat:
                result_dict[new_feat] = result_dict.pop(feat)     
    return result_dict


def get_feats_without_prerequisites(character, class_1, dataset_name, level= None, level_2 = None, dataset_name_2 = None, feat_amount=None):

    if character.c_class != class_1:
        return None

    base_no_prereq = []
    amount = ceil(character.c_class_level/2)
    
    dataset = dataset_name
    # print("this is your dataset", dataset)
    base = dataset.copy()
    base_no_prereq = no_prereq_loop(character, base)
    # print("base no prereq", base_no_prereq)
    total_choices = base_no_prereq

    if amount == None:
        amount = 0

    chosen_feats = choosing_feats(character, amount, base, total_choices)

    return chosen_feats

def choosing_feats(character, amount, base, total_choices):
    chosen_feats = set()
    i = 0
    # added this logic so low level characters don't break
    if amount == None or amount <= 0:
        return []
    
    while i < amount + 1:
        # added this logic so low level characters don't break
        if amount == None or amount <= 0:
            return []        
        chosen = random.choice(total_choices)
        # print(f"this is the {i}th choice and this is your {chosen}")
        prereq_list = no_prereq_loop(character, base, "prereq_list")
        # print(character.c_class)
        # print(character.chooseable)
        # print("this is your prereq list", prereq_list)
        chosen_feats.add(chosen.lower())
        i = len(chosen_feats)
        
        total_choices.append(chosen.lower()) 
        total_choices.extend(prereq_list)
        total_choices = remove_duplicates_list(character, total_choices)
        total_choices=list(set(total_choices))

        character.chooseable.add(chosen)
        
    return chosen_feats

def generic_feat_chooser(character, class_1, casting_level_str,feat_type, info_column ):
    if class_1 == character.c_class:
        feat_data = pd.read_csv(f'data/feats.csv', sep='|', on_bad_lines='skip')
        # print("these are all the types", feat_data['type'].unique())
        feat_types = feat_data['type'].unique()
        # print("All feat_data types:", feat_types)
        extraction_list = ['name', 'prerequisites', 'description']
        if casting_level_str in ("mid", "high"):
            query_i = feat_data.loc[
                (feat_data['type'] == feat_type.capitalize()) 
                | (feat_data['type'] == 'General') 
                | (feat_data['type'] == 'Item Creation')
                | (feat_data['type'] == 'Story') 
                | (feat_data['type'] == 'Achievement'), 
                extraction_list
            ]
        else:
            query_i = feat_data.loc[
                (feat_data['type'] == feat_type.capitalize()) 
                | (feat_data['type'] == 'General') 
                | (feat_data['type'] == 'Story') 
                | (feat_data['type'] == 'Achievement'), 
                extraction_list
            ]

        query_i = query_i.drop_duplicates(subset='name', keep='first')
        feat_result_dict = query_i.set_index('name')[['prerequisites', 'description']].to_dict(orient='index')
        feat_result_dict = transform_result_dict(character, feat_result_dict)

        feat_result_dict.update(feat_result_dict)

        chosen_feats = get_feats_without_prerequisites(character, character.c_class, feat_result_dict, feat_amount= character.feat_amounts)
        chosen_feats.remove("")
        cleaned_chosen_feats = capitalize_feats(character, chosen_feats)
        # print("cleaned_chosen_feats: ",cleaned_chosen_feats)
        character.chosen_feats = cleaned_chosen_feats

        return cleaned_chosen_feats
    
def capitalize_feats(character, chosen_feats):
    fillers = ["the", "of", "and", "a", "an", "in", "on", "at", "to", "for"]  # Add more as needed
    cleaned_chosen_feats = []
    for feats in chosen_feats:
        words = feats.split()
        capitalized_words = []
        for word in words:
            if '-' in word:
                parts = word.split('-')
                # print("these are the parts " + str(parts))
                capitalized_parts = [part.capitalize() for part in parts]
                capitalized_words.append('-'.join(capitalized_parts))
            else:
                capitalized_words.append(word.capitalize() if word.lower() not in fillers else word)
        feat = ' '.join(capitalized_words)
        cleaned_chosen_feats.append(feat)
    return cleaned_chosen_feats




def simple_list_chooser(character, class_1, *dataset_names, max_num=float('inf'), **kwargs):
    if character.c_class.lower() == class_1.lower():
        chosen = []
        chosen_dict = {}
        for dataset_name in dataset_names:
            dataset_input = getattr(data, dataset_name)
            dataset = character.json_list_grabber(dataset_input, ',', **kwargs)
            # print(f"This is your dataset for {dataset_name}: {dataset}")
            formula_calc = formula_grabber(character, dataset_name, **kwargs)
            if isinstance(dataset, dict):
                dataset = list(dataset.keys())
            # chosen.append(random.sample(dataset, k=min(formula_calc, max_num)))
            chosen_dict[dataset_name] = random.sample(dataset, k=min(formula_calc, max_num))
            character.data_dict.update({'class features': chosen_dict})
        # print(chosen)
        return chosen

def formula_grabber(character, dataset_name):
    formula = getattr(data, 'formulas').get(dataset_name,1)
    # print(f'this is your formula {formula}')
    amount = eval(formula)
    return amount  