#!/usr/bin/perl

use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";

require 'bracket.pl';

my $tourney = $q->param('t') || "m";
$tourney =~ s/^\d+//;
my $myteam = $q->param('q') || "Duke";

print "<h2>$myteam</h2><p>\n";

my $total_wins = 0;
my $total_losses = 0;
my $years = 0;
print "<table border=1 rules=\"all\" cellpadding=2>\n";
print qq(
<tr bgcolor="#cccccc">
  <th align="left">Year&nbsp;&nbsp;&nbsp;</th>
  <th align="left">Seed&nbsp;&nbsp;&nbsp;</th>
  <th align="left">Games&nbsp;&nbsp;&nbsp;</th>
  <th align="left">Record&nbsp;&nbsp;&nbsp;</th>
</tr>);
foreach my $fn (sort {$b cmp $a} <*$tourney/teams>) {
	my ($year) = $fn =~ /^(\d{4})/;
	my $seed = 0;
	%team = ();
	setup("$year$tourney/teams");
  my @ret = read_winners("$year$tourney/actual");
  @actual = @{$ret[0]};
  @score_winners = @{$ret[1]};
  @score_losers = @{$ret[2]};
  @overtimes = @{$ret[3]};
  @loser = get_losers(@actual);

	foreach (keys %team) {
		if ($team{$_} eq $myteam) { $seed = $_; }
	}

	next if !$seed;   # didn't make the tourney that year
	my ($sa, $sb) = $seed =~ /(\d+)\.(\d+)/;
	my $first_opp = (17-$sa).".$sb";
	my $last_won = 0;
	foreach (0..63) { if ($actual[$_] eq $seed) { $last_won = $_; last; } }
	$last_won = $last_won ? int(log2($last_won)) : 6;
	$color = ('ffaaaa','ffff99','aaffaa','bbbbff','ffffff','dddddd','bbbbbb')[$last_won];
	print qq(
<tr bgcolor="#$color">
  <td valign="top"><a href="standings.cgi?t=$year$tourney">$year</a></td>
  <td valign="top">).int($seed)."</td><td>";
	my ($wins, $losses) = (0, 0);
	for(my $game=63; $game>=0; $game--) {
		next if $actual[$game] != $seed && $loser[$game] != $seed;
		#print "Y=$year G=$game W=$actual[$game] L=$loser[$game] SW=$score_winners[$game] SL=$score_losers[$game]<br>\n";
		my $score;
		if (defined $score_winners[$game]) {
			$score = ", $score_winners[$game]-$score_losers[$game]";
			if ($overtimes[$game] == 1) { $score .= " OT"; }
			elsif ($overtimes[$game] > 1) { $score .= " $overtimes[$game]OT"; }
		}

		if ($actual[$game] eq $seed) {
			if ($game < 32 || defined $team{$first_opp}) {   # not a bye
				print gamelink($year, $game, "Defeated") . " " . teamlink($year, $team{$loser[$game]})."$score<br>\n";
				$wins++;
			}
			if ($game >= 32) { $g = int($game/2); } else { $g = int($g/2); }
		}
		elsif ($game == $g) {
			print gamelink($year, $game, "Lost") . " to " . teamlink($year, $team{$actual[$game]})."$score<br>\n";
			$losses++;
			last;
		}
		if ($actual[$game] eq $first_opp) {
			print gamelink($year, $game, "Lost") . " to " . teamlink($year, $team{$first_opp})."$score<br>\n";
			$losses++;
			last;
		}
	}
	close(RESULTS);

	$years++;
	$total_wins += $wins;
	$total_losses += $losses;
	print "</td><td valign=\"top\">$wins-$losses</td></tr>\n";
}
print "</table>\n";

print "<br>\n";
print "Years in the tournament: $years<br>\n";
print "Record: $total_wins-$total_losses<br>\n";

sub gamelink {
	"<a href=\"onegame.cgi?t=$_[0]$tourney&g=$_[1]\">$_[2]</a>";
}

sub teamlink {
	"<a href=\"team.cgi?t=$_[0]$tourney&q=$_[1]\">$_[1]</a>";
}
