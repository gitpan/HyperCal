#!/usr/bin/perl
##############################################################
#   File:  del_date.pl                                        
#   Author:  Rich Bowen - rbowen@rcbowen.com                  
#   Purpose:  Allows you to delete an event from a particular 
#   	day on the calendar                                   
#   Date:  Dec 27, 1997                                       
##############################################################
use RCBowen;
use HyperCal;
use Time::JulianDay;
# use strict 'vars';

my %FORM = ();
FormParse(\%FORM);

PrintHeader();

if ($FORM{routine} eq "del")	{
	($template, $details) = DeleteEvent(\%FORM);
	} else {
	($template, $details) = DisplayForm(\%FORM);
}

PrintTemplate($templates, $template, $details);

########

sub DisplayForm	{
	#  Really, all I want to do here is the "are you sure" thing.
	my ($form) = @_;
	my $template = 'delete_confirm';
	my %details = %$form;

	#  Read in the data file
	open (EVENTS, "$datebook");
	my @events = <EVENTS>;
	close EVENTS;
	chomp @events;

	@events = grep /$delimiter$form->{id}$/, @events;

	#  Is someone trying to hack us?
	my $event;
	if ($event = pop @events)	{
		my $pointer = EventSplit($event);
		my %Event = %$pointer;
		for $key (keys %Event)	{
			$details{$key} = $Event{$key};
		}  #  End for

		$details{del_date} = "$base_url$del_date";
		$details{disp_day} = "$base_url$disp_day";

		#  What we really want $day to day is actually
		#  the day, in this_year;
		my ($year, $month, $day) = inverse_julian_day($details{day});
		$details{day} = julian_day($details{this_year},$month,$day);

	}  else  {
		$template = 'error';
		$details{error} = "You have entered an invalid event ID";
	}

	return ($template, \%details);
}  #  End sub details


sub DeleteEvent	{
	#  Delete the event from the event file
	my ($form) = @_;
	my ($template, %details);

	open (EVENTS, "$datebook");
	@events = <EVENTS>;
	close EVENTS;
	chomp(@events);

	@events = grep !/($delimiter)($form->{ID})$/, @events;

	open (EVENTS, ">$datebook");
	for (@events)	{
		print EVENTS "$_\n";
		}
	close EVENTS;

	#  Send them on their merry way
	$template = 'redirect';
	$details{URL} = "$base_url$disp_day?day=$form->{day}"; 

	return ($template, \%details);
}  #  End sub
