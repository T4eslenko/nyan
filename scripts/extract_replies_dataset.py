import sys
import random

from tqdm import tqdm

from nyan.util import read_jsonl, write_jsonl

input_path = sys.argv[1]
output_path = sys.argv[2]

docs = list(tqdm(read_jsonl(input_path)))
docs = [doc for doc in docs if doc["patched_text"] and doc["language"] == "ru"]
docs.sort(key=lambda x: x["pub_time"])
print(len(docs))

url2doc = {d["url"]: d for d in docs}
url2idx = {d["url"]: idx for idx, d in enumerate(docs)}
replies = [(r["reply_to"], r["url"]) for r in docs if "reply_to" in r]
print(len(replies))
existing_replies = [(url_from, url_to) for url_from, url_to in replies if url_from in url2doc and url_to in url2doc]
print(len(existing_replies))

save_fields = ("patched_text", "url", "pub_time", "language")
def shrink(obj):
    return {field: obj[field] for field in obj if field in save_fields}

pairs = []
for url_from, url_to in existing_replies:
    anchor_doc = shrink(url2doc[url_to])
    anchor_idx = url2idx[url_to]
    positive_doc = shrink(url2doc[url_from])
    random_shift = random.randint(50, 1000)
    negative_idx = max(anchor_idx - random_shift, 0)
    negative_doc = shrink(docs[negative_idx])
    pairs.append({
        "anchor": anchor_doc,
        "positive": positive_doc,
        "negative": negative_doc
    })

write_jsonl(output_path, pairs)
