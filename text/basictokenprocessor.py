from .tokenprocessor import TokenProcessor
import re
from porter2stemmer import Porter2Stemmer

class BasicTokenProcessor(TokenProcessor):
    """A BasicTokenProcessor creates terms from tokens by removing all non-alphanumeric characters 
    from the token, and converting it to all lowercase."""
    whitespace_re = re.compile(r"\W+")
    
    # def process_token(self, token : str) -> str:
    #     return re.sub(self.whitespace_re, "", token).lower() # remove punctuations 
        
    def remove_hyphens(self, token):
        list_of_tokens = []
        if '-' in token:
            list_of_tokens = token.split('-')
            t = ''
            for i in list_of_tokens:
                t += i
            list_of_tokens.append(t)
        else:
            list_of_tokens = [token]

        return list_of_tokens

    def process_token(self, list_of_tokens):
        stemmer = Porter2Stemmer()
        processed_list_of_tokens = []

        for tok in list_of_tokens:
            if tok != '':
                tok = re.sub(self.whitespace_re, "", tok).lower()
                tok = re.sub(r"^\W+|\W+$", "", tok)
                # tok = re.sub(r'[^\w\s]', '', tok)   # remove all punctuations in tok
                tok = tok.replace("'","")
                tok = tok.replace('"','')
                if tok:
                    processed_list_of_tokens.append(stemmer.stem(tok))        

        return processed_list_of_tokens

    def process_query(self, list_of_tokens):
        stemmer = Porter2Stemmer()
        processed_list_of_tokens = []
        new_list_of_tokens = '-'.join(list_of_tokens).split('-')
        for tok in new_list_of_tokens:
                    
            if tok != '':
                tok = re.sub(self.whitespace_re, "", tok).lower()
                tok = re.sub(r"^\W+|\W+$", "", tok)
                # tok = re.sub(r'[^\w\s]', '', tok)   # remove all punctuations in tok
                tok = tok.replace("'","")
                tok = tok.replace('"','')
                if tok:
                    processed_list_of_tokens.append(stemmer.stem(tok))        

        return processed_list_of_tokens

