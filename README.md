# ethnicity
Get ethnicity from name.  Currently, we cover the following ethnicities:

* Anglo-Saxon
* Arabic
* Chinese
* Fijian
* German
* Greek
* Hawaiian
* Hispanic  (Spanish and Mexican)
* Indian  (excluding islamic states)
* Iranian
* Italian
* Japanese
* Khmer (Cambodian)
* Korean
* Polish
* Portuguese  (Portuguese and Brazilian)
* Russian
* Samoan
* South-Slavic (Serbian, Croatian, Bosnian, Slovenian)
* Thai
* Turkish
* Vietnamese

## Data Sources
* [Surnames by race (the US Census data)](https://www.census.gov/topics/population/genealogy/data/2010_surnames.html)  
* [Most common Japanese surnames](https://www.japantimes.co.jp/life/2009/10/11/lifestyle/japans-top-100-most-common-family-names/#.WsR48i9L3BI)
* [Most common Indian surnames](https://www.quora.com/What-are-some-of-the-most-common-Indian-last-names)
* [Most common Greek surnames](https://chartcons.com/common-greek-last-names/)
* [Most common Italian surnames](http://www.italianames.com/italian-last-names.php)
* [Samoan surnames](https://www.quora.com/What-are-some-Samoan-last-names)
* [Hawaiian surnames](https://en.wiktionary.org/wiki/Category:Hawaiian_surnames)
* [German surnames](https://en.wikipedia.org/wiki/List_of_the_most_common_surnames_in_Germany)
* [Most popular Spanish names](http://www.lavanguardia.com/vangdata/20150520/54431756037/los-100-nombres-de-hombre-y-mujer-mas-frecuentes-en-espana.html)
* [Most frequent Spanish surnames](http://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177009&menu=resultados&idp=1254734710990)
* [Most common Portuguese surnames](https://pt.wikipedia.org/wiki/Lista_dos_cem_apelidos_mais_frequentes_em_Portugal#cite_note-1)
* [Most common names I Brazil](https://censo2010.ibge.gov.br/nomes/#/ranking)
* [Most common surnames in Brazil](https://nomeschiques.com/apelidos-populares-de-pessoas/)
* [Most common Russian surnames](http://russkg.ru/index.php?option=com_content&view=article&id=4390:-500&catid=84:2012-12-02-23-13-33&Itemid=63)
* [Popular baby names in NSW, Australia](http://www.bdm.nsw.gov.au/Pages/about-us/facts-statistics.aspx)
* [Most common surnames in Saudi Arabia](http://forebears.co.uk/saudi-arabia)
* [Most common surnames in Egypt](http://forebears.co.uk/egypt)
* [Most common surnames in Lebanon](http://forebears.co.uk/lebanon)
* [Most common surnames in Morocco](http://forebears.co.uk/morocco)
* [Most common Palestinian Surnames](http://mepeace.org/forum/topics/palestinian-tribes-clans-and)
* [Most common surnames in Kuwait](http://forebears.co.uk/kuwait)
* [Most common surnames in Europe](https://en.wikipedia.org/wiki/List_of_most_common_surnames_in_Europe)

## Installation
```
pip3 install ethnicity
```

## Usage
```
from ethnicity import Ethnicity

# initialize and create dictionaries
e = Ethnicity().make_dicts()  

# apply to a list of names
e.get(['emele kuoi', 'andrew miller', 'peter', 'andrey',  'nima al hassan', 'tomasz bolowski', 'christiano ronaldo', 'parisa karimi,', 'lisa bowen', 'melissa chan'])

# which gives you a pandas dataframe as below
                 Name    Ethnicity
0          Emele Kuoi       fijian
1       Andrew Miller  anglo-saxon
2               Peter          ---
3              Andrey      russian
4      Nima Al Hassan       arabic
5     Tomasz Bolowski       polish
6  Christiano Ronaldo   portuguese
7       Parisa Karimi      iranian
8          Lisa Bowen  anglo-saxon
9        Melissa Chan      chinese
```
