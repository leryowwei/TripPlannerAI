""" Data_wrangler python package's main entry point code

    To run the package, please use command:
        python -m data_wrangler [-h] --inp path_to_data [--wf wordfinder_config] [--ml multilabel_config]

    args:
        [ ]: optional arguments
        path_to_data: provide folder path to where the data_scraper .json files are stored
        wordfinder_config: Default config = 0. Configuration for how scores are calculated in word finder.
                        0 = one hot encoding, 1 = weighted words, 2 = weighted and normalised
        multilabel_config: Default config = 0. Configuration for how scores are calculated in nlp multilabel
                        classification. 0 = one hot encoding, 1 = raw scores
"""
import spacy
import os
import argparse
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .utils import read_json_file, logger, read_excel_as_df, write_output_pickle
from .unpack_dict import unpack_dict
from .validate import validate_data
from .analyse_text import analyse_text
from .text_preprocessor import TextPreprocessor
from .word_finder import wordfinder_main
from .duration import find_duration_of_loc
from .pp_dict import pp_dict


def main(inp_path, wf_config, ml_config):
    """ Main function for data wrangler
    """
    start = datetime.now()

    # set up relevant paths
    parent_path = os.path.abspath('..')
    nlp_mm_path = os.path.join(parent_path, 'NLP_ML', 'nlp_multilabel_model')
    nlp_loc_path = os.path.join(parent_path, 'NLP_ML', 'nlp_loc_model')
    misc_path = os.path.join(parent_path, 'Miscellaneous')
    output_path = os.path.join(parent_path, 'Data_scraper', 'output_data')

    # check if input data path exist
    if not os.path.exists(inp_path):
        raise FileNotFoundError('Path for data_scraper data: {} does not exist...'.format(inp_path))
    else:
        logger.info('Path to data_scraper data: {} provided by user...'.format(inp_path))

    # log message about configurations for word finder and NLP multilabel classification
    add_text = {0: 'one hot encoding', 1: 'weightage words', 2: 'Weightage and normalised'}
    logger.info('Word finder configuration: {} - {}, defined by user...'.format(wf_config, add_text[wf_config]))

    add_text = {0: 'one hot encoding', 1: 'raw score'}
    logger.info('NLP Multilabel Classification configuration: {} - {}, defined by user...'.format(ml_config,
                                                                                                  add_text[ml_config]))

    # create output data folder
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    # check if categories excel file exist. If yes, read in the sheets
    venue_cat_path = os.path.join(misc_path, 'venue_categories.xlsx')
    logger.info("Reading in venue categories from {}...".format(venue_cat_path))
    if os.path.exists(venue_cat_path):
        venue_categories = {'google': read_excel_as_df(venue_cat_path, 'Google', lower=True),
                            'foursquare': read_excel_as_df(venue_cat_path, 'Foursquare', lower=True),
                            'tag_duration': read_excel_as_df(venue_cat_path, 'Tag_duration', lower=True)}
    else:
        raise FileNotFoundError('Google/foursquare file does not exist in {}...'.format(venue_cat_path))

    # load NLP models - Multilabel
    logger.info("Loading Spacy Multilabel model...")
    try:
        nlp_multilabel = spacy.load(nlp_mm_path)
    except:
        raise ValueError(
            "NLP multilabel model not found. Please check if the trained model is in {}.".format(nlp_folder_path) +
            "Otherwise, please run the script /NLP_ML/train_entity.py.")

    # load NLP models - loc
    logger.info("Loading Spacy Loc model...")
    try:
        nlp_loc = spacy.load(nlp_loc_path)
    except:
        raise ValueError("NLP loc model not found. Please check if the trained model is in {}.".format(nlp_loc_path) +
                         "Otherwise, please run the script /NLP_ML/train_entity.py.")

    # create vader sentiment analyzer object
    analyser = SentimentIntensityAnalyzer()

    # create textpreprocessor object
    textpreprocessor = TextPreprocessor(nlp_loc, analyser)

    # start to post-process all data
    inp_dict = {}
    count = 1

    logger.info("Post-processing json files...")

    for filename in os.listdir(inp_path):
        # read in all json files from input data path and store as dictionary - ignore TMP files
        if filename.endswith('.json') and not filename.startswith('TMP'):
            # (1) read in json files and store as dictionary
            tmp_dict = read_json_file(os.path.join(output_path, filename))
            logger.info("-------- {}. {} --------".format(count, tmp_dict['name']))

            # (2) validate trip advisor and api data - set them to empty dict if not valid when compared to google data
            tmp_dict = validate_data(tmp_dict)

            # (2) unpack json dictionaries to a standard dictionary
            tmp_dict = unpack_dict(tmp_dict)

            # (3) post-process dictionary to add tags, post-process reviews and additional info not available from APIs
            tmp_dict = pp_dict(tmp_dict, venue_categories)

            # (4) post-process reviews to characterise the location
            # run NLP and word finder on the reviews to characterise the location
            tmp_dict = analyse_text(tmp_dict, ml_config, nlp_multilabel)
            tmp_dict = wordfinder_main(tmp_dict, wf_config, textpreprocessor)

            # (5) post-process reviews to find out the suggested duration for the location
            tmp_dict = find_duration_of_loc(tmp_dict, nlp_loc)

            # (6) remove unwanted keys from dictionary as we don't need them at all
            for key in ['reviews', 'combined_reviews_tips']:
                del tmp_dict[key]

            # (7) store dictionary to final dictionary
            inp_dict[tmp_dict['name']] = tmp_dict

            count = count + 1

    # convert final data to pandas dataframe and write out as output files
    logger.info('-----------------------')
    logger.info('Finished compiling data. Converting them to dataframe...')
    output_file_name = 'TripPlannerData_{}'.format(datetime.today().strftime('%Y%m%d_%H%M%S'))
    df = pd.DataFrame.from_dict(inp_dict, orient='index')
    df.to_html('{}.html'.format(output_file_name))
    logger.info('Output html file created as {}.html...'.format(output_file_name))
    write_output_pickle(df, '', output_file_name)

    # record time taken 
    end = datetime.now()
    time_taken = end - start
    logger.info('Process completed...')
    logger.info('Time taken for the process: {}'.format(time_taken))


if __name__ == "__main__":
    # setup argparser
    parser = argparse.ArgumentParser(description='Data scraping engine for trip planner AI tool...')
    parser.add_argument('--inp', type=str,
                        help='Path to the folder where all the json files generated by data scraper are stored.')
    parser.add_argument('--wf', type=int, default=0, choices=[0, 1, 2, 3],
                        help='Default config = 0. Configuration for how scores are calculated in word finder. '
                             '0 = one hot encoding, 1 = weighted words, 2 = weighted and normalised')
    parser.add_argument('--ml', type=int, default=0, choices=[0, 1],
                        help='Default config = 0. Configuration for how scores are calculated in nlp multilabel '
                             'classification. 0 = one hot encoding, 1 = raw scores')
    args = parser.parse_args()

    # call main function
    main(args.inp, args.wf, args.ml)
