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
	
	def __init__(self, verbose=False):

		self.VERBOSE = verbose

		self.DATADIR = os.path.join(os.path.curdir, 'data')

		self.ETHNICITIES = set("""indian japanese greek arabic turkish
									thai vietnamese balkan italian samoan
										hawaiian khmer chinese korean polish fijian english german spanish portuguese russian""".split())
		
		assert self.ETHNICITIES <= set(os.listdir(self.DATADIR)), '** error ** data is missing for some ethnicities!'

		# map the included ethnicities to race
		self.RACE_TO_ETHN = {'asian': {'indian', 'japanese', 'vietnamese', 'chinese', 'korean', 'khmer', 'thai'},
							 'white': {'greek', 'turkish', 'balkan', 'italian', 'polish', 
							 							 			'english', 'german', 'portuguese', 'russian'},
							 'black': {'arabic'},
							 'latino': {'spanish'}}
		
		self.SEPARATORS = re.compile(r'[-,_/().]')

		# folder to store created dictionaries (for testing purposes)
		self.TEMP_DIR = os.path.join(os.path.curdir, 'temp')

		# quotes on how to add full name components to first and last names: we require minimal counts
		# e.g. 1 means just add all available, while 2 means add only those that occur at least twice 
		self.QUOTES = {'russian': {'last_names': 1, 'first_names': 2},
						'indian': {'last_names': 1, 'first_names': 3},
						'japanese': {'last_names': 1, 'first_names': 2},
						'vietnamese': {'last_names': 1, 'first_names': 2},
						'chinese': {'last_names': 1, 'first_names': 4},
						'korean': {'last_names': 1, 'first_names': 2},
						'khmer': {'last_names': 1, 'first_names': 1},
						'thai': {'last_names': 2, 'first_names': 1},
						'greek': {'last_names': 1, 'first_names': 2},
						'turkish': {'last_names': 1, 'first_names': 2},
						'balkan': {'last_names': 1, 'first_names': 2},
						'italian': {'last_names': 1, 'first_names': 2},
						'polish': {'last_names': 2, 'first_names': 1},
						'english': {'last_names': 2, 'first_names': 1},
						'german': {'last_names': 2, 'first_names': 2},
						'portuguese': {'last_names': 1, 'first_names': 1},
						'arabic': {'last_names': 1, 'first_names': 1},
						'spanish': {'last_names': 1, 'first_names': 2},
						'fijian': {'last_names': 1, 'first_names': 1}
						}

		self.SURNAME_NOT_ENOUGH = {'english', 'german'}
		self.NAME_IS_ENOUGH = {'arabic', 'japanese', 'fijian', 'samoan', 'hawaiian'}

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

	def __writejson(self, dic, file):
		"""
		write a dictionary that has set entries to json
		"""
		dic_ = defaultdict(lambda: defaultdict(list))
		for l in dic:
			for _ in dic[l]:
				dic_[l][_] = list(dic[l][_])

		json.dump(dic_, open(file, 'w'))


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
					if self.VERBOSE:
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
						for name_, count in Counter(lst).most_common():
							if count >= self.QUOTES[e][name]:
								if name == 'last_names':
									self.ETHNIC_SURNAMES_U[name_[0]][name_].add(e)
								elif name == 'first_names':
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
		
		# store dictionaries (for testing purposes, to see what's in there)

		if not os.path.exists(self.TEMP_DIR):
			os.mkdir(self.TEMP_DIR)

		self.__writejson(self.ETHNIC_NAMES_U, os.path.join(self.TEMP_DIR, 'dic_names_.json'))
		self.__writejson(self.ETHNIC_SURNAMES_U, os.path.join(self.TEMP_DIR, 'dic_surnames_.json'))
		self.__writejson(self.ETHNIC_ENDINGS_U, os.path.join(self.TEMP_DIR, 'dic_sur_endings_.json')) 

		json.dump(self.RACE_DIC, open(os.path.join(self.TEMP_DIR, 'dic_race_.json'),'w'))

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
		return self.ETHNIC_NAMES_U[word[0]].get(word, set())

	def search_surnames(self, word):
		"""
		find word in the surname dictionary (arranged by letter)
		"""
		return self.ETHNIC_SURNAMES_U[word[0]].get(word, set())

	def search_surname_endings(self, word):
		"""
		find word in the surname ending dictionary (arranged by letter)
		"""
		found = set()

		for n in range(5,2,-1):
			_ = word[-n:]
			ethnicity_set = self.ETHNIC_ENDINGS_U[_[0]].get(_, None)
			if ethnicity_set:
				found.update(ethnicity_set)
				if len(ethnicity_set) == 1:
					return found

		return found

	def search_race(self, word):
		"""
		find race
		"""
		return self.RACE_DIC[word[0]].get(word, None)


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
	
	def get(self, st):

		st = self._normalize(st)
		
		if not st:
			return None

		_name, _surname = self._split_name_surname(st)

		name_ethnicities = self.search_names(_name)
		print('name_ethnicities=',name_ethnicities)
		surname_ethnicities = self.search_surnames(_surname)
		print('surname_ethnicities=',surname_ethnicities)
		surname_ending_ethnicities = self.search_surname_endings(_surname)
		print('surname_ending_ethnicities=',surname_ending_ethnicities)
		race = self.search_race(_surname)

		ethnicity = None

		# if both name and surname point to a specific ethnicity
		_ns = name_ethnicities & surname_ethnicities
		if len(_ns) == 1:
			return _ns

		# if name only
		if len(name_ethnicities) == 1:
			if name_ethnicities & self.NAME_IS_ENOUGH:
				return name_ethnicities

		# if surname only 
		if len(surname_ethnicities) == 1:
			if not (surname_ethnicities & self.SURNAME_NOT_ENOUGH):
				return surname_ethnicities

		# if name and surname ending point to something definite
		_nse = name_ethnicities & surname_ending_ethnicities
		if len(_nse) == 1:
			return _nse

		# if surname endings only
		if len(surname_ending_ethnicities) == 1:
			if not (surname_ending_ethnicities & self.SURNAME_NOT_ENOUGH):
				return surname_ending_ethnicities

		# if name only
		if len(name_ethnicities) == 1:
			return name_ethnicities


		# if name may be multiple ethnicities, race can help to decide
		if race:
			_sr = surname_ethnicities & self.RACE_TO_ETHN[race]
			if len(_sr) == 1:
				return _sr
			_ser = surname_ending_ethnicities & self.RACE_TO_ETHN[race]
			if len(_ser) == 1:
				return _ser
			_nr = name_ethnicities & self.RACE_TO_ETHN[race]
			if len(_nr) == 1:
				return _nr

		# by now it seems it's hard to pick a single ethnicity, so if there are only 2 candidates..
		if len(_ns) == 2:
			return _ns

		return ethnicity
				

if __name__ == '__main__':

	e = Ethnicity().make_dicts()

	test_names = ['jessica hui', 'robert schulz', 'vlad petrovskiy', 'mariam smith',
						'peter mallow', 'raj kumar', 'iker pozzi', 'mohammad johnson', 
						'bastian ozil', 'frank patrakos', 'david fuentes', 'kim yoon',
						'emele kuoi', 'andrew reid', 'pyotr slakowski', 'igor korostil', 'nima sharifi','mehrdad pegah']

	for name in test_names:
		_ = e.get(name)
		print(f'{name.upper()} is {next(iter(_)).upper() if _ else None}')
