#!/bin/sh

if [ -n "$PATH_INFO" ]; then
	echo Location: http://piki.org/cgi-bin/bracket/index.cgi
	echo Content-type: text/html
	echo
	echo Foo
	exit
fi
echo Content-type: text/html
echo
echo "<html><head><title>NCAA Basketball Tournament Brackets</title>"
echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"/_bracket.css\">"
echo "</head>"
echo "<body><table border=1 rules=\"all\" cellpadding=3><tr bgcolor=\"#cccccc\"><th>Men</th><th>Women</th><th>Men's NIT</th><th>Men's CBI</th></tr>"
for year in `seq 2017 -1 1982`; do
	echo "<tr>"
	if test -d "${year}m"; then
		echo "  <td><a href=\"standings.cgi?t=${year}m\">$year</a></td>"
	else
		echo "  <td></td>"
	fi
	if test -d "${year}w"; then
		echo "  <td><a href=\"standings.cgi?t=${year}w\">$year</a></td>"
	else
		echo "  <td></td>"
	fi
	if test -d "${year}n"; then
		echo "  <td><a href=\"standings.cgi?t=${year}n\">$year</a></td>"
	else
		echo "  <td></td>"
	fi
	if test -d "${year}c"; then
		echo "  <td><a href=\"standings.cgi?t=${year}c\">$year</a></td>"
	else
		echo "  <td></td>"
	fi
	echo "</tr>"
done
echo "</table></body></html>"
