import torch
from textattack.shared import utils
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from .language_model_constraint import LanguageModelConstraint

class GPT2(LanguageModelConstraint):
    """ A constraint based on the GPT-2 language model. 
        
        
        from "Better Language Models and Their Implications" 
            (openai.com/blog/better-language-models/)
    
    """
    def __init__(self, **kwargs):
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.model.to(utils.get_device())
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        super().__init__(**kwargs)
    
    def get_log_prob_at_index(self, tokenized_text, word_index):
        """ Gets the probability of the word at index `word_index` according
            to GPT-2.
        """
        prefix = tokenized_text.text_until_word_index(word_index)
        
        if not utils.has_letter(prefix):
            # This language model perplexity is not defined with respect to
            # a word without a prefix. If the prefix is null, just return the
            # log-probability 0.0.
            return 0.0
        
        token_ids = self.tokenizer.encode(prefix)
        tokens_tensor = torch.tensor([token_ids])
        tokens_tensor = tokens_tensor.to(utils.get_device())
        
        with torch.no_grad():
            outputs = self.model(tokens_tensor)
        predictions = outputs[0]
        
        next_word_ids = self.tokenizer.encode(tokenized_text.words[word_index])
        next_word_prob = predictions[0, -1, next_word_ids[0]]
        return next_word_prob

    
    
