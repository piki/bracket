#!/usr/bin/perl

use FindBin 1.51 qw( $RealBin );
use lib $RealBin;

require 'bracket.pl';
use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";

my $tourney = $q->param('t') || "2023m";
my $hide = $q->cookie('hidejunk');
setup("$tourney/teams");
my $gameno = $q->param('g');
my @ret = read_winners("$tourney/actual");
my @actual = @{$ret[0]};
my @score_winners = @{$ret[1]};
my @score_losers = @{$ret[2]};
my @score_overtimes = @{$ret[3]};
my @schedule = read_schedule("$tourney/schedule");
my ($ta, $tb);
if ($gameno >= 32) {
	($ta, $tb) = split/,/, $game{$gameno};
}
else {
	($ta, $tb) = ($actual[$gameno*2+1], $actual[$gameno*2]);
}
my $gametitle;
if ($ta && $tb) {
	$gametitle = "$team{$ta} - $team{$tb}";
}
else {
	$gametitle = "Game $gameno";
}
open(CS, "<$tourney/cs-brackets") || die "open: $!";
while (<CS>) {
	chomp;
	my ($name, $code) = split/\s+/, $_;
	next if $hide && $name =~ /^_/;
	my @winners = find_winners($code);
	$pick{$name} = $winners[$gameno];
}

%out = teams_out(@actual);

print "<html>\n<head>\n<title>Results for $gametitle</title>\n";
print "<link rel=\"stylesheet\" type=\"text/css\" href=\"/_bracket.css\">\n";
print "</head>\n\n";
print "<body>\n";
print "<table border=1 rules=\"rows\" cellpadding=3>\n";
print "<tr bgcolor=\"#cccccc\"><th align=\"left\">name</th><th align=\"left\">pick</th></tr>\n";
if (defined $actual[$gameno]) {
	print "<tr><td>Actual result</td><td>";
	print "$team{$actual[$gameno]}";
	if (defined $score_winners[$gameno]) {
		print " ($score_winners[$gameno]-$score_losers[$gameno]";
		if ($overtimes[$gameno] == 1) { print " OT"; }
		elsif ($overtimes[$gameno] > 1) { print " $overtimes[$gameno]OT"; }
		print ")";
	}
}
else {
	print "<tr><td colspan=2>Game has not happened yet\n";
	if (defined $schedule[$gameno]) {
		print "<br>Airtime: $schedule[$gameno]\n";
	}
}
print "</td><tr>\n";
foreach (sort keys %pick) {
	my $color;
	if (defined $actual[$gameno]) {
		$color = ($pick{$_} eq $actual[$gameno]) ? "#ccffcc" : "#ffcccc";
	}
	elsif ($out{$pick{$_}}) {
		$color = "#ffcccc";
	}
	$color ||= "#ffffff";
	print "<tr bgcolor=\"$color\"><td>$_</td><td>$team{$pick{$_}}</td></tr>\n";
}
print "</table>\n</body>\n</html>\n";
