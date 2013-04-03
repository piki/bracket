#!/usr/bin/perl

require 'bracket.pl';

use CGI qw/:standard/;
$q = new CGI;
my $tourney = $q->param('t') || "2013m";
my $code = $q->param('c') || "0.0.0.0.0.0.0.0";
my $name = $q->param('name') || 0;

if($name){
    write_bracket($tourney, $name, $code);
    print "Location: standings.cgi\n\n";
} else {
    print "Location: make-entry.cgi?t=$tourney&c=$code\n\n";
}
