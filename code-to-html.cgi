#!/usr/bin/perl

require 'bracket.pl';

use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";
print "<link rel=\"stylesheet\" type=\"text/css\" href=\"/_bracket.css\">\n";
$|=1;

my $tourney = $q->param('t') || "2012m";
$tourney =~ s/[^0-9mwn]+//g;
my $title = make_title($tourney);
if ($q->param('actual')) {
	print "<html><head><title>$title</title></head>\n";
	system("./html-new.pl $tourney actual");
}
else {
	my $code = $q->param('c');
	my $name = $q->param('n');
	$code =~ s/[^0-9.]+//g;
	$name =~ s/[^a-zA-Z_0-9.]+//g;
	#print "tourney=\"$tourney\" code=\"$code\" name=\"$name\"<br>";
	print "<html><head><title>$title: $name</title></head>\n";
	print "<center><font size=\"+2\">$title: $name</font><br>\n";
	print "<a href=\"code-to-ps.cgi?t=$tourney&c=$code&n=$name\">postscript version</a></center><p><br><br>\n";
	system("./html-new.pl $tourney $code $name");
}
