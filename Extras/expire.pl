#!/usr/bin/perl
########################################################
##  Expire old events and announcements.  This script ##
##  should be run periodically, say, with cron.       ##
##  This is not a CGI program.  It is to be run       ##
##  from the console                                  ##
########################################################
use lib '..';
use HyperCal;
use Time::JulianDay;
my (@new_events, @new_announce, $pointer, %Event, %Announce, $day,
    $today, $old_day, @events,
     );

$today = local_julian_day(time);
$old_day = $today - $Config->{old};

#  First, get rid of old events
open (EVENTS, "$datebook");
@events = <EVENTS>;
close EVENTS;
chomp @events;

for (@events)	{
	$pointer = EventSplit($_);
	%Event = %$pointer;
	push @new_events, $_ 
			unless ($Event{day} < $old_day && ! $Event{annual});
}

open (EVENTS, ">$datebook");
for (@new_events)	{
	print EVENTS "$_\n";
}
close EVENTS;

#  Then, get rid of old announcements
open (ANNOUNCE, "$announce");
my @announce = <ANNOUNCE>;
close ANNOUNCE;
chomp @announce;

for (@announce)	{
	$pointer = AnnounceSplit($_);
	%Announce = %$pointer;
	$day = ($Announce{year} eq "xxxx") ? 0 : 
		julian_day($Announce{year}, $Announce{month}, 1);
	push @new_announce, $_ 
			unless ($day > 0 && $day < $old_day);
}

open (ANNOUNCE, ">$announce");
for (@new_announce)	{
	print ANNOUNCE "$_\n";
}
close ANNOUNCE;
