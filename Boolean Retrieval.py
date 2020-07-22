from IR import document, normalization
import os

index = document.Index(tokenizer = normalization.query_tokenizer)

dir = input("Directory: ")
if os.path.exists(dir) and os.path.isdir(dir):
    print(f"Loading documents from {os.path.abspath(dir)}")
    for file in os.listdir(dir):
        processor = document.make_preprocessor(os.path.join(dir, file), tokenizer = normalization.tokenizer)
        if processor is not None:
            processor.read()
            for i in range(0, processor.count()):
                index.add(processor.unit(i))
    with open('index.txt', 'w+') as out:
        for word in index.keywords():
            ids = list(map(lambda unit: unit.string(), index[word]))
            out.write(f"{word}: {ids}\n")
    print(f"Loading complete. {index.count()} document units were found.\n")
    query = input("Enter a query to search: ")
    while query:
        units = index.search(query) 
        if units is not None:
            print(f"[{query}] was found in {len(units)} document units.")
            for unit in units: print(unit.string())
            print()
        else: print(f"[{query}] was not found.\n")
        query = input("Enter a keyword to search: ")
else: print(f"{dir}: no such directory.")

