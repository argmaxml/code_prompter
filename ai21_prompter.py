import requests
import json
from pathlib import Path
from ast import literal_eval
from typing import List, Dict, Tuple
import ai21

__dir__ = Path(__file__).absolute().parent

class AI21Query:
    def __init__(self, secret, model="j2-grande-instruct", n=10):
        ai21.api_key=secret
        self.ai21 = ai21
        self.model = model
        self.n = n
    
    def complete(self, **kwargs):
        if "model" not in kwargs:
            kwargs["model"] = self.model
        if "n" not in kwargs:
            kwargs["numResults"] = self.n
        else:
            kwargs["numResults"]=kwargs["n"]
        if "prompt" not in kwargs:
            raise ValueError("prompt is required")
        url = "https://api.openai.com/v1/completions"
        ret = ai21.Completion.execute(**kwargs)
        return [{"text":v.data.text,"finishReason":v.finishReason["reason"]} for v in ret.completions]

    def str_query(self, prompt):
        completions = self.complete(prompt=prompt, stop='"')
        ret = []
        for c in completions:
            if c["finishReason"]!="endoftext":
                continue
            ret.append(c["text"].strip())
        return ret

    def literal_query(self, prompt,force_type=None):
        completions = self.complete(prompt=prompt, stop=["\n", ";"])
        ret = []
        for c in completions:
            if c["finishReason"]!="endoftext":
                continue
            try:
                lit = literal_eval(c["text"].strip())
            except:
                continue
            if force_type is not None and not isinstance(lit, force_type):
                continue
            ret.append(lit)
        return ret


    def list_query(self, prompt,force_type=None):
        completions = self.complete(prompt=prompt, stop="]")
        ret = []
        for c in completions:
            if c["finishReason"]!="endoftext":
                continue
            try:
                lit = literal_eval("["+c["text"] + "]")
            except:
                continue
            if force_type is not None:
                lit = [l for l in lit if isinstance(l, force_type)]
            if len(lit)==0:
                continue
            ret.append(lit)
        return ret

class ClassificationQuery(AI21Query):
    def __init__(self, secret, model="j2-grande-instruct", n=10):
        super().__init__(secret, model, n)
    
    def tag(self, text):
        triple = '"""'
        prompt = f"""
        text = {triple}{text}{triple}
        # extract tags from text
        tags = extract_tags(text)

        assert tags == [
        """.strip()
        return self.list_query(prompt, str)

    def classify(self, text, cls):
        triple = '"""'
        if type(cls)==list:
            cls_arr = ",".join(["'"+str(c)+"'" for c in cls])
            prompt = f"""
            text = {triple}{text}{triple}
            #  classify returns True if the text is belongs to the corresponding class
            assert classify("Harry Ptter", ["book", "movie", "food"]) == [True, True, False]
            assert classify("Wild coyote", ["wildlife", "economics"]) == [True, False]
            assert classify(text, [{cls_arr}]) == [
            """.strip()
            lst = self.list_query(prompt)
            lst = [dict(zip(cls,l)) for l in lst if len(l)==len(cls)]
            return lst
        elif type(cls)==str:            
            prompt = f"""
            text = {triple}{text}{triple}
            #  check if text is classified correctly
            assert is_{cls}(text) ==
            """.strip()
            return self.literal_query(prompt)
    

class ExtrapolationQuery(AI21Query):
    def __init__(self, secret, model="j2-grande-instruct", n=10):
        super().__init__(secret, model, n)
    
    def extrapolate_function_value(self, function_name:str,  examples: Dict[str, str], query: str):
        pattern = "assert {f}({q}) == {v}"
        prompt = "\n".join([pattern.format(f=function_name, q=json.dumps(q), v=json.dumps(v)) for q,v in examples.items()])
        prompt += f"\nassert {function_name}({json.dumps(query)}) == "
        return self.literal_query(prompt)

    def reverse_extrapolate_function(self, function_name:str,  examples:Dict[str, str], query: str):
        pattern = "assert {v} == {f}({q})"
        prompt = "\n".join([pattern.format(f=function_name, q=json.dumps(q), v=json.dumps(v)) for q,v in examples.items()])
        prompt += f"\nassert {json.dumps(query)} == {function_name}(\""
        return self.str_query(prompt)

if __name__ == "__main__":
    with open(__dir__ / "config.json") as f:
        config = json.load(f)
    
    cq = ClassificationQuery(config["ai21_token"])

    txt = """
An always-on account portal can help drive the highest demand. By directing potential customers to
micro-sites, partner portals, or deal rooms, you can tailor the focus of the messaging and content they see.
Depending on their interests, previous engagement, and where they are in the buying journey, content is
dynamically displayed.This lets you build a connected, relevant, and personalized buyer journey based on your customers' data.
Combining firmographics, buying stage, and intent, you can create memorable experiences designed
specifically for every buyer
    """

    print ("="*20+"TAGS"+"="*20)
    print(cq.tag(txt))
    print ("="*20+"IS_BUSINESS"+"="*20)
    print(cq.classify(txt,"business"))
    print ("="*20+"CLASSES"+"="*20)
    print(cq.classify(txt,["fashion", "sport", "finance"]))

    eq = ExtrapolationQuery(config["ai21_token"])
    print ("="*20+"EXTRAPOLATE"+"="*20)
    print(eq.extrapolate_function_value("abbreviate", {"User Id": "userid", "Document id": "docid",}, "time of day"))

    print(eq.reverse_extrapolate_function("abbreviate", {"User Id": "userid", "Document id": "docid",}, "dow"))
