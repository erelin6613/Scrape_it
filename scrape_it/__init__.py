"""
Scrape_it

Author: Valentyna Fihurska

Lisence: Apache-2.0

Scrape_it is a tool for extracting valueble information 
from the website of interest. Save your time on reading 
and crawling through the website and leave it for Scrape_it!

Find an example how to run program in the run.py
or refer to README 


Note on additional .txt files in regex directory

name_stop_words.txt - Contains words to filter unneeded words
						during the search of entity's name

email_keywords.txt - Specific file to filter emails based on 
						keywords it might contain (this is
						as needed for current task)

regex.txt - some regular expressions to search phone numbers;
			at the current time is not in use, phonenumbers
			package is used instead; one of improvements
			should be a workflow which would allow efficient
			and accurate phone matching with good filter
			pipeline from 'scraping trash'

address.txt - some regular expressions to match addresses,
				not perfect expesially given the diversity
				of different address formats accross 
				different countries
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#import .scrape_it
from .scrape_it import Scrape_it


__version__ = '0.3.8'

if __name__ == '__main__':
    import doctest
    doctest.testmod()

