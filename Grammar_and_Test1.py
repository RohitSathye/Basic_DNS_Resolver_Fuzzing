import random
import re
import dns.resolver
from fuzzingbook.Grammars import Grammar

START_SYMBOL = "<start>"
RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')

# Grammar for DNS queries
URL_GRAMMAR: Grammar = {
    "<start>": ["<hostname> <rtype> <rclass>"],
    "<hostname>": [
        "google.com", "vt.edu", "facebook.com",
        "nonexistentdomain.abc", "xn--d1acufc.xn--p1ai",  # punycode
        "verylong" * 30 + ".com"                          # stress test
    ],
    "<rtype>": [
        "A", "NS", "CNAME", "SOA", "MX", "TXT",
        "AAAA", "SRV", "PTR", "DNSKEY", "RRSIG",
        "INVALIDTYPE"  # invalid token
    ],
    "<rclass>": ["IN", "CH", "HS", "NONE", "INVALIDCLASS"]
}

def nonterminals(expansion):
    if isinstance(expansion, tuple):
        expansion = expansion[0]
    return RE_NONTERMINAL.findall(expansion)

def simple_grammar_fuzzer(grammar, start_symbol=START_SYMBOL,
                          max_nonterminals=10, max_expansion_trials=100):
    term = start_symbol
    expansion_trials = 0
    while len(nonterminals(term)) > 0:
        symbol_to_expand = random.choice(nonterminals(term))
        expansions = grammar[symbol_to_expand]
        expansion = random.choice(expansions)
        if isinstance(expansion, tuple):
            expansion = expansion[0]
        new_term = term.replace(symbol_to_expand, expansion, 1)
        if len(nonterminals(new_term)) < max_nonterminals:
            term = new_term
            expansion_trials = 0
        else:
            expansion_trials += 1
            if expansion_trials >= max_expansion_trials:
                raise Exception("Too many expansion trials")
    return term

# Run fuzzing
num_queries = 20
queries = []
results = []
errors = []

for _ in range(num_queries):
    fuzzed_query = simple_grammar_fuzzer(URL_GRAMMAR)
    parts = fuzzed_query.split(" ")
    hostname, rtype, rclass = parts[0], parts[1], parts[2]

    try:
        sub_results = []
        answer = dns.resolver.resolve(hostname, rtype, rclass)
        for val in answer:
            sub_results.append(val.to_text())
        results.append(sub_results)
        errors.append("No Error")
    except Exception as e:
        results.append([])
        errors.append(str(e))

    queries.append(fuzzed_query)

# Print summary
for q, r, e in zip(queries, results, errors):
    print(f"Query: {q}\nResult: {r}\nError: {e}\n{'-'*50}")
