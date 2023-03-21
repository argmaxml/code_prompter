# Codex Prompter

Prompt engineering can be a tedious task inaccurate tasks. However, with a formal language (such as python) the prompts are more strutured.

The output of an LLM like codex, is also highly structured.

For example, for the following prompt we would expect the LLM to output a valid array

```
  assert extract_tags("https://www.argmaxml.com") == [
```

This simple OpenAI codex wrapper structures the prompt as a python code, then it filters out only the outputs that are valid syntactically.

## Example usages

### Classification
```
    from codex_prompter import ClassificationQuery
    cq = ClassificationQuery("openai_secret")
    print ("="*20+"TAGS"+"="*20)
    print(cq.tag(txt))
    print ("="*20+"IS_BUSINESS"+"="*20)
    print(cq.classify(txt,"business"))
    print ("="*20+"CLASSES"+"="*20)
    print(cq.classify(txt,["fashion", "sport", "finance"]))
    
```

### Inverting a function
```
    from codex_prompter import ExtrapolationQuery
    eq = ExtrapolationQuery("openai_secret")
    print ("="*20+"EXTRAPOLATE"+"="*20)
    print(eq.extrapolate_function_value("abbreviate", {"User Id": "userid", "Document id": "docid",}, "time of day"))

    print(eq.reverse_extrapolate_function("abbreviate", {"User Id": "userid", "Document id": "docid",}, "dow"))
```
