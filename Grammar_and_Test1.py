import random
import re
from fuzzingbook.Grammars import Grammar
import dns.resolver

result =[]
Errors = []
queries = []
sub_results = []

def nonterminals(expansion):
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return RE_NONTERMINAL.findall(expansion)

def is_nonterminal(s):
    return RE_NONTERMINAL.match(s)
    
START_SYMBOL = "<start>"
RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')

class ExpansionError(Exception):
    pass

URL_GRAMMAR: Grammar = {
    "<start>":
        ["<query>"],
    "<query>":
        ["<scheme>.<host>:<Type>,<class>"],
    "<scheme>":
        ["www"],
    "<host>":  
        ["vt.edu", "google.com", "linkedin.com","whentowork.com","usa.gov","facebook.com"],
    "<Type>":
        ["type A","type NS","type MD","type MF","type CNAME","type SOA","type MB","type MG","type MR","type NULL","type WKS","type PTR","type HINFO","type MINFO","type MX","type TXT"],
    "<class>":
        ["class IN","class CS","class CH","class HS"]    
}

def simple_grammar_fuzzer(grammar: Grammar, 
                          start_symbol: str = START_SYMBOL,
                          max_nonterminals: int = 10,
                          max_expansion_trials: int = 100,
                          log: bool = False) -> str:
    
    term = start_symbol
    expansion_trials = 0

    while len(nonterminals(term)) > 0:
        symbol_to_expand = random.choice(nonterminals(term))
        expansions = grammar[symbol_to_expand]
        expansion = random.choice(expansions)
        # In later chapters, we allow expansions to be tuples,
        # with the expansion being the first element
        if isinstance(expansion, tuple):
            expansion = expansion[0]

        new_term = term.replace(symbol_to_expand, expansion, 1)

        if len(nonterminals(new_term)) < max_nonterminals:
            term = new_term
            if log:
                print("%-40s" % (symbol_to_expand + " -> " + expansion), term)
            expansion_trials = 0
        else:
            expansion_trials += 1
            if expansion_trials >= max_expansion_trials:
                raise ExpansionError("Cannot expand " + repr(term))

    return term

number_of_seeds = 10
seeds = [
    simple_grammar_fuzzer(
        grammar=URL_GRAMMAR,
        max_nonterminals=10) for i in range(number_of_seeds)]
#print(*seeds,sep='\n')

for i in seeds:
    queries.append(i)
    components = i.split(':')
    #print(components[0][4:])
    subcomponents = components[1].split(',')
    #print(subcomponents)
    types = subcomponents[0].split(' ')
    #print(types[1])
    classes = subcomponents[1].split(' ')
    #print(classes[1])

    try:
        result_temp = dns.resolver.resolve(components[0][4:],types[1],classes[1])
        #result.append(result_temp)
        for val in result_temp:
            server = val.to_text()
            sub_results.append(server)
        result.append(sub_results)
        Errors.append("No Error")
        #print(f"{result=}")
    except Exception as Argument:
        result.append("No result")
        #file2_results.write("No result \n")
        Errors.append(Argument)

#print(*queries,sep='\n')     

print(f"{queries=}")
print(f"{result=}")
print(f"{Errors=}")
