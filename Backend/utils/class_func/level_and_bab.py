from math import ceil, floor
import random

def randomize_level(character, min_num, max_num):
    if not isinstance(min_num, int) or min_num <= 0: 
        min_num = 1
    if not isinstance(max_num, int) or max_num <= 0:
        max_num = 20    
    # for now (we won't deal with multiclasses)
    if character.c_class_2 == '':
        print('this is is blank class_2')
        pre_level = random.randint(min_num, max(min_num, max_num))
        level = min(pre_level,40)
        c_class_level = level
        c_class_2_level = 0
        update_level(character, level, c_class_level, c_class_2_level)
    elif character.dip == True:
        pre_level = random.randint(min_num, max(min_num, max_num))
        level = min(pre_level,40)
        c_class_level = level-1
        c_class_2_level = 1
        update_level(character, level, c_class_level, c_class_2_level)
    else:
        pre_level = random.randint(min_num, max(min_num, max_num))
        level = min(pre_level,40)            
        pre_c_class_level = random.randint((min_num-1,level-1))
        c_class_level = min(pre_c_class_level,39)            
        c_class_2_level = level - c_class_level
        update_level(character, level, c_class_level, c_class_2_level)    

    character.capped_level_1 = min(c_class_level,20)
    character.capped_level_2 = min(c_class_2_level,20)     

        # we create capped levels for things like spells just in case we'll need it for many functions
#should this be update feats, since we're updating feat amount [it 100% depends on level]
def update_level(character, level, c_class_level, c_class_2_level, flaw_flag=None, homebrew_amount=None):
    character.level = level
    character.c_class_level = c_class_level
    character.c_class_2_level = c_class_2_level              

    if flaw_flag == None:
        character.feat_amounts = (ceil(character.level/2) + min(len(character.flaw),3))
    else:
        character.feat_amounts = ( ceil(character.level/2) )

    if homebrew_amount != None:
        character.feat_amounts = (4 + ceil(character.level/2) + floor(character.level/5) + max((len(character.flaw)-2),0) )

    _update_bab_total(character)


def update_level_ability_score(character, level):
    character.level=level
    character.extra_ability_score_levels=floor(level/4)



def _update_bab_total(character):
    character.bab = character.class_data[character.c_class]['bab']
    # set as an integer so our function beneath works
    character.bab_total = 0
    if character.bab == 'L':
        character.bab_total += floor(character.level *.5)
    elif character.bab == 'M':
        character.bab_total += floor(character.level *.75)
    else: 
        character.bab_total += character.level * 1