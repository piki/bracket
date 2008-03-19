#!/usr/local/bin/perl

require 'bracket.pl';
my $tourney = $ARGV[0] || "2008m";
setup("$tourney/teams");

use CGI qw/:standard/;

$q = new CGI;

print "Content-type: text/html\n\n";
print "<link rel=\"stylesheet\" type=\"text/css\" href=\"bracket.css\">\n";

for ($i=63; $i>=32; $i--) {
  my $win = $q->param("g$i");
  my $lose = 17+$win-2*int($win);
  $upset[$i] = $win > 9;
  if ($upset[$i]) {
    print "Upset in game $i: $win ($team{$win}) over $lose ($team{$lose})<br>\n";
  }
}
for ($i=31; $i>=1; $i--) {
  my $a = 2*$i+1;
  my $b = 2*$i;
  my $ta = $q->param("g$a");
  my $tb = $q->param("g$b");
  my $win = $q->param("g$i");
  my $lose;
  if ($ta == $win) {
    $upset[$i] = $ta > $tb;
    $lose = $tb;
  }
  else {
    $upset[$i] = $tb > $ta;
    $lose = $ta;
  }
  if ($upset[$i]) {
    print "Upset in game $i: $win ($team{$win}) over $lose ($team{$lose})<br>\n";
  }
}
foreach ($i=63; $i>=1; $i--) { print $upset[$i]+0; }
print "\n";
foreach (0..7) { $output[$_] = 0; }
for ($i=63; $i>=1; $i--) {
  if ($upset[$i]) {
    $output[int((63-$i)/8)] |= (1<<((63-$i)%8));
  }
}
print "<br>\n";

$code = join '.', @output;
print qq(<hr>Send this string to <a href="mailto:reynolds\@cs.duke.edu?subject=bracket&body=$code">Patrick</a>: <b>);
print "$code</b>\n";
print "<br>\n";

$|=1;
print "<hr>\n";
system("./html-new.pl $tourney $code $name");
