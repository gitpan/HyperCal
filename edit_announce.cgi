#!/usr/bin/perl
#
##############################################
#   file: edit_announce.pl                    
#   Author: Rich Bowen                        
#   Date: December 29, 1997                   
#                                             
#   Edit announcements for a particular month 
##############################################
use RCBowen;
use HyperCal;
use strict 'vars';

my %FORM= ();
FormParse(\%FORM);

my $routine = switch($FORM{action});

PrintHeader();
my ($template, $details) = &{$routine}(\%FORM);

PrintTemplate($templates, $template, $details);

sub switch	{
	my ($action) = @_;
	if ($action eq "")	{
		$action = "default";
	}
	my %switch = ('default'=>'DisplayAnnounce',
				  'edit_form'=>'EditForm',
				  'edit'=>'Edit',
				  'del_confirm'=>'DeleteConfirm',
				  'delete'=>'Delete'
				  );
	return $switch{$action};
}

sub DisplayAnnounce  {
	#  List all the announcements for this month
	my ($form) = @_;
	my (@announce, $line,
		$pointer, %Announce);
	my $template = 'list_announce';
	my %details = %$form;

	open (ANNOUNCE, "$announce");
	@announce = <ANNOUNCE>;
	close ANNOUNCE;

	@announce = grep /^($form->{month})($delimiter)/, @announce;

	for $line (@announce)	{
		$pointer = AnnounceSplit($line);
		%Announce = %$pointer;

		$details{announce} .= qq~
		<tr><td>$Announce{announcement}
		<small>
		[ <a href="$edit_announce?id=$Announce{id}&year=$form->{year}&month=$form->{month}&action=edit_form">Edit</a>]
		[ <a href="$edit_announce?id=$Announce{id}&year=$form->{year}&month=$form->{month}&action=del_confirm">Delete</a>]
		</small>
		~;
	}  #  End for

	body_tag($form->{month}, \%details);
	return ($template, \%details);
} #  End sub DisplayAnnounce

sub EditForm  {
	my ($form) = @_;
	my %details = %$form;
	my $template = 'edit_announce';
	my ($pointer, %Announce);

   	#  Get the announcement details                           
   	open (ANNOUNCE, "$announce");                             
   	my @announce = (<ANNOUNCE>);                              
   	close ANNOUNCE;                                           
   	chomp @announce;                                          
                                                                 
   	@announce = grep /($delimiter)($form->{id})$/, @announce; 
   	$pointer = AnnounceSplit($announce[0]);                   
   	%Announce = %$pointer;                                    
                                                                 
   	body_tag($Announce{month}, \%details);                    
   	$details{month} = $Announce{month};                       
   	$details{announcement} = $Announce{announcement};         
   	$details{url} = $base_url . $edit_announce;               
                                                                 
   	if ($Announce{year} eq "xxxx")	{                         
   		$details{annual} = "CHECKED";                         
   	}  #  End if                                              
	
	return ($template, \%details); 
}  #  End sub EditForm

sub Edit  {
	my ($form) = @_;
	my %details = ();
	my ($year);

	open (ANNOUNCE, "$announce");
	my @announce = <ANNOUNCE>;
	close ANNOUNCE;
	chomp @announce;

	@announce = grep !/($delimiter)($form->{id})$/, @announce;

	#  Build the correct new one
	if ($form->{annual})	{
		$year = "xxxx"
	}  else  {
		$year = $form->{year};
	}
	my $new_announce = join $delimiter, ($form->{month},
									  $year,
									  $form->{announcement},
									  $form->{id}
									 );
	push @announce, $new_announce;

	open (ANNOUNCE, ">$announce");
	for (@announce)	{
		print ANNOUNCE "$_\n";
	}
	close ANNOUNCE;

	my $template = 'redirect';
	$details{URL} = "$hypercal?month=$FORM{month}&year=$FORM{year}";

	return ($template, \%details);
}

sub DeleteConfirm  {
	my ($form) = @_;
	my %details = %$form;
	my $template = 'del_announce';
	my ($pointer, %Announce);

   	#  Get the announcement details                           
   	open (ANNOUNCE, "$announce");                             
   	my @announce = (<ANNOUNCE>);                              
   	close ANNOUNCE;                                           
   	chomp @announce;                                          
                                                                 
   	@announce = grep /($delimiter)($form->{id})$/, @announce; 
   	$pointer = AnnounceSplit($announce[0]);                   
   	%Announce = %$pointer;                                    
                                                                 
   	body_tag($Announce{month}, \%details);                    
   	$details{month} = $Announce{month};                       
   	$details{announcement} = $Announce{announcement};         
   	$details{url} = $base_url . $edit_announce;               
                                                                 
	return ($template, \%details); 
}  #  End sub EditForm

sub Delete  {
	my ($form) = @_;
	my %details = ();
	my ($year);

	open (ANNOUNCE, "$announce");
	my @announce = <ANNOUNCE>;
	close ANNOUNCE;
	chomp @announce;

	@announce = grep !/($delimiter)($form->{id})$/, @announce;

	open (ANNOUNCE, ">$announce");
	for (@announce)	{
		print ANNOUNCE "$_\n";
	}
	close ANNOUNCE;

	my $template = 'redirect';
	$details{URL} = "$hypercal?month=$FORM{month}&year=$FORM{year}";

	return ($template, \%details);
}

