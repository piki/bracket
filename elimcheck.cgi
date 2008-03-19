#!/usr/bin/perl

require 'bracket.pl';

use CGI qw/:standard/;
                                                                                                                                           
$q = new CGI;
                                                                                                                                           
print "Content-type: text/html\n\n";
                                                                                                                                           
my $tourney = $q->param('t') || "2008m";
my $hide = $q->cookie('hidejunk');
setup("$tourney/teams");
my @actual = @{(read_winners("$tourney/actual"))[0]};
my %out = teams_out(@actual);
open(CS, "<$tourney/cs-brackets") || die "open: $!";
while (<CS>) {
	chomp;
	my ($name, $code) = split/\s+/, $_;
	next if $hide && $name =~ /^_/;
	my @predicted = find_winners($code);
	$predicted{$name} = \@predicted;
	my ($score, $possible) = get_scores(\@predicted);
	$scores{$name} = $score;
	$possibles{$name} = $possible;
	$codes{$name} = $code;
}

$best_score = $scores{(sort { $scores{$b} <=> $scores{$a} } keys %scores)[0]};
	@k = sort keys %scores;

print qq(
<html>
<head>
<title>Eliminated!</title>
<link rel="stylesheet" type="text/css" href="bracket.css">
</head>
<body>
<table rules="all" border=1 cellpadding=2>
  <tr bgcolor="#cccccc">
    <td>name</td>
    <td>score</td>
    <td>max</td>
    <td>margin</td>
);
foreach $name (@k) {
	next if $name =~ /^_/;
	#print "    <td>".substr($name,0,5)."</td>\n";
	print "    <td>$name</td>\n";
}
print "  </tr>\n";
foreach $name (@k) {
	my %vs;
	my $beaten;
	my $highest_opp;
	my $margin;
	foreach my $opponent (@k) {
		next if $opponent =~ /^_/;
		next if $name eq $opponent;
		$vs{$opponent} = (eliminated_check($predicted{$name}, $predicted{$opponent}, \@actual, \%out))[1];
		$highest_opp = $vs{(sort { $vs{$b} <=> $vs{$a} } @k)[0]};
		$margin = $possibles{$name} - $highest_opp;
		$beaten ||= ($vs{$opponent} > $possibles{$name});
	}
	my $color = $beaten ? "ffcccc" : "d7ffd7";
	print qq(
  <tr>
    <td bgcolor="#$color"><a href="code-to-html.cgi?t=$tourney&c=$codes{$name}&n=$name">$name</a></td>
    <td bgcolor="#$color"><a href="bracket-score.cgi?t=$tourney&c=$codes{$name}">$scores{$name}</a></td>
    <td bgcolor="#$color">$possibles{$name}</td>
    <td bgcolor="#$color">$margin</td>
);
	foreach my $opponent (@k) {
		next if $opponent =~ /^_/;
		if ($name eq $opponent) {
			print "    <td></td>\n";
			next;
		}
		if ($possibles{$name} < $vs{$opponent}) {
			print "    <td bgcolor=\"#ffcccc\">$vs{$opponent}</td>\n";
		}
		else {
			print "    <td>$vs{$opponent}</td>\n";
		}
	}
	print "  </tr>\n";
}
print "</table>\n";

sub get_scores {
	my @predicted = @{$_[0]};
	my $score;
	my $possible;

	$score = 0;
	for ($i=63; $i>=1; $i--) {
		my $r = 6 - int(log2($i));
		if (defined $actual[$i]) {
			$right = ($actual[$i] == $predicted[$i]) + 0;
	#		print "game $i (r=$r): right=$right\n";
			if ($right) {
				$score += $score_factor[$r-1];
			}
		}
		else {
			if (!$out{$predicted[$i]}) {
				$possible += $score_factor[$r-1];
			}
		}
	}
	$possible += $score;
	($score, $possible);
}
