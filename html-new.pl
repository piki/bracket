#!/usr/bin/perl
#
# Usage:
#   html-new.pl <tourney> actual
#   html-new.pl <tourney> <code> <name>

@colors = ( "#e8e8e8", "#d4d4d4", "#c0c0c0", "#acacac", "#b0b0b0", "#00005f" );

require 'bracket.pl';

my $tourney = $ARGV[0] || "2017m";
my $title = make_title($tourney);
setup("$tourney/teams");
if ($ARGV[1] eq "actual") {
	my @ret = read_winners("$tourney/actual");
	@winner = @{$ret[0]};
	@score_winner = @{$ret[1]};
	@score_loser = @{$ret[2]};
	@overtimes = @{$ret[3]};
}
else {
	my @ret = read_winners("$tourney/actual");
	@actual = @{$ret[0]};
	%out = teams_out(@actual);
	@winner = find_winners($ARGV[1]);
 	$title .= ": $ARGV[2]";
}
my @schedule = read_schedule("$tourney/schedule");
@loser = get_losers(@winner);

@bracket = map { uc($_) } @bracket;

print qq(<table border=0 cellpadding=1 cellspacing=1 width="100%">);
if ($bracket[0]) { print qq(
<tr><td align="center" colspan=4 bgcolor="$colors[5]"><b><font size="+1" color="#ffffff">$bracket[0]</b></td><td>
</td><td align="center" colspan=4 align="right" bgcolor="$colors[5]"><b><font size="+1" color="#ffffff">$bracket[2]</b></td></tr>
); }
bracket(1, 3);
print qq(<tr height=10><td colspan=4></td><td colspan=4></td></tr>);
if ($bracket[1]) { print qq(
<tr><td align="center" colspan=4 bgcolor="$colors[5]"><b><font size="+1" color="#ffffff">$bracket[1]</b></td>
<td align="center" colspan=4 align="right" bgcolor="$colors[5]"><b><font size="+1" color="#ffffff">$bracket[3]</b></td></tr>); }
bracket(2, 4);
print qq(</table>);
print qq(</body></html>);

sub bracket {
	my ($b1, $b2) = @_[0..1];

	foreach my $row (1..8) {
		print "<tr>";
		foreach my $col (1..4) { do_cell($b1, $col, $row); }
		if ($b1 == 1 && $row == 1) { finalfour(); }
		foreach my $col (1..4) { do_cell($b2, 5-$col, $row); }
		print "</tr>\n";
	}
}

sub do_cell {
	my ($bracket, $round, $row) = @_[0..2];
	return unless ($row-1) % (1<<($round-1)) == 0;

	if ($round == 1) {
		my $g = 64 - $row - 8*($bracket-1);
		my @seed = split/,/,$game{$g};
		my @score;
		if ($winner[$g] == $seed[0]) { @score = ($score_winner[$g], $score_loser[$g]); }
			else { @score = ($score_loser[$g], $score_winner[$g]); }

		my $popup = "";
		if (defined $schedule[$g]) { $popup = qq(onmouseover="javascript:popup('$schedule[$g]', this)" onmouseout="kill(this, '$colors[0]')"); }

		if ($team{$seed[0]} && $team{$seed[1]}) {
			print "<td $popup class=\"brak\" width=\"10%\" bgcolor=\"$colors[0]\">";
			print "<a href=\"team.cgi?t=$tourney&q=".esc($team{$seed[0]})."\">";
			print "(".int($seed[0]).") $team{$seed[0]}</a>";
			if (defined $score[0]) { print " - $score[0]"; }
			if ($overtimes[$g] == 1) { print " (OT)"; }
			elsif ($overtimes[$g] > 1) { print " ($overtimes[$g]OT)"; }
		}
		else {
			print "<td $popup class=\"brak\" width=\"10%\">";
		}

		print "<br>";
		if ($team{$seed[1]} && $team{$seed[0]}) {
			print "<a href=\"team.cgi?t=$tourney&q=".esc($team{$seed[1]})."\">";
			print "(".int($seed[1]).") $team{$seed[1]}</a>";
			if (defined $score[1]) { print " - $score[1]"; }
		}
		print "</td>\n";
	}
	else {
		my $oldrow = int(1 + ($row-1) / (1<<($round-2)));
		my $g = (1<<(8-$round)) - $oldrow - (1<<(5-$round))*($bracket-1);
		if ($winner[$g] eq "0.0" || $winner[$g-1] eq "0.0") {
			print "<td $popup class=\"brak\" width=\"10%\" rowspan=" . (1<<($round-1)) . ">";
			print "</td>\n";
		}
		else {
			my $popup;
			if (defined $schedule[$g/2]) {
				$popup = qq(onmouseover="javascript:popup('$schedule[$g/2]', this)" onmouseout="kill(this,'$colors[$round-1]')");
			}
			print "<td $popup class=\"brak\" width=\"10%\" bgcolor=\"$colors[$round-1]\" rowspan=" . (1<<($round-1)) . ">";
			print_team($g,$overtimes[$g/2]);
			print "<br>\n";
			print_team($g-1);
			print "</td>\n";
		}
	}
}

sub finalfour {
	my @ff;
	my $champ;
	foreach my $g (1..3) {
		my $popup = "";
		if (defined $schedule[$g]) { $popup = qq(onmouseover="javascript:popup('$schedule[$g]', this)" onmouseout="kill(this)"); }

		my @score = ($winner[$g*2+1] == $winner[$g])
			? ($score_winner[$g], $score_loser[$g])
			: ($score_loser[$g], $score_winner[$g]);

		$ff[$g] = "";
		foreach my $n (0..1) {
			if (defined $winner[$g*2+1-$n]) {
				$ff[$g] .= "<a href=\"onegame.cgi?t=$tourney&g=".($g*2+1-$n)."\">";
				my $text = "(".int($winner[$g*2+1-$n]).") $team{$winner[$g*2+1-$n]}</a>";
				if (eliminated($g*2+1-$n)) {
					$text = qq(<span class="eliminated">$text</span>);
				}
				elsif (confirmed($g*2+1-$n)) {
					$text = qq(<span class="confirmed">$text</span>);
				}
				$ff[$g] .= $text;
				if (defined $score[$n]) { $ff[$g] .= " - $score[$n]"; }
				if (!$n) {
					if ($overtimes[$g] == 1) { $ff[$g] .= " (OT)"; }
					elsif ($overtimes[$g] > 1) { $ff[$g] .= " ($overtimes[$g]OT)"; }
					$ff[$g] .= "<br>";
				}
			}
			else {
				$ff[$g] .= "<a href=\"onegame.cgi?t=$tourney&g=".($g*2+1-$n)."\">"
					. "$unknown</a><br>";
			}
		}
	}
	if (defined $winner[1]) {
		$champ = "(".int($winner[1]).") $team{$winner[1]}</a>";
		if ($out{$winner[1]}) {
			$champ = qq(<span class="eliminated">$champ</span>);
		}
		elsif ($actual[1]) {
			$champ = qq(<span class="confirmed">$champ</span>);
		}
	}
	else {
		$champ = "$unknown";
	}
	my $popup3;
	if (defined $schedule[3]) {
		$popup3 = qq(onmouseover="javascript:popup('$schedule[3]', this)" onmouseout="kill(this,'#ffffff')");
	}
	my $popup2;
	if (defined $schedule[2]) {
		$popup2 = qq(onmouseover="javascript:popup('$schedule[2]', this)" onmouseout="kill(this,'#ffffff')");
	}
	my $popup1;
	if (defined $schedule[1]) {
		$popup1 = qq(onmouseover="javascript:popup('$schedule[1]', this)" onmouseout="kill(this,'#ffffff')");
	}
	print qq(
<td width="20%" rowspan=19 valign="middle">
  <table width="100%">
  <tr>
    <td colspan=3 align="center" bgcolor="#000000"><font color="#ffffff">FINAL FOUR</font></td>
  </tr><tr>
    <td $popup3 class="brak">$ff[3]</td>
    <td $popup2 align="right">
      <table cellpadding=0 cellspacing=0><tr><td class="brak">$ff[2]</td></tr></table>
    </td>
  </tr>
  <tr><td>&nbsp;</td></tr>
  <tr>
    <td colspan=3 align="center" bgcolor="#000000"><font color="#ffffff">CHAMPIONSHIP</font></td>
  </tr><tr>
    <td $popup1 colspan=3 align="center">$ff[1]</td>
  </tr><tr><td height=25></td></tr><tr>
    <td colspan=3 align="center" bgcolor="#000000"><font color="#ffffff">NATIONAL CHAMPIONS</font></td>
  </tr><tr>
    <td colspan=3 align="center"><a href="onegame.cgi?t=$tourney&g=1">$champ</a></td>
  </tr>
  </table>
</td>);
}

sub esc {
	my $ret = $_[0];
	$ret =~ s/&/%26/g;
	$ret;
}

sub print_team {
	my $g = $_[0];
	my $nextg = int($g/2);
	my $ot = $_[1];
	if (defined $winner[$g]) {
		my $score = ($winner[$g] == $winner[$nextg]) ? $score_winner[$nextg] : $score_loser[$nextg];
		print qq(<!-- winner[$nextg]=").$winner[int($nextg)].qq(" schedule[$nextg]=").$schedule[int($nextg)].qq(" -->);
		if ($team{$loser[$g]}) {
			print "<a href=\"onegame.cgi?t=$tourney&g=$g\">";
		}
		else {
			print "<a href=\"team.cgi?t=$tourney&q=".esc($team{$winner[$g]})."\">";
		}

		my $text = "(".int($winner[$g]).") $team{$winner[$g]}</a>";
		if (eliminated($g)) {
			print qq(<span class="eliminated">$text</span>);
		}
		elsif (confirmed($g)) {
			print qq(<span class="confirmed">$text</span>);
		}
		else { print $text; }

		if (defined $score) { print " - $score"; }
		if ($ot == 1) { print " (OT)"; }
		elsif ($ot > 1) { print " (${ot}OT)"; }
	}
	else {
		print "<a href=\"onegame.cgi?t=$tourney&g=$g\">";
		print "$unknown</a>";
	}
}

sub eliminated {
	my $g = shift;
	($actual[$g] && $actual[$g] != $winner[$g]) || (!$actual[$g] && $out{$winner[$g]});
}

sub confirmed {
	my $g = shift;
	!eliminated($g) && $actual[$g];
}
