A=CzEnAli_1.0

get_manual_wordalignments:
	curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1804/$A.tar.gz
	mkdir $A_unpacked
	cd $A_unpacked
	tar -zxvf ../$A
	qs

get_alignments:
	cat $A_unpacked/merged_data/*/* > all.xml
	grep '<english>' 'all.xml'| sed -e 's/ *<english>//' -e s@'</english> *'@@ > all.en
	grep '<czech>' 'all.xml'| sed -e 's/ *<czech>//' -e s@'</czech> *'@@ > all.cs
	grep '<sure>' 'all.xml'| sed -e 's/ *<sure>//' -e s@'</sure> *'@@ > all.sure

install_fastalign:
	git clone https://github.com/clab/fast_align.git
	cd fast_align
	mkdir build
	cd build
	cmake ..
	make
	cd ../..

F=fast_align/build

L=all.en-cs

align:
	paste all.en all.cs | sed 's/\t/ ||| /' > $L
	$F/fast_align -d -o -v -i    $L > $L.f
	$F/fast_align -d -o -v -r -i $L > $L.r
	$F/atools -i $L.f -j $L.r -c intersect > $L.i
	
zero2one:
	python3 zero2one.py < $L.i > $L.i1

