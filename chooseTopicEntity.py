# -*- coding:utf-8 -*-

import csv
import tsv
import json
import pandas as pd


def extract_by_new_rules():
    # already change "tosh.o" into "tosh"
    with open("querys.txt.json", 'r') as load_f:
        querys = json.load(load_f)
        csv_file = open("entities.csv", 'wb')
        writer = csv.writer(csv_file)
        total = len(querys["sentences"])
        recall = 0
        query_id = 0
        single_noun = 0 # topic entity is a single noun
        double_noun = 0 # noun list is multiple, but in ease, we selece the last noun as our topic entity
        for item in querys["sentences"]:
            writing_list = []
            flag = [0] * 25  # for continuing noun sequence
            noun_list_index = []
            for word in item["tokens"]:
                string = word["originalText"]
                index = word["index"]
                if word["pos"] == "NN" or word["pos"] == "NNS" or word["pos"] == "NNPS" or word["pos"] == "NNP":
                    noun_list_index.append(word["index"])

                # continuing noun sequence
                if (flag[word["index"]] == 0) and \
                        (word["pos"] == "NN" or word["pos"] == "NNS" or word["pos"] == "NNPS" or word["pos"] == "NNP"):
                    while ((index < len(item["tokens"])) and (flag[index] == 0) and
                            item["tokens"][index]["pos"] == "NN" or item["tokens"][index]["pos"] == "NNS" or
                            item["tokens"][index]["pos"] == "NNP" or item["tokens"][index]["pos"] == "NNPS"):
                            string = string + ' ' + item["tokens"][index]["originalText"]
                            flag[index] = 1
                            index += 1
                    flag[index] = 1
                    if string != word["originalText"]:
                        writing_list.append(string)
                    elif index < len(item["tokens"]) and item["tokens"][index]["pos"] == "POS":
                        writing_list.append(string)

                # adjective

                elif word["pos"] == "JJ":
                    i = index
                    while i < len(item["tokens"]) and flag[i] == 0:
                        if (item["tokens"][i]["pos"] == "NN" or item["tokens"][i]["pos"] == "NNS" or
                                item["tokens"][i]["pos"] == "NNP" or item["tokens"][i]["pos"] == "NNPS"):
                            string = string + ' ' + item["tokens"][i]["originalText"]
                            flag[i] = 1
                            i += 1
                        else:
                            break
                    flag[i] = 1
                    if string != word["originalText"]:
                        writing_list.append(string)
                    elif (word["ner"] == "NATIONALITY" or word["ner"] == "COUNTRY" or
                          word["ner"] == "STATE_OR_PROVINCE" or word["ner"] == "LOCATION"):
                        writing_list.append(string)

            if writing_list == []:
                single_noun += 1
            if writing_list == [] and noun_list_index != []:
                if len(noun_list_index) > 1:
                    double_noun += 1
                writing_list.append(item["tokens"][noun_list_index[len(noun_list_index)-1]-1]["originalText"])

            if writing_list:
                recall += 1
            else:
                print(item["index"])
            query_id += 1
            # print(writing_list)
            # writer.writerow(writing_list)
            # entities_in_list = [writing_list]
            # writer.writerow(entities_in_list)

        csv_file.close()
        print(recall * 1.0 / total)
        print(single_noun * 1.0 / total)
        print(double_noun * 1.0 / total)


def tag():
    l = open("querys.txt.json", 'r')
    result = open("tag-for-all-word-query.csv", "wb")
    writer = csv.writer(result)
    json_file = json.load(l)
    for item in json_file["sentences"]:
        writing_list = []
        final = ""
        for word in item["tokens"]:
            final += word["originalText"] + "//" + word["pos"] + ' '
        writing_list.append(item["index"])
        writing_list.append(final)
        writer.writerow(writing_list)


if __name__ == "__main__":
    extract_by_new_rules()
    # tag()

# 如果多个名词连续出现认为是实体
# 如果名词出现在's之前，认为是实体
# 我发现很多两个单词的实体，例如who was rosemary clooney married to ? 中，
# 实体应该是rosemary clooney，但是rosemary clooney被识别成了 形容词 + 名词，我想因该是形容词 + 名词这种组合出现的比较频繁。
# 规则3 ：出现形容词 + 名词的组合也认为是实体