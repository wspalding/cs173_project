import numpy
import nltk
from nltk.tag import StanfordNERTagger
import os
import sys
import pandas
import time

books_dir = 'books/'
character_dir = 'character_lists/'
results_dir = 'results/'


def main():
    # get args (program is sys.argv[0], args start at 1)
    for arg in sys.argv[1:]:
        print(arg)
#    print("working")

    tagger = StanfordNERTagger('stanford_ner/' + 'classifiers/english.muc.7class.distsim.crf.ser.gz',
                           'stanford_ner/' + 'stanford-ner-3.9.2.jar')

    

    # import datasets
    
    for file in os.listdir(books_dir):
        start = time.time()
#        print(file)
        results_dict = {}
        book_name = file.split('.')[0]
        
#        print("book name = ", book_name)
        results_file = book_name + '_resuts.csv'
        char_file = os.listdir(character_dir + book_name)[0]
        char_list = pandas.read_csv(character_dir + book_name + '/' + char_file, engine='python')[['name']].copy()
        char_list['in_book'] = False
        char_list['in_character_list'] = True
        
        print("opening file: ", file)
        print("results in: ", results_file)
        print("character_list size: \n", char_list.head())

        f = open(books_dir + file)
        i = 0

        for line in f:
            # run tagger
            results = tagger.tag(line.split())
#            print("line: ", line)
            for result in results:
                tag_val = result[0]
                tag_type = result[1]
                if tag_type == 'PERSON':
                    try:
                        search = char_list['name'].str.contains(tag_val)
                        if (search == False).all():
                            char_list = char_list.append({'name': tag_val, 'in_book': True, 'in_character_list': False}, ignore_index=True)
                        else:
                            char_list.loc[search,'in_book'] = True
                        print('type: ', tag_type, 'val: ', tag_val)
                    except:
                        print('type: ', tag_type, 'val: ', tag_val, 'ERROR')
            if i % 100 == 0:
                char_list.to_csv(results_dir + results_file)
                print('{} lines completed'.format(i))
            i += 1
        char_list.to_csv(results_dir + results_file)
        print(i)
        
        end = time.time()
        print('time elapsed: ', end - start, ' seconds')
#            print("\n")



if __name__ == "__main__":
    main()

print("done")

