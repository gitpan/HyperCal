#!/usr/bin/perl
##########################################################
#   Add an announcement                                   
#   Announcements will be displayed on the bottom of the  
#   calendar - or wherever you put the %%%announce%%% tag 
#   Announcements can be for one month, or annual         
#                                                         
#   Rich Bowen                                            
#   RCBowen.com                                           
#   Dec 29, 1997                                          
#                                                         
##########################################################
use RCBowen;
use HyperCal;
use strict 'vars';

my %FORM = ();
FormParse(\%FORM);
my ($template, $details);

PrintHeader();

if ($FORM{routine} eq "add_announce")	{
	($template, $details) = AddAnnounce(\%FORM);
}  else  {
	($template, $details) = DisplayForm(\%FORM);
}

PrintTemplate($templates, $template, $details);
######################################

sub DisplayForm	{
	my ($form) = @_;
	my $template = "add_announce";

	if (! $form->{month})	{
		#  Default to this month
		my @tmp_time = localtime(time);
		$form->{month} = $tmp_time[4] +1;
		$form->{year} = $tmp_time[5] +1900;
	}

	my %details = %$form;

	body_tag("$form->{month}", \%details);
	$details{month_text} = month_txt($form->{month});

	$details{url} = "$base_url$add_announce";

	return ($template, \%details);
}  #  End sub details

sub AddAnnounce	{
	my ($form) = @_;
	my $template;
	my %details = %$form;
	my ($year, $id, $announcement);
	
	if ($form->{annual})	{
		$year = "xxxx"
	}  else  {
		$year = $form->{year}
	}

	if ($form->{announce}	eq "")	{
		$template = 'error';
		$details{error} = "You did not enter anything for the announcement";
	}  else  {
		$id = GetId($announce_id);
		$form->{announce} =~ s/\n/<br>/g;

		$announcement = join $delimiter, ($form->{month},
										  $year,
										  $form->{announce},
										  $id
										 );

		open (ANNOUNCE, ">>$announce");
		print ANNOUNCE "$announcement\n";
		close ANNOUNCE;

		#  Send them on their merry way
		$template = "redirect";
		$details{URL} = "$hypercal?month=$form->{month}&year=$form->{year}";
	}

	return ($template, \%details);
}