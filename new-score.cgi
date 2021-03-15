#!/usr/bin/perl

use FindBin 1.51 qw( $RealBin );
use lib $RealBin;

require 'bracket.pl';
use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";

my $tourney = $q->param('t') || "2019m";
setup("$tourney/teams");
my $who = $q->param('n');
my @actual = @{(read_winners("$tourney/actual"))[0]};
my @losers = get_losers(@actual);
my %out = teams_out(@actual);
open(CS, "<$tourney/cs-brackets") || die "open: $!";
while (<CS>) {
	chomp;
	my ($name, $code) = split/\s+/, $_;
	next if $name =~ /^_/;
	my @winners = find_winners($code);
	$pick{$name} = \@winners;
	$codes{$name} = $code;
	$n_entries++;
}

print "<html>\n<head>\n<title>Aggressiveness summary for $who</title>\n";
print "<link rel=\"stylesheet\" type=\"text/css\" href=\"/_bracket.css\">\n";
print "</head>\n\n";
print "<body>\n";
print "<table border=1 rules=\"all\" cellpadding=3>\n";
print "<tr bgcolor=\"#cccccc\">\n";
print "<th>game</th>\n";
print "<th>round</th>\n";
print "<th>winner</th>\n";
print "<th>loser</th>\n";
print "<th>points</th>\n";
print "<th>weighted</th></tr>\n";

for ($i=63; $i>=1; $i--) {
	my $round = 6-int(log2($i));
	if ($actual[$i]) {
		my $pot = 0;
		foreach my $name (keys %pick) {
			$pot++ if ($actual[$i] != $pick{$name}[$i]);
		}
		next if !$pot;
		my $correct = $n_entries - $pot;
		if ($actual[$i] == $pick{$who}[$i]) {
			$score{$who} += $pot/$correct;
			printf "<tr><td>$i</td><td>$round</td><td>$team{$actual[$i]}</td><td>$team{$losers[$i]}</td><td>%.2f</td><td>%.2f</td></tr>\n", $pot/$correct, $pot/$correct*$score_factor[$round-1];
		}
	}
	else {
		my $try_pick = $pick{$who}[$i];
		next if $out{$try_pick};
		my $pot = 0;
		foreach my $name (keys %pick) {
			$pot++ if ($try_pick != $pick{$name}[$i]);
		}
		next if !$pot;
		my $correct = $n_entries - $pot;
		$possible{$who} += $pot/$correct;
		printf "<tr bgcolor=\"#cccccc\"><td>$i</td><td>$round</td><td>$team{$try_pick}?</td><td>&nbsp;</td><td>%.2f</td><td>%.2f</td></tr>\n", $pot/$correct, $pot/$correct*$score_factor[$round-1];
	}
}

print "</table></body></html>\n";
