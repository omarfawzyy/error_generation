from nltk.tokenize import sent_tokenize
from errorify import errorify
import multiprocessing
import os
import argparse

def blocks(files, size=65536):
    while True:
        b = files.read(size)
        if not b: break
        yield b
def count_lines(f):
    with open(f, "r", encoding="utf-8",errors='ignore') as f:
        return sum(bl.count("\n") for bl in blocks(f))
def generate_from_slice(inputs):
    src_file,idx_slice = inputs
    start,end = idx_slice
    working_dir = os.path.join(os.path.dirname(src_file), "working")
    corr_dir = os.path.join(working_dir,"corr")
    ori_dir = os.path.join(working_dir,"ori")
    os.makedirs(corr_dir,exist_ok=True)
    os.makedirs(ori_dir,exist_ok=True)
    ori_file = os.path.join(ori_dir,str(start))
    cor_file = os.path.join(corr_dir,str(start))
    with open(ori_file,'w') as ori,open(cor_file,'w') as cor:
        for i,line in enumerate(open(src_file,'r')):
            if i < start: continue
            if i >= end: break
            # lowercase capitalized first word in sentence 
            sents = sent_tokenize(line)
            lowercased = []
            for sent in sents:
                words = sent.strip().split()
                first_word = words[0].lower()
                words = [first_word] + words[1:]
                lowercased.append(" ".join(words))
            example = " ".join(lowercased)

            corr_example = errorify(example)
            cor.write(f"{corr_example}\n")
            ori.write(f"{line.strip()}\n")
            
def generate_corrupt_data(src_file):
    ori_size = count_lines(src_file)
    cpu_count = multiprocessing.cpu_count()
    start_idxs = [start for start in range(0,ori_size,ori_size//cpu_count)]
    start_end_idxs = [(start,start + ori_size//cpu_count) for start in start_idxs if start + ori_size//cpu_count <=ori_size]
    if start_end_idxs[-1][1] < ori_size:
        start_end_idxs.append((start_end_idxs[-1][1],ori_size))
    args = [(src_file,slice) for slice in start_end_idxs]
    pool = multiprocessing.Pool(cpu_count)
    pool.map(generate_from_slice,args)
    pool.close()
    pool.join()

    #combine data
    cor_file = src_file+".src"
    ori_file = src_file+".trg"
    os.system(f"cat {os.path.dirname(src_file)}/working/cor/* > {cor_file}")
    os.system(f"cat {os.path.dirname(src_file)}/working/ori/* > {ori_file}")
    os.system(f"rm -r {os.path.dirname(src_file)}/working")

if __name__=="main":
    parser = argparse.ArgumentParser()
    parser.add_argument("-original_file",type=str)
    args = parser.parse_args()
    generate_corrupt_data(args.original_file)