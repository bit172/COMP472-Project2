from utils import *
import math
import pprint

v = n = s_factor = training_file = test_file = None


def count_c_frequencies(ts):
    """
    Counts the frequency of each characters in an array of tweet strings
    :param ts: list of tweets
    :return: dictionary of { character: # times character appears in all tweets }
    """
    bag = {}
    for t in ts:
        for c in t:
            if c in bag.keys():
                bag[c] += 1
            else:
                bag[c] = 1 + s_factor
    return bag


def total_c(categorized_tweets):
    """
    Count the total number of characters found in the tweets per language
    :param categorized_tweets: dictionary of tweets by language
    :return: dictionary of total number of characters based on language
    """
    c_totals = {}
    for language, tweets in categorized_tweets.items():
        count = 0
        for tweet in tweets:
            for character in tweet:
                count += 1
        count += total_c_in_v(v) * s_factor
        c_totals[language] = count
    return c_totals


#
def c_frequencies_in_langs(categorized_tweets):
    """
    Count the frequency for each character per language
    :param categorized_tweets: dictionary of tweets by language
    :return: dictionary of character frequencies with language key
    """
    frequencies = {}
    for language, tweets in categorized_tweets.items():
        if language in frequencies.keys():
            frequencies[language].append(count_c_frequencies(tweets))
        else:
            frequencies[language] = count_c_frequencies(tweets)
    return frequencies


#
def compute_cond_probs(frequencies, total_c_counts):
    """
    Find conditional probabilities for each c per lang
    :param frequencies: dictionary of character frequencies with language key
    :param total_c_counts: dictionary of total number of characters based on language
    :return: dictionary of conditional probabilities with language key
    """
    cond_probs = {}
    for lang, frequency in frequencies.items():
        bag = {}
        total = total_c_counts[lang]
        for c, count in frequency.items():
            bag[c] = math.log10(count / total)
        if len(bag) < total_c_in_v(v):  # if we don't have all characters in the bag
            bag['<NOT-APPEAR>'] = math.log10(s_factor / total)
        cond_probs[lang] = bag

    return cond_probs


def output_most_prob_lang_and_required_els(test_tweets, cond_probs):
    """
    Find most probable language for each tweet and
    store most prob lang and required elements in an output file
    :param test_tweets: list of testing tweets
    :param cond_probs: dictionary of conditional probabilities with language key
    :return: None
    """
    f = open(output_file_name(v, n, s_factor), "w")
    for test_tweet in test_tweets:
        probabilities = {}  # stores the probability of all languages for each tweet
        tweet = test_tweet[2]
        for language, c_probs in cond_probs.items():
            probabilities[language] = 0
            # compute the probability of each language by adding the probabilities of
            # each characters that appear in the tweet
            for c in tweet:
                if c in c_probs.keys():
                    probabilities[language] += c_probs[c]
                else:
                    probabilities[language] += c_probs['<NOT-APPEAR>']
        f.write(generate_output_str(probabilities, test_tweet))
    f.close()


def execute(input_v, input_n, input_s, input_train, input_test):
    global v, n, s_factor, training_file, test_file
    (v, n, s_factor, training_file, test_file) = (input_v, input_n, input_s, input_train, input_test)

    raw_training_tweets = read(training_file)
    categorize_tweets = categorize(raw_training_tweets, v)

    total_c_counts = total_c(categorize_tweets)
    frequencies = c_frequencies_in_langs(categorize_tweets)

    cond_probs = compute_cond_probs(frequencies, total_c_counts)
    # pprint.pprint(cond_probs, width=1)

    raw_test_tweets = read(test_file)
    test_tweets = process_tweets(raw_test_tweets, v)

    output_most_prob_lang_and_required_els(test_tweets, cond_probs)
    print(compute_accuracy(v, n, s_factor))