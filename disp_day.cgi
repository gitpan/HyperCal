#!/usr/bin/perl
#  Display Day.  Reads in database and prints appointments for the
#  selected day.  Allows option of adding new appointment.
#
use RCBowen;
use HyperCal;
use Time::JulianDay;
use Time::CTime;
use strict 'vars';

my %FORM = ();
FormParse(\%FORM);
PrintHeader();

my $details = details(\%FORM);
PrintTemplate($templates,'display',$details);

##############################################

sub details	{
	my ($form) = @_;
	my %details = %$form;
	my ($begin, $end);
	my $today = local_julian_day(time);
	if (! $form->{day}) {
		$form->{day} = $today;
	}

	my  ($year, $month, $day) = inverse_julian_day($form->{day});
	#  page color, link color, etc
	&body_tag($month, \%details);

	#  Read in database.
	open (DATES, "$datebook");
	my @dates=<DATES>;
	close DATES;
	my ($event, $events, %Event,@todays_events,
		$date, $tmp_day, $tmp_month);

	for $date (@dates)	{
		$event = EventSplit($date);
		if ($event->{annual})	{
			(undef, $tmp_month, $tmp_day) 
						= inverse_julian_day($event->{day});
			if ($tmp_month == $month && $tmp_day == $day)	{
				push (@todays_events, $date);
			}  #  End if
		}  else  {	
			if ($form->{day} == $event->{day})	{
				push (@todays_events, $date);
			}  #  End if
		}  #  End else
	} #  End for dates

	my $howmany = @todays_events;
	if ($howmany > 0)	{
		for $events (sort @todays_events)	{
			$event = EventSplit($events);
			%Event = %$event;

			$details{appointments} .= qq~
			<tr>
			<td>$Event{description}  <small>[
			 <a href="$edit_date?id=$Event{id}&this_year=$year">Edit event</a> ]
			 [ <a href="$del_date?id=$Event{id}&this_year=$year">Delete event</a> ]
			 </small>
			</td>
			<td>
			~;

			if ($Event{begin} eq "0000" && $Event{end} eq "0000")	{
				$details{appointments} .= "-";
			} elsif ($Event{end} eq "0000")	{
				$begin = AmPm($Event{begin});
				$details{appointments} .= "$begin";
			}  else  {
				$begin = AmPm($Event{begin});
				$end = AmPm($Event{end});
				$details{appointments} .= "$begin - $end";
			}
			$details{appointments} .= "</td></tr>";
			
		}  #  End for
	}  else  {  #  There were no events for this day
		$details{appointments} = 
		  "<tr><th colspan=2 align=center>** No Events **<br>";
	}

	$details{add} = "$base_url$add_date?day=$form->{day}";
	$details{calendar} = "$base_url$hypercal?month=$month&year=$year";
	$details{day_txt} = strftime("%A, %B %o, %Y",
			localtime(jd_secondslocal($form->{day})));

	return \%details;			
}  #  End sub details