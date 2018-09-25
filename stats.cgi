#!/usr/bin/perl

# global statistics
#   $most_overtimes  -- count of most overtimes in a game
#   @most_overtimes_t -- strings describing all games with $most_overtimes overtimes
#   $closest[0..7]   -- closest 1/16, 8/9, 5/12, 6/11, etc.
#   $furthest[0..7]  -- biggest spread 1/16, 8/9, etc.
#   $total[0..7]/$count[0..7] -- average spread 1/16, 8/9, etc.
#   $r_closest[1..6] -- closest spread by round
#   $r_furthest[1..6] -- biggest spread by round
#   $most_won[1..16] -- most rounds won by an X seed
#   $fewest_won[1..16] -- fewest rounds won by an X seed
#   $survived{"$round.$seed"} -- number of $seed teams remaining after $round
#   $winning_count[$a][$b] -- number of times an $a seed has beaten a $b seed, any round
#   $total_games
#   $games_alphabetical

require 'bracket.pl';

print "Content-type: text/html\n\n";

use CGI qw/:standard/;
$q = new CGI;
my $tourney = $q->param('t') || "m";

foreach my $tourney (<????$tourney>) {
	my ($y) = $tourney =~ /^(\d{4})/;
	#next if ($y < 1985);
	show_stats($tourney);
}

%seed_expectations = (
	1 => 4,
	2 => 3,
	3 => 2,
	4 => 2,
	5 => 1,
	6 => 1,
	7 => 1,
	8 => 1,
	9 => 0,
	10 => 0,
	11 => 0,
	12 => 0,
	13 => 0,
	14 => 0,
	15 => 0,
	16 => 0
);

print "<html>\n<head>\n<title>Bracket statistics</title>\n";
print "<link rel=\"stylesheet\" type=\"text/css\" href=\"/_bracket.css\">\n";
print "<style type=\"text/css\">\nth {color:#000000;background:#cccccc}\n</style>\n";
print "</head>\n<body>\n";

print "<b>Total completed games</b>: $total_games<br>\n";
printf "<b>Total upsets</b>: $total_upsets (%.2f%%)<br>\n", ($total_upsets*100.0/$total_games);
printf "<b>Total wins by alphabetically superior school</b>: $games_alphabetical (%.2f%%)<br>\n", ($games_alphabetical*100.0/$total_games);

print "<table rules=\"all\" border=1 cellpadding=3>\n<tr>\n<th colspan=6>";
print "Smallest and largest margins of victory, first round</th></tr>\n";
print "<tr>\n";
print "<th rowspan=2>Pairing</th><th colspan=2>Smallest</th>";
print "<th colspan=2>Largest</th><th rowspan=2>Average</th></tr>\n";
print "<tr><th>pts</th><th>teams</th><th>pts</th><th>teams</th></tr>\n";

foreach my $i (0..7) {
	my $label = $game{63-$i};
	$label =~ s/\.\d+//g;
	print "<tr><td>$label</td><td>$closest[$i]</td>"
		."<td>".(join"<br>",@{$closest_t[$i]})."</td><td>$furthest[$i]</td>"
		."<td>".(join"<br>",@{$furthest_t[$i]})."</td>"
		."<td>".int(0.5+$total[$i]/$count[$i])."</td></tr>\n";
}
print "</table>\n";

print "<p><table rules=\"all\" border=1 cellpadding=3>\n<tr>\n<th colspan=5>";
print "Smallest and largest margins of victory, by round</th></tr>\n";
print "<tr>\n";
print "<th rowspan=2>Round</th><th colspan=2>Smallest</th>";
print "<th colspan=2>Largest</th></tr>\n";
print "<tr><th>pts</th><th>teams</th><th>pts</th><th>teams</th></tr>\n";
foreach my $r (1..6) {
	print "<tr><td>$round_name[$r]</td><td>$r_closest[$r]</td>"
		."<td>".(join"<br>",@{$r_closest_t[$r]})."</td><td>$r_furthest[$r]</td>"
		."<td>".(join"<br>",@{$r_furthest_t[$r]})."</td></tr>\n";
}
print "</table>\n";

print "<p><table rules=\"all\" border=1 cellpadding=3>\n<tr>\n<th colspan=5>";
print "Most and fewest victories, by seed</th></tr>\n";
print "<tr>\n";
print "<th rowspan=2>Seed</th><th colspan=2>Most</th>";
print "<th colspan=2>Fewest</th></tr>\n";
print "<tr><th>games</th><th>teams</th><th>games</th><th>teams</th></tr>\n";
foreach my $seed (1..16) {
	printf "<tr><td>$seed</td><td align=\"center\">%d<br>", $most_won[$seed];
	if ($most_won[$seed] == 6) {
		print "won championship</td>";
	}
	else {
		print "lost in ".$round_name[$most_won[$seed]+1]."</td>";
	}
	print "<td>".(join"<br>",trunc_list(8,@{$most_won_t[$seed]}))."</td>";
	print "<td align=\"center\">$fewest_won[$seed]<br>lost in "
		.$round_name[$fewest_won[$seed]+1]."</td>"
		."<td>".(join"<br>",trunc_list(8,@{$fewest_won_t[$seed]}))."</td></tr>\n";
}
print "</table>\n";

print "<p><table rules=\"all\" border=1 cellpadding=3>\n<tr>\n<th colspan=2>";
print "Most overtimes</th></tr>\n";
print "<tr><td>${most_overtimes}OT</td><td>".join("<br>",@most_overtimes_t)."</td></tr></table>\n";

print "<p><table rules=\"all\" border=1 cellpadding=3>\n<tr>\n<th colspan=7>";
print "Teams still alive after each round, by seed</th></tr>\n";
print "<tr>\n";
print "<th>Seed</th>";
foreach my $r (1..6) {
	print "<th>$round_name[$r]</th>";
}
print "</tr>\n";
foreach my $seed (1..16) {
	print "<tr><td>$seed</td>";
	foreach my $r (1..6) {
		print "<td>".$survived{"$r.$seed"}."</td>";
	}
	print "</tr>\n";
}
print "</table>\n";

my $year = 1900 + (localtime())[5];
print "<p><table rules=\"all\" border=1 cellpadding=3\n<tr>\n<th colspan=4>";
print "Longest active tournament streaks</th></tr><tr><th>Team</th><th>Years</th><th>Avg seed</th><th>Avg games won</th></tr>\n";
my %streak;
my %avgseed;
my %avgwon;
foreach my $t (keys %seeding) {
	my $y = $year;
	my $sum = 0;
	my $totalwon = 0;
	while (exists $seeding{$t}{$y}) {
		$sum += $seeding{$t}{$y} if $y < $year;
		$totalwon += $gameswon{$t}{$y} if $y < $year;
print "<!-- gameswon{$t}{$y} = $gameswon{$t}{$y} -->\n";
		$y--;
	}
	if ($year > $y) {
		$streak{$t} = $year - $y;
		if ($year > $y + 1) {
			$avgseed{$t} = $sum / ($year - $y - 1);
			$avgwon{$t} = $totalwon / ($year - $y - 1);
		}
	}
}
my $count = 0;
foreach my $t (sort { $streak{$b} <=> $streak{$a} || $avgwon{$b} <=> $avgwon{$a} } keys %streak) {
	printf qq(<tr><td><a href="team.cgi?t=$year$tourney&q=$t">%s</a></td><td>%d</td><td>%.2f</td><td>%.2f</td></tr>\n), $t, $streak{$t}, $avgseed{$t}, $avgwon{$t};
	last if ++$count == 20;
}
print "</table>\n";

my %avg_mov;
my %min_mov;
print "<p><table rules=\"all\" border=1 cellpadding=3\n<tr>\n<th colspan=3>";
print "Most dominant champions</th></tr><tr><th>Team</th><th>Average margin of victory</th><th>Minimum margin of victory</th></tr>\n";
$count = 0;
foreach my $mov (sort { $b <=> $a } keys %avg_mov) {
	foreach my $team (@{$avg_mov{$mov}}) {
		my ($tlink) = $team =~ /\((\d{4})\)/;
		print qq(<tr><td><a href="standings.cgi?t=$tlink$tourney">$team</a></td><td>$mov</td><td>$min_mov{$team}</td></tr>\n);
	}
	last if ++$count == 20;
}
print "</table>\n";

print "<p><table rules=\"all\" border=1 cellpadding=3\n<tr>\n<th colspan=17>";
print "Odds of winning for all seed pairings</th></tr><tr><td></td>\n";
foreach my $col (1..16) {
	print "<th>$col</th>";
}
print "</tr>\n";
foreach my $row (1..16) {
	my @colors = ( "#ccffcc", "#aaddaa", "#88bb88", "#669966" );
	print "<tr><th>$row</th>";
	foreach my $col (1..16) {
		if ($row == $col) {
			print "<td align=\"center\" bgcolor=\"#ffffff\">$winning_count[$row][$col]</td>";
		}
		elsif ($winning_count[$col][$row] + $winning_count[$row][$col] == 0) {
			print "<td bgcolor=\"#cccccc\"></td>";
		}
		else {
			my $round = get_round($row, $col);
			my $color = $colors[$round-1];
			$pct = 100.0*$winning_count[$row][$col] / ($winning_count[$col][$row] + $winning_count[$row][$col]);
			printf "<td bgcolor=\"$color\">%d-%d (%.1f%%)</td>", $winning_count[$row][$col], $winning_count[$col][$row], $pct;
		}
	}
	print "</tr>\n";
}
print "</table>\n";


my $endyear = 1900 + (localtime())[5];
my $startyear = int($endyear / 10) * 10;
print "<p><table rules=\"all\" border=1 cellpadding=3\n<tr>\n<th colspan=5>";
print "<a name=\"achievers\">Under/overachievers, $startyear-$endyear</a></th></tr><tr><th>Team</th><th>Games won</th><th>Seed expectations</th><th>diff</th><th>ratio</th></tr>\n";
my %totalwon;
my %shouldawon;
foreach my $t (keys %seeding) {
	for my $y ($startyear..$endyear) {
		my $sum = 0;
		my $totalwon = 0;
		if (exists $seeding{$t}{$y}) {
			$totalwon{$t} += $gameswon{$t}{$y};
			$shouldawon{$t} += $seed_expectations{$seeding{$t}{$y}};
		}
	}
}
foreach my $t (sort { $totalwon{$b}-$shouldawon{$b} <=> $totalwon{$a}-$shouldawon{$a} || $totalwon{$b}/($shouldawon{$b}||1) <=> $totalwon{$a}/($shouldawon{$a}||1) || $totalwon{$b} <=> $totalwon{$a} || $a cmp $b } keys %gameswon) {
	next if $shouldawon{$t} < 3;
	my $ratio = $totalwon{$t}/$shouldawon{$t};
	$bestratio ||= $ratio;
	my $color = 0x888888;
	if ($ratio > 1) {
		$color = 0x888888 + ((0x77 * (($ratio-1)/($bestratio-1))) << 8);
	}
	elsif ($ratio < 1) {
		$color = 0xff8888 - ((0x77 * $ratio) << 16);
	}
	printf qq(<tr bgcolor="#%06x"><td><a href="team.cgi?t=$year$tourney&q=$t">%s</a></td><td>%d</td><td>%d</td><td>%2d</td><td>%.2f</td></tr>\n),
		$color, $t, $totalwon{$t}, $shouldawon{$t}, $totalwon{$t}-$shouldawon{$t}, $ratio;
}
print "</table>\n";


sub show_stats {
	my $tourney = $_[0];
	print "<!-- $tourney -->\n";
	my ($tyear) = $tourney =~ /^(\d+)/;
	setup("$tourney/teams");
	my @refs = read_winners("$tourney/actual");
	my @actual = @{$refs[0]};
	my @score_winner = @{$refs[1]};
	my @score_loser = @{$refs[2]};
	my @overtimes = @{$refs[3]};
	my @loser = get_losers(@actual);

	foreach my $i (0..7) {
		foreach my $j (0..3) {
			my $g = 63 - 8*$j - $i;

			my ($a, $b) = who_played($g, @actual);
			$seeding{$team{$a}}{$tyear} = int($a);
			$seeding{$team{$b}}{$tyear} = int($b);

			next if !(defined $score_winner[$g] && defined $score_loser[$g]);
			my $spread = $score_winner[$g] - $score_loser[$g];
			my $name = "(".int($a).")$team{$a} - (".int($b).")$team{$b}, $score_winner[$g]-$score_loser[$g] ($tourney)";

			if ($spread == $closest[$i]) {
				push @{$closest_t[$i]}, $name;
			}
			elsif (!defined $closest[$i] || $spread < $closest[$i]) {
				$closest[$i] = $spread;
				@{$closest_t[$i]} = ( $name );
			}

			if ($spread == $furthest[$i]) {
				push @{$furthest_t[$i]}, $name;
			}
			elsif ($spread > $furthest[$i]) {
				$furthest[$i] = $spread;
				@{$furthest_t[$i]} = ( $name );
			}

			$total[$i] += $spread;
			$count[$i]++;
		}
	}

	my $champ = (who_played(1, @actual))[0];
	my $champ_movtotal;
	my $champ_games_played;
	my $champ_minmov = 1000;

	foreach my $g (1..63) {
		my $r = 6-int(log2($g));
		next if !$actual[$g];
		my ($a, $b) = who_played($g, @actual);
		$survived{"$r.".int($a)}++;

		die unless $actual[$g] eq $a;
		$gameswon{$team{$a}}{$tyear}++;

		next if !defined $team{$a} || !defined $team{$b};  # Bye

		print "<!-- $game: ($a) $team{$a} defeats ($b) $team{$b} -->\n";
		$total_games++;
		$games_alphabetical++ if $team{$a} lt $team{$b};
		$total_upsets++ if int($a) > int($b);

		if ($actual[$g]) {
			$winning_count[int($a)][int($b)]++;
		}

		my $winner_name = "(".int($a).")$team{$a} ($tourney)";
		my $loser_name = "(".int($b).")$team{$b} ($tourney)";
		if ($r == $most_won[int($a)]) {
			push @{$most_won_t[int($a)]}, $winner_name;
		}
		elsif ($r > $most_won[int($a)]) {
			$most_won[int($a)] = $r;
			@{$most_won_t[int($a)]} = ( $winner_name );
		}

		if (!defined $fewest_won[int($b)] || $r-1 < $fewest_won[int($b)]) {
			$fewest_won[int($b)] = $r-1;
			@{$fewest_won_t[int($b)]} = ( $loser_name );
		}
		elsif ($r-1 == $fewest_won[int($b)]) {
			push @{$fewest_won_t[int($b)]}, $loser_name;
		}

		next if !(defined $score_winner[$g] && defined $score_loser[$g]);
		my $spread = $score_winner[$g] - $score_loser[$g];
		my $name = "(".int($a).")$team{$a} - (".int($b).")$team{$b}, $score_winner[$g]-$score_loser[$g] ($tourney)";

		if ($a == $champ) {
			$champ_games_played++;
			$champ_movtotal += $spread;
			if ($spread < $champ_minmov) { $champ_minmov = $spread; }
		}

		if ($spread == $r_closest[$r]) {
			push @{$r_closest_t[$r]}, $name;
		}
		elsif (!defined $r_closest[$r] || $spread < $r_closest[$r]) {
			$r_closest[$r] = $spread;
			@{$r_closest_t[$r]} = ( $name );
		}

		if ($spread == $r_furthest[$r]) {
			push @{$r_furthest_t[$r]}, $name;
		}
		elsif ($spread > $r_furthest[$r]) {
			$r_furthest[$r] = $spread;
			@{$r_furthest_t[$r]} = ( $name );
		}

		if ($overtimes[$g] == $most_overtimes) {
			push @most_overtimes_t, $name;
		}
		elsif ($overtimes[$g] > $most_overtimes) {
			$most_overtimes = $overtimes[$g];
			@most_overtimes_t = ( $name );
		}
	}

	print "<!-- champ=$champ $team{$champ} movtotal=$champ_movtotal gp=$champ_games_played -->\n";
	if ($champ_games_played) {
		my $avg = sprintf "%.2f", $champ_movtotal/$champ_games_played;
		my $tname = "$champ $team{$champ} ($tyear)";
		$avg =~ s/\.0*$//;
		push @{$avg_mov{$avg}}, $tname;
		$min_mov{$tname} = $champ_minmov;
	}
}

sub trunc_list {
	my $max = shift @_;
	if ($#_+1 > $max) {
		my @ret = @_[($#_-$max+2)..$#_];
		#my @ret = @_[0..($max-2)];
		push @ret, "... (".($#_+1-($max-1))." others)";
		return @ret;
	}
	else {
		return @_;
	}
}

sub get_round {
	my ($a, $b) = @_;
	foreach my $r (1..6) {
		$rmax = (1<<(4-$r));       # 1->8, 2->4, etc.
		$rsum = 2*$rmax + 1;       # 1->17, 2->9, etc.
		if ($a + $b == $rsum) { return $r; }
		if ($a > $rmax) { $a = $rsum-$a; }
		if ($b > $rmax) { $b = $rsum-$b; }
	}
	print "SHOULD NOT GET HERE!\n";
	return 0;
}
