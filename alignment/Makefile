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



