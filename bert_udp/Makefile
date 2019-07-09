sample:
	cat sample.input | generate-skip-sentences.py > sample.conllu
	./apply.sh
	./get_scores.py sample.conllu sample.npz > sample.scores
