#!/usr/bin/perl
# Add/Delete/Edit announcements for HyperCal
use HyperCal;
use strict 'vars';

my $form = FormParse;
my ($template, $details, @Actions, $routine);

PrintHeader();

@Actions = qw(New Add EditList Edit
			Update Confirm Delete
			);
$routine = Switch("$form->{action}",\@Actions, 'New');
($template, $details) = &{$routine}($form);
PrintTemplate ($Config->{templates}, $template, $details);

sub New	{
	my ($details) = @_;
	my ($template);
	
	$template = "add_announce";

	if (! $details->{month})	{
		#  Default to this month
		my @tmp_time = localtime(time);
		$details->{month} = $tmp_time[4] +1;
		$details->{year} = $tmp_time[5] +1900;
	}

	body_tag("$details->{month}", $details);
	$details->{month_text} = month_txt($details->{month});

	$details->{url} = $Config->{base_url} . "announcement." . $Config->{ext};

	return ($template, $details);
}  #  End sub New

sub Add	{
	my ($details) = @_;
	my ($template, $year, $id, $announcement, $lockfile,
		);
	
	if ($details->{annual})	{
		$year = "xxxx"
	}  else  {
		$year = $details->{year}
	}

	if ($details->{announce}	eq "")	{
		$template = 'error';
		$details->{error} = "You did not enter anything for the announcement";
	}  else  {
		$id = GetId($Config->{announce} . ".id");
		$details->{announce} =~ s/\n/<br>/g;

		$announcement = join $Config->{delimiter}, ($details->{month},
							 $year,
							 $details->{announce},
							 $id
							 );
		#  Get a lock on the lock file
		$lockfile = $Config->{announce} . ".lock";
		open (LOCK, ">$lockfile");
		flock LOCK, 2;

		open (ANNOUNCE, ">>$Config->{announce}");
		print ANNOUNCE "$announcement\n";
		close ANNOUNCE;
		
		#  Release lock
		flock LOCK, 8;
		close LOCK;

		#  Send them on their merry way
		$template = "redirect";
		$details->{URL} = "index.$Config->{ext}?month=$details->{month}&year=$details->{year}";
	}

	return ($template, $details);
} #  End sub Add

sub EditList  {
	#  List all the announcements for this month
	my ($form) = @_;
	my (@announce, $line,
		$pointer, %Announce);
	my $template = 'list_announce';
	my %details = %$form;

	open (ANNOUNCE, "$Config->{announce}");
	@announce = <ANNOUNCE>;
	close ANNOUNCE;

	@announce = grep /^($form->{month})($Config->{delimiter})/, @announce;

	for $line (@announce)	{
		$pointer = AnnounceSplit($line);
		%Announce = %$pointer;

		$details{announce} .= qq~
		<tr><td>$Announce{announcement}
		<small>
		[ <a href="announcement.$Config->{ext}?id=$Announce{id}&year=$form->{year}&month=$form->{month}&action=Edit">Edit</a>]
		[ <a href="announcement.$Config->{ext}?id=$Announce{id}&year=$form->{year}&month=$form->{month}&action=Confirm">Delete</a>]
		</small>
		~;
	}  #  End for

	body_tag($form->{month}, \%details);
	return ($template, \%details);
} #  End sub DisplayAnnounce

sub Edit  {
	my ($form) = @_;
	my %details = %$form;
	my $template = 'edit_announce';
	my ($pointer, %Announce);

   	#  Get the announcement details                           
   	open (ANNOUNCE, "$Config->{announce}");                             
   	my @announce = (<ANNOUNCE>);                              
   	close ANNOUNCE;                                           
   	chomp @announce;                                          
                                                                 
   	@announce = grep /($Config->{delimiter})($form->{id})$/, @announce; 
   	$pointer = AnnounceSplit($announce[0]);                   
   	%Announce = %$pointer;                                    
                                                                 
   	body_tag($Announce{month}, \%details);                    
   	$details{month} = $Announce{month};                       
   	$details{announcement} = $Announce{announcement};         
   	$details{url} = $Config->{base_url} . "announcement." . $Config->{ext};               
                                                                 
   	if ($Announce{year} eq "xxxx")	{                         
   		$details{annual} = "CHECKED";                         
   	}  #  End if                                              
	
	return ($template, \%details); 
}  #  End sub EditForm

sub Update  {
	my ($form) = @_;
	my ($details, $year, @announce, $new_announce,
	    $template, $lockfile,
	    );

	open (ANNOUNCE, "$Config->{announce}");
	@announce = <ANNOUNCE>;
	close ANNOUNCE;
	chomp @announce;

	@announce = grep !/($Config->{delimiter})($form->{id})$/, @announce;

	#  Build the correct new one
	if ($form->{annual})	{
		$year = "xxxx"
	}  else  {
		$year = $form->{year};
	}
	$new_announce = join $Config->{delimiter}, ($form->{month},
								  $year,
								  $form->{announcement},
								  $form->{id}
								 );
	push @announce, $new_announce;

	#  Get a lock on the lock file
	$lockfile = $Config->{announce} . ".lock";
	open (LOCK, ">$lockfile");
	flock LOCK, 2;

	open (ANNOUNCE, ">$Config->{announce}");
	for (@announce)	{
		print ANNOUNCE "$_\n";
	}
	close ANNOUNCE;
	
	#  Release lock
	flock LOCK, 8;
	close LOCK;

	$template = 'redirect';
	$details->{URL} = "index.$Config->{ext}?month=$form->{month}&year=$form->{year}";

	return ($template, $details);
} #  End sub Update

sub Confirm  {
	my ($details) = @_;
	my ($Announce, $template, @announce,
	    $lockfile,
	   );

	$template = 'del_announce';

   	#  Get the announcement details                           
   	open (ANNOUNCE, "$Config->{announce}");                             
   	@announce = <ANNOUNCE>;                              
   	close ANNOUNCE;                                           
   	chomp @announce;                                          
                                                                 
   	@announce = grep /($Config->{delimiter})($details->{id})$/, @announce; 
   	$Announce = AnnounceSplit($announce[0]);                   
                                                                 
   	body_tag($Announce->{month}, $details);                    
   	$details->{month} = $Announce->{month};                       
   	$details->{announcement} = $Announce->{announcement};         
   	$details->{url} = $Config->{base_url} . "announcement." . $Config->{ext};
                                                                 
	return ($template, $details); 
}  #  End sub EditForm

sub Delete  {
	my ($form) = @_;
	my ($details, $year, @announce,
	    $template, $lockfile,
		);

	open (ANNOUNCE, "$Config->{announce}");
	@announce = <ANNOUNCE>;
	close ANNOUNCE;
	chomp @announce;

	@announce = grep !/($Config->{delimiter})($form->{id})$/, @announce;

	#  Get a lock on the lock file
	$lockfile = $Config->{announce} . ".lock";
	open (LOCK, ">$lockfile");
	flock LOCK, 2; # lock

	open (ANNOUNCE, ">$Config->{announce}");
	for (@announce)	{
		print ANNOUNCE "$_\n";
	}
	close ANNOUNCE;

	#  Release lock
	flock LOCK, 8; # unlock
	close LOCK;

	$template = 'redirect';
	$details->{URL} = "index.$Config->{ext}?month=$form->{month}&year=$form->{year}";

	return ($template, $details);
}