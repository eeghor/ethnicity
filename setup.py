from setuptools import setup
import os

setup(name='ethnicity',
      version='0.0.20',
      description='Get ethnicity from name',
      long_description='',
      classifiers=[
      	'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Filters"
      ],
      url='https://github.com/eeghor/ethnicity',
      author='Igor Korostil',
      author_email='eeghor@gmail.com',
      license='MIT',
      packages=['ethnicity'],
      package_dir = {'ethnicity': 'ethnicity'},
      install_requires=['pandas'],
      python_requires='>=3.6',
      include_package_data=True,
      data_files = [('', ['/'.join([t[0], t[1].pop()]) for t in [(_[0], [f for f in _[-1] if ('.txt' in f) or ('.csv' in f)]) for _ in os.walk(os.path.join(os.path.dirname(__file__),'ethnicity', 'data')) if (not _[1]) and _[-1]] if '.' not in  t[0]])],
      keywords='ethnicity name')
