import random
import lemminflect
from nltk.tokenize import word_tokenize 

def errorify(sent,word_trees): 
    tokens = word_tokenize(sent)
    if tokens == []: return sent
    
    #reverse character alteration of tokenizer
    for idx in range(len(tokens)):
        if tokens[idx] in ["''","``"]:
            tokens[idx] = '"'
   
    # selecting number of errors based on sentece length
    error_num_probs = [
                [30,[5,6,7,8,9],[0.1,0.15,0.15,0.3,0.3]],
                [20,[4,5,6,7,8],[0.1,0.15,0.15,0.3,0.3]],
                [16,[3,4,5,6,7],[0.1,0.15,0.15,0.3,0.3]],
                [9,[3,4,5,6],[0.15,0.25,0.3,0.3]],
                [6,[2,3,4],[0.3,0.45,0.25]],
                [3,[1,2],[0.5,0.5]],
                [1,[0,1],[0.5,0.5]]
                ] 
    for info in error_num_probs:
        min_len,err_nums,probs = info
        if len(tokens)>=min_len:
            err_num = random.choices(population=err_nums,weights=probs)[0]
            break

    # producing errors
    ops = ["delete","substitute","misspell","transpose","concatenate"]
    selected_ops = random.choices(population=ops,weights=[0,0.4,0.45,0.03,0.12],k=err_num)
    token_indices = list(range(len(tokens)))
    for op in selected_ops:
        rand_idx = random.choice(token_indices) 
        if op == "delete":
            del tokens[rand_idx]
            unchanged_indices = token_indices[:token_indices.index(rand_idx)]
            changed_indices = [idx-1 for idx in token_indices if idx>rand_idx]
            token_indices = unchanged_indices+changed_indices
        if op == "substitute":
            sub = substitute(tokens[rand_idx],word_trees)
            tokens[rand_idx] = sub
            del token_indices[token_indices.index(rand_idx)]
        if op == "misspell":
            misspelled_word = misspell(tokens[rand_idx])
            tokens[rand_idx] = misspelled_word
            del token_indices[token_indices.index(rand_idx)]
        if op == "concatenate":
            if rand_idx == len(tokens)-1:
                concat_indices = (rand_idx-1,rand_idx)
            else:
                concat_indices = (rand_idx,rand_idx+1) 
            concat = tokens[concat_indices[0]]+tokens[concat_indices[1]]
            tokens = tokens[:concat_indices[0]]+[concat]+tokens[concat_indices[1]+1:]
            unchanged_indices = token_indices[:token_indices.index(concat_indices[0])]
            changed_indices = [idx-1 for idx in token_indices if idx>concat_indices[1]]
            token_indices = unchanged_indices+changed_indices
        if op == "transpose":
            if rand_idx == len(tokens)-1:
                swapped_indices = (rand_idx-1,rand_idx)
            else:
                swapped_indices = (rand_idx,rand_idx+1) 
            replaced_word = tokens[swapped_indices[0]]
            tokens[swapped_indices[0]] = tokens[swapped_indices[1]]
            tokens[swapped_indices[1]] = replaced_word    
    return " ".join(tokens)    
def substitute(word,word_trees):
    substitutions = {
    "prepositions" : [
        "for","at","in","by","from","about",
        "with","to","of","before", "after", 
        "during", "on","since","until","across",
        "through","among","into","toward"
    ],
    "singular_prons" : ["he","she","it","her","his"],
    "plural_prons" : ["them","their","theirs","they"],
    "wh_words" : ["which","where", "what", "how", "when", "who", "whose", "whom"],
    "articles":["a","the","an"]
    }   
    for label,subs in substitutions.items():
        if word in subs:
            rand_word = random.choice(subs)
            while rand_word == word:
                rand_word = random.choice(subs)
            return rand_word
    for base,labels in word_trees.items():
        for label in labels:
            if word_trees[base][label] == word:
                random_word = random.choice(list(word_trees[base].values()))
                return random_word
    return word
def misspell(word):
    
    # check if word is valid
    if lemminflect.getAllInflections(word) == {}:
        return word
    
    letters = [
                "a","b","c","d","e","f","g","h","i","j","k","l","m","n",
                "o","p","q","r","s","t","u","v","w","x","y","z"
            ]
    error_num_probs = [
        [10,[1,2,3],[0.75,0.15,0.10]],
        [5,[1,2],[0.8,0.2]],
        [3,[1],[1]],
        [1,[0],[1]]         
        ]
    for prob in error_num_probs:
        min_len,err_nums,probs = prob
        if len(word)>=min_len:
            err_num = random.choices(population=err_nums,weights=probs)[0]
            break
    for i in range(err_num):
        operations = ["delete","insert","transpose","replace"]
        operations_probs = [0.3,0.15,0.25,0.3]
        chosen_operation = random.choices(population=operations,weights=operations_probs)[0]
        random_idx = random.choice(range(len(word)) )
        if chosen_operation == "delete":
            word = list(word)
            if random_idx == len(word)-1:
                word = word[:-1]
            else:
                word = word[:random_idx]+word[random_idx+1:]
            word = "".join(word)
        if chosen_operation == "insert":
            word = list(word)
            if random_idx == len(word)-1:
                word = word[:-1]+list(random.choice(letters))
            else:
                word = word[:random_idx]+[random.choice(letters)]+word[random_idx+1:]
            word = "".join(word)
        if chosen_operation == "transpose" and len(word)>1:
            word = list(word)
            if random_idx == 0:
                idx = random_idx+1
            else:
                idx = random_idx-1
            replaced = word[idx]
            word[idx] = word[random_idx]
            word[random_idx] = replaced
            word = "".join(word)
        if chosen_operation == "replace":
            word = list(word)
            replacing_letter = random.choice(letters)
            word[random_idx] = replacing_letter
            word = "".join(word)
    return word
