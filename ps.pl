# Postscript utility routines
#
# ps_begin(pages, fonts, title, orientation):
#       begin outputting a Postscript document -- output headers
#       and initialize state
#   pages: the number of pages in the document [1]
#   fonts: a comma-separated list of fonts used in the document [Times-Roman]
#   title: the document's title [Untitled]
#   orientation: Portrait or Landscape [unset = Portrait]
#
# ps_setfont(font, size): set the current font
#   font: the font to use [Times-Roman]
#   size: the size to use, in points [12]
#
# ps_text(text, x, y, justification): print out a line of text
#   text: what to print
#   x, y: dimensions, in inches from the lower-left corner of the page,
#         of the lower-left corner of the text
#   justification: 0=>left (default), 1=>center, 2=>right
#
# ps_path(x, y, x2, y2, ...): draw a path connecting all points given
#
# ps_showpage(last): end the current page and optionally begin a new one
#   last: 1 if this is the last page, 0 if not [0]
#
# ps_end: end outputting Postscript -- flush page and output trailer
#
# EXAMPLE
#   ps_begin();
#   ps_setfont("Courier", 24);
#   ps_text("Foo", 2.0, 2.5);
#   ps_end();

1;

sub ps_begin {
	my ($pages, $fonts, $title, $orientation) = @_;

	$pages ||= 1;
	$fonts ||= "Times-Roman";
	$title ||= "Untitled";

	print "%!PS-Adobe-1.0\n";
	print "%%DocumentFonts: $fonts\n";
	print "%%Title: $title\n";
	print "%%Creator: $0\n";
	print "%%CreationDate: " . localtime() . "\n";
	print "%%Orientation: $orientation\n" if $orientation;
	print "%%DocumentPaperSizes: Letter\n";
	print "%%Pages: $pages\n";
	print "%%EndComments\n\n";
	print "%%EndProlog\n\n";
	print "%%Page: 1 1\n";
	print "%%PageFonts: $fonts\n\n";
	
	$ps_need_to_show_page = 1;
	$ps_current_font = "";
	$ps_current_page = 1;
	$ps_fonts = $fonts;
}

sub ps_setfont {
	my ($font, $size) = @_;
	$font ||= $ps_fonts;
	$font =~ s/,.*//;
	$size ||= 12;
	print "/$font findfont $size scalefont setfont\n";
	$ps_current_font = $font;
}

sub ps_text {
	my ($text, $x, $y, $justify) = @_;
	if (!$text) { return; }
	$x ||= 1;
	$y ||= 1;
	$x *= 72;
	$y *= 72;
	if (!$ps_current_font) { ps_setfont(); }
	if ($justify == 1) {
		print "$x ($text) stringwidth pop 2 div sub";
	}
	elsif ($justify == 2) {
		print "$x ($text) stringwidth pop sub";
	}
	else {
		print $x;
	}
	print " $y moveto\n($text) show\n";
}

sub ps_path {
	my $close = shift;
	my $a = (shift) * 72;
	my $b = (shift) * 72;
	print "newpath $a $b moveto";
	while ($#_ >= 1) {
		$a = (shift) * 72;
		$b = (shift) * 72;
		print " $a $b lineto";
	}
	if ($close) { print " closepath"; }
	print " stroke\n";
}

sub ps_showpage {
	print "showpage\n\n";
	$ps_need_to_show_page = 0;
	++$ps_current_page;
	if (!$_[0]) {
	  print "%%Page: $ps_current_page $ps_current_page\n";
	  print "%%PageFonts: $fonts\n\n";
	}
}

sub ps_end {
	if ($ps_need_to_show_page) {
		ps_showpage(1);
	}
	print "%%Trailer\n";
}
