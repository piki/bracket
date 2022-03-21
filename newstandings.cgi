#!/usr/bin/perl

use FindBin 1.51 qw( $RealBin );
use lib $RealBin;

require 'bracket.pl';
use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";

my $tourney = $q->param('t') || "2022m";
setup("$tourney/teams");
my @actual = @{(read_winners("$tourney/actual"))[0]};
my %out = teams_out(@actual);
open(CS, "<$tourney/cs-brackets") || die "open: $!";
while (<CS>) {
	chomp;
	my ($name, $code) = split/\s+/, $_;
	next if $name =~ /^_/;
	my @winners = find_winners($code);
	$pick{$name} = \@winners;
	$codes{$name} = $code;
}
@realpeople = keys %pick;
$n_entries = $#realpeople + 1;

for ($i=63; $i>=1; $i--) {
	my $round = 6-int(log2($i));
	if ($actual[$i]) {
		my $pot = 0;
		foreach my $name (@realpeople) {
			$pot++ if ($actual[$i] != $pick{$name}[$i]);
		}
		my $correct = $n_entries - $pot;
		foreach my $name (keys %pick) {
			if ($actual[$i] == $pick{$name}[$i]) {
				$score{$name} += $pot/$correct * $score_factor[$round-1];
			}
		}
	}
	#else {
		foreach my $might_win (keys %pick) {
			my $try_pick = $pick{$might_win}[$i];
			my $pot = 0;
			foreach my $name (@realpeople) {
				$pot++ if ($try_pick != $pick{$name}[$i]);
			}
			my $correct = $n_entries - $pot;
			if (!$actual[$i] && !$out{$try_pick}) {
				$possible{$might_win} += $pot/$correct * $score_factor[$round-1];
			}
			$aggression{$might_win} += $pot/$correct * $score_factor[$round-1];
		}
	#}
}

foreach my $name (keys %codes) {
	$possible{$name} += $score{$name};
}

foreach my $name (keys %codes) {
	$upsets{$name} = bitcount($codes{$name});
}

$best_score = $score{(sort { $score{$b} <=> $score{$a} } keys %score)[0]};

print qq(
<html>
<head>
<title>Aggressiveness standings</title>
<link rel="stylesheet" type="text/css" href="/_bracket.css">
</head>
<body>
Click on a column name to sort.  Click on 'HTML' or 'Postscript' to
view someone's bracket.  Entries shown in
<font color="#ff2020">red</font> have been mathematically
eliminated.
<p>
<table border=1 rules="all" cellpadding=3>
<tr bgcolor="#cccccc">
<th align="left"><a href="newstandings.cgi?t=$tourney&sort=n">name</a></th>
<th align="left"><a href="newstandings.cgi?t=$tourney&sort=s">score</a></th>
<th align="left"><a href="newstandings.cgi?t=$tourney&sort=p">possible</a></th>
<th align="left"><a href="newstandings.cgi?t=$tourney&sort=a">aggression</a></th>
<th align="left">code</th>
<th align="left"><a href="newstandings.cgi?t=$tourney&sort=u">upsets</a></th>
<th align="left">brackets</th>
</tr>);

if ($q->param('sort') eq "p") {
	@k = sort { $possible{$b} <=> $possible{$a} } keys %pick;
}
elsif ($q->param('sort') eq "s") {
	@k = sort { $score{$b} <=> $score{$a} } keys %pick;
}
elsif ($q->param('sort') eq "a") {
	@k = sort { $aggression{$b} <=> $aggression{$a} } keys %pick;
}
elsif ($q->param('sort') eq "u") {
	@k = sort { $upsets{$b} <=> $upsets{$a} } keys %pick;
}
else {
	@k = sort keys %pick;
}

foreach my $name (@k) {
	if ($possible{$name} < $best_score) {
		print "<tr bgcolor=\"#ffcccc\">\n  <td>$name</td>\n";
	}
	else {
		print "<tr>\n  <td>$name</td>\n";
	}
	printf "<td><a href=\"new-score.cgi?t=$tourney&n=$name\">%.2f</a></td>\n", $score{$name};
	printf "<td>%.2f</td>\n", $possible{$name};
	printf "<td>%.2f</td>\n", $aggression{$name};
	print "<td>$codes{$name}</td>\n";
	print "<td>$upsets{$name}</td>\n";
	print "  <td><a href=\"code-to-html.cgi?t=$tourney&c=$codes{$name}&n=$name\">HTML</a> <a href=\"code-to-ps.cgi?t=$tourney&c=$codes{$name}&n=$name\">Postscript</a></td>\n</tr>\n";
}

print "</table>\n<p>\n";
print "Actual bracket so far: <a href=\"code-to-ps.cgi?t=$tourney&actual=1\">Postscript</a><br>\n";
print "Who's <a href=\"whosleft.cgi?t=$tourney\">left</a>?<br>\n";
print "Have you been <a href=\"elimcheck.cgi?t=$tourney\">eliminated</a>?<br>\n";
#print "Code so far: ".(join'.', get_perfect_code())."<br>\n";

print "<p>Click on a game in the bracket below to see the actual result\n";
print "(if the game has been played yet) and everyone's picks for that\n";
print "game.\n";
$|=1;
system("./html-new.pl $tourney actual");

print "</body></html>\n";
