#!/usr/bin/perl
#  Displays a month's worth of days.
use RCBowen;
use HyperCal;
use Time::JulianDay;
use Time::DaysInMonth;

my %FORM = ();
FormParse(\%FORM);

PrintHeader();
my ($template, $details) = Details(\%FORM);

PrintTemplate($templates, $template, $details);

#######################

sub Details	{
	my ($form) = @_;
	my $template = "month_view";
	my ($today, $day, $event, %Event, @thismonth_datebook,
		$i, $todays_events, $line, $emon, $eday, $tday);
	my %details = %$form;

	if ($form->{month} && $form->{year})	{
		#  Don't do anything.  Use the dates given
	}  else  {  #  Default to this month
		$today = local_julian_day(time);
		($form->{year}, $form->{month}, $day) = inverse_julian_day($today);
	}

	$begin = julian_day($form->{year}, $form->{month}, 1);
	$end = julian_day($form->{year}, $form->{month},
						 days_in($form->{year}, $form->{month}));

	month_txt("$form->{month}");
	body_tag($form->{month}, \%details);
	$details{hypercal} = $base_url . $hypercal;

	#  Read in database.
	open (DATES, "$datebook");
	@dates=<DATES>;
	close DATES;

	for (@dates)	{
		my $event = EventSplit($_);
		%Event = %$event;

		if ($Event{annual} || (($Event{day} >= $begin) && 
					($Event{day} <= $end)) )	{
			push @thismonth_datebook, $_;
		} #  End if
	}  #  End for
	@dates = @thismonth_datebook;

	#  Now, loop through the month  ...
	for ($i=$begin; $i<=$end; $i++)	{
		$todays_events = "";
		(undef, undef, $tday) = inverse_julian_day($i);
		for $line (@dates)	{
			$event = EventSplit($line);
			%Event = %$event;

			#  How about annual events?
			if ($Event{annual}) 	{
				(undef, $emon, $eday) = inverse_julian_day($Event{day});
				if ($eday == $tday && $emon == $form->{month})	{
					$todays_events .= qq~
					<dd>$Event{description}
					~;
				}
			}  else	{  # The rest of the events
				if ($Event{day} == $i) {
					$todays_events .= qq~
					<dd>$Event{description}
					~;
				}  #  End if
			} #  End else 
		}  #  End for dates
		if ($todays_events)	{
			$details{events} .= qq~
			<dt><b><a href="$disp_day?day=$i">$tday</a></b>
			$todays_events
			<hr width=10% align=left>
			~;
		}  #  End if
	}  #  End for $i

	#  Other stuff ...

	$details{add_event} = $add_date . "?month=" . $form->{month}
				. "&year=" . $form->{year};

	return ($template, \%details);
} #  End sub details