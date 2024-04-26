from graphviz2drawio import graphviz2drawio

xml = graphviz2drawio.convert('data/grouped_workers.dot')

print(xml)

with open('data/a.xml', 'w') as f:
    f.write(xml)
