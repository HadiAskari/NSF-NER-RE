
from transformers import pipeline

from tqdm.auto import tqdm
import pickle as pkl
from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import json
from ast import literal_eval
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import argparse


def filter_sentences(paragraph, keywords):
    # Split the paragraph into sentences
    sentences = sent_tokenize(paragraph)
    
    # Convert keywords to lowercase for case-insensitive matching
    keyword_set = set(word for word in keywords)
    
    filter_sentences=[]
    for sentence in sentences:
        for keyword in keyword_set:
            if keyword in sentence:
                filter_sentences.append(sentence)
                break

    
    # Rejoin the filtered sentences
    result = ' '.join(filter_sentences)
    return result

def generate_res(chatbot,text,software,hardware,vulnerability):
    
    results=[]
    
    # for text1,soft,hard,vul in tqdm(zip(text,software,hardware,vulnerability)):
    #     temp=[]
        # for desc in text1:
            # print(desc)
            # print(soft)
            # print(hard)
        # print(vul)
    messages = [
        {"role": "system", "content": f"""
    You are an excellent content relation extractor. You will be provided with detailed text information a news article, a list of Software named entities in that text, a list of Hardware entities in that text, and a list of cyber-security vulnerabilities in that text. 
    For each Software or Hardware Entity, please answer Yes or No, depending on the text, whether that entity has the Vulnerabilities in the Vulnerability list or not if the entites are present in the text.
    For an example set of lists :

    Software list: [Software 1, Software 2]
    Hardware list: [Hardware1, Hardware2]
    Vulnerability list: [Vulnerability1, Vulnerability 2]
    
    Your output should be:
    
    Software 1 - Vulnerability 1: Your Answer
    Software 2 - Vulnerability 1: Your Answer
    Software 1 - Vulnerability 2: Your Answer
    Software 2 - Vulnerability 2: Your Answer
    Hardware 1 - Vulnerability 1: Your Answer
    Hardware 2 - Vulnerability 1: Your Answer
    Hardware 1 - Vulnerability 2: Your Answer
    Hardware 2 - Vulnerability 2: Your Answer
    
    
    Please list out all of the combinations of Software, Hardware, Vulnerabilities along with their names. 
    Please consider both Software and Hardware entities (if both of them have values)

    """.strip()
    },
        {"role": "user", "content": "Here is the textual description and the named entities of the article: Description: {}. Here is the Software list: {}. Here is the Hardware list: {}. Here is the Vulnerability list: {}".format(str(text),str(software),str(hardware),str(vulnerability))}, #
    ]
        # with open('see_new.txt', 'w') as f:
        #     f.write(str(messages))
        # break
        
    res=chatbot(messages)
    # print(res)
    print(res[0]['generated_text'][2]['content'])
    results.append(res[0]['generated_text'][2]['content'])
    # print(res[0]['generated_text'][2]['content'])
    
    # results.append(temp)
    return results

def return_list(df,key):
    item_list=[]

    for items in df.itertuples():
        #print(items[key])
        item_list.append(literal_eval(items[key]))
        
    return item_list


if __name__=='__main__':
    nltk.download('punkt_tab')
    # bnb_config = transformers.BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_use_double_quant=True,
    # )
    parser = argparse.ArgumentParser()
    
    # Define four arguments
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--software", type=str, required=True)
    parser.add_argument("--hardware", type=str, required=True)
    parser.add_argument("--vulnerability", type=str, required=True)

    # Parse the arguments
    args = parser.parse_args()
    text=args.text
    software=json.loads(args.software)
    hardware=json.loads(args.hardware)
    vulnerability=json.loads(args.vulnerability)


    model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
    model = AutoModelForCausalLM.from_pretrained(
            model_name,
            #load_in_4bit=True,
            #quantization_config=bnb_config,
            #torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
    
    chatbot = pipeline(
        "text-generation", 
        model=model, 
        tokenizer = tokenizer, 
        #torch_dtype=torch.bfloat16, 
        device_map="auto",
        max_new_tokens=1000,
        temperature=0.001
    )

    keywords=software+hardware+vulnerability
    text_filtered=filter_sentences(text,keywords)
    print(text_filtered)
    
    # df=pd.read_csv('Hacker_100.csv')
    # df=df.iloc[0:2]
    # text=return_list(df,1)
    # software=return_list(df,2)
    # hardware=return_list(df,3)
    # vulnerability=return_list(df,4)

    output=generate_res(chatbot,text_filtered,software,hardware,vulnerability)
    # df['Llama3']=output
    # df.to_csv('Subsampled_eval_dataset_Llama3-8b.csv', index=False)
   #print(output)
    # df['RE']=output
    # df.to_csv('Hacker_100_RE.csv',index=False)


    