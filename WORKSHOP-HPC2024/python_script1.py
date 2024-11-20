import os
import sys
import numpy as np
import pandas as pd

# Please use transformers==4.45.2
import transformers
import torch

    
def main():

    # loading model for Huggingface hub
    model_id = "aisingapore/gemma2-9b-cpt-sea-lionv3-instruct"

    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )
    
    messages = [
        {"role": "user", "content": "Apa sentimen dari kalimat berikut ini?\nKalimat: Buku ini sangat membosankan.\nJawaban: "},
    ]

    outputs = pipeline(
        messages,
        max_new_tokens=256,
    )
    print(outputs[0]["generated_text"][-1])

    

    
if __name__ == '__main__':
    
    main()
    
    
    
