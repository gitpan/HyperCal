#!/usr/bin/perl
# Add/Edit/Delete events
use HyperCal;
use Time::JulianDay;
use strict 'vars';

my ($template, $details, $form, @Actions, $routine);

$form = FormParse;
PrintHeader();
@Actions = qw(New Add Edit Update
              Confirm Delete
              );
$routine = Switch("$form->{action}",\@Actions, 'New');
($template, $details) = &{$routine}($form);
PrintTemplate ($Config->{templates}, $template, $details);

#####################
sub New {
	my ($form) = @_;
	my ($template, %details, $i, $year);
	
	$template = "add_date";
	%details=%$form;
	
	if (! $form->{day})	{
		$form->{day} = local_julian_day(time);
		if ($form->{month})	{
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
		$details{months} .= ">$Config->{months}[$i]\n";
	}  #  End for

	for ($i=1;$i<=31;$i++)	{
		$details{days} .= "<option value=\"$i\"";
		if ($i == $details{day})	{
			$details{days} .= " SELECTED";
		}
		$details{days} .= ">$i\n";
	}  #  End for
		

	$details{base_url} = $Config->{base_url};
	$details{add_date} = "event.$Config->{ext}";
	$details{old} = $Config->{old};
	return ($template, \%details);
}  #  End sub New

sub Add	{
	my ($form) = @_;
	my (%details, $id,
        $begin, $end, $day,
		$annual, $newappt, @new_appointments,
		$date, $template, $lockfile,
	    );
	
	# Strip returns from description field to make it one continuous string.
	$form->{'desc'} =~ s/\n/<br>/g;

	# Get id number
	$id = GetId($Config->{datebook} . ".id");

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

	$begin = (sprintf "%.2d", $form->{hour}) 
	       		. (sprintf "%.2d", $form->{min});
	$end = (sprintf "%.2d", $form->{hour_done}) 
	       		. (sprintf "%.2d", $form->{min_done});
	$day = julian_day($form->{year}, $form->{month}, $form->{day});

	#  Is this an annual event?
	$annual = ($form->{annual}) ? 1 : 0;

	#  Add the new appointment to the database.
	$newappt= join $Config->{delimiter}, 
			($day, $begin, $end, $annual,
			$form->{desc}, 0,
			0, $id);
	push @new_appointments, $newappt;

	#  Something here for recurring events?
	#  Definately on the To Do list. Available in HyperCal Pro

	#  Get a lock on the lock file
	$lockfile = $Config->{datebook} . ".lock";
	open (LOCK, ">$lockfile");
	flock LOCK, 2;

	#  Write database back to disk file.
	open (DATES,">>$Config->{datebook}") 
		or die ("Was unable to open $Config->{datebook} file for writing: $!\n");
	for $date (@new_appointments) {
		print DATES "$date\n"
	}  #  End for
	close DATES;
	
	#  Release lock
	flock LOCK, 8;
	close LOCK;

	#  Send them on their merry way
	$template = "redirect";
	$details{URL} = "$Config->{base_url}index.$Config->{ext}?action=Day&day=$day";
	
	return ($template, \%details); 
}	# End sub Add

sub Edit	{
	my ($form) = @_;
	my $template = "edit_date";
	my ($line, $event, $pointer, %Event, %details, $i);

	#  Get the event
	open (EVENTS, "$Config->{datebook}");
	for $line (<EVENTS>)	{
		if ($line =~ /($Config->{delimiter})($form->{id})$/)	{
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
	$details{base_url} = $Config->{base_url};
	$details{edit_date} = "event.$Config->{ext}";
	$details{old} = $Config->{old};
	$details{id} = $form->{id};
	$details{this_year}  = $form->{this_year};

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
		$details{months} .= ">$Config->{months}[$i]\n";
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
} #  End sub Edit

sub Update	{
	my ($form) = @_;
	$form->{desc} =~ s/\n/<br>/g;
	my ($template, %details, $date, $id, $lockfile,
	    $begin, $end, $day, $return_day,
		$newappt, $annual, @dates,
		);

	# Get id number
	$id = $form->{id};

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

	$begin = (sprintf "%.2d", $form->{hour}) 
	       		. (sprintf "%.2d", $form->{min});
	$end = (sprintf "%.2d", $form->{hour_done}) 
	       		. (sprintf "%.2d", $form->{min_done});
	$day = julian_day($form->{year}, $form->{month}, $form->{day});
	$return_day = julian_day($form->{this_year}, $form->{month}, $form->{day});
	
	$annual = ($form->{annual}) ? 1 : 0 ;

	#  Add the new appointment to the database.
	$newappt= join $Config->{delimiter}, 
			($day, $begin, $end, $annual,
			$form->{desc}, 0,
			0, $id);

	#  Get a lock on the lock file
	$lockfile = $Config->{datebook} . ".lock";
	open (LOCK, ">$lockfile");
	flock LOCK, 2;

	#  Remove the current version of this date
	open (DATES, "$Config->{datebook}");
	@dates = <DATES>;
	close DATES;
	chomp @dates;

	@dates = grep !/($Config->{delimiter})($id)$/, @dates;

	#  Put the new version on there
	push @dates, $newappt;

	#  Write database back to disk file.
	open (DATES,">$Config->{datebook}") 
		or die ("Was unable to open $Config->{datebook} file for writing: $!\n");
	foreach $date (@dates) {
		print DATES "$date\n"
	} # End foreach
	close DATES;
	
	#  Release lock
	flock LOCK, 8;
	close LOCK;

	$template = 'redirect';
	$details{URL} = "$Config->{base_url}index.$Config->{ext}?action=Day&day=$return_day";
	
	return ($template, \%details); 
} #  End sub Update

sub Confirm	{
	my ($form) = @_;
	my $template = 'delete_confirm';
	my %details = %$form;
	my ($key, $event, $pointer, %Event);

	#  Read in the data file
	open (EVENTS, "$Config->{datebook}");
	my @events = <EVENTS>;
	close EVENTS;
	chomp @events;

	@events = grep /$Config->{delimiter}$form->{id}$/, @events;

	#  Is someone trying to hack us?
	if ($event = pop @events)	{
		$pointer = EventSplit($event);
		%Event = %$pointer;
		for $key (keys %Event)	{
			$details{$key} = $Event{$key};
		}  #  End for

		$details{del_date} = "$Config->{base_url}event.$Config->{ext}";
		$details{disp_day} = "$Config->{base_url}index.$Config->{ext}";

		#  What we really want $day to day is actually
		#  the day, in this_year;
		my ($year, $month, $day) = inverse_julian_day($details{day});
		$details{day} = julian_day($details{this_year},$month,$day);

	}  else  {
		$template = 'error';
		$details{error} = "You have entered an invalid event ID";
	}

	return ($template, \%details);
}  #  End sub Confirm

sub Delete	{
	#  Delete the event from the event file
	my ($form) = @_;
	my ($template, %details, @events, $lockfile);

	open (EVENTS, "$Config->{datebook}");
	@events = <EVENTS>;
	close EVENTS;
	chomp(@events);

	@events = grep !/($Config->{delimiter})($form->{ID})$/, @events;

	#  Get a lock on the lock file
	$lockfile = $Config->{datebook} . ".lock";
	open (LOCK, ">$lockfile");
	flock LOCK, 2;

	open (EVENTS, ">$Config->{datebook}");
	for (@events)	{
		print EVENTS "$_\n";
	} # End for
	close EVENTS;
	
	#  Release lock
	flock LOCK, 8;
	close LOCK;

	#  Send them on their merry way
	$template = 'redirect';
	$details{URL} = "$Config->{base_url}index.$Config->{ext}?action=Day&day=$form->{day}"; 

	return ($template, \%details);
}  #  End sub Delete