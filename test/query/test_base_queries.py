# encoding: utf-8

from marrow.mongo.core import Document, Field


class Example(Document):
	name = Field()
	age = Field()

EXAMPLE = Example("Alice", 27)


TRUTHY_CASES = [
		# Comparison
		
		# $eq
		(EXAMPLE.name == "Alice"),
		(EXAMPLE.age == 27),
		
		# $gt
		(EXAMPLE.name > "Aa"),
		(EXAMPLE.age > 18),
		
		# $gte
		# $lt
		# $lte
		# $ne
		# $in
		# $nin
		
		# Logical
		
		# $or
		# $and
		# $not
		# $nor
		
		# Element
		
		# $exists
		# $type
		
		# Evaluation
		
		# $mod
		# $regex
		# $text
		# $where
		
		# Geospatial
		
		# $geoWithin
		# $geoIntersects
		# $near
		# $nearSphere
		
		# Array
		
		# $all
		# $elemMatch
		# $size
		
		# Bitwise
		
		# $bitsAllSet
		# $bitsAnySet
		# $bitsAllClear
		# $bitsAnyClear
		
		# Comments
		
		# $comment
		

	]

FALSY_CASES = [
	]
