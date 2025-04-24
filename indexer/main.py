from opensearchpy import OpenSearch
from transformers import AutoTokenizer, AutoModel
from trafilatura import fetch_url, extract

top_urls = [
    'https://itmo.ru',
    'https://habr.com/ru/companies/spbifmo/news/742522/',
    'https://neerc.ifmo.ru/wiki/index.php?title=Эквивалентность_состояний_ДКА',
    'https://itmo.ru/ru/viewperson/1/vasilev_vladimir_nikolaevich.htm',
    'https://student.itmo.ru/ru/dormitory/',
    'https://student.itmo.ru/ru/booking/',
    'https://student.itmo.ru/ru/scholarship/',
    'https://github.com/whytrall/is-faq/blob/master/docs/study/grants.md',
    'https://github.com/whytrall/is-faq/blob/master/docs/study/session.md',
    'https://github.com/whytrall/is-faq/blob/master/docs/study/evaluation.md',
    'https://lib.itmo.ru',
    'https://books.ifmo.ru',
    'https://mathdep.itmo.ru',
    'https://student.itmo.ru/ru/organization/',
    'https://student.itmo.ru/ru/kronbars/',
    'https://se.ifmo.ru/courses/programming',
    'https://abit.itmo.ru/program/master/ai_systems',
]

# max_length = 16
# stride = 2

# tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
# model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased")

# def get_embedding(text: str):
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=Tr>
#     outputs = model(**inputs)
#     return outputs.pooler_output.detach().numpy()

# def split_text_with_overlap(text, max_length, stride):
#     tokens = tokenizer.tokenize(text)

#     chunks = []
#     for i in range(0, len(tokens), max_length - stride):
#         chunk_tokens = tokens[i:i + max_length]
#         chunk_text = tokenizer.convert_tokens_to_string(chunk_tokens)
#         chunks.append(chunk_text)

#     return chunks

# client = OpenSearch(
#     hosts=[{'host': 'localhost', 'port': 9200}],
#     http_auth=('admin', 'An76bFnuiBFguui6!njfd!?56'),
#     use_ssl=False,
#     verify_certs=False,
# )

# index_name = 'itmo_rag_index'

# index_settings = {
#     "settings": {
#         "index": {
#             "knn": True,
#             "knn.algo_param": {
#                 "ef_search": 5000,
#                 "ef_construction": 5000,
#                 "m": 16
#             }
#         }
#     },
#     "mappings": {
#         "properties": {
#             "embedding": {
#                 "type": "knn_vector",
#                 "dimension": 768
#             }
#         }
#     }
# }

# try:
#     response = client.indices.delete(index=index_name)
#     print(f"Index '{index_name}' deleted successfully.")
#     print("Response:", response)
# except Exception as e:
#     print(f"Error deleting index '{index_name}':", e)

# if not client.indices.exists(index=index_name):
#     client.indices.create(index=index_name, body=index_settings)

for top_url in top_urls:
  content = extract(fetch_url(top_url), include_comments=True, include_tables=False)
  #   for chunk in split_text_with_overlap(content, max_length, stride):
  #     doc_embedding = get_embedding(chunk)
#   document = {
#       'id': top_url,
#       'embedding': get_embedding(content).tolist()[0],
#   }
#   client.index(index=index_name, id=document['id'], body=document)
#   print(f"Indexed document {document['id']}")

  with open(f'/home/dima/itmogpt/knowledge_base/{top_url.strip('/').lstrip('https://').replace("/", "_")}.txt', 'w') as file:
    # Write the string to the file
    file.write(content)
