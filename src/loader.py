loader = PyPDFLoader("paper.pdf")
docs = loader.load()

text = "\n".join(doc.page_content for doc in docs)