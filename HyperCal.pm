package HyperCal;

require Exporter;
@ISA = Exporter;
@EXPORT = qw(body_tag
			month_txt
			EventSplit
			AnnounceSplit
			GetId
			convert_time
			AmPm			

			$server_name
			$delimiter
			$base_url
			$templates
			$ext
			$old
			$title
			$highlight
			$td_color
			@month_images
			$add_date
			$del_date
			$edit_date
			$disp_day
			$add_announce
			$del_announce
			$edit_announce
			$month_view
			$hypercal
			$datebook
			$hypercal_id
			$announce
			$announce_id
			@months
			$DisplayNumber
			$DisplayEvents
			);

use vars qw($VERSION $server_name $delimiter $base_url $templates
			$ext $old $title $highlight $td_color @month_images
			$add_date $del_date $edit_date $disp_day $add_announce
			$del_announce $edit_announce $month_view $hypercal
			$datebook $hypercal_id $announce $announce_id @months
			$DisplayNumber $DisplayEvents
			);


#################################################
##  VARIABLES - SET THESE TO YOUR LOCAL CONFIG ##
#################################################
$VERSION="3.01";
$server_name = "www.rcbowen.com";
$delimiter = "~~";

# URL of the directory in which these files live
$base_url="/scripts/hypercal/";

#  Location of the hypercal templates - you need to specify full path
$templates = "/home/rbowen/public_html/scripts/hypercal/templates";

# Names of the various program files
#  Some sites only allow cgi's with a .cgi extension
#  so you might need to change your file extension to "cgi"
$ext = "cgi";

#  Number of days to keep past dates
$old=370;

# Title of the calendar.
$title="HyperCal Version $VERSION";

#  1 is on, 0 is off.  Should we display the number
#  of events on that day, or the event text.
#  For some very high traffic calendars, you 
#  might not want to display all the events.
$DisplayNumber=1;
$DisplayEvents=0;

###############################################################
#   Customize the colors and images appearing in the calendar: 
###############################################################

$highlight="ivory";  # What color should "today" be highlighted in?
$td_color = "lightblue"; #  How about the rest of the table cells?

#  This array contains the locations of images for the various
#  months.  The format is
#  [url_for_icon,url_for_background,bgcolor,text,link,visited link]
#  This array must contain 12 elements. Any field where you have 
#  no preference, indicate by 'none'
@month_images=(
	['/images/months/january.gif','none','333399','none','FFFF00','55FF8B'],
	['/images/months/february.gif','none','none','none','none','none'],
	['/images/months/march.gif','none','lightgreen','none','none','none'],
	['/images/months/april.gif','none','none','none','none','none'],
	['/images/months/may.gif','none','none','none','none','none'],
	['/images/months/june.gif','none','none','none','none','none'],
	['/images/months/july.gif','none','none','none','none','none'],
	['none','none','none','none','none','none'],
	['none','none','FFFFFF','000000','none','none'],
	['/images/months/october.gif','none','000000','FFFF00','00DD00','9168D7'],
	['/images/months/november.gif','none','FFFFFF','000033','none','none'],
	['/images/months/december.gif','none','DDDDFF','FF3333','none','none']
	);

# Other files
#  You probably don't want to change this stuff

$add_date="add_date.$ext";
$del_date="del_date.$ext";
$edit_date="edit_date.$ext";
$disp_day="disp_day.$ext";
$add_announce="add_announce.$ext";
$del_announce="del_announce.$ext";
$edit_announce="edit_announce.$ext";
$month_view="month.$ext";
$hypercal="hypercal.$ext";

#  Data files
$datebook="datebook";
$hypercal_id="hypercal_id";
$announce="announce";
$announce_id="announce_id";

@months=('December', 'January', 'February',
		 'March', 'April', 'May', 'June',
		 'July', 'August', 'September',
		 'October', 'November', 'December');

#########################################################
sub body_tag	{
	my ($month,$details) = @_;

	$details->{month_text} = &month_txt($month);

	my @fields=('image','background','bgcolor','text','link','vlink');

	for (0..5)	{
		$details->{$fields[$_]} = 
			" $fields[$_] = $month_images[$month-1][$_] "
				unless ($month_images[$month-1][$_] eq "none");
			}  #  End for
	$details->{month_image} = "<img src=\"$month_images[$month-1][0]\">"
			 unless ($month_images[$month-1][0] eq "none");
}  #  End sub body_tag

sub error_print	{
PrintHeader();
my $error = shift;
print "<b>$error</b><br>";
exit(0);
}

sub EventSplit	{
	my ($string) = @_;
	chomp $string;
	my %Event = ();

	($Event{day},
	 $Event{begin},
	 $Event{end},
	 $Event{annual},
	 $Event{description},
	 $Event{type},
	 $Event{recurringid},
	 $Event{id} ) = split (/$delimiter/, $string);

	return \%Event;
}

sub AnnounceSplit	{
	my ($string) = @_;
	chomp $string;
	my %Announce = ();

	($Announce{month},
	 $Announce{year},
	 $Announce{announcement},
	 $Announce{id} ) = split (/$delimiter/, $string);

	return \%Announce;
}

sub GetId	{
my $idfile = shift;
open (ID, "$idfile") 
       || &error_print("Was unable to open the ID file for reading");
my $id=<ID>;
close ID;
$id++;
if ($id>=999999) {$id=1};
open (NEWID,">$idfile")  
      || &error_print ("Was unable to open the ID file ($idfile) for writing");
print NEWID $id;
close NEWID;
return $id;
}

#
#	Sub 24time
#  Rewrites time into 24hr format.
#
sub convert_time	{
my ($HOUR, $MINS, $merid) = @_;

if ($merid eq "pm") {
 $HOUR+=12;
 if ($HOUR==24) {$HOUR=12}
		}
if ($HOUR==12 && $merid eq "am"){$HOUR=24};
if ($HOUR>24){$HOUR=23};
if ($MINS>59){$MINS=59};
$HOUR=sprintf "%02.00f",$HOUR;
$MINS=sprintf "%02.00f",$MINS;
}

sub AmPm	{
	my $time_string = shift;
	my $ret;

	my ($hour, $min) = ($time_string =~ /(\d\d)(\d\d)/);
	$hour =~ s/^0//;
	if ($hour == 12)	{
		$ret = "12:$min pm";
	} elsif ($hour > 12)	{
		$hour -= 12;
		$ret = "$hour:$min pm";
	}  else  {
		$ret = "$hour:$min am";
	}
	return $ret;
}

sub month_txt   {  # converts number to month text
my $month = shift;
return ( ('ERROR','January','February','March',
			'April','May','June','July',
			'August','September','October',
			'November','December')[$month] );
                }

#########################################################
# Do not change this, Do not put anything below this.
# File must return "true" value at termination
1;
##########################################################
