cs-ud-dev.words: cs-ud-dev.forms
	sed 's/ /\n/g' $< > $@

cs-ud-dev.freql: cs-ud-dev.words
	sort $< | uniq -c | sort -nr > $@

