#!/usr/bin/perl
#
#	Administrative features for HyperCal
###########################################
#
#	Add new users
#	Remove users
#	Reset user's password
#	Expire old dates
# 	Set system variables
###########################################
require 'variables';
require 'httools.pl';
print "Content-type: text/html \n\n";

($sub=$ENV{'PATH_INFO'})=~s#^/##;
#  Get the subroutine desired and strip leading /

#  Determine which routine to do:
if ($sub eq "")	{&panel}
elsif ($sub eq "new_user") {&new_user_2}
elsif ($sub eq "del_user") {&del_user_2}
elsif ($sub eq "switchboard") {&switchboard}


############
#SUBROUTINES
############

sub panel	{
# Prints the main control panel of the admin functions.
######################

print <<"HTML";
<html>
<head><title>HyperCal Administrative Control</title></head>
<body>
<h2>HyperCal - Administrative control</h2>
<hr>
<form method=post action="$cal_admin/switchboard">
Administrative functions:<br>
<input type=radio name="function" value="new_user">  Add a new user<br>
<input type=radio name="function" value="del_user">  Remove a user<br>
Reset a user's password - Option not yet available<br>
Set the system variables - Option not yet available<br>
<hr>
<input type=submit value="Select option">
</form>
<br>
<hr width=33%>
<center>
[ <a href="$base_url$hypercal">HyperCal</a> | <a href="http://www.aiclex.com/webmaster/perl/HyperCal.html">About HyperCal</a> ]
</center>

</body></html>

HTML
	}	#  End of sub control


sub switchboard	{
#  Retrieves info from the control panel and redirects to the appropriate
#  routine.
&form_parse;

$function=$FORM{'function'};

&$function; # This will call the routine called $function
	    #  Where function is one of
	    #  new_user, del_user, reset_user, set_vars
		}

sub new_user	{
print <<HTML
<html>
<head><title>Add a new user</title></head>
<body>
<h2>Add a new user</h2>
<hr>
<form method=post action="$base_url$cal_admin/new_user">
Enter the email address of the new user:
<input name="email"><br>
Enter the user name of the new user:
<input name="uid"><br>
Enter the full name of the user, as they would like it on the calendar:<br>
<input name="user_name"><br>
Enter your password (Calendar Administrator)
<input type=password size=25 name="pass"><br>
<hr>
The password of the new user will be the same as their user name.  They will need to change it to something more secure as soon as possible.<br>
<input type=submit value="Add user">
</form>
<center>
[ <a href="$cal_admin">Administrative functions</a> | <a href="$base_url$hypercal">HyperCal</a> ]
</center>
</body></html>
HTML
		}

sub new_user_2	{

&form_parse;
print "<html><head><title>Adding User ...</title></head>";
print "User <b>$FORM{'uid'}</b> being added.....";
print "<hr>";
# foreach $key (keys %FORM)	{
# print "$key = $FORM{$key} <br> \n";}

#  Read the .htpasswd file into an array.
open (PASS, $htpass);
@file=<PASS>;
close PASS;
foreach $line (@file)	{
chop $line;
($user,$crypted_word)=split(/:/,$line);
$PASS{$user}=$crypted_word;		}

#  If the admin password is correct, add the user.
if ($PASS{$admin_uid} eq crypt($FORM{'pass'},$PASS{$admin_uid}))  {

	#  Read in the .htgroup file
	open (GROUP,$htgroup);
	@groups=<GROUP>;
	close GROUP;
	for (@groups) {chop};

	#  Add the new user to the relevant group.
	open (GROUP, ">$htgroup");
	foreach $line (@groups) {
	($group, $members)=split(/:/,$line);
	if ($group eq "calendar") {
		        if ($members=~/$FORM{'uid'}/)
			  {print "User is already in the group calendar.<br>"}	
			else {$line.=" $FORM{'uid'}";}}
	print GROUP "$line\n";	}  # end foreach
	close GROUP;

	#  We already have the password file, just add the new user
	$user=$FORM{'uid'};
if ($PASS{$user} eq "") {
    srand(time ^ $$);                                       # random seed
    @saltchars=('a'..'z','A'..'Z',0..9,'.','/');            # valid salt chars
    $salt=$saltchars[int(rand($#saltchars+1))];     # first random salt char
    $salt.=$saltchars[int(rand($#saltchars+1))];    # second random salt char
	
	$new_password=crypt($user,$salt);
	$line="$user:$new_password";
	open (PASS, ">>$htpass");
	print PASS "$line\n";
	close PASS;		}
else {print "User is already in the passwd file.<br>";}

#  Make a user directory for the new user
$uid=$FORM{'uid'};
$user_name=$FORM{'user_name'};

mkdir ("$users_dir$uid", 0777);
if ($!=~/exists/)	{
print "The directory $users_dir$uid already exists.  Either there is another user by that name, or this user has already been added.<br>";}

else	{

open (FILE,">$users_dir/$uid/datebook");
close FILE;
chmod 0666, "$users_dir/$uid/datebook";

open (FILE,">$users_dir/$uid/announce");
close FILE;
chmod 0666, "$users_dir/$uid/announce";

open (FILE,">$users_dir/$uid/hypercal_id");
close FILE;
chmod 0666, "$users_dir/$uid/hypercal_id";

open (VARS, ">$users_dir/$uid/variables");
print VARS <<EndOfFile;
#########################################################################
#  Variables

\$add_date.="/personal";
\$del_date.="/personal";
\$disp_day.="/personal";
\$edit_announce.="/personal";
\$hypercal.="/personal";

# Other files

\$datebook="\$users_dir/$uid/datebook";
\$hypercal_id="\$users_dir/$uid/hypercal_id";
\$announce="\$users_dir/$uid/announce";

\$title="Personal calendar, $user_name";
# Title of the calendar.

\$personal_on="yes";

##########################################################
# Do not change this, Do not put anything below this.
# File must return "true" value at termination
1;
##########################################################
EndOfFile
		}  # end else
#  Users directory and files should be right now

print <<"HTML";
User added - unless there are error messages above..<br>
<hr>
<center>
[ <a href="$base_url$hypercal">HyperCal</a> | <a href=$base_url$cal_admin>CalAdmin</a> ]
</center>
HTML

&mail_user;  # send mail to the new user.
  } # end if passwords matched

else	{  # If the admin passwd does not match, chastise the hacker.
print <<"HTML";
Your password does not match the administrative password, you hacker person!<br>
Check the password and <a href="$base_url$cal_admin">try again</a>.
<hr>
HTML
	}  # end else

print "</body></html>";

}  # End of sub new_user_2

sub mail_user	{

#  Send mail to the new user informing them

$SENDMAIL='/usr/lib/sendmail';  # This is the location of the           
                                # sendmail program on your system       
                                                                        
open (MAIL, "| $SENDMAIL $FORM{'email'}");                                  
print MAIL "Reply-to: $email ($admin_mail)\n";                                
print MAIL "From: $admin_mail ($admin)\n";                                    
print MAIL "To: $FORM{'uid'}\n";                                          
print MAIL "Subject: New User ID\n\n";                                       
print MAIL "========================================================\n";
print MAIL "========================================================\n";
print MAIL "You have been added as a user on the calendar.\n";
print MAIL "Your user id is $FORM{'uid'} and your password, at the moment is $FORM{'uid'}.\n";
print MAIL "Please change your password as soon as possible.  You can do this by going\n";
print MAIL "to the calendar, selecting the CHANGE PASSWORD link, and\n";
print MAIL "following the instructions.\n";
print MAIL "\n";
close MAIL;

}		#  end mail_user
	


sub del_user	{
print <<HTML;
<html>
<head><title>Delete a user</title></head>
<body>
<h2>Delete a user</h2>
Please select the user you wish to delete:<br>
<form method=post action="$base_url$cal_admin/del_user">
<select name="user_delete">
HTML

@options=`ls $users_dir`;
foreach $option (@options)	{
print "<option>$option</option>";	}
print "</select><br>";
print "Enter your password:<br>";
print "<input type=password name=\"passwd\"><hr>";
print "<input type=submit value=\"Delete the user\">";
print "<hr></body></html>";
}	# end of sub del_user

sub del_user_2	{
#  Do the dirty work:  remove the user's directory, and their
#  name from the group file.
&form_parse;

#  Read the .htpasswd file into an array.
open (PASS, $htpass);
@file=<PASS>;
close PASS;
foreach $line (@file)	{
chop $line;
($user,$crypted_word)=split(/:/,$line);
$PASS{$user}=$crypted_word;		}

#  If the admin password is correct, nuke the user.
if ($PASS{$admin_uid} eq crypt($FORM{'passwd'},$PASS{$admin_uid}))  {
$success=`rm -r $users_dir/$FORM{'user_delete'}`;

#  You still need to remove them from the group file.
#  Perhaps from the .htpasswd file too - perhaps this is an option

print $success;
print "The user <b>$FORM{'user_delete'}</b> has been deleted.";	
print "<br>";
print "<center>";
print "[ <a href=\"$base_url$hypercal\">HyperCal</a> | <a href=\"$base_url$cal_admin\">CalAdmin</a> ]";
print "</center>\n";
print "</body></html>";}
else {print "passwords don't match"}	}

sub reset_user	{
print "sub reset_user";}


sub set_vars	{
print "sub set_vars";	}
