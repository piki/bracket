#!/usr/bin/perl

require 'bracket.pl';

use CGI qw/:standard/;
$q = new CGI;
print "Content-type: text/html\n\n";
print "<link rel=\"stylesheet\" type=\"text/css\" href=\"/_bracket.css\">\n";
$|=1;

my $tourney = $q->param('t') || "2012m";
my $code = $q->param('c') || "0.0.0.0.0.0.0.0";
$tourney =~ s/[^0-9mwn]+//g;

@colors = ( "#e8e8e8", "#d4d4d4", "#c0c0c0", "#acacac", "#b0b0b0", "#00005f" );

setup("$tourney/teams");
#$unknown = "<font color=\"red\">$unknown</font>";
@winner = find_winners($code);
@loser = get_losers(@winner);

@bracket = map { uc($_) } @bracket;

print qq#
<html>
<head><title>$title</title>
<style type="text/css">
\#dek    { POSITION:absolute; VISIBILITY:hidden; Z-INDEX:200; }
</style>
<script language="javascript">
var winner = new Array(0#, (join',',@winner), qq#);
var team = new Array();
var game = new Array();
#;
foreach (sort keys %team) { print "team[$_]=\"$team{$_}\";"; }
foreach (32..63) { print "game[$_]=\"$game{$_}\";"; }
print qq#
function pick(evt,number) {
	if (number < 32) {
		if (!winner[number*2] || !winner[number*2+1]) return;
		pick_popup(evt, number, winner[number*2+1], winner[number*2]);
	}
	else {
		var seeds = game[number].split(",");
		pick_popup(evt, number, seeds[0], seeds[1]);
	}
}

</script>
</head>
<body>

Welcome to the new bracket entry page!  If it doesn't work for you, send
<a href="mailto:dukepiki\@gmail.com">me</a> an email and use <a
href="old-make-entry.cgi">the old page</a> instead.
<br>
<div style="visibility: visible; display: none;" id="dek"></div>
<script language="javascript">
function getMouseCoordinates(e){
  var lx=0;
  var ly=0;
  if(!e){
    var e=window.event;
  }
  if(e.pageX||e.pageY){
    lx=e.pageX;
    ly=e.pageY;
  }else{
    if(e.clientX||e.clientY){
      lx=e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
      ly=e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
    }
  }
  return {x:lx,y:ly};
}
var Xoffset = -22;
var Yoffset = -38;
if (document.all) {  // IE
var Xoffset = -33;
var Yoffset = -35;
}
var skn;
skn = document.getElementById("dek").style;
skn.visibility = "visible";
skn.display = "none";

function pick_popup(evt,game,team1,team2){
  var pos = getMouseCoordinates(evt);
  var content='<div style="position:absolute; top:'+(pos.y+Yoffset)
    +'px; left:'+(pos.x+Xoffset)+'px">'
    +'<TABLE cellpadding=4 border=3 bgcolor="\#ffffff" rules="all">'
    +'<TD class="popup">'
		+'<a href="javascript:commit('+game+','+team1+')">('+Math.floor(team1)+') '+team[team1]+'</a><br>'
		+'<a href="javascript:commit('+game+','+team2+')">('+Math.floor(team2)+') '+team[team2]+'</a>'
    +'</TD></TABLE></div>';
  document.getElementById("dek").innerHTML=content;
  skn.display = '';
}
function kill() {
  skn.display = "none";
}
function commit(game, t) {
	kill();
	var old = winner[game] || -1;
	if (old == t) return;

	do {
		winner[game] = t;
		document.getElementById("g"+game).innerHTML = "("+Math.floor(t)+") "+team[t];
		game = Math.floor(game/2);
	} while (game >= 1 && winner[game] == old);

	update_code();
}
function update_code() {
	var code = new Array(0,0,0,0,0,0,0,0);
	for (g=63; g>=1; g--) {
		var byt = Math.floor((63-g) / 8);
		var bit = (63-g) % 8;
		var a,b;
		if (g < 32) {
			a = winner[g*2+1];
			b = winner[g*2];
		}
		else {
			var seeds = game[g].split(",");
			a = seeds[0];
			b = seeds[1];
		}
		if (winner[g] > a || winner[g] > b) {
			code[byt] |= 1<<bit;
			//alert("upset in game "+g+".  a="+a+" b="+b+" winner[g]="+winner[g]);
		}
	}
	var theCode = code.join(".");
	document.getElementById("code").innerHTML = theCode;
	document.getElementById("sendmail").href = "mailto:dukepiki\@gmail.com?subject=bracket%20code&body=" + theCode;
	document.getElementById("saveit").href = "make-entry.cgi?t=$tourney&c="+theCode;
}

</script>

<h1>$title</h1>
#;

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

		if ($team{$seed[0]} && $team{$seed[1]}) {
			print "<td class=\"brak\" width=\"10%\" bgcolor=\"$colors[0]\">";
			print "<b>(".int($seed[0]).") $team{$seed[0]}</b>";
		}
		else {
			print "<td class=\"brak\" width=\"10%\">";
		}

		print "<br>";
		if ($team{$seed[1]} && $team{$seed[0]}) {
			print "<b>(".int($seed[1]).") $team{$seed[1]}</b>";
		}
		print "</td>\n";
	}
	else {
		my $oldrow = int(1 + ($row-1) / (1<<($round-2)));
		my $g = (1<<(8-$round)) - $oldrow - (1<<(5-$round))*($bracket-1);
		print "<td class=\"brak\" width=\"10%\" bgcolor=\"$colors[$round-1]\" rowspan=" . (1<<($round-1)) . ">";
		print_team($g);
		print "<br>\n";
		print_team($g-1);
		print "</td>\n";
	}
}

sub finalfour {
	my @ff;
	my $champ;
	foreach my $g (1..3) {
		$ff[$g] = "<a id=\"g".($g*2+1)."\" href=\"javascript:void(0)\" "
			. "onclick=\"pick(event,".($g*2+1).")\">(".int($winner[$g*2+1]).") $team{$winner[$g*2+1]}</a><br>";
		$ff[$g] .= "<a id=\"g".($g*2)."\" href=\"javascript:void(0)\" "
			. "onclick=\"pick(event,".($g*2).")\">(".int($winner[$g*2]).") $team{$winner[$g*2]}</a>";
	}
	$champ = "(".int($winner[1]).") $team{$winner[1]}";
	print qq(
<td width="20%" rowspan=19 valign="middle">
  <table width="100%">
  <tr>
    <td colspan=3 align="center" bgcolor="#000000"><font color="#ffffff">FINAL FOUR</font></td>
  </tr><tr>
    <td class="brak">$ff[3]</td>
    <td align="right">
      <table cellpadding=0 cellspacing=0><tr><td class="brak">$ff[2]</td></tr></table>
    </td>
  </tr>
  <tr><td>&nbsp;</td></tr>
  <tr>
    <td colspan=3 align="center" bgcolor="#000000"><font color="#ffffff">CHAMPIONSHIP</font></td>
  </tr><tr>
    <td colspan=3 align="center">$ff[1]</td>
  </tr><tr><td height=25></td></tr><tr>
    <td colspan=3 align="center" bgcolor="#000000"><font color="#ffffff">NATIONAL CHAMPIONS</font></td>
  </tr><tr>
    <td colspan=3 align="center"><a id=\"g1\" href="javascript:void(0)\" onclick=\"pick(event,1)">$champ</a></td>
  </tr>
  </table>
<br><br><br><br>
<center>
Your bracket code:<br>
<b><div id="code">$code</div></b>
<p>
Mail it to <a id="sendmail" href="mailto:dukepiki\@gmail.com?subject=bracket%20code&body=$code">Patrick</a>
<p>
<a id="saveit" href="make-entry.cgi?t=$tourney&c=$code">Save</a> this page for later.
</center>
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
	print "<a id=\"g$g\" href=\"javascript:void(0)\" onclick=\"pick(event,$g)\">";
	print "(".int($winner[$g]).") $team{$winner[$g]}</a>";
}
