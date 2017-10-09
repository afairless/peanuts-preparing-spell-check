#! /usr/bin/env python3


def get_sibling_directory_path(sibling_directory_name):
    '''
    returns path for a specified folder that is in the same parent directory as
        the current working directory
    '''

    import os

    current_path = os.getcwd()
    last_separator_position = current_path.rfind(os.sep)
    parent_directory_path = current_path[0:last_separator_position]
    sibling_directory_path = os.path.join(parent_directory_path,
                                          sibling_directory_name)
    return(sibling_directory_path)


def read_table(table_filepath, column_of_lists):
    '''
    reads table from 'csv' file
    each item in column 'column_of_lists' is read as a list; as currently
        written, the function can read only 1 column as a list
    '''

    import pandas as pd
    from ast import literal_eval

    # '^' used as separator because it does not appear in any text descriptions
    table = pd.read_csv(table_filepath, sep='^',
                        converters={column_of_lists: literal_eval})

    return(table)


def compile_misspellings(table_filepath, force_recompile=False):
    '''
    compiles table of misspellings and suggested corrections from spell checker
        using a U.S. English dictionary
    '''

    import os
    import enchant
    from enchant.checker import SpellChecker
    import pandas as pd

    compiled_filename = 'compiled_misspellings.csv'

    if not force_recompile:
        if os.path.isfile(compiled_filename):
            compiled = read_table(compiled_filename, 'suggestions')
            return(compiled)

    table = read_table(table_filepath, 'text_by_panels')
    table_col = 3
    dictionary = enchant.Dict('en_US')
    #checker = enchant.checker.SpellChecker(dictionary)     # produces error
    checker = SpellChecker(dictionary)

    filenames = []
    panel_numbers = []
    containing_text = []
    misspellings = []
    suggestions = []

    for i in range(len(table)):
        text = table.iloc[i, table_col]
        for j in range(len(text)):
            checker.set_text(text[j])
            for e in checker:
                filenames.append(table.iloc[i, 0])
                panel_numbers.append(j)
                containing_text.append(text[j])
                misspellings.append(e.word)
                suggestions.append(dictionary.suggest(e.word))

    compiled = pd.DataFrame({'filename': filenames,
                             'panel_index': panel_numbers,
                             'containing_text': containing_text,
                             'misspellings': misspellings,
                             'suggestions': suggestions})
    compiled = compiled[['filename', 'panel_index', 'containing_text',
                         'misspellings', 'suggestions']]
    compiled.to_csv(compiled_filename, sep='^', index=False)

    return(compiled)


def print_df_strings(a_dataframe, search_string, search_column, show_column):
    '''
    prints strings from a dataframe for visual inspection
    '''

    for i in range(len(a_dataframe)):
        #if search_string in a_dataframe.iloc[i, search_column]:
        if search_string == a_dataframe.iloc[i, search_column]:
            print(search_string)
            print(a_dataframe.iloc[i, show_column])
            print('\n')


def write_list_to_text_file(a_list, text_file_name, overwrite_or_append = 'a'):
    '''
    writes a list of strings to a text file
    appends by default; change to overwriting by setting to 'w' instead of 'a'
    '''

    try:
        textfile = open(text_file_name, overwrite_or_append, encoding = 'utf-8')
        for element in a_list:
            textfile.write(element)
            textfile.write('\n')

    finally:
        textfile.close()


def read_text_file(text_filename, as_string=False):
    '''
    reads each line in a text file as a list item and returns list by default
    if 'as_string' is 'True', reads entire text file as a single string
    '''

    text_list = []

    try:
        with open(text_filename) as text:
            if as_string:
                # reads text file as single string
                text_list = text.read().replace('\n', '')
            else:
                # reads each line of text file as item in a list
                for line in text:
                    text_list.append(line.rstrip('\n'))
            text.close()
        return(text_list)

    except:
        return('There was an error while trying to read the file')


def make_valid_spellings_list(misspell_table, return_list=True):
    '''
    sets up and documents process for manually viewing and editing
        'misspell_table' into a 'valid_spell_list' that provides a customized
        list of words that the spell checker will accept
    the original list of misspellings, from an initial run of the spell checker,
        found 3743 misspellings
    in editing the text file of the list, I scrutinized frequent misspellings
        closely, which included reading the original context and sometimes
        referring to the comic itself
    less frequent misspellings were reviewed more quickly with special attention
        for possible character names; generally for these less frequent words, I
        removed them (thereby letting the next run of the spell checker change
        them) only if I was quite confident that the misspelling didn't
        accurately transcribe the comic and that the spell checker would pick
        the correct substitute
    I included some notes as comments below on my choices; the notes include a
        category of 'words that are retained and are not corrected by 1st
        checker option', which will require customized attention to correct
    if 'return_list' is 'True', the edited list is read from its text file and
        returned
    '''

    # counts of how many times each misspelled word occurs
    #misspell_counts = misspell_table['misspellings'].value_counts()
    #misspell_count_list = list(misspell_counts.keys())

    # create files of the original and edited word lists
    original_list_file = 'misspell_list.txt'
    valid_spell_list_file = 'valid_spell_list.txt'
    write_list_to_text_file(original_list_file, original_list_file, 'w')
    # WARNING:  The line below will overwrite the manually edited file
    #write_list_to_text_file(original_list_file, valid_spell_list_file, 'w')

    '''
    # view words manually and interactively to determine whether to retain them
    word = 'Saslly'
    i = misspell_count_list.index(word)
    print_df_strings(misspell_table, list(misspell_count_list)[i], 3, 2)
    print_df_strings(misspell_table, list(misspell_count_list)[i], 3, 4)
    print_df_strings(misspell_table, list(misspell_count_list)[i], 3, 0)
    '''

    # NOTES ON MANUAL EDITING PROCESS
    #
    #
    # words that are retained:
    #
    # "'im", which is accurately transcribed and is short for "him"
    # "ve", which is part of "I've"
    # "de" is from French dialogue
    # "da" is from singing
    # 'ka', which is an accurate transcription of Snoopy's thought
    # "te" is from singing
    # "dum" is from singing
    # 'goodby' accurately transcribes the comic
    # 'Il' is from French dialogue
    # 'VATDHKWXJUFIBLSCNOQGEYR' accurately transcribes the comic
    #
    #
    # words that are retained and are not corrected by 1st checker option:
    #
    # an 'i' with a squiggly mark over it; should be an apostrophe
    # "say's" misspells 'says'; spell checker option #3 corrects it
    # 'Charie' misspells 'Charlie'; spell checker option #2 corrects it
    # 'Salley' misspells 'Sally'; spell checker option #2 corrects it
    # 'loks' misspells 'looks'; spell checker option #2 corrects it
    # 'Beaglscout' misspells 'Beaglescout'; spell checker doesn't correct it
    # 'Bown' misspells 'Brown'; spell checker option #3 corrects it
    # 'Lius' misspells 'Linus'; spell checker option #3 corrects it
    # 'eys' misspells 'eyes'; spell checker option #4 corrects it
    # 'ozzes' misspells 'ounces'; spell checker doesn't correct it
    # 'Charlei' misspells 'Charlie'; spell checker option #2 corrects it
    # 'Linu' misspells 'Linus'; spell checker option #2 corrects it
    # 'disterbense' misspells 'disturbance'; I haven't checked the comic
    # 'Luc' misspells 'Lucy'; spell checker option #5 corrects it
    # 'Vioet' misspells 'Violet'; spell checker option #2 corrects it
    # 'hom' misspells 'home'; spell checker option #7 corrects it
    # 'son't' misspells 'don't'; spell checker option #2 corrects it
    # 'blandet' misspells 'blanket'; spell checker option #3 corrects it
    # 'mit' misspells 'mitt' in one comic but is correct German in another
    # 'Charle' misspells 'Charlie'; spell checker option #2 corrects it
    # 'Salluy' misspells 'Sally'; spell checker option #2 corrects it
    # 'ZSNOOPY' misspells 'Z SNOOPY'; spell checker option #2 corrects it
    # 'legionaires' misspells 'legionnaires'; spell checker option #2 corrects it
    # 'Patrcia' misspells 'Patricia'; spell checker option #2 corrects it
    # 'Suppertie' misspells 'Suppertime'; spell checker doesn't correct it
    # 'Barown' misspells 'Brown'; spell checker option #2 corrects it
    # 'bBrown' misspells 'Brown'; spell checker option #3 corrects it
    # 'Brownas' misspells 'Brown as'; spell checker option #2 corrects it
    # 'ZBrown' misspells 'Brown'; spell checker option #2 corrects it
    # 'Woodst' misspells 'Woodstock'; spell checker doesn't correct it
    # 'Beagscout' misspells 'Beaglescout'; spell checker doesn't correct it
    # 'ZZMarcie' misspells 'ZZ Marcie'; spell checker doesn't correct it
    # 'Paty' misspells 'Patty'; spell checker option #3 corrects it
    # 'Reun' misspells 'Rerun'; spell checker option #5 corrects it
    # 'Bhown' misspells 'Brown'; spell checker option #2 corrects it
    # 'Lcy' misspells 'Lucy'; spell checker option #3 corrects it
    # 'Saly' misspells 'Sally'; spell checker option #4 corrects it
    # 'Charli' misspells 'Charlie'; spell checker option #2 corrects it
    # 'Mrcie' misspells 'Marcie'; spell checker option #2 corrects it
    # 'VBrown' misspells 'Brown'; spell checker option #2 corrects it
    # 'Beeth' misspells 'Beethoven'; spell checker option #2 corrects it
    # 'Cameroun' misspells 'Cameroon'; spell checker option #2 corrects it
    # 'Pepperiment' misspells 'Peppermint'; spell checker option #3 corrects it
    # 'Sallu' misspells 'Sally'; spell checker option #4 corrects it
    # 'Flinstone' misspells 'Flintstone'; spell checker doesn't correct it
    # 'Marce' misspells 'Marcie'; spell checker option #4 corrects it
    # 'Rereun's' misspells 'Rerun's'; spell checker option #4 corrects it
    # 'Lcu' misspells 'Lucy'; spell checker option doesn't correct it
    # 'Patt' misspells 'Patty'; spell checker option doesn't correct it
    # 'blockhed' misspells 'blockhead'; spell checker option option #2 corrects it
    # 'Serman' misspells 'Shermy'; spell checker option doesn't correct it
    # 'Barown' misspells 'Brown'; spell checker option #2 corrects it
    # 'skake' misspells 'skate'; spell checker option #2 corrects it
    #
    #
    # words that are not retained and are corrected by 1st checker option:
    #
    # originally, I relied on the spell checker to correct these, but in
    # validation/quality checking, I noticed a case where 'Snooey' was changed
    # to 'snoot' instead of 'Snoopy'; this called into question how consistently
    # the checker handles all these cases below, so I've moved them to the
    # customized dictionary in 'custom_corrections' to be safe
    #
    # 'Shroeder' misspells 'Schroeder'; spell checker corrects it
    # 'CHarlie' misspells 'Charlie'; spell checker corrects it
    # 'SNoopy' misspells 'Snoopy'; spell checker corrects it
    # 'Chalrie' misspells 'Charlie'; spell checker corrects it
    # 'Schroder' misspells 'Schroeder'; spell checker corrects it
    #
    # 'Chrlie' misspells 'Charlie'; spell checker corrects it
    # 'Charllie' misspells 'Charlie'; spell checker corrects it
    # 'Chrarlie' misspells 'Charlie'; spell checker corrects it
    # 'Charliee' misspells 'Charlie'; spell checker corrects it
    # 'TCharlie' misspells 'Charlie'; spell checker corrects it
    # 'Chralie' misspells 'Charlie'; spell checker corrects it
    # 'Cahrlie' misspells 'Charlie'; spell checker corrects it
    # 'Charlies' misspells 'Charlie'; spell checker corrects it
    # 'Chalres' misspells 'Charlie'; spell checker corrects it
    # 'Borwn' misspells 'Brown'; spell checker corrects it
    # 'Bronw' misspells 'Brown'; spell checker corrects it
    # 'Brwon' misspells 'Brown'; spell checker corrects it
    # 'Bropwn' misspells 'Brown'; spell checker corrects it
    # 'Schreoder' misspells 'Schroeder'; spell checker corrects it
    # 'Scxhroeder' misspells 'Schroeder'; spell checker corrects it
    # 'Shroecder' misspells 'Schroeder'; spell checker corrects it
    # 'Shcroeder' misspells 'Schroeder'; spell checker corrects it
    # 'Schoreder' misspells 'Schroeder'; spell checker corrects it
    # 'Schroder's' misspells 'Schroeder's'; spell checker corrects it
    # 'Schoeder' misspells 'Schroeder'; spell checker corrects it
    # 'Scroeder' misspells 'Schroeder'; spell checker corrects it
    # 'Shroeder's' misspells 'Schroeder'; spell checker corrects it
    # 'Snooy's' misspells 'Snoopy's'; spell checker corrects it
    # 'Snooy' misspells 'Snoopy'; spell checker corrects it
    # 'Snopy' misspells 'Snoopy'; spell checker corrects it
    # 'Snoopt' misspells 'Snoopy'; spell checker corrects it
    # 'Snnopy's' misspells 'Snoopy'; spell checker corrects it
    # 'Snoopu' misspells 'Snoopy'; spell checker corrects it
    # 'Snooppy' misspells 'Snoopy'; spell checker corrects it
    # 'Smnoopy' misspells 'Snoopy'; spell checker corrects it
    # 'Snoopyt' misspells 'Snoopy'; spell checker corrects it
    # 'Soopy' misspells 'Snoopy'; spell checker corrects it
    # 'Snnopy' misspells 'Snoopy'; spell checker corrects it
    # 'Snooopy' misspells 'Snoopy'; spell checker corrects it
    # 'SNoopy's' misspells 'Snoopy'; spell checker corrects it
    # 'Snoppy' misspells 'Snoopy'; spell checker corrects it
    # index 226 = 'Snoopys' misspells 'Snoopy'; spell checker corrects it
    # 'Pepermint' misspells 'Peppermint'; spell checker corrects it
    # 'Pepprmint' misspells 'Peppermint'; spell checker corrects it
    # 'Peppermaint' misspells 'Peppermint'; spell checker corrects it
    # 'Peppermiont' misspells 'Peppermint'; spell checker corrects it
    # 'Pepppermint' misspells 'Peppermint'; spell checker corrects it
    # 'Perppermint' misspells 'Peppermint'; spell checker corrects it
    # 'Pepperint' misspells 'Peppermint'; spell checker corrects it
    # 'Woodstaock' misspells 'Woodstock'; spell checker corrects it
    # 'Woodsrock' misspells 'Woodstock'; spell checker corrects it
    # 'Wookstock' misspells 'Woodstock'; spell checker corrects it
    # 'Woodstack' misspells 'Woodstock'; spell checker corrects it
    # 'Wodstock' misspells 'Woodstock'; spell checker corrects it
    # 'Woostock' misspells 'Woodstock'; spell checker corrects it
    # 'Woosdstock' misspells 'Woodstock'; spell checker corrects it
    # 'Linuis' misspells 'Linus'; spell checker corrects it
    # 'Liunus' misspells 'Linus'; spell checker corrects it
    # 'Linmus' misspells 'Linus'; spell checker corrects it
    # 'Linu's' misspells 'Linus'; spell checker corrects it
    # 'Linuys' misspells 'Linus'; spell checker corrects it
    # 'Luct' misspells 'Lucy'; spell checker corrects it
    # 'Luicy' misspells 'Lucy'; spell checker corrects it
    # 'Sallt' misspells 'Sally'; spell checker corrects it
    # 'SAlly' misspells 'Sally'; spell checker corrects it
    # 'Rereun' misspells 'Rerun'; spell checker corrects it
    # 'RErun' misspells 'Rerun'; spell checker corrects it
    # 'VIolet' misspells 'Violet'; spell checker corrects it
    # 'Violt' misspells 'Violet'; spell checker corrects it
    # 'Violeta' misspells 'Violet'; spell checker corrects it
    # 'Tschaikousky' misspells 'Tchaikovsky'; spell checker corrects it
    # 'Tschaikowsky' misspells 'Tchaikovsky'; spell checker corrects it
    # 'Maarcie' misspells 'Marcie'; spell checker corrects it
    # 'Sopphie' misspells 'Sophie'; spell checker corrects it
    # 'Eurdora' misspells 'Eudora'; spell checker corrects it
    # 'SPike' misspells 'Spike'; spell checker corrects it
    # stopped recording these notes after here

    if return_list:
        valid_spell_list = read_text_file(valid_spell_list_file)
        return(valid_spell_list)
    else:
        return()


def custom_corrections():
    '''
    creates dictionary that specifies customized spelling corrections that the
        standard English dictionary does not correctly address
    '''
    corrections = {'Charie': 'Charlie',
                   chr(236): '\'',
                   chr(237): '\'',
                   chr(238): '\'',
                   'say\'s': 'says',
                   'Salley': 'Sally',
                   'loks': 'looks',
                   'mealSuppertime': 'meal Suppertime',
                   'Beaglscout': 'Beaglescout',
                   'Bown': 'Brown',
                   'Lius': 'Linus',
                   'eys': 'eyes',
                   'lsat': 'last',
                   'ozzes': 'ounces',
                   'Charlei': 'Charlie',
                   'Linu': 'Linus',
                   'disterbense': 'disturbance',
                   'Luc': 'Lucy',
                   'Vioet': 'Violet',
                   'hom': 'home',
                   'son\'t': 'don\'t',
                   'blandet': 'blanket',
                   'Charle': 'Charlie',
                   'Salluy': 'Sally',
                   'legionaires': 'legionnaires',
                   'Patrcia': 'Patricia',
                   'Suppertie': 'Suppertime',
                   'Barown': 'Brown',
                   'bBrown': 'Brown',
                   'Brownas': 'Brown as',
                   'ZBrown': 'Brown',
                   'Woodst': 'Woodstock',
                   'Beagscout': 'Beaglescout',
                   'Paty': 'Patty',
                   'Reun': 'Rerun',
                   'Bhown': 'Brown',
                   'Lcy': 'Lucy',
                   'Saly': 'Sally',
                   'Charli': 'Charlie',
                   'Mrcie': 'Marcie',
                   'VBrown': 'Brown',
                   'Beeth': 'Beethoven',
                   'Cameroun': 'Cameroon',
                   'Pepperiment': 'Peppermint',
                   'Sallu': 'Sally',
                   'Flinstone': 'Flintstone',
                   'Marce': 'Marcie',
                   'Rereun\'s': 'Rerun\'s',
                   'Lcu': 'Lucy',
                   'Patt': 'Patty',
                   'blockhed': 'blockhead',
                   'Greeings': 'Greetings',
                   'Schlabotnik': 'Shlabotnik',
                   'SCHLABOTNIK': 'SHLABOTNIK',
                   'Patrcia': 'Patrcia',
                   'Humperdink': 'Humperdinck',
                   'Peppent': 'Peppermint',
                   #'mit': 'mitt',    # this corrects a reference to a baseball
                                        # mitt, but incorrectly changes a German word
                   'Serman': 'Shermy',
                   'Barown': 'Brown',
                   'ZSNOOPY': 'Z SNOOPY',
                   'ZZMarcie': 'ZZ Marcie',
                   'chompSnoopy': 'chomp Snoopy',
                   'MMMMMMMMMCharlie': 'MMMMMMMMM Charlie',
                   'TickleSnoopy': 'Tickle Snoopy',
                   'thatSally': 'that Sally',
                   'rulerSally': 'ruler Sally',
                   'HELucy': 'HE Lucy',
                   'PHOOEYPatty': 'PHOOEY Patty',
                   'HEECharlie': 'HEE Charlie',
                   'soFrieda': 'so Frieda',
                   'Snoopylifts': 'Snoopy lifts',
                   'SLURPSnoopy': 'SLURP Snoopy',
                   'muchLydia': 'much Lydia',
                   'BALLCharlie': 'BALL Charlie',
                   'Snoopyt': 'Snoopy t',
                   'Lucyhands': 'Lucy hands',
                   'todayPatty': 'today Patty',
                   'chooLinus': 'choo Linus',
                   'SnoopySnoopy': 'Snoopy Snoopy',
                   'happenedCharlie': 'happened Charlie',
                   'Pattycomes': 'Patty comes',
                   'PattyMarcie': 'Patty Marcie',
                   'bloodSnoopy': 'blood Snoopy',
                   'Linussays': 'Linus says',
                   'HmmCharlie': 'Hmm Charlie',
                   'Beagscout': 'Beaglescout',
                   'SchroederWho': 'Schroeder Who',
                   'MeCharlie': 'Me Charlie',
                   'WAAHCharlie': 'WAAH Charlie',
                   'HASchroeder': 'HA Schroeder',
                   'WhewSnoopy': 'Whew Snoopy',
                   'wormWOODSTOCK': 'worm WOODSTOCK',
                   'whistlingCharlie': 'whistling Charlie',
                   'YAWNCharlie': 'YAWN Charlie',
                   'SchroederPatty': 'Schroeder Patty',
                   'girlSnoopy': 'girl Snoopy',
                   'badLUCY': 'bad LUCY',
                   'beastCharlie': 'beast Charlie',
                   'PANTCharlie': 'PANT Charlie',
                   'ol\'Charlie': 'ol\' Charlie',
                   'themMARCIE': 'themMARCIE',
                   'youSally': 'you Sally',
                   'mouthSALLY': 'mouthSALLY',
                   'DUMLUCY': 'DUM LUCY',
                   'CaliforniaLINUS': 'California LINUS',
                   'olderLucy': 'older Lucy',
                   'DaySally': 'Day Sally',
                   'rulerSNOOPY': 'ruler SNOOPY',
                   'CHOMPLucy': 'CHOMP Lucy',
                   'themLucy': 'them Lucy',
                   'notLucy': 'not Lucy',
                   'winerySNOOPY': 'winery SNOOPY',
                   'speakSNOOPY': 'speak SNOOPY',
                   'callSNOOPY': 'call SNOOPY',
                   'mailLucy': 'mail Lucy',
                   'BrownCharlie': 'Brown Charlie',
                   'o\'clockWOODSTOCK': 'o\'clock WOODSTOCK',
                   'MOVEDCharlie': 'MOVED Charlie',
                   'DSally': 'DSally',
                   'itCharlie': 'it Charlie',
                   'onSchroeder': 'onSchroeder',
                   'MMMMMSNOOPY': 'MMMMM SNOOPY',
                   'SHAKECharlie': 'SHAKE Charlie',
                   'NoJoseph': 'No Joseph',
                   'SIGHCharlie': 'SIGH Charlie',
                   'timeCharlie': 'time Charlie',
                   'forteCharlie': 'forte Charlie',
                   'sureCharlie': 'sure Charlie',
                   'meShermy': 'me Shermy',
                   'YawnLinus': 'Yawn Linus',
                   'Lius': 'Linus',
                   'moung': 'mound',
                   'Snooy': 'Snoopy',
                   'Marice': 'Marcie',
                   'Shroeder': 'Schroeder',
                   'CHarlie': 'Charlie',
                   'SNoopy': 'Snoopy',
                   'Chalrie': 'Charlie',
                   'Schroder': 'Schroeder',
                   'Borwn': 'Brown',
                   'Chrlie': 'Charlie',
                   'Charllie': 'Charlie',
                   'Chrarlie': 'Charlie',
                   'Charliee': 'Charlie',
                   'TCharlie': 'Charlie',
                   'Chralie': 'Charlie',
                   'Cahrlie': 'Charlie',
                   'Charlies': 'Charlie',
                   'Chalres': 'Charlie',
                   'Borwn': 'Brown',
                   'Bronw': 'Brown',
                   'Brwon': 'Brown',
                   'Bropwn': 'Brown',
                   'Schreoder': 'Schroeder',
                   'Scxhroeder': 'Schroeder',
                   'Shroecder': 'Schroeder',
                   'Shcroeder': 'Schroeder',
                   'Schoreder': 'Schroeder',
                   'Schoeder': 'Schroeder',
                   'Scroeder': 'Schroeder',
                   'Schroder\'s': 'Schroeder\'s',
                   'Shroeder\'s': 'Schroeder\'s',
                   'Snooy\'s': 'Snoopy\'s',
                   'Snooy': 'Snoopy',
                   'Snopy': 'Snoopy',
                   'Snoopt': 'Snoopy',
                   'Snnopy': 'Snoopy',
                   'Snoopu': 'Snoopy',
                   'Snooppy': 'Snoopy',
                   'Smnoopy': 'Snoopy',
                   'Snoopyt': 'Snoopy',
                   'Soopy': 'Snoopy',
                   'Snnopy': 'Snoopy',
                   'Snooopy': 'Snoopy',
                   'SNoopy': 'Snoopy',
                   'Snoppy': 'Snoopy',
                   'Snoopys': 'Snoopy',
                   'Pepermint': 'Peppermint',
                   'Pepprmint': 'Peppermint',
                   'Peppermaint': 'Peppermint',
                   'Peppermiont': 'Peppermint',
                   'Pepppermint': 'Peppermint',
                   'Perppermint': 'Peppermint',
                   'Pepperint': 'Peppermint',
                   'Woodstaock': 'Woodstock',
                   'Woodsrock': 'Woodstock',
                   'Wookstock': 'Woodstock',
                   'Woodstack': 'Woodstock',
                   'Wodstock': 'Woodstock',
                   'Woostock': 'Woodstock',
                   'Woosdstock': 'Woodstock',
                   'Linuis': 'Linus',
                   'Liunus': 'Linus',
                   'Linmus': 'Linus',
                   'Linuys': 'Linus',
                   'Linu\'s': 'Linus',
                   'Luct': 'Lucy',
                   'Luicy': 'Lucy',
                   'Sallt': 'Sally',
                   'Rereun': 'Rerun',
                   'RErun': 'Rerun',
                   'Violt': 'Violet',
                   'Violeta': 'Violet',
                   'Tschaikousky': 'Tchaikovsky',
                   'Tschaikowsky': 'Tchaikovsky',
                   'Maarcie': 'Marcie',
                   'Sopphie': 'Sophie',
                   'Eurdora': 'Eudora',
                   'skake': 'skate'}
    return(corrections)


def replace_substring(a_string, original_str, replacement_str):
    '''
    replaces substring 'original_str' with 'replacement_str' in 'a_string'
    '''

    import re

    start_idx = [s.start() for s in re.finditer(original_str, a_string)]

    for i in range(len(start_idx)-1, -1, -1):
        end_idx = start_idx[i] + len(original_str)
        new_string = a_string[:start_idx[i]] + replacement_str + a_string[end_idx:]
        a_string = new_string

    return(a_string)


def correct_string_misspellings(a_string, corrections_dict, character_names,
                                dictionary, checker, tokenizer):
    '''
    Given 'a_string', returns a spelling-corrected 'a_string'
    Corrections customized for descriptions of Peanuts comics are applied first,
        then a standard English dictionary is used for corrections
    '''

    # customized corrections
    tokens = [w[0] for w in tokenizer(a_string)]
    for k in corrections_dict:
        if k in tokens:
            a_string = replace_substring(a_string, k, corrections_dict[k])
    a_string = a_string.lower()

    # correct string according to spell check with full English dictionary
    checker.set_text(a_string)
    for e in checker:
        suggestions = dictionary.suggest(e.word)
        if suggestions:
            a_string = replace_substring(a_string, e.word, suggestions[0])
    a_string = a_string.lower()     # spell check dictionary capitalizes some words

    return(a_string)


def main():
    '''
    Spell-checks and corrects descriptions of Peanuts comics
    Misspellings that a standard English dictionary can not correct are handled
        by customized corrections
    Table with descriptions is read from a 'csv' file; spelling-corrected
        descriptions are added as the right-most column in the table and written
        out to a new 'csv' file in the present working directory
    '''

    import os
    import enchant
    from enchant.checker import SpellChecker
    from enchant.tokenize import get_tokenizer

    table_folder = '04_divide_text'
    table_file = 'table.csv'
    table_filepath = os.path.join(get_sibling_directory_path(table_folder),
                                  table_file)

    table_col = 3
    text_col_name = 'text_by_panels'
    table = read_table(table_filepath, text_col_name)

    #misspell_table = compile_misspellings(table_filepath)
    valid_words = read_text_file('valid_spell_list.txt')
    valid_words = [s.lower() for s in valid_words]

    character_names = read_text_file('character_names.txt')
    character_names = [s.lower() for s in character_names]

    valid_words.extend(character_names)
    write_list_to_text_file(valid_words, 'valid_spell_list_lower.txt', 'w')

    dictionary = enchant.DictWithPWL('en_US', 'valid_spell_list_lower.txt')
    checker = SpellChecker(dictionary)
    tokenizer = get_tokenizer('en_US')

    customized_corrections = custom_corrections()

    message_interval = 100
    comics_list = []
    table_len = len(table)

    for j in range(table_len):

        # loop status message
        if (j % message_interval) == 0:
            print('Processing file {0} of {1}, which is {2:.0f}%'
                .format(j + 1, table_len, 100 * (j + 1) / table_len))

        panels_list = []
        for i in range(len(table.iloc[j, table_col])):
            panels_list.append(correct_string_misspellings(
                table.iloc[j, table_col][i], customized_corrections,
                character_names, dictionary, checker, tokenizer))

        comics_list.append(panels_list)

    text_corrected_col_name = 'text_spell_corrected'
    table[text_corrected_col_name] = comics_list

    table.to_csv('table.csv', sep='^', index=False)


if __name__ == '__main__':
    main()
