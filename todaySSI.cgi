#!/usr/bin/perl
#  List today's events
#	Suitable for SSI
use RCBowen;
use HyperCal;
use Time::JulianDay;

$jd = local_julian_day(time);

open (DATES, "$datebook");
@dates = <DATES>;
close DATES;

PrintHeader();

@dates = grep /^$jd$delimiter/, @dates;
for (@dates)	{
	$pointer = EventSplit($_);
	%Event = %$pointer;
	print "<li>$Event{description}<br>\n";
}