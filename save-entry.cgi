#!/usr/bin/perl

require 'bracket.pl';

use CGI qw/:standard/;
$q = new CGI;

my $tourney = $q->param('t') || "2013m";
my $code = $q->param('c') || "0.0.0.0.0.0.0.0";
my $name = $q->param('name') || 0;

if($name){
    write_bracket($tourney, $name, $code);
    print "Location: standings.cgi\n\n";
}

print qq#
<html>
<head>

<script type="text/javascript">

function goodName(name) {
    if (name.length == 0) {
        return false;
    }
    var reg = new RegExp('^[\_\\\\w\\\\s]+\$');
    return reg.test(name);
}

function getName() {
    var name;
    var result;
    do {
        name = prompt("Enter your name (letters and numbers only)", "");
        if (name == null) {
            alert("Bracket not submitted");
            window.location = "make-entry.cgi?t=$tourney&c=$code";
            return;
        }
        result = goodName(name);
    } while (!result);
    
    window.location = "save-entry.cgi?t=$tourney&c=$code&name=" + name;
}

function hasPassed(){
    alert("Deadline has passed");
    window.location = "standings.cgi";
}

</script>
    
</head>
#;

if(!before_deadline($tourney)){
    print qq# <body onload="hasPassed()">#;
} else {
    print qq# <body onload="getName()">#;
}

print qq# </body></html>#;
