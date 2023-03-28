# Code Prompter

Prompt engineering can be a tedious task inaccurate tasks. However, with a formal language (such as python) the prompts are more strutured.

The output of an LLM optimized to predict code is also highly structured.

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
    
    print(cq.tag("Tinder", most_common=3))
    # output: [("Dating", 4), ("Social", 2), ("hookups", 1)]

    print(cq.classify("Gucci sweaters now on sale as stock drops", ["fashion", "sport", "finance"]))
    # output: [{"sport": True, "finance": False, "fashion":True}]
    
```

### Inverting a function
```
    from codex_prompter import ExtrapolationQuery
    eq = ExtrapolationQuery("openai_secret")
    
    print(eq.extrapolate_function_value("abbreviate", {"User Id": "userid", "Document id": "docid",}, "time of day"))
    # output: ["ToD", "timeofday"]

    print(eq.reverse_extrapolate_function("abbreviate", {"User Id": "userid", "Document id": "docid",}, "dow"))
    # output: ["Day of week", "definition of work"]
```
