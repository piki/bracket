#!/bin/bash -e

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
this_year=$(date +"%Y")
tourneys="m w n c"
for year in `seq ${this_year} -1 1982`; do
	empty=true
	for t in $tourneys; do
		if test -d "${year}${t}"; then
			empty=false
		fi
	done

	if $empty; then continue; fi
	echo "<tr>"
	for t in $tourneys; do
		if test -d "${year}${t}"; then
			echo "  <td><a href=\"standings.cgi?t=${year}${t}\">$year</a></td>"
		else
			echo "  <td></td>"
		fi
	done
	echo "</tr>"
done
echo "</table></body></html>"
