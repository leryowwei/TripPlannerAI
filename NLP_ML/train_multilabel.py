"""
This module trains spacy's multi-label classifiction function to recognise different
styles crafted for the trip planner algorithm.

Example of styles are cultural, nightlife, foodie, adventurous etc...

(1) The code first reads in the CSV file which contains the training data.
(2) Then, it trains the NLP model using the data.
(3) The trained NLP model is saved in the /NLP_ML/nlp_multilabel_model folder 
and is accessible to other codes.

For more details, see the documentation:
* Training: https://spacy.io/usage/training

"""
import spacy
import csv
import os
import pandas as pd
import numpy as np
from pathlib import Path
from spacy.util import minibatch, compounding

# ---- User defined input/constants ------
NLP_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
PATH_TRAIN_DATA_CSV = os.path.join(NLP_FOLDER_PATH, "style_of_travel.csv")

# NLP model
NLP_MODEL = "en_core_web_lg"

# output directory for NLP model
OUTPUT_DIR_MODEL = os.path.join(NLP_FOLDER_PATH, "nlp_multilabel_model")

# NLP training settings
NLP_ITER = 50
DATA_LIMIT = 5000

# categories in training data (NEED TO CHANGE ROW 56 AS WELL)
CATEGORIES = ['Cultural', 'Adventurous', 'Relaxing', 'Foodie', 'Nightlife', 'Shopping', 'Romantic', 'Nature']

# ---------------------------------------
def read_training_data():
    #read in data
    train_df=pd.read_csv(PATH_TRAIN_DATA_CSV, encoding="unicode_escape", quoting=csv.QUOTE_ALL, engine="python")
    
    # remove blank data
    train_df['Text'].replace('', np.nan, inplace=True)
    train_df.dropna(subset=['Text'], inplace=True)
    train_df
    
    # remove data with n/a
    train_df = train_df[['Text'] + CATEGORIES].dropna()
    
    # list of tuples of text and labels
    # TODO - NEED TO IMPROVE THIS
    train_df['tuples'] = train_df.apply(lambda row: (row['Text'],[row['Cultural'],row['Adventurous'],
                                                                  row['Relaxing'], row['Foodie'], row['Nightlife'], 
                                                                  row['Shopping'], row['Romantic'], row['Nature']]), axis=1)
    train_data = train_df['tuples'].tolist()
    
    return train_data

def load_data(train_data, limit=0, split=0.8):
    np.random.shuffle(train_data)
    train_data = train_data[-limit:]
    texts, cats = zip(*train_data)
    split = int(len(train_data) * split)
    return (texts[:split], cats[:split]), (texts[split:], cats[split:])

def evaluate(tokenizer, textcat, texts, cats):
    docs = (tokenizer(text) for text in texts)
    tp = 1e-8  # True positives
    fp = 1e-8  # False positives
    fn = 1e-8  # False negatives
    tn = 1e-8  # True negatives

    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]['cats']
        for label, score in doc.cats.items():
            if label not in gold:
                continue
            if score >= 0.5 and gold[label] >= 0.5:
                tp += 1.
            elif score >= 0.5 and gold[label] < 0.5:
                fp += 1.
            elif score < 0.5 and gold[label] < 0.5:
                tn += 1
            elif score < 0.5 and gold[label] >= 0.5:
                fn += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f_score = 2 * (precision * recall) / (precision + recall)
    return {'textcat_p': precision, 'textcat_r': recall, 'textcat_f': f_score}

def train_multilabel(model=None, output_dir=None, n_iter=100, n_texts = 5000):
    """ Train spacy model for multi-label text classification """

    # load or create NLP model
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    # add the text classifier to the pipeline if it doesn't exist
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'textcat' not in nlp.pipe_names:
        textcat = nlp.create_pipe('textcat')
        nlp.add_pipe(textcat, last=True)
    # otherwise, get it, so we can add labels to it
    else:
        textcat = nlp.get_pipe('textcat')

    # add labels to the model    
    for label in CATEGORIES:
        textcat.add_label(label)

    # read training data from csv file
    train_data = read_training_data()

    # split data set to training and testing data
    print("Loading training data...")
    (train_texts, train_cats), (dev_texts, dev_cats) = load_data(train_data, limit=n_texts)
    print("Using {} examples ({} training, {} evaluation)"
          .format(len(train_texts) + len(dev_texts), len(train_texts), len(dev_texts)))

    # form train data from dataset
    x = []

    for ite in range(len(train_cats)):
      tempx = {}
      tempx['cats'] = {}
      for ite2, label in enumerate(CATEGORIES):
        tempx['cats'][label] = train_cats[ite][ite2]

      x.append(tempx)
    print(x)

    train_data = list(zip(train_texts,x))

    # convert dev cats into dict
    x = []
    for ite in range(len(dev_cats)):
      tempx = {}
      tempx['cats'] = {}
      for ite2, label in enumerate(CATEGORIES):
        tempx['cats'][label] = dev_cats[ite][ite2]
      x.append(tempx)

    dev_cats = x

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'textcat']
    with nlp.disable_pipes(*other_pipes):  # only train textcat
        optimizer = nlp.begin_training()
        print("Training the model...")
        print('{:^5}\t{:^5}\t{:^5}\t{:^5}'.format('LOSS', 'P', 'R', 'F'))
        for i in range(n_iter):
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(train_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.2,
                          losses=losses)
            with textcat.model.use_params(optimizer.averages):
                # evaluate on the dev data split off in load_data()
                scores = evaluate(nlp.tokenizer, textcat, dev_texts, dev_cats)
            print('{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}'  # print a simple table
                  .format(losses['textcat'], scores['textcat_p'],
                          scores['textcat_r'], scores['textcat_f']))
            
    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

#### Run code #############
train_multilabel(model=NLP_MODEL, output_dir=OUTPUT_DIR_MODEL, n_iter=NLP_ITER, n_texts=DATA_LIMIT)