import whoosh, os
from whoosh.filedb.filestore import FileStorage

schema_commit = whoosh.fields.Schema(repository_id=whoosh.fields.ID(stored=True), 
    commit_id=whoosh.fields.ID(stored=True),
    author=whoosh.fields.TEXT(stored=True),
    date=whoosh.fields.DATETIME,
    message=whoosh.fields.ID(stored=True))

indexdir = "indexdir"

storage = FileStorage(indexdir)

exists = whoosh.index.exists_in(indexdir)

if exists:
    ix = storage.open_index(indexname="usages")
else:
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
    ix = storage.create_index(schema_commit, indexname="usages")
