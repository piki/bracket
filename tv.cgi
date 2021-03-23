#!/usr/bin/perl

use FindBin 1.51 qw( $RealBin );
use lib $RealBin;

require 'bracket.pl';

use CGI qw/:standard/;

$q = new CGI;

print "Content-type: text/html\n\n";

my $tourney = $q->param('t') || "2021m";
setup("$tourney/teams");
my @schedule = read_schedule("$tourney/schedule");
my @ret = read_winners("$tourney/actual");
@winner = @{$ret[0]};


foreach (1..$#schedule) { push @{$sched_map{$schedule[$_]}}, $_ if $schedule[$_]; }
print qq(
<html>
<head>
<title>TV schedule</title>
<link rel="stylesheet" type="text/css" href="/_bracket.css">
</head>

<body>
<table cellspacing=0 cellpadding=2>
);
foreach (sort datesort keys %sched_map) {
	foreach my $g (@{$sched_map{$_}}) {
		if ($g >= 32) {
			my @seed = split/,/,$game{$g};
			$team1 = "(".seed($seed[0]).") $team{$seed[0]}";
			$team2 = "(".seed($seed[1]).") $team{$seed[1]}";
		}
		else {
			$team1 = $winner[$g*2+1];
			$team1 = $team1 ? "(".seed($team1).") $team{$team1}" : $unknown;
			$team2 = $winner[$g*2];
			$team2 = $team2 ? "(".seed($team2).") $team{$team2}" : $unknown;
		}
		$color = $winner[$g] ? qq(bgcolor="#cccccc") : "";
		print
qq(<tr $color>
	<td><a href="onegame.cgi?g=$g">$team1 vs. $team2</a></td>
	<td>&nbsp;</td>
	<td>$_</td>
</tr>
);
	}
}
print "</table>\n";

sub datesort {
	my $f1 = (split/\s+/,$a,2)[1];
	my $f2 = (split/\s+/,$b,2)[1];
	$f1 cmp $f2;
}

sub seed {
	(split/\./,$_[0])[0];
}
