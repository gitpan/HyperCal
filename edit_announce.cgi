#!/usr/bin/perl
#
#	edit_announce
#
#	This script will handle the three types of editing
#	of the announce file - add new announcements, delete
#	existing announcements, and edit existing announcements.
#
 
#	Make sure that this points to the right place:
require 'variables';
require 'httools.pl';
&header;

($sub=$ENV{'PATH_INFO'})=~s#^/##;
if ($sub=~/personal/){require $personal};

($month,$year,$command)=split(/&/,$ENV{'QUERY_STRING'});

if ($command eq "addit") { &addit }
elsif ($command eq "delete") { &delete }
elsif ($command eq "delete_2") { &delete_2 }
else { &do_form };

sub do_form	{
# This part will print the html form to collect the data

&month_txt("$month");
&title("Add an announcement to $month_txt $year.");

print "<h2>Add an announcement to $month_txt, $year.</h2>";
print "<hr>";
print "<form method=post action=$base_url$edit_announce?$month&$year&addit>";
print "<b>Announcement:</b><br>";
print "<input name=\"announce\" size=40><hr>";
print "<input type=hidden name=\"month\" value=\"$month\">";
print "<input type=hidden name=\"year\" value=\"$year\">";
print "<input type=submit value=\"Add it\"><br>";

&footer;
}    #   This is the end of &do_form

sub addit	{
 
&form_parse;
&month_txt("$FORM{'month'}");
&title("Announcement added to $month_txt, $FORM{'year'}");

#   Get the new id number
open (ID, "$hypercal_id");
@id=<ID>;
for(@id){chop};
@id[1]++;
if (@id[1]>=999999){@id[0]=1};
$id=@id[1];
open (ID, ">$hypercal_id");
for $each (@id)	{
print ID "$each\n";}

#	Write the announcement out to the file
open (FILE, ">>$announce");
print FILE "$FORM{'month'}_$FORM{'year'}&&$FORM{'announce'}&&$id\n";

print "Announcement added.  Go back to <a href=$base_url$hypercal?$FORM{'month'}&$FORM{'year'}>$month_txt, $FORM{'year'}</a> - you will need to reload the page to see your changes.";
&footer;

		}	# This is the end of &addit	

sub delete	{
open (ANN, "$announce");
@entries=<ANN>;
for (@entries){chop};

&title("Delete entry from $month\/$year.");
print "<h3>Select announcement(s) to delete</h3>";
print "<hr>";
print "<form method=post action=$base_url$edit_announce?$month&$year&delete_2>";

$date=$month."_".$year;
for $announces (@entries)	{
($mo,$text,$id_no)=split(/&&/,$announces);
if ($mo eq $date)	{
print "<input type=checkbox name=\"$id_no\">   $text<br>";}
				}
print "<hr>";
print "<input type=submit value=\"Delete announcement\">";

	}		#  This is the end of &delete

sub delete_2	{
&form_parse;
&title("Announcement(s) deleted from $month\/$year");
open (ANN, $announce);
@announces=<ANN>;
for(@announces){chop};
for $announces (@announces)	{
($dat,$anno,$id_no)=split(/&&/,$announces);
$found=0;
foreach $key (keys %FORM)	{
if ($key==$id_no) {$found=1};	}
push (@new_announce,$announces) unless ($found==1);
				}   #  End for $announces

open (ANN, ">$announce");
for (@new_announce) {print ANN; print ANN "\n";}

print "<h2>Announcement deleted</h2>";
print "You may now go back to <a href=$base_url$hypercal?$month&$year>$month\/$year</a>.";
print "<hr>";
&footer;
	}	#	End of delete_2
