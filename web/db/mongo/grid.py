# encoding: utf-8

"""MongoDB GridFS file serving support."""

if __debug__:
	log = __import__('logging').getLogger(__name__)


def render_grid_file(context, f):
	"""Allow direct use of GridOut GridFS file wrappers as endpoint responses."""
	
	f.seek(0)  # Ensure we are reading from the beginning.
	response = context.response  # Frequently accessed, so made local.  Useless optimization on Pypy.
	
	if __debug__:  # We add some useful diagnostic information in development, omitting from production due to sec.
		response.headers['Grid-ID'] = str(f._id)  # The GridFS file ID.
		log.debug("Serving GridFS file.", extra=dict(
				identifier = str(f._id),
				filename = f.filename,
				length = f.length,
				mimetype = f.content_type
			))
	
	response.conditional_response = True
	response.accept_ranges = 'bytes'  # We allow returns of partial content, if requested.
	response.content_type = f.content_type  # Direct transfer of GridFS-stored MIME type.
	response.content_length = f.length  # The length was pre-computed when the file was uploaded.
	response.content_md5 = response.etag = f.md5  # As was the MD5, used for simple integrity testing.
	response.last_modified = f.metadata.get('modified', None)  # Optional additional metadata.
	response.content_disposition = 'attachment; filename=' + f.name  # Preserve the filename through to the client.
	
	# Being asked for a range or not determines the streaming style used.
	if context.request.if_range.match_response(response):
		response.body_file = f  # Support seek + limited read.
	else:
		response.app_iter = iter(f)  # Assign the body as a streaming, chunked iterator.
	
	return True

