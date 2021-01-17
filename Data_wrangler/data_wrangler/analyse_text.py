"""This module analyses the reviews, paragraphs and customer tips to characterise the location using NLP
   multilabel model"""

import numpy as np


def convert_one_hot_encode(results):
    """Normalise mean scores and then convert them to one hot encoding"""
    one_hot_encode = {k: v / max(results.values()) for k, v in results.items()}
    one_hot_encode = {k: 1 if v >= 0.5 else 0 for k, v in one_hot_encode.items()}
    return one_hot_encode


def analyse_text(loc_dict, config, nlp):
    """Utilises Spacy multi label classification to characterise the style of location
       based on the text provided. Text provided are reviews, paragraphs and customer
       tips

       Note: This NLP model is the trained NLP model for multi-label classification
    """
    # get the combined reviews and tips
    combined_string = loc_dict['combined_reviews_tips']

    # add paragraph to the combined string
    if loc_dict['paragraph']:
        combined_string = "{} {}".format(combined_string, loc_dict['paragraph'])

    # run NLP to get mean scores
    if combined_string != '':
        sentences = [i for i in nlp(combined_string).sents]

        # form dictionaries
        score = {}  # to store score from nlp for each sentence
        mean_score = {}  # to store mean score

        # find out scores given by nlp
        for x in sentences:
            x = str(x)

            # skip nlp scoring if the string is empty
            if x != "":
                docx = nlp(str(x))
                for key in docx.cats:
                    if key not in score:
                        score[key] = []
                    score[key].append(docx.cats[key])

        # calculate mean NLP score for each of the categories
        for key in score:
            mean_score[key] = np.mean(score[key])

        # assign score to dictionary depending on user's specified config
        if config == 0:
            # convert to one hot encoding and assign back to dictionary
            loc_dict['styles_score_nlp'] = convert_one_hot_encode(mean_score)
        else:
            # assign raw scores
            loc_dict['styles_score_nlp'] = mean_score
    else:
        loc_dict['styles_score_nlp'] = {}

    return loc_dict
