import os
import json
from unidecode import unidecode

import re
import time
from collections import defaultdict
from string import ascii_lowercase



class Ethnicity(object):

	"""
	get ethnicity from name
	"""
	
	def __init__(self):

		self.DATADIR = os.path.join(os.path.curdir, 'data')

		self.ETHNICITIES = """indian japanese greek arabic turkish
									thai vietnamese balkan italian samoan
										hawaiian khmer chinese korean polish""".split()

		print(f'ethnicities: {len(self.ETHNICITIES)}')
		
		self.ETHNIC_NAMES_U = json.load(open(os.path.join(self.DATADIR, 'data_names_u_.json'), 'r'))
		print(f'unique names: {len({n for l in self.ETHNIC_NAMES_U for n in self.ETHNIC_NAMES_U[l]})}')

		self.ETHNIC_ENDINGS_U = json.load(open(os.path.join(self.DATADIR, 'data_surname_end_u_.json'), 'r'))
		print(f'unique surname endings: {len({n for l in self.ETHNIC_ENDINGS_U for n in self.ETHNIC_ENDINGS_U[l]})}')

		self.SEPARATORS = re.compile(r'[-,_/().]')
		
		# make name and surname dictionaries by letter for required ethnicities
		self.names = dict()
		self.surnames = dict()

		
	def _normalize(self, st):
		
		if not isinstance(st, str):
			return None

		_st = unidecode(st.lower().strip())

		if len(_st) < 2:
			return None

		# replace separators with white spaces
		_st = re.sub(self.SEPARATORS,' ', _st)

		# remove all non-letters
		_st = ''.join([c for c in _st if c in ascii_lowercase + ' ']).strip()

		if not _st:
			return None

		# split and join again in case there are any stray white spaces
		_st = ' '.join(_st.split())
	 
		return _st

	def _by_letter(self, name, what):
		"""
		find unique name or surname by letter
		"""
		assert what in 'name surname_ending'.split(), f'function _by_letter must receive a valid what value!'

		if what == 'name':	

			_l1 = name[0]
	
			try:
				return self.ETHNIC_NAMES_U[_l1].get(name, None)
			except:
				return None

		elif what == 'surname_ending':

			for last in range(4, 1, -1):

				_ = name[-last:]

				_l1 = _[0]

				try:
					return self.ETHNIC_ENDINGS_U[_l1][_]
				except:
					continue

	def _split_name_surname(self, st):
		"""
		st is presumably a full name; split it into name and surname
		"""
		_words = st.split()

		if len(_words) == 2:
			_name, _surname = _words
		elif len(_words) == 1:
			_name = _words.pop()
			_surname = None
		else:
			# ignore the middle
			_name = _words[0]
			_surname = words[-1]

		if _name and len(_name) < 2:
			_name = None

		return (_name, _surname)

	def _find_unique(self, name, surname):

		_name, _surname = name, surname

		if _name:
			eth_unique_name = self._by_letter(_name, 'name')
			if eth_unique_name:
				return eth_unique_name
		if _surname:
			eth_surn_ending = self._by_letter(_surname, 'surname_ending')
			if eth_surn_ending:
				return eth_surn_ending
	
	def get(self, st):

		st = self._normalize(st)
		
		if not st:
			return None

		_name, _surname = self._split_name_surname(st)

		ethnicity = self._find_unique(_name, _surname)

		if not ethnicity:
			ethnicity = self._find_unique(_surname, _name)

		return ethnicity
				

if __name__ == '__main__':

	e = Ethnicity()
	print(e.get('alingoglu akio 0&&& '))
