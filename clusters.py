from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
import scipy as sp
import os

def dist_norm(v1, v2):
    v1_normalized = v1/sp.linalg.norm(v1.toarray())
    v2_normalized = v2/sp.linalg.norm(v2.toarray())
    delta = v1_normalized - v2_normalized
    return sp.linalg.norm(delta.toarray())

vectorizer = CountVectorizer(min_df=1, decode_error='ignore')

code_samples_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "code_samples")
if not os.path.isdir(code_samples_directory):
    print 'Code samples directory not found.'
    exit()

corpus = []

"""
for code_sample in os.listdir(code_samples_directory):
    f = open(os.path.join(code_samples_directory, code_sample))
    lines = [line.rstrip('\n') for line in f]
    f.close()
    corpus.extend(lines)
"""

for code_sample in os.listdir(code_samples_directory):
    f = open(os.path.join(code_samples_directory, code_sample))
    corpus.append(f.read().replace('\n', ' '))
    f.close()

vectorized = vectorizer.fit_transform(corpus)

num_languages = 5

km = KMeans(n_clusters=num_languages, init='random', n_init=1, verbose=1)
km.fit(vectorized)

test_file_name = raw_input('Enter the name of a file: ')
while test_file_name != 'quit':
    with open(test_file_name) as test_file:
    #python_vec = vectorizer.transform([line.rstrip('\n') for line in python_test_file])
        test_vec = vectorizer.transform([test_file.read().replace('\n', ' ')])
        test_label = km.predict(test_vec)[0]
        similar_indices = (km.labels_==test_label).nonzero()[0]

        similar = []
        for i in similar_indices:
            dist = sp.linalg.norm((test_vec - vectorized[i]).toarray())
            similar.append((dist, corpus[i]))
        similar = sorted(similar)
        print 'The most similar file has a normalized distance of {} and looks like this:'.format(similar[0][0])
        print similar[0][1]
        print 'The second most similar file has a normalized distance of {} and looks like this:'.format(similar[1][0])
        print similar[1][1]
        print 'The third most similar file has a normalized distance of {} and looks like this:'.format(similar[2][0])
        print similar[2][1]
        test_file_name = raw_input('Enter the name of a file: ')
