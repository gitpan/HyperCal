#
#	Determine if the personal part is being called, and alter 
# 	some variables accordingly.
#####

#  The string passed in from the main program is $sub
$sub=~s/personal\///;	# strip the "personal" off of the string;

$user_id=$ENV{'REMOTE_USER'};	# Get the user id from the auth info

$user_variables=~s/USERNAME/$user_id/;
require "$user_variables";

1;
