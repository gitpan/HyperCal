#!/usr/bin/perl
#
#	Add Date
#
#	Prints html form for input of new appointment.  Sends the
#   form input to part_2 for processing.
#	Richard Bowen, 12/14/95
#	modified 12/26/1997
#	rbowen@rcbowen.com
#_____________________________________________________
use RCBowen;
use HyperCal;
use Time::JulianDay;
use strict 'vars';

#  Get the arguments
my %FORM=();
FormParse(\%FORM);

#
#	Determine which part of the script is being called
#__________________________________

my ($template, $details);
if ($FORM{routine} eq "add_date") {
	($template,$details) = add_date(\%FORM)
}  else  {
	($template, $details) = display_form(\%FORM);
}

PrintHeader();
PrintTemplate($templates, $template, $details);

####################
sub display_form {
	my ($form) = @_;
	my $template = "add_date";
	my %details=%$form;
	my ($i);

	if (! $form->{day})	{
		$form->{day} = local_julian_day(time);
		if ($form->{month})	{
			my $year;
			if ($form->{year})	{
				$year = $form->{year};
			}  else  {
				($year, undef, undef) = inverse_julian_day($form->{day});
			}
			$form->{day} = julian_day($year, $form->{month},1);
		}
	}
	
	($details{year},$details{month},$details{day}) = 
		inverse_julian_day($form->{day});

	$details{month_text} = month_txt($details{month});
	body_tag($details{month},\%details);

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
		

	$details{base_url} = $base_url;
	$details{add_date} = $add_date;
	$details{old} = $old;
	return ($template, \%details);
}  

sub add_date	{
	#	Receives the post data from add_form and adds the information
	#  to the database.  Format of database is currently:
	# Get data from form post.
	#  Variables are:
	#	day, month, year
	#  hour, min, ampm, desc, freq, perp
	#  hour_done, min_done, ampm_done, days, weeks, months
	#  Annual
	my %details = ();
	my ($form) = @_;

	# Strip returns from description field to make it one continuous string.
	$form->{'desc'} =~ s/\n/<br>/g;

	# Get id number
	my $id = GetId($hypercal_id);

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

	#  Is this an annual event?
	my $annual = ($form->{annual}) ? 1 : 0;

	#  Add the new appointment to the database.
	my $newappt= join $delimiter, 
			($day, $begin, $end, $annual,
			$form->{desc}, 0,
			0, $id);
	my @new_appointments;
	push @new_appointments, $newappt;

	#  Something here for recurring events?

	#  Write database back to disk file.
	open (DATES,">>$datebook") 
		|| &error_print ("Was unable to open the datebook file for writing.");
	my $date;
	foreach $date (@new_appointments) {
		print DATES "$date\n"
		}
	close DATES;

	#  Send them on their merry way
	my $template = "redirect";
	$details{URL} = "$base_url$disp_day?day=$day";
	
	return ($template, \%details); 
}	# End of part_2
