#!/usr/bin/perl
use HyperCal;
use strict 'vars';
use Time::JulianDay;
use Time::DaysInMonth;
use Time::CTime;

my ($form, $template, $details, @Actions, $routine);

$form = FormParse;
PrintHeader();
@Actions = qw(Main Day Month Event
             );
$routine = Switch($form->{action},\@Actions, 'Main');
($template, $details) = &{$routine}($form);
PrintTemplate ($Config->{templates}, $template, $details);

###############################
# Subroutines ...

sub Main  {
	my ($form) = @_;  
	my %FORM = %$form;
	my ($this_month, $this_year, $line, $count,
		@thismonth_datebook,$event,
		$date_place, $day, $_mon, $_day,
		%Day, %Events, $x,
		%details, $template,
		$today, $today_year, $today_month, $today_mday,
		@datebook,
		);
	%details = %$form;
	$template = "hypercal";

	# Determine what "today" is.
	$today = local_julian_day(time);
	($today_year, $today_month, $today_mday) = inverse_julian_day($today);

	if (! $details{month}) {	#  Defaults to current date if none specified.
		$this_month = $today_month;
		$this_year = $today_year;
	} else	{
		#  Get the month, year, from the command line
		$this_month = $form->{month};
		$this_year = $form->{year};
	}  #  End if...else
	my $first_day = julian_day($this_year, $this_month, 1);
	my $last_day = $first_day + days_in($this_year, $this_month);
	my $first_dow = day_of_week($first_day);

	$details{year} = $this_year;
	$details{month_text} = month_txt($this_month);

	#  page color, link color, etc
	&body_tag($this_month, \%details);

	#	Read datebook into memory
	#
	open (DATES, $Config->{datebook}) 
		or die "Unable to open $Config->{datebook}: $!";
	@datebook=<DATES> ;
	close DATES;

	#    pull out just the events for this month, hmmmm?
	for (@datebook)	{
		$event = EventSplit($_);

		if ($event->{annual})	{ # "fix" annual events
			(undef, $_mon, $_day) = inverse_julian_day($event->{day});
			$event->{day} = julian_day($this_year, $_mon, $_day);
		}
		if (($event->{day} >= $first_day) && 
				($event->{day} <= $last_day)) {
			push @{$Day{$event->{day}}}, $event->{id};
			$Events{$event->{id}} = $event;
		}
	}  #  End for
	@datebook = ();

	$details{calendar} .= "<tr><td colspan=$first_dow></td>\n" 
				unless ($first_dow == 0);

	my $week_day = $first_dow;

	#  Loop through all the days in the month

	my $end_of_month = days_in($this_year, $this_month);
	for ($date_place = 1; $date_place <= $end_of_month; $date_place++)	{

		#  Print that day's stuff
		$day = $first_day + $date_place - 1;

		#  Is is a sunday?  Begin a new row
		if ($week_day == 0) {
			$details{calendar} .= "<tr> "
			}  #  End if sunday

		$details{calendar} .= "<td valign=top align=left";

		#  Highlight today
		if ($day == $today and $Config->{highlight} ne "none")	{
			$details{calendar} .= " bgcolor=\"$Config->{highlight}\""
		} else	{
			if ($Config->{td_color} ne "" and $Config->{td_color} ne "none")	{
				$details{calendar} .= " bgcolor=\"$Config->{td_color}\""
			}
		}  #  End if..else
		$details{calendar} .= ">\n";
		$details{calendar} .= "<a href=\"$Config->{base_url}index.$Config->{ext}?action=Day&day=$day\">$date_place</a>";

		# What happens this day?
		if ( exists ($Day{$day}) )	{ # There are events today
			if ($Config->{DisplayEvents})	{
				foreach $x ( @{$Day{$day}} )	{
					$event = $Events{$x};
					$details{calendar} .= "<br><small>$event->{description}</small>";
				}  #  End for
			}  #  End if
			if ( $Config->{DisplayNumber} && ( @{$Day{$day}} ) )	{
				$count = @{$Day{$day}};
				$details{calendar} .= "<br><small>($count)</small>";
			}  #  End if
		} # End if defined
		$details{calendar} .= "</td>\n";
		
		#  Is is a Saturday?  That's the end of the row.
		if ($week_day == 6) {
			$details{calendar} .= "</tr>\n"
			}  #  End if saturday

		$week_day ++;
		if ($week_day == 7) {$week_day = 0};  #  Start the week over
	}  # End for date_place - repeated for each day in the month


	# Announcements for the month
	open (ANNO, "$Config->{announce}");
	my @announce=<ANNO>;
	close ANNO;
	my $any_announce = "no";
	my ($announces, %Announce,$pointer);

	for $announces (@announce)	{
		$pointer = AnnounceSplit($announces);
		%Announce = %$pointer;
		if ($Announce{month} eq $this_month && 
			($Announce{year} eq $this_year || $Announce{year} eq "xxxx") )   {
			if ($any_announce eq "no")  {
				$details{announcements} = "<tr><td align=center colspan=7>"
				}
			$details{announcements} .= "<center><b>$Announce{announcement}</b></center>";
	   		$any_announce="yes";
	   		}  #  end if
		}  #  End for

	#  Goto form

	$details{'goto'} = qq~
	<form method=GET action="$Config->{base_url}index.$Config->{ext}">
	<input type=submit value="Jump"> to 
	<select name="month">
	~;

	for (1..12)	{
		$details{'goto'} .= "<option value=\"$_\"";
		if ($_ == $this_month)	{
			$details{'goto'} .= " SELECTED"
		}
		$details{'goto'} .= ">$Config->{months}[$_]";
	}  # End for

	$details{'goto'} .= qq~
	</select>
	<input name="year" size=4 value="$this_year">
	</form></center>
    ~;

	#  Link to other months
	$details{month_view} = "$Config->{base_url}index.$Config->{ext}?action=Month&month=$this_month&year=$this_year";

	my $last_year=$this_year;
	my $last_month=($this_month-1);
	if ($last_month == 0)	{
		$last_month=12;
		$last_year=($this_year-1)
	} #  End if
	$details{prev_view} = "$Config->{base_url}index.$Config->{ext}?action=Main&month=$last_month&year=$last_year";

	my $next_year=$this_year;
	my $next_month=($this_month+1);
	if ($next_month == 13)	{
		$next_month=1;
		$next_year=($this_year+1)
	}  #  End if
	$details{next_view} = "$Config->{base_url}index.$Config->{ext}?action=Main&month=$next_month&year=$next_year";

	$details{current} = "$Config->{base_url}index.$Config->{ext}?action=Main";

	#  Links to edit announcements

	$details{edit_announcements} = 
		"<a href=\"$Config->{base_url}announcement.$Config->{ext}?action=New&month=$this_month&year=$this_year\">Add announcements for this month</a>";
	$details{add_event} = "$Config->{base_url}event.$Config->{ext}?action=New&month=$this_month&year=$this_year";

	if ($any_announce eq "yes")	{
			$details{edit_announcements} .= qq~ 
		| <a href="$Config->{base_url}announcement.$Config->{ext}?action=EditList&month=$this_month&year=$this_year">Edit
		             announcements for this month</a>
		~;
	}  #  End if

	$details{version} = $Config->{VERSION};
	return ($template, \%details);
}  #  End sub Main

sub Day	{
	my ($form) = @_;
	my %details = %$form;
	my $template = 'display';
	my ($begin, $end,
	    $event, $events, %Event,@todays_events,
		$date, $tmp_day, $tmp_month,
		@dates,
		);
	my $today = local_julian_day(time);
	if (! $form->{day}) {
		$form->{day} = $today;
	}

	my  ($year, $month, $day) = inverse_julian_day($form->{day});
	#  page color, link color, etc
	body_tag($month, \%details);

	#  Read in database.
	open (DATES, "$Config->{datebook}");
	@dates=<DATES>;
	close DATES;

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
			 <a href="$Config->{base_url}event.$Config->{ext}?action=Edit&id=$Event{id}&this_year=$year">Edit event</a> ]
			 [ <a href="$Config->{base_url}event.$Config->{ext}?action=Confirm&id=$Event{id}&this_year=$year">Delete event</a> ]
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

	$details{add} = "$Config->{base_url}event.$Config->{ext}?action=New&day=$form->{day}";
	$details{calendar} = "$Config->{base_url}index.$Config->{ext}?month=$month&year=$year";
	$details{day_txt} = strftime("%A, %B %o, %Y",
			localtime(jd_secondslocal($form->{day})));

	return ($template, \%details);
}  #  End sub Day

sub Month	{
	my ($form) = @_;
	my $template = "month_view";
	my ($today, $day, $event,
		%Event, @thismonth_datebook,
		$i, $todays_events, $line,
		$emon, $eday, $tday,
		$begin, $end, @dates,
		);
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
	$details{hypercal} = $Config->{base_url} . "index." . $Config->{ext};

	#  Read in database.
	open (DATES, "$Config->{datebook}");
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
			<dt><b><a href="index.$Config->{ext}?action=Day&day=$i">$tday</a></b>
			$todays_events
			<hr width=10% align=left>
			~;
		}  #  End if
	}  #  End for $i

	#  Other stuff ...

	$details{add_event} = "event.$Config->{ext}?action=New&month=" . $form->{month}
				. "&year=" . $form->{year};

	return ($template, \%details);
} #  End sub Month

sub Event	{
	my ($form) = @_;
	my %details = %$form;
	my $template = 'display';
	my ($begin, $end);
	my $today = local_julian_day(time);
	if (! $form->{day}) {
		$form->{day} = $today;
	}

	my  ($year, $month, $day) = inverse_julian_day($form->{day});
	#  page color, link color, etc
	&body_tag($month, \%details);

	#  Read in database.
	open (DATES, "$Config->{datebook}");
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
			 <a href="event.$Config->{ext}?action=Edit&id=$Event{id}&this_year=$year">Edit event</a> ]
			 [ <a href="event.$Config->{ext}?action=Delete&id=$Event{id}&this_year=$year">Delete event</a> ]
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

	$details{add} = "$Config->{base_url}event.$Config->{ext}?action=New&day=$form->{day}";
	$details{calendar} = "$Config->{base_url}index.$Config->{ext}?month=$month&year=$year";
	$details{day_txt} = strftime("%A, %B %o, %Y",
			localtime(jd_secondslocal($form->{day})));

	return ($template,\%details);			
}  #  End sub Event