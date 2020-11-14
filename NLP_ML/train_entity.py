"""
This module trains spacy's named entity recogniser:
    
(1) improve spacy's prediction for entity 'LOC' so that it can
recognise the places/locations that we are interested in.
(2) train spacy to recognise a new entity called 'duration'. i.e. time to spend at once location

e.g. 1. Have a cup of tea at Cafe Max. Cafe Max will be the location that we want.
e.g. 2. It has been a great adventure and we've spent 2 hours there. 2 hours is the duration.

Trained NLP model is saved in the /NLP_ML/nlp_loc_model folder and is accessible to other codes.

For more details, see the documentation:
* Training: https://spacy.io/usage/training
* NER: https://spacy.io/usage/linguistic-features#named-entities

"""
import plac
import random
import warnings
import spacy
import os
from pathlib import Path
from spacy.util import minibatch, compounding

# ---- User defined input/constants ------
NLP_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))

# NLP model
NLP_MODEL = "en_core_web_lg"

# output directory for NLP model
OUTPUT_DIR_MODEL = os.path.join(NLP_FOLDER_PATH, "nlp_loc_model")

# NLP training settings
NLP_ITER = 50

# ----------- training data to train spacy model -------------
TRAIN_DATA = [
    # --- LOC ---
    #example
    ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
    ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
    #singapore
    ("Experience the mythological Ten Courts of Hell at Haw Par Villa", {"entities": [(50, 63, "LOC")]}),
    ("Occupy a table at New Ubin Seafood", {"entities": [(18, 34, "LOC")]}),
    ("Stop and smell the roses at Gardens by the Bay", {"entities": [(28, 46, "LOC")]}),
    ("Explore the island via the Coast-to-Coast (C2C) Trail", {"entities": [(27, 53, "LOC")]}),
    ("Explore contemporary Nordic cuisine Restaurant Zén", {"entities": [(36, 50, "LOC")]}),
    ("Walk through Bukit Brown Cemetery (if you dare)", {"entities": [(13, 33, "LOC")]}),
    ("Traipse around Jewel Changi Airport", {"entities": [(15, 35, "LOC")]}),
    ("Visit SEA Aquarium at Resorts World Sentosa", {"entities": [(6, 43, "LOC")]}),
    #langkawi
    ("Kuah Night Market", {"entities": [(0, 17, "LOC")]}),
    ("Visit Eagle Square", {"entities": [(6, 18, "LOC")]}),
    ("Visit the Art in Paradise 3D Museum", {"entities": [(10, 35, "LOC")]}),
    #penang
    ("Paya Terubong Nasi Lemak | 5 AM", {"entities": [(0, 24, "LOC")]}),
    ("5.00 pm: Visit the Buddhist Temples of Pulau Tikus", {"entities": [(19, 50, "LOC")]}),
    ("Air Itam Sister Curry Mee | 8AM", {"entities": [(0, 25, "LOC")]}),
    ("CY Choy Road Hokkien Mee | 7AM", {"entities": [(0, 24, "LOC")]}),]

# ---------------------------------------------------------

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)

def train_spacy_entity(model=None, output_dir=None, n_iter=100):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    # only train NER
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
        # show warnings for misaligned entity spans once
        warnings.filterwarnings("once", category=UserWarning, module='spacy')

        # reset and initialize the weights randomly – but only if we're
        # training a new model
        if model is None:
            nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.2,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            print("Losses", losses)

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        for text, _ in TRAIN_DATA:
            doc = nlp2(text)
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
            print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

#------------------------------------------------
# run the code - loads global spacy model and save it in a different location
train_spacy_entity(model=NLP_MODEL, output_dir=OUTPUT_DIR_MODEL, n_iter=NLP_ITER )