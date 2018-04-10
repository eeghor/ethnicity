import os
import json
from unidecode import unidecode
import pandas as pd

import math
import re
import time
from collections import defaultdict, Counter
from string import ascii_lowercase

class Ethnicity(object):

	"""
	get ethnicity from name
	"""
	
	def __init__(self):

		self.DATADIR = os.path.join(os.path.curdir, 'data')

		self.ETHNICITIES = set("""indian japanese greek arabic turkish
									thai vietnamese balkan italian samoan
										hawaiian khmer chinese korean polish fijian english german spanish""".split())
		
		assert self.ETHNICITIES <= set(os.listdir(self.DATADIR)), '** error ** data is missing for some ethnicities!'

		print(f'ethnicities: {len(self.ETHNICITIES)}')

		# map the included ethnicities to race
		self.RACE_TO_ETHN = {'asian': ['indian', 'japanese', 'vietnamese', 'chinese', 'korean', 'khmer', 'thai'],
							 'white': ['greek', 'turkish', 'balkan', 'italian', 'polish', 'english', 'german'],
							 'black': ['arabic'],
							 'latino': ['spanish']}
		
		self.SEPARATORS = re.compile(r'[-,_/().]')

	def __readtext(self, file):
		"""
		read from a text file line by line
		"""
		return {unidecode(l.strip()) for l in open(os.path.join(self.DATADIR, file),'r').readlines() if l.strip()}

	def __writetext(self, what, file):
		"""
		write what to a text file
		"""
		with open(os.path.join(self.DATADIR, file),'w') as f:
			for _ in sorted(list(what)):
				f.write(f'{unidecode(_.strip())}\n')

	def make_dicts(self, refresh=True):
		"""
		create a dictionary like this:
		{'korean': {'full_names': ['name1', 'name2',..],
					'first_names': ['name1', 'name2',..]}}
		"""

		d = defaultdict(lambda: defaultdict())

		for e in self.ETHNICITIES:

			for _ in 'full_names first_names last_names last_names_common'.split():

				try:
					f = f'{e}/{_}/{_}_.txt'
					if refresh:
						self.__writetext(self.__readtext(f), f)
					d[e][_] = list(self.__readtext(f))
				except:
					print(f'warning: can\'t find {e} {_}!')		


		self.ETHNIC_NAMES_U = defaultdict(lambda: defaultdict(set))
		self.ETHNIC_SURNAMES_U = defaultdict(lambda: defaultdict(set))
		self.ETHNIC_ENDINGS_U = defaultdict(lambda: defaultdict(set))

		# create a dictionary like {'a': 'aaron': ['english', 'fijian'],
		#  								   'abu': ['polish', 'khmer']}

		for e in d:

			for n in d[e]['first_names']:
				self.ETHNIC_NAMES_U[n[0]][n].add(e)

			# and another dictionary for last name endings like
			# {'b': 'sky': ['japanese', 'italian'],
			# 		'ozzi': ['italian']}

			if 'last_names' in d[e]:
				for n in d[e]['last_names']:
					self.ETHNIC_SURNAMES_U[n[0]][n].add(e)

			# extras: add the most popular names/surnames from the full names if available
			if 'full_names' in d[e]:
				for name in ['first_names', 'last_names']:
					if name in d[e]:
						pick_idx = -1 if (name == 'last_names') else 0
						lst = [full_name.split()[pick_idx] for full_name in d[e]['full_names']]
						for name_, count in Counter(lst).most_common(math.floor(0.8*len(lst))):
							if name == 'last_names':
								if count > 1:
									self.ETHNIC_SURNAMES_U[name_[0]][name_].add(e)
							elif name == 'first_names':
								if count > 2:
									self.ETHNIC_NAMES_U[name_[0]][name_].add(e)

			# if common surnames are available, simply add them all
			try:
				for sur in d[e]['last_names_common']:
					self.ETHNIC_SURNAMES_U[sur[0]][sur].add(e)
			except:
				pass

		# dictionary for surname endings
		for l in self.ETHNIC_SURNAMES_U:
			for n in self.ETHNIC_SURNAMES_U[l]:
				for s in range(3,6):  # note: 3,4,5
					_ = n[-s:]
					self.ETHNIC_ENDINGS_U[_[0]][_].update(self.ETHNIC_SURNAMES_U[l][n])
	

		# create a race dictionary like 
		# {'d': {'david': 'white', 'diego': 'latino'}}

		self.RACE_DIC = defaultdict(lambda: defaultdict())

		race = {'pctwhite': 'white', 
				'pctblack': 'black', 
				'pctapi': 'asian', 
				'pctaian': 'native', 
				'pct2prace': 'mixed', 
				'pcthispanic': 'latino'}

		d = pd.read_csv(os.path.join(self.DATADIR, 'Names_2010Census.csv')).iloc[:,[0,5,6,7,8,9,10]].dropna()
		d['name'] = d['name'].str.lower()
		d.iloc[:,1:] = d.iloc[:,1:].applymap(lambda x: 0 if not str(x).replace('.','').isdigit() else x)
		d['max'] = d.iloc[:,1:].astype(float).max(axis=1)
		d['race'] = (d.iloc[:,1:-1].astype(float).idxmax(axis=1)
					.where(d['max'] > 70, None)
					 .apply(lambda x: race.get(x, None)))
		d.drop('max', axis=1, inplace=True)
		d = d[d['race'].notnull()]

		for r in d.iterrows():
			_name = r[1]['name']
			self.RACE_DIC[_name[0]][_name] = r[1]['race']

		
		return self
	
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

	def search_names(self, word):
		"""
		find word in the name dictionary (arranged by letter)
		"""
		return self.ETHNIC_NAMES_U[word[0]].get(word, None)

	def search_surnames(self, word):
		"""
		find word in the surname dictionary (arranged by letter)
		"""
		return self.ETHNIC_SURNAMES_U[word[0]].get(word, None)

	def search_surname_endings(self, word):
		"""
		find word in the surname ending dictionary (arranged by letter)
		"""
		return self.ETHNIC_ENDINGS_U[word[0]].get(word, None)

	def search_race(self, word):
		"""
		find race
		"""
		return self.RACE_DIC[word[0]].get(word, None)


	# def _by_letter(self, name, what):
	# 	"""
	# 	find unique name or surname by letter
	# 	"""
	# 	assert what in 'name surname_ending race'.split(), f'function _by_letter must receive a valid what value!'

	# 	if what == 'name':	

	# 		_l1 = name[0]
	
	# 		try:
	# 			return self.ETHNIC_NAMES_U[_l1].get(name, None)
	# 		except:
	# 			return None

	# 	elif what == 'surname_ending':

	# 		for last in range(4, 1, -1):

	# 			_ = name[-last:]

	# 			_l1 = _[0]

	# 			try:
	# 				return self.ETHNIC_ENDINGS_U[_l1][_]
	# 			except:
	# 				continue

	# 	elif what == 'race':

	# 		try:
	# 			return self.RACE_DIC[name[0]].get(name, None)
	# 		except:
	# 			return None


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
			_surname = _words[-1]

		if _name and len(_name) < 2:
			_name = None

		return (_name, _surname)

	# def _find_unique(self, name, surname):

	# 	_name, _surname = name, surname

	# 	if _name:
	# 		eth_unique_name = self._by_letter(_name, 'name')
	# 		if eth_unique_name:
	# 			return eth_unique_name

	# 	if _surname:
	# 		eth_surn_ending = self._by_letter(_surname, 'surname_ending')
	# 		rc = self._by_letter(_surname, 'race')
	# 		print('rc=', rc)
	# 		if eth_surn_ending:
	# 			return eth_surn_ending

	
	def get(self, st):

		st = self._normalize(st)
		
		if not st:
			return None

		_name, _surname = self._split_name_surname(st)

		print(f'_name = {_name} _surname = {_surname}')

		print(f'found names: {self.search_names(_name)}')
		print(f'found surnames: {self.search_surnames(_surname)}')
		print(f'found surname endings: {self.search_surname_endings(_surname)}')
		print(f'found race: {self.search_race(_surname)}')


		# return ethnicity
				

if __name__ == '__main__':

	e = Ethnicity().make_dicts()

	print(e.get('carlos sanchez'))
