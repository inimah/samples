import os
import sys
import numpy as np
import pandas as pd
from math import exp

from .variables import (
    openai_config,
    inference_cost_per_1000_tokens,
    info,
) # 要使用绝对导入包，不然导入这个模块的时候会报错
from openai import OpenAI, BadRequestError
from .load_prompt import render_prompt, convert_filled_prompt_to_chat_messages
from .utils import cache
import copy

class ChatGPTInstance:
    def __init__(self):
        # self.args = args
        self.config = self.set_config()
        self.client = OpenAI(api_key=self.config['api_key'], base_url=self.config['api_base'])


    def get_model_list(self):
        return self.client.models.list()

    def set_config(self):
        config = {}

        config['api_key'] = openai_config['api_key']
        if not openai_config['api_key']:
            env_key = os.environ.get('OPENAI_KEY', None)
            config['api_key'] = env_key
        assert config['api_key'] is not None, 'No OpenAI Key provided!'
        config['api_base'] = openai_config['api_base']
        config['model_map'] = openai_config['model_map']
        config['template_generate_cache_file'] = openai_config['template_generate_cache_file']
        config['chat_generate_cache_file'] = openai_config['chat_generate_cache_file']

        return config

    def inference_cost(self, response, model):
        prompt_cost, completion_cost = inference_cost_per_1000_tokens[model]
        prompt_token = response.usage.prompt_tokens
        completion_token = response.usage.completion_tokens
        total_cost = (prompt_token * prompt_cost + completion_token * completion_cost) / 1000

        return total_cost


    @cache(cache_type='chatgpt_template_generate')
    def template_generate(self, **kwargs):
        template_file = kwargs['template_file']
        prompt_parameter_values = kwargs['prompt_parameter_values'] # 这里我们需要传入每次不同生成任务对应的模板变量（如新闻文本）
        max_tokens = kwargs['max_tokens']
        temperature = kwargs['temperature']
        num_choices = kwargs["num_choices"]
        model=kwargs.get('model', 'gpt-35-turbo-16k')
        article_backup = prompt_parameter_values['article'][:1000] if 'article' in prompt_parameter_values else None

        rendered_prompt = render_prompt(template_file, prompt_parameter_values)

        messages = convert_filled_prompt_to_chat_messages(rendered_prompt)

        prompt_parameter_values_copy = copy.deepcopy(prompt_parameter_values)
        prompt_parameter_values_copy['article'] = article_backup
        rendered_prompt_copy = render_prompt(template_file, prompt_parameter_values_copy)
        messages_copy = convert_filled_prompt_to_chat_messages(rendered_prompt_copy)

        # add log_probs in GPT generation 
        try:
            response = self.client.chat.completions.create(
                model=self.config['model_map'][model],
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                n=num_choices,
                logprobs=True, # uncomment for long text completion
            )
        except BadRequestError as e:

            error_info = e.args[0]
            if 'context_length_exceeded' in error_info:
                info('context_length_exceeded, use first 1000 words')
                response = self.client.chat.completions.create(
                    model=self.config['model_map'][model],
                    messages=messages_copy,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=num_choices
                )

            else:
                raise e

        cost = self.inference_cost(response, model)
        
        #print("response.choices[0].logprobs.content:")
        #sys.stdout.flush()
        #print(response.choices[0].logprobs.content)
        #sys.stdout.flush()
        
        '''
        [ChatCompletionTokenLogprob(token='NE', bytes=[78, 69], logprob=-0.039785016, top_logprobs=[TopLogprob(token='NE', bytes=[78, 69], logprob=-0.039785016), TopLogprob(token='NOT', bytes=[78, 79, 84], logprob=-3.2446914)]), 
        ChatCompletionTokenLogprob(token='UT', bytes=[85, 84], logprob=-1.9361265e-07, top_logprobs=[TopLogprob(token='UT', bytes=[85, 84], logprob=-1.9361265e-07), TopLogprob(token='URAL', bytes=[85, 82, 65, 76], logprob=-16.43907)]), 
        ChatCompletionTokenLogprob(token='RAL', bytes=[82, 65, 76], logprob=-5.5122365e-07, top_logprobs=[TopLogprob(token='RAL', bytes=[82, 65, 76], logprob=-5.5122365e-07), TopLogprob(token='R', bytes=[82], logprob=-15.624642)])]
        '''

        aggregated_bytes = []
        joint_logprob = 0.0
        
        # uncomment for long text generation
        #logprobs = [token.logprob for token in response.choices[0].logprobs.content]

        # Iterate over tokens, aggregate bytes and calculate joint logprob
        for token in response.choices[0].logprobs.content:
            '''
            print("Token:", token.token)
            sys.stdout.flush()
            print("Log prob:", token.logprob)
            sys.stdout.flush()
            print("Linear prob:", np.round(exp(token.logprob) * 100, 2), "%")
            sys.stdout.flush()
            print("Bytes:", token.bytes, "\n")
            sys.stdout.flush()
            '''
            aggregated_bytes += token.bytes
            joint_logprob += token.logprob

        # Decode the aggregated bytes to text
        #aggregated_text = bytes(aggregated_bytes).decode("utf-8")
        aggregated_text = bytes(aggregated_bytes).decode("utf-8", errors='ignore')

        #print("Joint prob:", np.round(exp(joint_logprob) * 100, 2), "%")
        #sys.stdout.flush()
            
        output_texts = aggregated_text
        output_probs = np.round(exp(joint_logprob) * 100, 2)
        #perplexity_score = np.exp(-np.mean(logprobs))
       
            
        return (output_texts, output_probs, cost)
        #return (output_texts, output_probs, perplexity_score, cost)
        #return (output_texts, perplexity_score, cost)

    @cache(cache_type='chatgpt_chat_generate')
    def chat_generate(self, **kwargs):
        messages = kwargs['messages']
        max_tokens = kwargs['max_tokens']
        temperature = kwargs['temperature']
        top_p = kwargs["top_p"]
        frequency_penalty = kwargs["frequency_penalty"]
        presence_penalty = kwargs["presence_penalty"]
        stop_tokens = kwargs["stop_tokens"]
        logit_bias = kwargs.get("logit_bias", {}) # 这个wikichat没有传
        num_choices = kwargs["num_choices"]
        model=kwargs.get('model', 'gpt-35-turbo-16k')

        response = self.client.chat.completions.create(
            model=self.config['model_map'][model],
            messages=messages,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            n=num_choices
        )

        cost = self.inference_cost(response, model)
        output_texts = response.choices[0].message.content.strip()
        return (output_texts, cost)










