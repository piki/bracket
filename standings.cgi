#!/usr/bin/perl

use FindBin 1.51 qw( $RealBin );
use lib $RealBin;

require 'bracket.pl';

use CGI qw/:standard/;

$q = new CGI;

print "Content-type: text/html\n";

my $tourney = $q->param('t') || "2024m";
my $sort = $q->param('sort') || "n";
if (defined $q->param('hidejunk')) {
	$hide = $q->param('hidejunk');
	print "Set-Cookie: hidejunk=$hide; expires=Mon, 16-Mar-2015 12:34:56 GMT; domain=piki.org; path=/cgi-bin/bracket/\n\n";
	print "<!-- hide param=\"$hide\" -->\n";
}
else {
	print "\n";
	$hide = $q->cookie('hidejunk');
}
print "<!-- hide cookie=\"$hide\" -->\n";
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

foreach (keys %codes) {
	$upsets{$_} = bitcount($codes{$_});
}

$best_score = $scores{(sort { $scores{$b} <=> $scores{$a} } keys %scores)[0]};
if ($q->param('sort') eq "p") {
	@k = sort { $possibles{$b} <=> $possibles{$a} } keys %scores;
}
elsif ($q->param('sort') eq "s") {
	@k = sort { $scores{$b} <=> $scores{$a} } keys %scores;
}
elsif ($q->param('sort') eq "u") {
	@k = sort { $upsets{$b} <=> $upsets{$a} } keys %scores;
}
else {
	@k = sort keys %scores;
}

#push @k, "Perfect";
#$codes{'Perfect'} = join'.', get_perfect_code();
#($scores{'Perfect'}, $possibles{'Perfect'}) = get_scores($codes{'Perfect'});

my $foo = $hide ? "show" : "hide";
my $foo2 = $hide ? 0 : 1;
my $title = make_title($tourney);
print qq(
<html>
<head>
<title>$title: standings</title>
<link rel="stylesheet" type="text/css" href="/_bracket.css">
</head>

<body>
);
$|=1;
system("./html-new.pl $tourney actual");
print qq(

  <center>
	<p><table cellpadding=0 cellspacing=0>
  <tr><td align="center"><a href="tv.cgi?t=$tourney">TV schedule</a></td></tr>
  <tr><td align="center" id="schedule_target">&nbsp;</td></tr>
  </table>
  </center>

<script TYPE="text/javascript">
<!--
var target = document.getElementById("schedule_target");
function popup(msg,tcell){
if (target != null) target.innerHTML = "<b>"+msg+"</b>";
if (tcell != null) tcell.bgColor = "#c0a0ff";
}

function kill(tcell,color){
	if (target != null) target.innerHTML = "&nbsp;";
  if (tcell != null) tcell.bgColor = color;
}
//-->
</SCRIPT>

<p><hr><p>
Click on a column name to sort.  Click on 'HTML' or 'Postscript' to
view someone's bracket.
<p>
Entries shown in <font color="#ff2020">red</font> have been
mathematically eliminated.  Click <a
href="elimcheck.cgi?t=$tourney">here</a> to find out who is eliminated how.
<p>
<table cellpadding=3 border=1 rules="all"><tr bgcolor="#cccccc">
<th align="left"><a href="standings.cgi?t=$tourney&sort=n">name</a>
(<a href="standings.cgi?t=$tourney&sort=$sort&hidejunk=$foo2">$foo
bonus brackets</a>)</th>
<th align="left"><a href="standings.cgi?t=$tourney&sort=s">score</a></th>
<th align="left"><a href="standings.cgi?t=$tourney&sort=p">possible</a></th>
<th align="left">code</th>
<th align="left"><a href="standings.cgi?t=$tourney&sort=u">upsets</a></th>
</tr>
);
foreach $name (@k) {
	my $eliminated = ($possibles{$name} < $best_score);
	if (!$eliminated) {
		foreach my $opponent (@k) {
			next if $opponent =~ /^_/;
			if ($possibles{$opponent} > $possibles{$name}) {
				$eliminated ||= eliminated_check($predicted{$name}, $predicted{$opponent}, \@actual, \%out);
			}
		}
	}
	#if ($name =~ /^_/) {
	#}
	if ($eliminated) {
		print qq(<tr bgcolor=\"#ffcccc\">\n  <td><a href="code-to-html.cgi?t=$tourney&c=$codes{$name}&n=$name">$name</a></td>\n);
	}
	else {
		print qq(<tr>\n  <td><a href="code-to-html.cgi?t=$tourney&c=$codes{$name}&n=$name">$name</a></td>\n);
	}
	print qq(
		<td><a href="bracket-score.cgi?t=$tourney&c=$codes{$name}">$scores{$name}</a></td>
		<td>$possibles{$name}</td>
		<td>$codes{$name}</td>
		<td>$upsets{$name}</td>
		</tr>
	);
}
print qq(
	</table>\n<p>
	Actual bracket so far: <a href="code-to-ps.cgi?t=$tourney&actual=1">Postscript</a><br>
	Who's <a href="whosleft.cgi?t=$tourney">left</a>?<br>
	Have you been <a href="elimcheck.cgi?t=$tourney">eliminated</a>?<br>

	<p>
);
print "Code so far: ".(join'.', get_perfect_code())."<br>\n";

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
