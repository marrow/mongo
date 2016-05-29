# encoding: utf-8






def matches(data, query):
	pass


def filter(records, query):
	for record in records:
		if matches(record, query):
			yield record


def project(data, query):
	"""MongoDB-style record projection."""
	include = {'_id'} if '_id' in data else set()
	exclude = set()
	
	for field in query:
		if field not in data:
			continue
		
		if query[field]:
			include.add(field)
			continue
		
		exclude.add(field)
		
		if field in include:
			include.remove(field)
	
	if exclude and exclude != {'_id'}:
		return data.__class__({i: data[i] for i in data if i not in exclude})
	
	return data.__class__({i: data[i] for i in include})


