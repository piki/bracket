#!/usr/bin/perl

require 'bracket.pl';
use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";

my $tourney = $q->param('t') || "2012m";
setup("$tourney/teams");
@actual = @{(read_winners("$tourney/actual"))[0]};
%out = teams_out(@actual);

print "<html>\n<head>\n<title>Who's left?</title>\n";
print "<link rel=\"stylesheet\" type=\"text/css\" href=\"/_bracket.css\">\n";
print "</head>\n\n";
print "<body>\n";
print "Teams remaining are shown in green.\n";
print "Teams that have been eliminated are shown in red cells, with the\n";
print "round they were eliminated in parentheses.\n<p>\n";
print "<table border=1 rules=\"all\" cellpadding=4>\n";
print "<tr bgcolor=\"#cccccc\">\n  <th>Seed</th>\n  <th>$bracket[0]</th>\n";
print "  <th>$bracket[1]</th>\n  <th>$bracket[2]</th>\n";
print "  <th>$bracket[3]</th>\n</tr>\n";
foreach my $seed (1..16) {
	next if !($team{"$seed.1"} || $team{"$seed.2"} || $team{"$seed.3"} || $team{"$seed.4"});
	print "<tr>\n  <td>$seed</td>\n";
	foreach my $region (1..4) {
		my $n = "$seed.$region";
		if (!defined $team{$n}) {
			print "  <td bgcolor=\"#dddddd\">&nbsp;</td>\n";
		}
		elsif ($out{$n}) {
			print "  <td bgcolor=\"#ffcccc\">$team{$n} ($out{$n})</td>\n";
		}
		else {
			print "  <td bgcolor=\"#ccffcc\">$team{$n}</td>\n";
		}
	}
	print "</tr>\n";
}
print "</table>\n</body>\n</html>\n";
