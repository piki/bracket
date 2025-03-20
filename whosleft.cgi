#!/usr/bin/perl

use FindBin 1.51 qw( $RealBin );
use lib $RealBin;

require 'bracket.pl';
use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";

my $tourney = $q->param('t') || "2025m";
setup("$tourney/teams");
@actual = @{(read_winners("$tourney/actual"))[0]};
%out = teams_out(@actual);

@colors = ( 'c35555', 'd36e6e', 'dd8888', 'eea3a3', 'eeaa55', 'cccc77' );
$win_color = '99ff99';

print "<html>\n<head>\n<title>Who's left?</title>\n";
print "<link rel=\"stylesheet\" type=\"text/css\" href=\"/_bracket.css\">\n";
print "</head>\n\n";
print "<body>\n";
if (scalar %out == 63) {
	print "The winner is shown in green.\n";
}
else {
	print "Teams remaining are shown in white.\n";
}
print "Teams that have been eliminated are shown in red cells, next to the\n";
print "round they were eliminated.\n<p>\n";
print "<table border=1 rules=\"all\" cellpadding=4>\n";
print "<tr bgcolor=\"#cccccc\">\n  <th>Seed</th>\n";
foreach my $b (@bracket) {
	print "  <th colspan=\"2\">$b</th>\n";
}
print "</tr>\n";
foreach my $seed (1..16) {
	next if !($team{"$seed.1"} || $team{"$seed.2"} || $team{"$seed.3"} || $team{"$seed.4"});
	print "<tr>\n  <td>$seed</td>\n";
	foreach my $region (1..4) {
		my $n = "$seed.$region";
		if (!defined $team{$n}) {
			print "  <td bgcolor=\"#dddddd\">&nbsp;</td>\n";
		}
		elsif ($out{$n}) {
			my $c = $colors[$out{$n}-1];
			my $round = 128 >> $out{$n};
			print "  <td bgcolor=\"#$c\">$team{$n}</td>\n";
			print "  <td bgcolor=\"#$c\">$round</td>\n";
		}
		elsif (scalar %out == 63) {
			print "  <td bgcolor=\"#$win_color\">$team{$n}</td>\n";
			print "  <td bgcolor=\"#$win_color\">W</td>\n";
		}
		else {
			print "  <td colspan=\"2\">$team{$n}</td>\n";
		}
	}
	print "</tr>\n";
}
print "</table>\n</body>\n</html>\n";
