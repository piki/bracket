#!/usr/bin/perl

$r1height = 30;

require 'bracket.pl';

use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";

my $tourney = $q->param('t') || "2019m";
my $title = make_title($tourney);
setup("$tourney/teams");
@winner = find_winners("0.0.0.0.0.0.0.0");
@loser = get_losers(@winner);
print qq(
<html>
<head><title>$title</title>
<script language="javascript">
function fixup(number) {
	if (number == 1) { return; }
	var subNumber = Math.floor(number/2);
	var toUpdate = "g"+subNumber;
	var updateWhich = 1-(number%2);
	var target = document.forms["theform"].elements[toUpdate];
	var chosen = document.forms["theform"].elements["g"+number];
	var newText = chosen.options[chosen.selectedIndex].text;
	var newValue = chosen.options[chosen.selectedIndex].value;
	var isSelected = target.options[updateWhich].selected;
	target.options[updateWhich] = new Option(newText, newValue, false, isSelected);
	if (isSelected) { fixup(subNumber); }
}
</script>

</head>
<body>
<h1>$title</h1>
<form name="theform" action="make-code.cgi" method="post">
);

foreach (1..4) { bracket($_, uc($bracket[$_-1])); }
finalfour();

print q(
<input type="submit">
</form>
);

sub bracket {
	my ($b, $bname) = @_[0..1];

	print "<p><table><tr>\n<td>\n	<table height=\"100%\">\n";
	print cell(16*$r1height, $bname);
	print "	</table>\n</td>\n<td>\n	<table height=\"100%\">\n";

	foreach my $i (1..8) {
		my $g = 64 - $i - 8*($b-1);
		my ($a, $b) = split/,/,$game{$g};
		print cell($r1height, "(".int($a).") $team{$a}");
		print cell($r1height, "(".int($b).") $team{$b}");
	}
	print "	</table>\n</td>\n";

	foreach my $r (1..4) {
		print "<td>\n	<table height=\"100%\">\n";
		foreach my $i (1..(1<<(4-$r))) {
			my ($t1, $t2, $sel);
			my $g = (1<<(7-$r)) - $i - (1<<(4-$r))*($b-1);
			if ($g >= 32) {
				$t1 = $winner[$g];
				$t2 = $loser[$g];
			}
			else {
				$t1 = $winner[$g*2+1];
				$t2 = $winner[$g*2];
			}
			if ($t1 ne $winner[$g]) {
				$sel = " selected";
			}
			print cell($r1height*2**$r, "<select name=\"g$g\" onchange='fixup($g)'><option value=\"$t1\">$team{$t1}<option value=\"$t2\"$sel>$team{$t2}</select>");
		}
		print "	</table>\n";
	}
	
	print "</td></tr></table>\n";
}

sub finalfour {
	print "<p><table><tr>\n<td>\n";

	foreach my $r (5..6) {
		print "<td>\n	<table height=\"100%\">\n";
		foreach my $i (1..(1<<(6-$r))) {
			my $g = (1<<(7-$r)) - $i;
			print cell($r1height*2**($r-4), "<select name=\"g$g\" onchange='fixup($g)'><option value=\"$winner[$g]\">$team{$winner[$g]}<option value=\"$loser[$g]\">$team{$loser[$g]}</select>");
		}
		print "	</table>\n";
	}
	
	print "</td></tr></table>\n";
}

sub cell {
	"		<tr><td height=\"$_[0]\">$_[1]</td></tr>\n";
}
