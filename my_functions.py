from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay, f1_score, precision_score, recall_score
from matplotlib import pyplot as plt
import pandas as pd
from collections import Counter
from itertools import islice
from string import punctuation



def get_distribution(data):
    '''
    Calculate the distribution of 'B' labels for each sublist in the input data.
    
    Parameters:
        data (list):
        A list of sublists, where each sublist contains tuples with two elements.
        The second element of the tuple represents the label ('B', 'I', 'O').

    Returns:
        dict:
        A dictionary where the keys are the indices of the sublists, and the values are
        the counts of 'B' labels in each corresponding sublist.
    '''
    return {i: len([x for x in t if (x[1] == 'B')]) for i, t in enumerate(data)}



def splitter(raw_data, split, distribution):
    '''
    Split the raw_data into training and testing sets based on a given ratio.

    Parameters:
        raw_data (list):
        A list of sublists, where each sublist represents a data bin.
        Each data bin contains words and labels (a 'sentence' or 'line') that need
        to be split into training and testing sets.
        
        split (float):
        The desired ratio for the split. It should be a value between 0 and 1,
        indicating the proportion of data to be used for training.

        distribution (dict):
        A dictionary containing the predefined distribution of 'B' labels for each
        sublist in the input raw_data. The keys are the indices of the sublists,
        and the values are the counts of 'B' labels in each corresponding sublist.
        This distribution can be obtained using the get_distribution function.

    Returns:
        tuple:
        A tuple containing two lists - train_bin and test_bin. These lists contain the
        sublists from the input raw_data, separated into the training and testing sets.
    '''
    train_bin = []
    test_bin = []
    ratio = split
    count = 0
    total = sum(distribution.values())

    for k, v in distribution.items():
        if count/total < ratio:
            train_bin.append(raw_data[k])
            count += v
        else:
            test_bin.append(raw_data[k])

    distr_train_bin = get_distribution(train_bin)
    distr_test_bin = get_distribution(test_bin)
    count_train_bin = sum(distr_train_bin.values())
    count_test_bin = sum(distr_test_bin.values())
    print(f"Desired split: {ratio}")
    print(f"Actual split: {round((count_train_bin/(count_train_bin + count_test_bin)),4)}")
    return train_bin, test_bin



def evaluator(y_true, y_pred, labels, size='small'):
    '''
    Evaluate the performance of a classifier by computing various metrics and displaying
    a classification report and a confusion matrix.

    Parameters:
        y_true (MatrixLike | ArrayLike):
        The ground truth labels for the classification task.
        It can be in matrix-like or array-like format.

        y_pred (MatrixLike | ArrayLike):
        The predicted labels for the classification task.
        It can be in matrix-like or array-like format, matching the shape of y_true.
        
        labels (ArrayLike):
        An array-like object containing the class labels for the problem.
        It is used in the classification report and confusion matrix to label each class.
        
        size (str):
        Optional. The size of the displayed confusion matrix.
        Possible values are 'small' (default) and 'big'. A bigger size provides more
        readability for larger confusion matrices.

    Returns:
        None: The function displays the computed metrics, classification report, and confusion matrix.

    Note:
        - The function makes use of the `accuracy_score`, `f1_score`, `precision_score`,
        `recall_score`, and `classification_report` functions from scikit-learn to compute
        the metrics and classification report.
        - The confusion matrix is displayed using matplotlib with the help of the
        `ConfusionMatrixDisplay` class from scikit-learn.
    '''
    print(f"accuracy: {accuracy_score(y_true, y_pred)}")
    print(f"f1 average: {f1_score(y_true, y_pred, average='macro')}")
    print()
    print(f"precision: {precision_score(y_true, y_pred, average=None)}")
    print(f"recall: {recall_score(y_true, y_pred, average=None)}")
    print(f"f1: {f1_score(y_true, y_pred, average=None)}")
    print()
    print(classification_report(y_true, y_pred, target_names=labels))

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    disp = ConfusionMatrixDisplay(cm, display_labels=labels)

    if size == 'big':
        fig, ax = plt.subplots(figsize=(9, 7))
    else:
        fig, ax = plt.subplots()

    disp.plot(ax=ax, cmap=plt.cm.Blues, values_format='d')

    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.xticks(rotation='vertical')
    plt.tight_layout()
    plt.show()



def word_analysis(dataframe, column):
    '''
    Analyzes tagged entities in a DataFrame and returns statistics on word counts, common bi-grams, tri-grams, and entity tags.

    Parameters:
        dataframe (pandas.DataFrame): A pandas DataFrame containing tagged entities.
        column (str): The name of the column containing entity tags.

    Returns:
        pandas.DataFrame: A new DataFrame with the following columns:
            - 'word_count': The most common words across all tagged entities with their corresponding counts.
            - 'bi-grams_count': The most common bi-grams (consecutive word pairs) across all tagged entities with their counts.
            - 'tri-grams_count': The most common tri-grams (consecutive word triplets) across all tagged entities with their counts.
            - 'B_count': The most common 'B' tags (beginning of entity) with their counts.
            - 'I_i_count': The most common first 'I' tags (inside of entity with word spans > 1) with their counts.
            - 'I_ii_count': The most common second 'I' tags (inside of entity with word spans > 2) with their counts.
            - 'I_iii_count': The most common third 'I' tags (inside of entity with word spans > 3) with their counts.
            - 'I_-i_count': The most common last 'I' tags (inside of entity at the end) with their counts.

        Note:
            If there are fewer than 20 unique elements for a category (e.g., bi-grams, tri-grams, tags),
            the DataFrame will have the missing entries filled with (None, 0).
    '''
    # initialise new df for results

    df = pd.DataFrame()

    # create list of strings of tagged entites

    entity_list = [' '.join(m['word']) for _, m in dataframe.groupby(dataframe[column].eq('B').cumsum().loc[dataframe[column] != 'O'])]

    # get common words and add to df with counts

    entity_all = ' '.join(entity_list)
    entity_all = entity_all.split()
    word_counts = Counter(entity_all)
    df['word_count'] = word_counts.most_common(20)

    # get common bi-grams and add to df with counts

    sequence_counter = Counter()
    for string in entity_list:
        words = string.split()
        for i in range(len(words) - 1):
            sequence = (words[i], words[i + 1])
            sequence_counter[sequence] += 1
    df['bi-grams_count'] = sequence_counter.most_common(20)

    # get common tri-grams and add to df with counts

    sequence_counter = Counter()
    for string in entity_list:
        words = string.split()
        for i in range(len(words) - 2):
            sequence = (words[i], words[i + 1], words[i + 2])
            sequence_counter[sequence] += 1

    most_common = sequence_counter.most_common(20)
    filled_most_common = list(islice(most_common, 20)) + [(None, 0)] * (20 - len(most_common))
    df['tri-grams_count'] = filled_most_common

    # get the B tag and add to df with counts

    b_tag = dataframe.loc[dataframe[column] == 'B', 'word'].tolist()
    word_counts = Counter(b_tag)
    most_common = word_counts.most_common(20)
    filled_most_common = list(islice(most_common, 20)) + [(None, 0)] * (20 - len(most_common))
    df['B_count'] = filled_most_common

    # get the first I tag for entities with word spans > 1

    i_ent = dataframe.loc[(dataframe[column] == 'I')
                   & (dataframe[column].shift(1) == 'B'),
                   'word'].tolist()
    word_counts = Counter(i_ent)
    most_common = word_counts.most_common(20)
    filled_most_common = list(islice(most_common, 20)) + [(None, 0)] * (20 - len(most_common))
    df['I_i_count'] = filled_most_common

    # get the second I tag for entities with word spans > 2

    ii_ent = dataframe.loc[(dataframe[column] == 'I')
                    & (dataframe[column].shift(1) == 'I')
                    & (dataframe[column].shift(2) == 'B'),
                    'word'].tolist()

    word_counts = Counter(ii_ent)
    most_common = word_counts.most_common(20)
    filled_most_common = list(islice(most_common, 20)) + [(None, 0)] * (20 - len(most_common))
    df['I_ii_count'] = filled_most_common

    # get the third I tag for entities with word spans > 3

    iii_ent = dataframe.loc[(dataframe[column] == 'I')
                     & (dataframe[column].shift(1) == 'I')
                     & (dataframe[column].shift(2) == 'I')
                     & (dataframe[column].shift(3) == 'B'),
                     'word'].tolist()

    word_counts = Counter(iii_ent)
    most_common = word_counts.most_common(20)
    filled_most_common = list(islice(most_common, 20)) + [(None, 0)] * (20 - len(most_common))
    df['I_iii_count'] = filled_most_common

    # get the last I tag for entities

    last_i_ent = dataframe.loc[(dataframe[column] == 'I')
                        & (dataframe[column].shift(-1) == 'O'),
                        'word'].tolist()

    word_counts = Counter(last_i_ent)
    most_common = word_counts.most_common(20)
    filled_most_common = list(islice(most_common, 20)) + [(None, 0)] * (20 - len(most_common))
    df['I_-i_count'] = filled_most_common

    # start count from 1 and rename index column

    df.index += 1
    df.columns.name = 'rank'

    return df



def O_checker(list_of_lists):
    '''
    Checks the presence of 'O' labels in a list of lists representing tagged elements.

    Parameters:
        list_of_lists (list): A list of lists containing tagged elements, where each sublist contains
        tuples of the form (word, label).

    Prints:
        Prints the number of lines (sublists) where all elements have the label 'O' (no BI labels).
        Prints the ratio of lines with no BI labels to the total number of lines (sublists).
    '''
    count = 0
    total_lists = len(list_of_lists)
    for sublist in list_of_lists:
        all_elements_O = all(t[1] == 'O' for t in sublist)
        if all_elements_O:
            count += 1
    ratio = count / total_lists if total_lists > 0 else 0
    print(f"Number of lines with no BI labels: {count}")
    print(f"Ratio: {round(ratio, 3)}")



def replacer(word):
    '''
    Replaces extraneous characters present in a word with specified replacements.

    Parameters:
        word (str): The input word that may contain extraneous characters.

    Returns:
        str: The word with extraneous characters replaced as follows:
            - Replaces '_', '/', '[', and ']' with an empty string ''.
            - Replaces '&amp;' with '&' (replaces HTML-encoded ampersand).
    '''
    chars = "_/[]"
    for char in chars:
        word = word.replace(char, '')
    word = word.replace('&amp;', '&')
    return word



def get_tokens(tokens):
    '''
    A generator function to reconcile spaCy NER with the original enumeration of
    the letters in order to preserve true label alignment.

    The function handles cases where only possessive noun forms and punctuation present a
    problem with aligning labels with word enumeration, so they are treated as exceptions.

    Parameters:
        tokens (iterable): An iterable of tuples representing tokens and their types.
        Each tuple contains three elements: (word, token_type, next_token).

    Yields:
        tuple: A tuple containing the next token and its corresponding token type.

    Example:
         token_data = [
             ('This', 'O', 'is'),
             ('a', 'O', 'sample'),
             ('text', 'B', 'with'),
             ('an', 'I', 'exception'),
             ("'s", 'O', 'and'),
             ('punctuation', 'O', '.')
         ]
         token_generator = get_tokens(token_data)
         next(token_generator)  # Output: ('This', 'O')
         next(token_generator)  # Output: ('is', 'O')
         next(token_generator)  # Output: ('a', 'O')
         next(token_generator)  # Output: ('sample', 'O')
         next(token_generator)  # Output: ('text', 'B')
         next(token_generator)  # Output: ('with', 'I')
         next(token_generator)  # Output: ('an', 'O')
         next(token_generator)  # Output: ('exception', 'I')
         next(token_generator)  # Output: ("'s", 'O')
         next(token_generator)  # Output: ('and', 'O')
         next(token_generator)  # Output: ('punctuation', 'O')
         next(token_generator)  # Raises StopIteration
    '''
    it = iter(tokens)
    _, token_type, next_token = next(it)
    word = yield
    while True:
        if next_token == word:
            word = yield next_token, token_type
            _, token_type, next_token = next(it)
        else:
            _, new_tt, tmp = next(it)
            next_token += tmp
            if tmp != "'s" and tmp not in punctuation:
                token_type = new_tt



def preprocess_for_lexical(data):
    '''
    Normalizes the input data for lexical look-up by converting all words to lower case and removing punctuation.

    Parameters:
        data (list of lists): A list of lists containing tuples representing words and their corresponding tags.

    Returns:
        list of lists: A new list of lists with each word converted to lower case and punctuation removed,
        while preserving the original tags.
    '''
    processed_data = []
    for sentence in data:
        processed_sentence = []
        for word, tag in sentence:
            word = word.lower()
            word = word.translate(str.maketrans("", "", punctuation))
            processed_sentence.append((word, tag))
        processed_data.append(processed_sentence)
    return processed_data



def lexi_maker(train_bin):
    '''
    Creates a lexical resource from the training data to store word frequencies based on their labels.

    Parameters:
        train_bin (list of lists): A list of lists containing tuples representing words and their corresponding labels.

    Returns:
        dict: A dictionary representing the lexical resource where each word is a key, and the value is a sub-dictionary
        with 'B' and 'I' keys. The 'B' key stores the count of the word as a 'B' tag, and the 'I'
        key stores the count of the word as an 'I' tag.
    '''

    lexical_dict = {}
    for sentence in train_bin:
        for word, label in sentence:
            if label == 'O':
                continue
            if word not in lexical_dict:
                lexical_dict[word] = {'B': 0, 'I': 0}
            lexical_dict[word][label] += 1
    return lexical_dict



def predict_labels(data, lex_dict):
    '''
    Predicts entity labels in the test data based on the lexical resource constructed from the training data.

    Parameters:
        data (list of lists): A list of lists containing tuples representing words and their corresponding tags.
        lex_dict (dict): A dictionary representing the lexical resource constructed from the training data,
        where each word is a key, and the value is a sub-dictionary with 'B' and 'I' keys. The 'B' key stores
        the count of the word as a 'B' tag, and the 'I' key stores the count of the word as an 'I' tag.

    Returns:
        list of lists: A new list of lists with predicted entity labels based on the lexical resource.
        Each sublist contains tuples representing words and their predicted labels.
    '''
    predicted_data = []
    for sentence in data:
        predicted_sentence = []
        for word,_ in sentence:
            if word not in lex_dict:
                predicted_sentence.append((word, 'O'))
            else:
                b_count = lex_dict[word]['B']
                i_count = lex_dict[word]['I']
                if b_count >= i_count:
                    predicted_sentence.append((word, 'B'))
                else:
                    predicted_sentence.append((word, 'I'))          
        predicted_data.append(predicted_sentence)
        
    return predicted_data 