def parse_query(query):
    tags = query.split(' ')
    query = {}
    if tags[0]!='':
        query = {"tags": { "$all" : list(set(tags))}}
    return {"query":query,
            "tags": tags}
