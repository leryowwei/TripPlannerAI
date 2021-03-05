"""This modules calculates the score for each label based on the paragraphs, descriptions and reviews of the location
   by finding if the words for a particular label is present in the text.
"""
from .constants import WORD_FINDER_LABELS
from .utils import form_str
import json


def wordfinder(preprocessed_para):
    """Find out if the words belonging to a specific label is in the paragraph provided.

       Return a list with all the labels that are found in the paragraph
    """
    wf_types = []
    for key, list_of_vals in WORD_FINDER_LABELS.items():
        check = any(text in list_of_vals for text in preprocessed_para.split())
        if check:
            wf_types.append(key)
    return wf_types


def wordfinder_main(loc_dict, config, textpreprocessor):
    """Calculate the score for each label based on the paragraphs, descriptions and reviews of the location
       The scores are dependent on the configuration specified by the user:
       Config 0 - One hot encoding. Each label set as 1 if any of the words of the label is found. Otherwise 0
       Config 1 - Weighted score - The text is divided to three categories: paragraphs, descriptions and tips/reviews.
                  For example, if romantic occurs in all three categories, romantic will have a score of 3.
       Config 2 - weighted score and normalised. Same as config 1 but the final scores will be normalised by the max score
                  so that the scores are all within the range of 0 to 1
    """
    wordfinder_list = []
    wordfinder_dic = {}

    # create dictionary based on each label
    for key in WORD_FINDER_LABELS:
        wordfinder_dic.update({key: 0})

    # calculate the scores for each label - different config has different ways of calculating the scores
    if config == 0:
        # combine everything into one big sentence
        sentences = form_str([loc_dict['foursquare_description'], loc_dict['paragraph'], loc_dict['combined_reviews_tips']])
        # pre-process the sentences
        pptext = textpreprocessor.preprocess_text(sentences, "pos")
        # check if any of the labels are found in the text
        wordfinder_list = wordfinder(pptext)
    elif config in [1, 2]:
        # consider description, paragraph and tips/reviews separately - different weightage
        # run pre-processing and check if any of the labels are found in the text using wordfinder function
        wordfinder_list = []

        for key in ['foursquare_description', 'paragraph', 'combined_reviews_tips']:
            if loc_dict[key]:
                sentence = form_str(loc_dict[key])
                wordfinder_list.extend(wordfinder(textpreprocessor.preprocess_text(sentence, "pos")))

    # (1) One hot encoding
    if config == 0:
        for i in wordfinder_list:
            wordfinder_dic.update({i: 1})
    # (2) word weightage
    elif config == 1:
        for i in wordfinder_list:
            wordfinder_dic.update({i: wordfinder_dic[i] + 1})
    # (3) Weighted/Normalised
    elif config == 2:
        for i in wordfinder_list:
            wordfinder_dic.update({i: wordfinder_dic[i] + 1})

        if sum(wordfinder_dic.values()) != 0:
            wordfinder_dic = {k: v / sum(wordfinder_dic.values()) for k, v in wordfinder_dic.items()}

    # assign scores back to master dict - create one key for one score
    for label in wordfinder_dic:
        key = "wordfinder_score_{}".format(label.lower())
        loc_dict[key] = wordfinder_dic[label]

    return loc_dict
