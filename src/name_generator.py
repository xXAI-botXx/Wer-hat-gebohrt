import random

def generate_akronym_name(list_of_words:list, n=10):
    generated_words = []
    for i in range(n):
        #word_len = random.randint(3, len(list_of_words))
        word_len = random.randint(3, 6)
        super_creative_word = ""
        cache_words = list_of_words.copy()

        for j in range(word_len):
            choice = random.choice(cache_words)
            cache_words.remove(choice)
            super_creative_word += choice[0:1]

        generated_words += [super_creative_word]

    return generated_words


key_words = ['drill', 'ai', 'feature-extraction', 'feature-engineering', 'feature-selection', 'data-loading', 'automated_software',
             'vorhersage', 'zeitreihen', 'tsfresh', 'timeseries', 'prediction', 'classification', 'klassifikation', 'machine-learning',
             'learning', 'user_interface', 'interactive', 'aki', 'hs', 'intelligent', 'preparing', 'who', 'extraction']


for suggestion in generate_akronym_name(key_words, 30):
    print(suggestion)

key_words = ['vadim', 'tobia', 'ippolito', 'antonio']

for suggestion in generate_akronym_name(key_words, 30):
    print(suggestion)
