#!/usr/bin/perl
#  Convert 3 Beta 1 files to 3 Beta 2 files
#  Not sure that this actually works.
use Time::JulianDay;

open (DATES, "datebook");
@dates = <DATES>;
close DATES;

chomp @dates;

for (@dates)	{
	($begintime, $endtime, $therest) = m/(.*?)~~(.*?)~~(.*)/;
	$day = local_julian_day($begintime);
	(undef, $min, $hour, undef, undef, undef, undef, undef, undef) =
		localtime($begintime);
	$begin = sprintf "%.2d",$hour . sprintf "%.2d",$min;
	(undef, $min, $hour, undef, undef, undef, undef, undef, undef) =
		localtime($endtime);
	$end = sprintf "%.2d",$hour . sprintf "%.2d",$min;
	$date = join "~~", $day, $begin, $end, $therest;
	push @newdates, $date;
}

open (DATES, ">newdates");
for (@newdates) {
	print DATES "$_\n";
}
close DATES;