#!/usr/bin/perl
#  List today's events
#	Suitable for SSI
use HyperCal;
use Time::JulianDay;
my ($jd, @dates, $event,
	);

$jd = local_julian_day(time);

open (DATES, "$Config->{datebook}");
@dates = <DATES>;
close DATES;

PrintHeader();

@dates = grep /^$jd$Config->{delimiter}/, @dates;
for (@dates)	{
	$event = EventSplit($_);
	print "<li>$event->{description}<br>\n";
}