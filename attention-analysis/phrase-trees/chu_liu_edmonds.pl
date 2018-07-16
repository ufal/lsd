#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use autodie;

use Graph;
use Graph::Directed;
use Graph::ChuLiuEdmonds;

# run e.g. with "-h" option to show doc
if ( @ARGV != 0 ) {
die("Usage: $0 < input_graphs > MSTs
input_graphs = length parent child weight p c w p c w... (one sentence per line)
MSTs = p-c p-c p-c p-c...
Uses 1-based indexing for parent and child; this is in accord with CoNLL where 0 is the root.
Computes MINIMUM spanning tree (use negative weights to get maximum).
Does not explicitly mark the root: the root is the node with no parent.
The 'length' is the number of tokens -- e.g. 5 for nodes 1 to 5.
");
}

while (<>) {
    chomp;
    my @input = split / /;
    my $N = shift @input;
    # parent child weight parent child weight ...
    my @edges = @input;
    #print "N=";
    #print($N);
    #print "\n";


    my $graph = Graph::Directed->new(vertices=>[(1 .. $N)]);
    $graph->add_weighted_edges(@edges);
    #foreach my $edge ($graph->edges) {
        #print $edge->[0];
        #print " ";
        #print $edge->[1];
        #print "\n";
        #}
    my $msts = $graph->MST_ChuLiuEdmonds($graph);
    #print "MST: \n";
    foreach my $edge ($msts->edges) {
        print $edge->[0];  # parent
        print "-";
        print $edge->[1];  # child
        print " ";
    }
    print "\n";
}

