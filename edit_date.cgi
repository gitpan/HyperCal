#!/usr/bin/perl
#####################################################################
#   Edit an existing event.                                          
#   This script is also in two parts - the first part, display_form, 
#   will display a form with the current event details in it.  The   
#   second part, edit_event, will take the contents of the form      
#   and modify the details of the event in the date file.            
#                                                                    
#   Rich Bowen                                                       
#   RCBowen.com                                                      
#   Dec 29, 1997                                                     
#####################################################################
use RCBowen;
use HyperCal;
use Time::JulianDay;

my %FORM = ();
FormParse(\%FORM);

PrintHeader();

if ($FORM{routine} eq "edit_event")	{
	($template, $details) = edit_event(\%FORM);
} else {
	($template, $details) = DisplayForm(\%FORM);
}

PrintTemplate($templates, $template, $details);

########################

sub DisplayForm	{
	my ($form) = @_;
	my $template = "edit_date";
	my ($line, $event, $pointer, %Event);

	#  Get the event
	open (EVENTS, "$datebook");
	for $line (<EVENTS>)	{
		if ($line =~ /($delimiter)($form->{id})$/)	{
			$event = $line;
			last;
		}
	}  #  End for
	close EVENTS;

	if ($event eq "")	{
		$template = 'error';
		$details{error} = "Event not found";
		return ($template, \%details);
	}
	$pointer = EventSplit($event);
	%Event = %$pointer;

	$details{description} = $Event{description};
	$details{base_url} = $base_url;
	$details{edit_date} = $edit_date;
	$details{old} = $old;
	$details{id} = $FORM{id};
	$details{this_year}  = $FORM{this_year};

	if ($Event{annual})	{
		$details{annual} = "CHECKED"
	}

	($details{year}, $details{month}, $details{day}) =
		inverse_julian_day($Event{day});

	($details{hour},$details{min}) = 
		($Event{begin} =~ /(\d\d)(\d\d)/); 
	$details{min} = sprintf "%.2d", $details{min};

	#  Get the right am/pm stuff on the time
	if ($details{hour} == 12)	{
		$details{pm} = "CHECKED"
	} elsif ($details{hour} > 12)	{
		$details{hour} -= 12;
		$details{pm} = "CHECKED"
	} else {  #  time is am
		$details{am} = "CHECKED"
	}  #  End if..else

	($details{endhour},$details{endmin}) =
		($Event{end} =~ /(\d\d)(\d\d)/); 
	$details{endmin} = sprintf "%.2d", $details{endmin};
	#  Get the right am/pm stuff on the time
	if ($details{endhour} == 12)	{
		$details{endpm} = "CHECKED"
	} elsif ($details{endhour} > 12)	{
		$details{endhour} -= 12;
		$details{endpm} = "CHECKED"
	} else {  #  time is am
		$details{endam} = "CHECKED"
	}  #  End if..else

	for ($i=1;$i<=12;$i++)	{
		$details{months} .= "<option value=\"$i\"";
		if ($i == $details{month})	{
			$details{months} .= " SELECTED";
		}
		$details{months} .= ">$months[$i]\n";
	}  #  End for

	for ($i=1;$i<=31;$i++)	{
		$details{days} .= "<option value=\"$i\"";
		if ($i == $details{day})	{
			$details{days} .= " SELECTED";
		}
		$details{days} .= ">$i\n";
	}  #  End for
		
	body_tag($details{month}, \%details);
	return ($template, \%details);
} #  End sub details

###################
#   Sub edit_event 
###################
sub edit_event	{
	my ($form) = @_;
	$form->{desc} =~ s/\n/<br>/g;
	my ($template);

	# Get id number
	my $id = $form->{id};

	if ($form->{hour} != 12 && $form->{ampm} eq "pm")	{
		$form->{hour} += 12;
	} elsif ($form->{hour} == 12 && $form->{ampm} eq "am")	{
		$form->{hour} = 0;
	}
	if ($form->{hour_done} != 12 && $form->{ampm_done} eq "pm")	{
		$form->{hour_done} += 12;
	} elsif ($form->{hour_done} == 12 && $form->{ampm_done} eq "am")	{
		$form->{hour_done} = 0;
	}

	my $begin = (sprintf "%.2d", $form->{hour}) 
	       		. (sprintf "%.2d", $form->{min});
	my $end = (sprintf "%.2d", $form->{hour_done}) 
	       		. (sprintf "%.2d", $form->{min_done});
	my $day = julian_day($form->{year}, $form->{month}, $form->{day});

	$annual = ($form->{annual}) ? 1 : 0 ;

	#  Add the new appointment to the database.
	$newappt= join $delimiter, 
			($day, $begin, $end, $annual,
			$FORM{desc}, 0,
			0, $id);

	#  Remove the current version of this date
	open (DATES, "$datebook");
	@dates = <DATES>;
	close DATES;
	chomp @dates;

	@dates = grep !/($delimiter)($id)$/, @dates;

	#  Put the new version on there
	push @dates, $newappt;

	#  Write database back to disk file.
	open (DATES,">$datebook") 
		|| &error_print ("Was unable to open the datebook file for writing.");
	foreach $date (@dates) {
		print DATES "$date\n"
		}
	close DATES;

	$template = 'redirect';
	$details{URL} = 
	    "$base_url$disp_day?day=$day";
	
	return ($template, \%details); 
} #  End sub edit_event
