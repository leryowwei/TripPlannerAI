from .constants import MY_STOPWORDS


class TextPreprocessor():

    def __init__(self, spacy_model, sentiment_analyzer):
        """
        Text preprocessing includes steps:
            1. Stop words removal
            2. Lemmatization
            3. Sentiment analyser
            4. Remove duplicates from the string [PENDING]
        """
        self.nlp = spacy_model
        self.sentiment_analyzer = sentiment_analyzer
        # define my own list of stopwords
        all_stopwords = self.nlp.Defaults.stop_words
        all_stopwords.difference_update({'no', 'not'})
        all_stopwords.update(MY_STOPWORDS)
        self.all_stopwords = all_stopwords

    def _stop_words_remover(self, doc):
        """Remove stopwords from tokenized sentence"""
        return [word for word in doc if not word.text.lower() in self.all_stopwords]

    @staticmethod
    def _lemmatize(doc):
        """Lemmatize tokenized sentence"""
        return [t.lemma_ for t in doc]

    @staticmethod
    def _lowercase(doc):
        """Convert text to lowercase"""
        return doc.lower()

    def sentiment_analyzer_scores(self, doc):
        """ Sentiment analyzer using vader
        https://medium.com/analytics-vidhya/simplifying-social-media-sentiment-analysis-using-vader-in-python-f9e6ec6fc52f
        """
        # join tokenized sentence
        sentence = " ".join(doc)
        score = self.sentiment_analyzer.polarity_scores(sentence)
        if score['compound'] >= 0.05:
            outcome = "pos"
        elif score['compound'] <= -0.05:
            outcome = "neg"
        else:
            outcome = "neu"
        return outcome

    def convert_para_to_sentences(self, para):
        """Convert a paragraph to sentences"""
        return [i for i in self.nlp(para).sents]

    def preprocess_text(self, para, sentiment_to_use=None):
        """Pre-process text"""

        # check that sentiment_to_use is defined properly
        if sentiment_to_use not in [None, 'pos', 'neg', 'neu']:
            raise ValueError('Sentiment to use: {}, specified by user is not recognised...'.format(sentiment_to_use))

        # change to lower case
        para = self._lowercase(para)

        # convert paragraph into sentences - if only one sentence, it places the sentence in a list
        sentences = self.convert_para_to_sentences(para)

        # loop through each sentence and pre-process the sentences
        # if sentiment_to_use is set as None, no sentence will be filtered away. Otherwise, only sentence with the
        # type of sentiment specified will be included in the results returned
        results = []
        for sentence in sentences:
            if sentiment_to_use:
                if self.sentiment_analyzer_scores(str(sentence)) == sentiment_to_use:
                    flag = True
                else:
                    flag = False
            else:
                flag = True

            if flag:
                doc = self.nlp(str(sentence))
                # remove stop words
                without_stop_words = self._stop_words_remover(doc)
                # lemmatize
                results.extend( self._lemmatize(without_stop_words))

        # Duplicates Remover - TODO: Should this be in?? Does it matter if there is duplciates?
        results = list(dict.fromkeys(results))

        # return as actual string
        return " ".join(results)
