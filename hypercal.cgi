#!/usr/bin/perl
#	HyperCal   by   Richard Bowen
#  A HTML datebook.  
#  This part draws the calendar and links it to the other scripts.
use RCBowen;
use HyperCal;
use strict 'vars';
use Time::JulianDay;
use Time::DaysInMonth;
use vars qw (%details
			);

PrintHeader();

#  Get the arguments
my %FORM = ();
FormParse(\%FORM);

my $details = details(\%FORM);  #  Get some more details
PrintTemplate($templates,'hypercal',$details);

###############################
#  End of main program


sub details	{
	#  Determine some of the details to be printed on the calendar
	my $form = shift;  #  Remember that $form is a reference
	my %FORM = %$form;
	my ($this_month, $this_year);
	my %details = %FORM;

	# Determine what "today" is.
	my $today = local_julian_day(time);
	my ($today_year, $today_month, $today_mday) = inverse_julian_day($today);

	if (! $details{month}) {	#  Defaults to current date if none specified.
		$this_month = $today_month;
		$this_year = $today_year;
	} else	{
		#  Get the month, year, from the command line
		$this_month = $FORM{month};
		$this_year = $FORM{year};
	}  #  End if...else
	my $first_day = julian_day($this_year, $this_month, 1);
	my $last_day = $today + days_in($this_year, $this_month);
	my $first_dow = day_of_week($first_day);

	$details{year} = $this_year;
	$details{month_text} = month_txt($this_month);

	#  page color, link color, etc
	&body_tag($this_month, \%details);

	#	Read datebook into memory
	#
	open (DATES, $datebook) or die "Unable to open datebook: $!";
	my @datebook=<DATES> ;
	close DATES;

	############################################################
	#   Since we are looking at just one month, it would        
	#    make sense at this point to take a few microseconds to 
	#    pull out just the events for this month, hmmmm?
	#  This will save time later        
	############################################################

	my (%Event,@thismonth_datebook,$event);
	for (@datebook)	{
		my $event = EventSplit($_);
		%Event = %$event;

		if ($Event{annual} || (($Event{day} >= $first_day) && 
					($Event{day} <= $last_day)) )	{
			push @thismonth_datebook, $_;
		} #  End if
	}  #  End for
	@datebook = @thismonth_datebook;


	#  Print some blank cells for the space before the first
	#  day of the month
	######################
	$details{calendar} .= "<tr><td colspan=$first_dow></td>\n" 
				unless ($first_dow == 0);

	my $week_day = $first_dow;

	#  Loop through all the days in the month
	my ($date_place, $day, $_mon, $_day);

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
		if ($day == $today and $highlight ne "none")	{
			$details{calendar} .= " bgcolor=\"$highlight\""
		} else	{
			if ($td_color ne "" and $td_color ne "none")	{
				$details{calendar} .= " bgcolor=\"$td_color\""
			}
		}  #  End if..else
		$details{calendar} .= ">\n";
		$details{calendar} .= "<a href=\"$base_url$disp_day?day=$day\">$date_place</a>";

		#  OK, now the time consuming part - what happens this day?
		my $line;
		for $line (@datebook)	{
			$event = EventSplit($line);
			%Event = %$event;

			#  How about annual events?
			if ($Event{annual}) 	{
				(undef, $_mon, $_day) = inverse_julian_day($Event{day});
				if ($_day == $date_place && $_mon == $this_month)	{
					$details{calendar} .= qq~
					<br><small>$Event{description}</small>
					~;
				}
			}  else	{  # The rest of the events
				if ($Event{day} == $day) {
					$details{calendar} .= qq~
					<br><small>$Event{description}</small>
					~;
				}  #  End if
			} #  End else 
		}  #  End for datebook
		$details{calendar} .= "</td>\n";
		
		#  Is is a Saturday?  That's the end of the row.
		if ($week_day == 6) {
			$details{calendar} .= "</tr>\n"
			}  #  End if saturday

		$week_day ++;
		if ($week_day == 7) {$week_day = 0};  #  Start the week over
	}  # End for date_place - repeated for each day in the month


	# Announcements for the month
	open (ANNO, "$announce");
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
	<form method=GET action=$base_url$hypercal>
	<input type=submit value="Jump"> to 
	<select name="month">
	~;

	for (1..12)	{
		$details{'goto'} .= "<option value=\"$_\"";
		if ($_ == $this_month)	{
			$details{'goto'} .= " SELECTED"
		}
		$details{'goto'} .= ">$months[$_]";
	}  # End for

	$details{'goto'} .= qq~
	</select>
	<input name="year" size=4 value="$this_year">
	</form></center>
    ~;

	#  Link to other months
	$details{month_view} = $base_url . $month_view 
					. "?month=$this_month&year=$this_year";

	my $last_year=$this_year;
	my $last_month=($this_month-1);
	if ($last_month == 0)	{
		$last_month=12;
		$last_year=($this_year-1)
	} #  End if
	$details{prev_month} ="$base_url$hypercal?month=$last_month&year=$last_year";

	my $next_year=$this_year;
	my $next_month=($this_month+1);
	if ($next_month == 13)	{
		$next_month=1;
		$next_year=($this_year+1)
	}  #  End if
	$details{next_month} = "$base_url$hypercal?month=$next_month&year=$next_year";

	$details{current} = "$base_url$hypercal";

	#  Links to edit announcements

	$details{edit_announcements} = 
		"<a href=\"$base_url$add_announce?month=$this_month&year=$this_year\">Add announcements for this month</a>";
	$details{add_event} = "$base_url$add_date?month=$this_month&year=$this_year";

	if ($any_announce eq "yes")	{
			$details{edit_announcements} .= qq~ 
		| <a href="$base_url$edit_announce?month=$this_month&year=$this_year">Edit
		             announcements for this month</a>
		~;
	}  #  End if

	$details{version} = $HyperCal::VERSION;
	return \%details;
}  #  End sub details

