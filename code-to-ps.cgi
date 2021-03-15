#!/usr/bin/perl

$lwidth = 0.86;
$lheight = 0.22;
$adjy = 0.05;
$adjx = 0.05;
$marksize = 0.12;

use FindBin 1.51 qw( $RealBin );
use lib $RealBin;

require 'bracket.pl';
require 'ps.pl';
use CGI qw/:standard/;
$q = new CGI;
print "Content-type: application/postscript\n\n";


my $tourney = $q->param('t') || "2008c";
my $title = make_title($tourney);;
setup("$tourney/teams");
if ($q->param('actual')) {
	my @ret = read_winners("$tourney/actual");
	@winner = @{$ret[0]};
	@score_winners = @{$ret[1]};
	@score_losers = @{$ret[2]};
	@overtimes = @{$ret[3]};
}
else {
	@winner = find_winners($q->param('c'));
	my @ret = read_winners("$tourney/actual");
	@actual = @{$ret[0]};
	@score_winners = @{$ret[1]};
	@score_losers = @{$ret[2]};
	@overtimes = @{$ret[3]};
	$title .= ": ".$q->param('n');
	@loser = get_losers(@actual);
}

%out = teams_out(@actual);

ps_begin(1, 'Times-Roman', 'Bracket', 'Landscape');
print "90 rotate 0 -630 translate\n";
ps_setfont('Times-Roman', 20);
ps_text($title, 5.5, 8, 1);
ps_setfont('Times-Roman', 8);
foreach (1..4) { bracket($_, uc($bracket[$_-1])); }
finalfour();
ps_showpage(1);
ps_end();

sub bracket {
	my ($b, $bname) = @_[0..1];

	my $top = 8 - 4*(1-($b%2));
	my $left = ($b <= 2) ? 0.5 : (10.5-$lwidth);
	my $rev = ($b <= 2) ? 1 : -1;

	print "% ---------------\n";
	print "% Bracket: $bname\n";
	print "% Round 0\n";
	my ($x, $y, $x2) = get_line_coords($b, 3, 1.5);
	ps_setfont('Times-Roman', 15);
	if ($b <= 2) {
		ps_text($bname, $x2-0.2, $y-0.1, 2);
	}
	else {
		ps_text($bname, $x+0.2, $y-0.1, 0);
	}
	ps_setfont('Times-Roman', 8);

	foreach my $i (1..8) {
		my $g = 64 - $i - 8*($b-1);
		my ($ta, $tb) = split/,/,$game{$g};
		next if !$team{$tb};   # Bye
		my $x = $left;
		my $x2 = $left + $lwidth;
		my $y = $top - $lheight*2*($i-1);
		my $y2 = $top - $lheight*(2*($i-1)+1);
		ps_text("(".int($ta).") $team{$ta}", $x, $y);
		ps_text("(".int($tb).") $team{$tb}", $x, $y2);
		if ($b <= 2) {
			make_line($x, $y-$adjy, $x2-$adjx);
			make_line($x, $y2-$adjy, $x2-$adjx);
		}
		else {
			make_line($x2, $y-$adjy, $x-$adjx);
			make_line($x2, $y2-$adjy, $x-$adjx);
		}
	}

	foreach my $r (1..4) {
		print "% Round $r\n";
		foreach my $i (1..(1<<(4-$r))) {
			my $g = (1<<(7-$r)) - $i - (1<<(4-$r))*($b-1);
	#		next if !$team{$winner[$g]}
	#			|| !$team{$winner[$g ^ 1]};  # Bye
			my ($x, $y, $x2) = get_line_coords($b, $r, $i);
			print_game($g, $x, $y, $x2);
			if ($r != 4) {
				if ($b <= 2) {
					make_line($x-$adjx, $y-$adjy, $x2-$adjx);
				}
				else {
					make_line($x2-$adjx, $y-$adjy, $x-$adjx);
				}
			}
		}
	}
}

sub print_game {
	my ($g, $x, $y, $x2, $ymark) = @_;
	$ymark ||= $y;
	if (defined $winner[$g]) {
		ps_text("(".int($winner[$g]).") $team{$winner[$g]}", $x, $y);
	}
	if (defined $score_winners[$g] && defined $score_losers[$g]) {
		my $score = "$score_winners[$g]-$score_losers[$g]";
		$score .= " (OT)" if ($overtimes[$g] == 1);
		$score .= " ($overtimes[$g]OT)" if ($overtimes[$g] > 1);
		ps_text($score, $x+0.16, $y-0.16, $x2);
	}
	if (defined $team{$loser[$g]}) {
		mark($winner[$g], $actual[$g], $x, $ymark+0.1, $x2, $y+0.03);
	}
}

sub finalfour {
	print "% ---------------\n";
	print "% FINAL FOUR\n";
	print "% Round 5\n";

	# lines under final-four team names
	my ($x, $y, $x2) = get_line_coords(1, 4, 1);
	make_line($x-$adjx, $y-$adjy, $x2-$adjx);
	($x, $y, $x2) = get_line_coords(2, 4, 1);
	make_line($x-$adjx, $y-$adjy, $x2-$adjx);
	($x, $y, $x2) = get_line_coords(3, 4, 1);
	make_line($x2-$adjx, $y-$adjy, $x-$adjx);
	($x, $y, $x2) = get_line_coords(4, 4, 1);
	make_line($x2-$adjx, $y-$adjy, $x-$adjx);

	# lines under champtionship-game team names
	($x, $y, $x2) = (0.5+5*$lwidth, 5, 0.5+6*$lwidth);
	ps_path(0, $x-$adjx, $y-$adjy, $x2-$adjx, $y-$adjy);
	($x, $y, $x2) = (10.5-5*$lwidth, 3.5, 10.5-6*$lwidth);
	ps_path(0, $x-$adjx, $y-$adjy, $x2-$adjx, $y-$adjy);

	# box around the big winner
	ps_path(1,
		5-$adjx, 4.2-$adjy,
		5+$lwidth-$adjx, 4.2-$adjy,
		5+$lwidth-$adjx, 4.4-$adjy,
		5-$adjx, 4.4-$adjy);

	print_game(3, 0.5 + 5*$lwidth, 5, 0.5 + 6*$lwidth);
	print_game(2, 10.5 - $lwidth - 5*$lwidth, 3.5, 10.5 - 5*$lwidth);
	print "% Round 6\n";
	print_game(1, 5, 4.2, 5 + $lwidth, 4.3);
}

sub make_line {
	if (defined $savex) {
		ps_path(0, $savex, $savey, $savex2, $savey, $savex2, $_[1], $savex, $_[1]);
		undef $savex;
	}
	else {
		($savex, $savey, $savex2) = @_[0..2];
	}
}

sub get_line_coords {
	my ($b, $r, $i) = @_[0..2];
	my $top = 8 - 4*(1-($b%2));
	my $left = ($b <= 2) ? 0.5 : (10.5-$lwidth);
	my $rev = ($b <= 2) ? 1 : -1;
	my $x = $left + $rev*$r*$lwidth;
	my $x2 = $x + $lwidth;
	my $y = $top - ((1<<$r)*($i-1+0.5)-0.5)*$lheight;

	($x, $y, $x2);
}

sub make_check {
	my ($x, $y) = @_[0..1];
	ps_path(0, $x-$marksize, $y+$marksize/2, $x-$marksize/2, $y, $x, $y+$marksize);
}

sub make_x {
	my ($x, $y) = @_[0..1];
	ps_path(0, $x-$marksize, $y+$marksize, $x, $y);
	ps_path(0, $x-$marksize, $y, $x, $y+$marksize);
}

sub mark {
	my ($winner, $actual, $x, $y, $x2, $y2) = @_[0..5];
	print "% mark: $winner $actual $x $y\n";
	if (defined $actual || $out{$winner}) {
		if ($winner == $actual) {
			make_check(($x+$x2)/2, $y);
		}
		else {
			ps_path(0, $x, $y2, $x2-0.1, $y2);
			if (defined $actual) {
				ps_text("(".int($actual).") $team{$actual}", $x, $y);
			}
			#make_x(($x+$x2)/2, $y);
		}
	}
}
