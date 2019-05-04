cs-ud-dev.words: cs-ud-dev.forms
	sed 's/ /\n/g' $< > $@

cs-ud-dev.freql: cs-ud-dev.words
	sort $< | uniq -c | sort -nr > $@

cs-ud-dev.nottop100: cs-ud-dev.freql
	tail -n +101 $< | cut -c9- > $@

cs-ud-dev.ntkshuf: cs-ud-dev.nottop100
	shuf $< > $@

cs-ud-dev.testwords: cs-ud-dev.ntkshuf
	head -n 10000 $< > $@

split_train_test.out:
	./split_train_test.py cs-ud-train.forms cs-ud-dev.forms > $@


