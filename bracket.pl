$unknown = "=======";
1;

sub find_winners {
	my @input = split/\./,$_[0];
	my @upset;
	my @winner;

	for ($i=63; $i>=1; $i--) {
		$upset[$i] = ($input[(63-$i)/8] >> ((63-$i)%8)) & 1;
	}

	for ($i=63; $i>=32; $i--) {
		my ($a,$b) = split/,/,$game{$i};
		if ($a > $b) { $winner[$i] = $upset[$i] ? $a : $b; }
		else { $winner[$i] = $upset[$i] ? $b : $a; }
	}
	for ($i=31; $i>=1; $i--) {
		my $a = $winner[$i*2];
		my $b = $winner[$i*2+1];
		if ($a > $b) { $winner[$i] = $upset[$i] ? $a : $b; }
		else { $winner[$i] = $upset[$i] ? $b : $a; }
	}

	@winner;
}

sub read_schedule {
	my @ret;
	open(SCHED, "<$_[0]") || return undef;
	while (<SCHED>) {
		chomp;
		if (/^(\d{1,2})\s+(.*)/) {
			$ret[$1] = $2;
		}
	}
	close(SCHED);
	@ret;
}

sub read_winners {
	my @actual;
	my @score_winner;
	my @score_loser;
	my @overtimes;
	open(ACTUAL, "<$_[0]") || die "$_[0]: $!";
	while (<ACTUAL>) {
		chomp;
		# <gameno> <winner> <win-score>-<lose-score> <#>OT
		if (/^(\d+)\s+(\d+\.\d)\s+(\d+)-(\d+)\s+(\d*)OT$/) {
			$actual[$1] = $2;
			$score_winner[$1] = $3;
			$score_loser[$1] = $4;
			$overtimes[$1] = $5 || 1;
		}
		# <gameno> <winner> <win-score>-<lose-score>
		elsif (/^(\d+)\s+(\d+\.\d)\s+(\d+)-(\d+)$/) {
			$actual[$1] = $2;
			$score_winner[$1] = $3;
			$score_loser[$1] = $4;
		}
		# <gameno> <winner>
		elsif (/^(\d+)\s+(\d+\.\d)$/) {
			$actual[$1] = $2;
		}
	}

	(\@actual, \@score_winner, \@score_loser, \@overtimes);
}

sub get_losers {
	my @actual = @_;
	my @losers;
	for (my $i=63; $i>=32; $i--) {
		next if !$actual[$i];
		my ($ta, $tb) = split/,/, $game{$i};
		$losers[$i] = ($ta == $actual[$i]) ? $tb : $ta;
	}
	for (my $i=31; $i>=1; $i--) {
		next if !$actual[$i];
		my ($ta, $tb) = ($actual[$i*2], $actual[$i*2+1]);
		$losers[$i] = ($ta == $actual[$i]) ? $tb : $ta;
	}
	@losers;
}

sub get_perfect_code {
	my $tourney = $q->param('t') || "2017m";
	my @ret = read_winners("$tourney/actual");
	my @actual = @{$ret[0]};
	my @code;
	my @upset;
	my $i;
	for ($i=63; $i>=32; $i--) {
		my ($a, $b) = split/,/, $game{$i};
		if ($a > $b && $actual[$i] == $a) { $upset[$i] = 1; }
		if ($b > $a && $actual[$i] == $b) { $upset[$i] = 1; }
	}
	for ($i=31; $i>=1; $i--) {
		my $a = $actual[$i*2+1];
		my $b = $actual[$i*2];
		if ($a > $b && $actual[$i] == $a) { $upset[$i] = 1; }
		if ($b > $a && $actual[$i] == $b) { $upset[$i] = 1; }
	}

	foreach $i (0..7) { $code[$i] = 0; }
	foreach $i (1..63) {
		if ($upset[$i]) {
			$code[int((63-$i)/8)] |= (1<<((63-$i)%8));
		}
	}

	@code;
}

sub teams_out {
	my @actual = @_;
	my %out;
	for ($i=63; $i>=1; $i--) {
		my ($a, $b);
		if ($i >= 32) {
			($a, $b) = split/,/,$game{$i};
		}
		else {
			($a, $b) = ($actual[$i*2], $actual[$i*2+1]);
		}
		if (defined $actual[$i]) {
			my $loser = $actual[$i] == $a ? $b : $a;
#			print "ACTUAL $i: $actual[$i] $team{$actual[$i]} beat $loser $team{$loser}\n";
			$out{$loser} = 6-int(log2($i));
		}
	}
	%out;
}

sub make_title {
	if ($_[0] =~ /^(\d{4})([mnw])$/) {
		my %idmap = (
			"m"=>"Men's NCAA Tournament",
			"n"=>"Men's NIT",
			"w"=>"Women's NCAA Tournament"
		);
		return "$1 $idmap{$2}";
	}
	else {
		return undef;
	}
}

sub who_played {
	my $g = shift;
	my ($a, $b);
	if ($g >= 32) {
		($a, $b) = split/,/, $game{$g};
	}
	else {
		($a, $b) = ($_[$g*2], $_[$g*2+1]);
	}
	if ($_[$g] == $a) { return ($a, $b); } else { return ($b, $a); }
}

# returns true iff "code1" cannot catch up to "code2"
# I believe that setting all undecided games in favor of "code1" and
# comparing scores is sufficient to perform this check.
sub eliminated_check {
	my @predicted1 = @{$_[0]};
	my @predicted2 = @{$_[1]};
	my @actual = @{$_[2]};
	my %out = %{$_[3]};
	my ($score1, $score2);

	$score = 0;
	for ($i=63; $i>=1; $i--) {
		my $r = 6 - int(log2($i));
		if (defined $actual[$i]) {
			if ($actual[$i] == $predicted1[$i]) {
				$score1 += $score_factor[$r-1];
			}
			if ($actual[$i] == $predicted2[$i]) {
				$score2 += $score_factor[$r-1];
			}
		}
		elsif (!$out{$predicted1[$i]}) {
			$score1 += $score_factor[$r-1];
			if ($predicted1[$i] == $predicted2[$i]) {
				$score2 += $score_factor[$r-1];
			}
		}
	}
	return wantarray ? ($score1, $score2) : ($score1 < $score2);
}

sub log2 {
        log($_[0])/log(2);
}

sub setup {
	my $config = $_[0];
	open(CONFIG, "<$config") || die "$config: $!";
	while (<CONFIG>) {
		chomp;
		if (/^team\s+(\d+\.\d)\s+(.*)$/) {
			$team{$1} = $2;
		}
		elsif (/^region\s+(\d+)\s+(.+)$/) {
			$bracket[$1] = $2;
		}
	}

	%game = (
		63 => "1.1,16.1", 62 => "8.1,9.1", 61 => "5.1,12.1", 60 => "4.1,13.1",
		59 => "6.1,11.1", 58 => "3.1,14.1", 57 => "7.1,10.1", 56 => "2.1,15.1",

		55 => "1.2,16.2", 54 => "8.2,9.2", 53 => "5.2,12.2", 52 => "4.2,13.2",
		51 => "6.2,11.2", 50 => "3.2,14.2", 49 => "7.2,10.2", 48 => "2.2,15.2",

		47 => "1.3,16.3", 46 => "8.3,9.3", 45 => "5.3,12.3", 44 => "4.3,13.3",
		43 => "6.3,11.3", 42 => "3.3,14.3", 41 => "7.3,10.3", 40 => "2.3,15.3",

		39 => "1.4,16.4", 38 => "8.4,9.4", 37 => "5.4,12.4", 36 => "4.4,13.4",
		35 => "6.4,11.4", 34 => "3.4,14.4", 33 => "7.4,10.4", 32 => "2.4,15.4"
	);

	@round_name = ( "", "first round", "second round", "Sweet 16", "Elite 8", "Final Four", "championship game" );

	@score_factor = ( 1, 2, 4, 6, 8, 10 );
}

sub bitcount {
	my @b = split/\./, $_[0];
	my $res = 0;
	foreach (@b) {
		while ($_) {
			if ($_ & 1) { $res++; }
			$_ >>= 1;
		}
	}
	$res;
}
