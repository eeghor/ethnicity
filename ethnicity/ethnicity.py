import os
import json
from unidecode import unidecode
import pandas as pd

import re
import time
from collections import defaultdict
from string import ascii_lowercase

class Ethnicity(object):

	"""
	get ethnicity from name
	"""
	
	def __init__(self, race_thresh=70):

		self.DATADIR = os.path.join(os.path.curdir, 'data')

		self.ETHNICITIES = set("""indian japanese greek arabic turkish
									thai vietnamese balkan italian samoan
										hawaiian khmer chinese korean polish fijian english""".split())
		
		assert self.ETHNICITIES <= set(os.listdir(self.DATADIR)), '** error ** data is missing for some ethnicities!'

		print(f'ethnicities: {len(self.ETHNICITIES)}')
		
		self.ETHNIC_NAMES_U = json.load(open(os.path.join(self.DATADIR, 'data_names_u_.json'), 'r'))
		print(f'unique names: {len({n for l in self.ETHNIC_NAMES_U for n in self.ETHNIC_NAMES_U[l]})}')

		self.ETHNIC_ENDINGS_U = json.load(open(os.path.join(self.DATADIR, 'data_surname_end_u_.json'), 'r'))
		print(f'unique surname endings: {len({n for l in self.ETHNIC_ENDINGS_U for n in self.ETHNIC_ENDINGS_U[l]})}')

		"""
		create a race dictionary (the US Census data); it should be like this:
		{'s': defaultdict(None,
						 {'smith': 'white',
						  'sanchez': 'latino',
						  'sullivan': 'white',
						  'stevens': 'white',
						  'simpson': 'white'
		"""
		self.RACE_DIC = defaultdict(lambda: defaultdict())

		race = {'pctwhite': 'white', 
				'pctblack': 'black', 
				'pctapi': 'asian', 
				'pctaian': 'native', 
				'pct2prace': 'mixed', 
				'pcthispanic': 'latino'}

		d = pd.read_csv(os.path.join(self.DATADIR, 'Names_2010Census.csv')).iloc[:,[0,5,6,7,8,9,10]].dropna()
		d['name'] = d['name'].str.lower()
		d.iloc[:,1:] = d.iloc[:,1:].applymap(lambda x: 0.0 if not str(x).replace('.','').isdigit() else x)
		d['max'] = d.iloc[:,1:].astype(float).max(axis=1)
		d['race'] = (d.iloc[:,1:-1].astype(float).idxmax(axis=1)
					.where(d['max'] > race_thresh, None)
					 .apply(lambda x: race.get(x, None)))
		d.drop('max', axis=1, inplace=True)
		d = d[d['race'].notnull()]

		for r in d.iterrows():
			_name = r[1]['name']
			self.RACE_DIC[_name[0]][_name] = r[1]['race']

		print(f'created race dictionary with the likeliest race for {len({s for l in self.RACE_DIC for s in self.RACE_DIC[l]})} surnames')

		# map the included ethnicities to race
		self.RACE_TO_ETHN = {'asian': ['indian', 'japanese', 'vietnamese', 'chinese', 'korean', 'khmer', 'thai'],
							 'white': ['greek', 'turkish', 'balkan', 'italian', 'polish'],
							 'black': ['arabic']}

		self.SEPARATORS = re.compile(r'[-,_/().]')
		
		# make name and surname dictionaries by letter for required ethnicities
		self.names = dict()
		self.surnames = dict()

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

	def _make_name_dict(self, refresh=True):

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

		return d

	def setup(self):

		d = self._make_name_dict()

		du = defaultdict(lambda: defaultdict(list))
		dx = defaultdict(lambda: defaultdict(set))

		for e in d:
			for n in d[e]['first_names']:
				du[n[0]][n].append(e)

		for e in d:
			if 'last_names' in d[e]:
				for n in d[e]['last_names']:
					for s in range(3,6):
						_ = n[-s:]
						dx[_[0]][_].add(e)

		self.ETHNIC_NAMES_U = du
		self.ETHNIC_ENDINGS_U = dx

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

	def _by_letter(self, name, what):
		"""
		find unique name or surname by letter
		"""
		assert what in 'name surname_ending race'.split(), f'function _by_letter must receive a valid what value!'

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

		elif what == 'race':

			try:
				return self.RACE_DIC[name[0]].get(name, None)
			except:
				return None


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

	def _find_unique(self, name, surname):

		_name, _surname = name, surname

		print('_surname=',_surname)

		if _name:
			eth_unique_name = self._by_letter(_name, 'name')
			if eth_unique_name:
				return eth_unique_name

		if _surname:
			eth_surn_ending = self._by_letter(_surname, 'surname_ending')
			rc = self._by_letter(_surname, 'race')
			print('rc=', rc)
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

		self._find_unique(_name, _surname)

		return ethnicity
				

if __name__ == '__main__':

	e = Ethnicity(race_thresh=67.5).setup()

	print(e.get('apaitia hodgson'))
