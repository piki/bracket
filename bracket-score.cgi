#!/usr/bin/perl

require 'bracket.pl';
use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/plain\n\n";

my $tourney = $q->param('t') || "2014m";
setup("$tourney/teams");
my @actual = @{(read_winners("$tourney/actual"))[0]};
my @loser = get_losers(@actual);
my @predicted = find_winners($q->param('c'));

%out = teams_out(@actual);

$score = 0;
for ($i=63; $i>=1; $i--) {
	my $r = 6 - int(log2($i));
	$max += $score_factor[$r-1];
	if (defined $actual[$i]) {
		$right = ($actual[$i] == $predicted[$i]);
#		print "game $i (r=$r): right=$right\n";
		if ($right) {
			$score += $score_factor[$r-1];
		}
		elsif ($loser[$i] == $predicted[$i]) {
			print "game $i (round $r) was wrong: $team{$actual[$i]} beat $team{$predicted[$i]}\n";
		}
		else {
			print "game $i (round $r) was wrong: $team{$predicted[$i]} didn't even play\n";
		}
	}
	else {
		if ($out{$predicted[$i]}) {
			print "game $i (round $r) will be wrong: $team{$predicted[$i]} is already out\n";
		}
		else {
			$possible += $score_factor[$r-1];
		}
	}
}
$possible += $score;
print "Score: $score / $max       Best possible: $possible / $max\n";
