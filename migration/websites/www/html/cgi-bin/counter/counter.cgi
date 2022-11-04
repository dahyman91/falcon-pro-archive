#!/usr/bin/perl
##############################################################################
# Notice
# ------
# This software is proprietary and may not be modified, copied,
# or reproduced in any manner without the expressed witten permission
# of  Virtual Publisher, Inc.  This software is distributed under a site
# license that permits it's use on a single domain/web site.
# The complete source code license agreement that accompanies this
# software is made a part of this software as if written herein.
#
#
# File:      ctr-pro.cgi
#
# Auth:      Virtual Publisher, Inc., Copyright 1996, 1997 All Rights Reserved
#            Website-http://virtualpublisher.com
# Version:   3.0
# Release:   1 Sep, 1997
#
#
# Desc:      Hits Counter - Standard Version "xbm"
#
#            This script works with both the "GET" and "POST" CGI
#            methods and is compatible with both Perl 4 and Perl 5.
#
###################################################################

$ErrMsg{'InvalidCtrVal'} = 
    'Counter was not reset. Invalid counter value $param1 ( must be a positive number )';
$ErrMsg{'ErrorOpenCtrFile'} =
    'Cannot open counter file $param1';
$ErrMsg{'ErrorOpenAccFile'} =
    'Cannot open access file $param1';
$ErrMsg{'ErrorUpdateFile'} =
    'Cannot update file $param1';
$ErrMsg{'ChmodFailed'} =
    'Cannot execute chmod command.';
$ErrMsg{'ErrorOpenFile'} =
    'Cannot open file $param1';
$ErrMsg{'ErrorOpenTemplate'} =
    'Cannot open template file $param1';
$ErrMsg{'ErrorOpenSetup'} =
    'Cannot open setup file $param1';

# config info from setup file
%conf = (); # PARAMETERS section
%templates = (); # TEMPLATES section

#------------------------------
&initialize;
&incrementCount;
#------------------------------
if ( $rst eq 'yes' ) {
    &record;
    exit(0);
}
#------------------------------
if ( $viz eq 'no' ) {	
    print ("Content-type: image/x-xbitmap\n\n");
    printf ("#define count_width 1\n#define count_height 1\n");
    print ("0x00");
} else {
    &generateBitmap;
    &writeBitmap;
}
&record;  
exit(0);


##############################################################################
# 	
#
##############################################################################
sub initialize {
	
	$minLen = 1;		# min number of digits in bitmap
	$cheight = 16;		# char height. 
	$| = 1;			# unbuffer the output


	$lock = 2;		# 2 | 4 = 6, lock it exclusively & non-blocking
	$unlock = 8;		# unlock the file
	

	%options = ();
	@args = ();
	@domain = ();
#-----------------------------------------
	$agent = "";
	$userURL = " ";
	$host = "";
	$ip = "";
	$arglist = "";
	if( defined($ENV{'HTTP_USER_AGENT'}) ) {
	    $agent = $ENV{'HTTP_USER_AGENT'};
	}
	if( defined($ENV{'HTTP_REFERER'}) ) {
	    $userURL = $ENV{'HTTP_REFERER'};
	}
	if( defined($ENV{'REMOTE_HOST'}) ) {
	    $host = $ENV{'REMOTE_HOST'};
	}
	if( defined($ENV{'REMOTE_ADDR'}) ) {
	    $ip = $ENV{'REMOTE_ADDR'};
	}
	if( defined($ENV{'QUERY_STRING'}) ) {
	    $arglist = $ENV{'QUERY_STRING'};
	}
#-----------------------------------------------------
@domain = split(/\./,$host);	
if ( $ip eq $host || scalar(@domain) == 0 ) {
	$country = $ip;
	$host = $ip;
} else {
	@domain = split(/\./,$host);
	if (scalar(@domain)==1) {
		$country = 'local';
	} else {
		$country = pop(@domain);
	}
}
#------------------------------------------------------

	@components   = split( /\// , $userURL );
	$namefilelong = $components[$#components];
	($namefile)   = split( /\./ , $namefilelong );


#------------------args------------------------
	@args = split(/\&/,$arglist);
	for $i ( @args ) {
		($var,$val) = split(/=/,$i);
		$options{$var}=$val;
	}
	
	$rst   = "no";
	$viz   = "yes";
	$isinv = "no";

	if ( defined $options{'rst'} ) {
		$rst = $options{'rst'};
	}
	if ( defined $options{'counternumber'} ) {
		$rstCtrVal = $options{'counternumber'};
	}
	if ( defined $options{'fnam'} ) {
		$namefile = $options{'fnam'};
	}
	if ( defined $options{'viz'} ) {
		$viz = $options{'viz'};
	}
	if ( defined $options{'isinv'} ) {
		$isinv = $options{'isinv'}; 		
	}
	if ( defined $options{'setup'} ) {
	    $SetupFile = $options{'setup'};
            # Convert %XX from hex numbers to alphanumeric
	    $SetupFile =~ s/%(..)/pack("c",hex($1))/ge;
	}
	else {
	    $SetupFile = "setup.txt";
	}
	# load configuration info
	%conf = &ReadConfigSection( $SetupFile, "PARAMETERS" );
	%templates = &ReadConfigSection( $SetupFile, "TEMPLATES" );

	$HTML_DIR = $conf{'HtmlDir'};
	$HTML_URL = $conf{'HtmlUrl'};
	$SCRIPT_URL = $conf{'ScriptUrl'};
	$accfilename = $conf{'AccFileName'};
	$htmldir = "${HTML_DIR}" ;

#-----------------------------------------

	$htmlfile = $htmldir . "/" . $conf{'LogsDir'} . "/" . $namefile . ".html";
	$counterFile = $htmldir . "/" . $conf{'LogsDir'} . "/" . $namefile . ".log" ;
	$accfile = $htmldir . "/" . $conf{'LogsDir'} . "/" . $accfilename . ".log";
	$accfilehtml = $htmldir . "/" . $conf{'LogsDir'} . "/" . $accfilename . ".html";
	$locationaccfilehtml = $HTML_URL . "/" . $conf{'LogsDir'} . "/" . 
	    $accfilename . ".html";
#-----------------------------------------

	#######################################################
	# 
	###############
    @dg =   ("00 00 e0 07 f0 0f 30 0c 30 0c 30 0c 30 0c 30 0c 30 0c 30 0c 30 0c 30 0c 30 0c f0 0f e0 07 00 00",    # 0
            "00 00 80 01 c0 01 e0 01 80 01 80 01 80 01 80 01 80 01 80 01 80 01 80 01 80 01 e0 07 e0 07 00 00",     # 1
            "00 00 e0 07 f8 1f 18 18 18 18 18 1c 00 0e 00 07 80 03 c0 01 e0 00 70 00 38 00 f8 1f f8 1f 00 00",     # 2
            "00 00 f0 07 f0 0f 30 0c 00 0c 00 0c 00 0c c0 0f c0 0f 00 0c 00 0c 00 0c 30 0c f0 0f f0 07 00 00",     # 3
            "00 00 00 06 00 0f 80 0f c0 0d e0 0c 70 0c f0 0f f0 0f 00 0c 00 0c 00 0c 00 0c 00 0c 00 0c 00 00",     # 4
            "00 00 e0 0f f0 0f 30 00 30 00 30 00 30 00 f0 07 e0 0f 00 0c 00 0c 00 0c 30 0c f0 07 e0 03 00 00",     # 5
            "00 00 20 00 30 00 30 00 30 00 30 00 30 00 f0 07 f0 0f 30 0c 30 0c 30 0c 30 0c f0 0f e0 0f 00 00",     # 6
            "00 00 f0 0f f0 0f 30 0c 30 0c 00 06 00 03 00 03 80 01 80 01 c0 00 c0 00 60 00 60 00 60 00 00 00",     # 7
            "00 00 e0 07 f0 0f 30 0c 30 0c 30 0c 60 06 c0 03 c0 03 60 06 30 0c 30 0c 30 0c f0 0f e0 07 00 00",     # 8
            "00 00 e0 07 f0 0f 30 0c 30 0c 30 0c e0 0f c0 0f 00 0e 00 0e 00 07 80 03 c0 01 e0 00 60 00 00 00");    # 9

	
	@idg = ("ff ff 1f f8 0f f0 cf f3 cf f3 cf f3 cf f3 cf f3 cf f3 cf f3 cf f3 cf f3 cf f3 0f f0 1f f8 ff ff",		#0
		"ff ff 7f fe 3f fe 1f fe 7f fe 7f fe 7f fe 7f fe 7f fe 7f fe 7f fe 7f fe 7f fe 1f f8 1f f8 ff ff",			#1
		"ff ff 1f f8 07 e0 e7 e7 e7 e7 e7 e3 ff f1 ff f8 7f fc 3f fe 1f ff 8f ff c7 ff 07 e0 07 e0 ff ff",			#2
		"ff ff 0f f8 0f f0 cf f3 ff f3 ff f3 ff f3 3f f0 3f f0 ff f3 ff f3 ff f3 3f f3 0f f0 0f f8 ff ff",			#3
		"ff ff ff f9 ff f0 7f f0 3f f2 1f f3 8f f3 0f f0 0f f0 ff f3 ff f3 ff f3 ff f3 ff f3 ff f3 ff ff",			#4
		"ff ff 1f f0 0f f0 cf ff cf ff cf ff cf ff 0f f8 1f f0 ff f3 ff f3 ff f3 cf f3 0f f8 1f fc ff ff",			#5
		"ff ff df ff cf ff cf ff cf ff cf ff cf ff 0f f8 0f f0 cf f3 cf f3 cf f3 cf f3 0f f0 1f f0 ff ff",			#6
		"ff ff 0f f0 0f f0 cf f3 cf f3 ff f9 ff fc ff fc 7f fe 7f fe 3f ff 3f ff 9f ff 9f ff 9f ff ff ff",			#7
		"ff ff 1f f8 0f f0 cf f3 cf f3 cf f3 9f f9 3f fc 3f fc 9f f9 cf f3 cf f3 cf f3 0f f0 1f f8 ff ff",			#8
		"ff ff 1f f8 0f f0 cf f3 cf f3 cf f3 1f f0 3f f0 ff f1 ff f1 ff f8 7f fc 3f fe 1f ff 9f ff ff ff");			#9

	@digits = @dg;
	if ( $isinv eq 'yes' ) {
		@digits = @idg;
	}
}
############################################################################
#	
############################################################################
sub writeBitmap {
	print "Content-type: image/x-xbitmap\n\n";
	printf "#define count_width %d\n#define count_height %d\n",
		$len*16, $cheight;
   	printf "static char count_bits[] = {\n";

   	for($i = 0; $i < ($#bytes + 1); $i++) {
   		print("0x$bytes[$i],");
   	}
   	print("};\n");
}

###############################################################################
# 
###############################################################################
sub generateBitmap {
   	$count = $stat_hash_infstat{'totalReads'};
   	@bytes = ();
   	$len = length($count) > $minLen ? length($count) : $minLen;
   	$formattedCount = sprintf("%0${len}d",$count);
	for ($y=0; $y < 16; $y++) {
   	   for ($x=0; $x < $len; $x++) {
       		$digit = substr($formattedCount,$x,1);
       		$byte = substr($digits[$digit],$y*6,2);
   			push(@bytes,$byte);
			$byte2 = substr($digits[$digit],$y*6+3,2);
			push(@bytes,$byte2);
   	   }
   	}
}

#############################################################################
# 	
#############################################################################
sub incrementCount {
    
    if (-e $accfile) {
	open(ACCFILE,"+<$accfile") || &Error( 'ErrorOpenAccFile', $accfile );
	flock( ACCFILE, $lock );
	#
	<ACCFILE>;
	while ( ($y=<ACCFILE>) ) {
	    chop($y);
	    ($var,$val) = split(/=/,$y);
	    $stat_hash_accfiles{$var}=$val;
	}
	
	if ( defined ( $stat_hash_accfiles{$namefile} ) ) {
	    $stat_hash_accfiles{$namefile}++;
	} else {
	    $stat_hash_accfiles{$namefile} = '1';
	}
	
    } else {
	open(ACCFILE,">$accfile") || 
	    &Error( 'ErrorOpenAccFile', $accfile );
	flock( LOGFILE, $lock );
	$stat_hash_accfiles{$namefile} = '1';
    }
    
    if( -e $counterFile ) {	
	
	open(LOGFILE,"+<$counterFile") || 
	    &Error( 'ErrorUpdateFile', $counterFile );
	flock(LOGFILE,$lock);
	#
	#get %stat_hash_infstat
	#
	<LOGFILE>;
	for ($i=1;$i<10;$i++) {
	    $y=<LOGFILE>;
	    chop($y);
	    ($var,$val) = split(/=/,$y);
	    $stat_hash_infstat{$var}=$val;
	}
	#
	#get %stat_hash{dayarray}
	#
	<LOGFILE>;
	$y=<LOGFILE>;
	chop($y);
	@stat_hash_dayarray =  split(/\s+/,$y) ;
	#
	#get %stat_hash{montharray}
	#
	<LOGFILE>;
	$y=<LOGFILE>;
	chop($y);
	@stat_hash_montharray =  split(/\s+/,$y) ;
	#
	#
	#
	<LOGFILE>;
	while ($y=<LOGFILE>) {
	    last if ($y =~ s/^\n//);
	    chop($y);
	    ($var,$val) = split(/=/,$y);
	    $stat_hash_idxcountry{$var}=$val;
	}
	#
	#
	#
	<LOGFILE>;
	for ($i=1;$i<21;$i++) {
	    $y = <LOGFILE>;
	    chop($y);
	    $stat_hash_visitors[$i] = $y;
	}
	#
	#
#-------------------
	&gettime;
#-------------------
	
	if ( $stat_hash_infstat{'lyear'} == $year ) {
	    $stat_hash_infstat{'yeartodate'}++;
	    if ( $stat_hash_infstat{'lmonth'} == $mon ) {
		$stat_hash_montharray[$mon]++;
		if ( $stat_hash_infstat{'lday'} == $mday ) {
		    $stat_hash_dayarray[$mday-1]++;
		    $stat_hash_infstat{'accesstoday'}++;
		} else {
		    $stat_hash_dayarray[$mday-1] = 1;
		    $stat_hash_infstat{'lday'} = $mday;
		    $stat_hash_infstat{'accesstoday'} = 1;
		}
	    } else {
		&checkmaxday;
		&anulday;
		$stat_hash_montharray[$mon] = 1;
		$stat_hash_dayarray[$mday-1] = 1 ;
		$stat_hash_infstat{'accesstoday'} = 1;
		$stat_hash_infstat{'lday'} = $mday;
		$stat_hash_infstat{'lmonth'} = $mon;
	    }
	} else {
	    &checkmaxday;
	    &anulday;
	    $stat_hash_infstat{'yeartodate'} = 1;
	    $stat_hash_montharray[$mon] = 1;
	    $stat_hash_dayarray[$mday-1] = 1;
	    $stat_hash_infstat{'accesstoday'} = 1;
	    $stat_hash_infstat{'lday'} = $mday;
	    $stat_hash_infstat{'lmonth'} = $mon;
	    $stat_hash_infstat{'lyear'} = $year;
	}
#----------------------- over with datas --------------------------
	
	if ( defined $stat_hash_idxcountry{$country} ) {
	    $stat_hash_idxcountry{$country}++; 
	} else { 
	    $stat_hash_idxcountry{$country} = '1';
	}

	shift @stat_hash_visitors;
	
	if($stat_hash_idxcountry{$country} ne '0') {
	    $stat_hash_visitors[20]="$host\t$date\t$agent";
	}
	if ($rst eq 'yes') {
	    if( defined( $rstCtrVal ) ) {
		if( $rstCtrVal !~ /^[0-9]+$/ ) {
		    &Error( 'InvalidCtrVal', $rstCtrVal );
		}
		$stat_hash_infstat{'totalReads'} = $rstCtrVal;
	    }
	    else {
		print "Content-type: text/html\n\n";
		print "<html>\n<head><title>Xbm Counter Reset Page</title></head>\n";
		print "<body bgcolor=\"#FFFFFF\" vlink=\"#FF0000\" alink=\"#C0C0C0\">\n";
		print "<form method=\"GET\" action=\"$conf{'ScriptUrl'}\">\n";
		print "<input type=\"hidden\" name=\"rst\" value=\"yes\">\n";
		print "<input type=\"hidden\" name=\"fnam\" value=\"$namefile\">\n";
		print "<input type=\"hidden\" name=\"setup\" value=\"$SetupFile\">\n";
		print "Reset counter to: <input type=\"text\" name=\"counternumber\" " .
		    "size=6> &nbsp;\n";
		print "<input type=\"submit\" value=\"Reset Counter\">\n";
		print "</form>\n";
		print "</body></html>\n";
		exit(0);
	    } 

	    print "Content-type: text/plain\n\n";
	    print "Counter reset to $rstCtrVal";

	}
	else {
	    $stat_hash_infstat{'totalReads'}++;
	}
#----------------------reset finished -----------------------------
	
	
	if ( ($stat_hash_infstat{'lmonth'}!=$month-1) || (! $maxday) ) {
	    &checkmaxday;
	    $stat_hash_infstat{'maxday'} = $maxday;
	}
	
       	if ($stat_hash_infstat{'accesstoday'} > $stat_hash_infstat{'high'}) { 
	    $stat_hash_infstat{'high'} = $stat_hash_infstat{'accesstoday'};
       	}
	
# new counter 
# -------------------------------------------------------------
    } 
    else { 	
	# new counter. open with write access
	open(LOGFILE,">$counterFile") || 
	    &Error( 'ErrorOpenCtrFile', $counterFile );
	
	flock( LOGFILE, $lock );
	#--------------------------------------
	&gettime;
	&checkmaxday;
	
	$stat_hash_infstat{'maxday'} = $maxday;
	
	&anulday;
	&anulmonth;
	
	$stat_hash_montharray[$mon] = 1;
	$stat_hash_dayarray[$mday-1] = 1;
	
	$stat_hash_infstat{'totalReads'} = 1;
	$stat_hash_infstat{'accesstoday'} = 1;
	$stat_hash_infstat{'high'} = 1;
	$stat_hash_infstat{'yeartodate'} = 1;
	$stat_hash_infstat{'maxday'} = $maxday;
	$stat_hash_infstat{'lday'} = $today; 
	$stat_hash_infstat{'lmonth'} = $mon;
	$stat_hash_infstat{'lyear'} = $year;
	$stat_hash_infstat{'creatdate'} = $day;
	$stat_hash_idxcountry{$country} = 1;

	for $i (1..20) {
	    $stat_hash_visitors[$i] = "none";
	}
	$stat_hash_visitors[20]="$host\t$date\t$agent";
    }
    
    if ($stat_hash_infstat{'totalReads'} == 1) {   
	$stat_hash_infstat{'creatdate'} = $day ;
    } 

#print the counterfile .......
#--------------------------------------------------------------------
    seek(LOGFILE,0,0);	# go to the first line to rewrite data
    print (LOGFILE "--[info_stat]\n");
    foreach $y ( keys %stat_hash_infstat ) {
	print (LOGFILE "$y=$stat_hash_infstat{$y}\n");
    }
    print (LOGFILE "--[dayarray]\n");
    foreach $y ( 0 .. $maxday-1 ) {
	print (LOGFILE "$stat_hash_dayarray[$y] ");
    };
    print (LOGFILE "\n--[montharray]\n");
    foreach $y ( 0 .. 11 ) {
	print (LOGFILE "$stat_hash_montharray[$y] ");
    };
    print (LOGFILE "\n--[idxcountry]--\n");
    foreach $y ( keys %stat_hash_idxcountry ) {
	print (LOGFILE "$y=$stat_hash_idxcountry{$y}\n");
    }
    print (LOGFILE "\n--[visitors]--\n");
    foreach $y (1..20) {
	print (LOGFILE "$stat_hash_visitors[$y]\n");
    }
    
    
    seek(ACCFILE,0,0);  
    
    print (ACCFILE "--[accfiles]--\n");
    foreach $y ( keys %stat_hash_accfiles ) {
	print (ACCFILE "$y=$stat_hash_accfiles{$y}\n");
    }
    
    $pos = tell(ACCFILE);
    truncate(ACCFILE, $pos) if $pos > 0;
    flock(ACCFILE,$unlock);
    close(ACCFILE);
#    $err = `chmod 777 $accfile`;
    &Error( 'ChmodFailed' ) if( $err ne '' );
    
    $pos = tell(LOGFILE);
    truncate(LOGFILE,$pos) if $pos >0;
    flock(LOGFILE,$unlock);
    close(LOGFILE);
#    $err = `chmod 777 $counterFile`;
    &Error( 'ChmodFailed' ) if( $err ne '' );
    
#--------------------------------------------------------------------
}
##############################################################################
#	
##############################################################################
sub gettime {
    ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
    $date = sprintf("%02d:%02d:%02d %02d/%02d/%02d",
		    $hour,$min,$sec,$year,$mon+1,$mday);
    $day = sprintf("%02d/%02d/%02d",$year,$mon+1,$mday);
    $today = sprintf("%02d",$mday);
    $month = sprintf("%02d",$mon+1);
}

#############################################################################
#	sub Record
#############################################################################
sub record {
    local(%templ,%acctempl);

    open(LOG,">${htmlfile}") 
	|| &Error( 'ErrorOpenFile', $htmlfile );

    flock( LOG, $lock );
    
    open(ACCFILEHTML,">${accfilehtml}")
	|| &Error( 'ErrorOpenFile', $accfilehtml );

    flock( ACCFILEHTML, $lock );
    
# get the report template file
    $repFile = "";
    $file = $HTML_DIR . "/" . $templates{'ReportTemplate'};
    open( TEMPL, $file )
	|| &Error( 'ErrorOpenTemplate', $file );

    while( <TEMPL> ) {
	$repFile .= $_;
    }
    close( TEMPL );
# get the account template file
    $accFile = "";
    $file = $HTML_DIR . "/" . $templates{'AccessTemplate'};
    open( TEMPL, $file )
	|| &Error( 'ErrorOpenTemplate', $file );
    while( <TEMPL> ) {
	$accFile .= $_;
    }
    close( TEMPL );
    
# initialize the hash for template formating
    $templ{'TotalVisitors'} = "<pre>     There have been <b>" .
	" $stat_hash_infstat{totalReads} </b> visitors since <b> " .
	    "$stat_hash_infstat{creatdate}.</b><br></pre>";
    $templ{'Reset'} = "<pre>\n     <a href=${SCRIPT_URL}?" .
	"rst=yes&setup=${SetupFile}>RESET COUNT</a>\n\n</pre>";
    $templ{'TodayVisitors'} = "<pre>     There have been <b> " .
	"$stat_hash_infstat{accesstoday} </b> visitors on $day and " .
	    "Highest hits/day so far is<b> $stat_hash_infstat{high} </b>\n</pre>" ;

    @nummonths = ();
    @nummonths = ( "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
		  "Aug", "Sep", "Oct", "Nov", "Dec" );
    
    $templ{'YearToDate'} = "<pre><hr size=1><b>     " .
	"Year to date : $stat_hash_infstat{yeartodate}\n</pre>";
    $templ{'DailyStats'} = "" ;
    $templ{'DailyStats'} .= "<pre><hr size=1><b>    " .
	" Daily Statistics</b>: $month\/$year\n";
    # hits/day
    $templ{'DailyStats'} .= "<hr><b>     Day        " .
	" Hits/day      Day         Hits/day      Day         Hits/day</b>\n";
    $format = "     @<<<<<<<<<< @<<<<<<<<<<<< @<<<<<<<<<< " .
	"@<<<<<<<<<<<< @<<<<<<<<<< @<<<<<<<<<<<<";
    for( $num=0; $num <= 10; $num++ ) {
	$crtday = $num+1; 
	$line = &my_formline( $format, $crtday, $stat_hash_dayarray[$num],
			     $crtday+11, $stat_hash_dayarray[$num+11], 
			     ($crtday+22 <= $maxday ? $crtday+22 : ""),
			     ( $crtday+22 <= $maxday ? $stat_hash_dayarray[$num+22] : "" ) ); 
	$templ{'DailyStats'} .= $line ;
    }

    $templ{'DailyStats'} .= "\n\n";
    # hits/month
    $templ{'DailyStats'} .= "<b>     Month       " .
	"Hits/month    Month       Hits/month</b>\n";
    $format = "     @<<<<<<<<<< @<<<<<<<<<<<< @<<<<<<<<<< @<<<<<<<<<<<<";

    for( $num=0; $num <= 5; $num++ ) {
	$crtday = $num+1; 
	$line = &my_formline( $format, $nummonths[$num], 
			     $stat_hash_montharray[$num], $nummonths[$num+6],
			     $stat_hash_montharray[$num+6]); 
	$templ{'DailyStats'} .= $line ;
    }
    $templ{'DailyStats'} .= "\n</pre>";
#-----------------------------------------
    $templ{'Countries'} .= "<pre><hr size=1><b>     Countries             Hits</b>\n\n";
    
    $format = "     @<<<<<<<<<<<<<<<<<<<< @<<<<<<<<<<<<<<<<<<<<";
    foreach $y ( keys %stat_hash_idxcountry ) {
	$line = &my_formline($format, $y, $stat_hash_idxcountry{$y});
	$templ{'Countries'} .= $line ;
    }
    $templ{'Countries'} .= "\n</pre>";
#------------------------------------------
    $templ{'AccessRef'} = "<pre><a href=${locationaccfilehtml}> " .
	"    Files accessed</a>\n</pre>";

    $acctempl{'Accesses'} = "<pre>\n";
    $acctempl{'Accesses'} .= "<hr size=1><b>     Files accessed...</b>\n\n";

    $format = "             @<<<<<<<<<<<<<<<<<<<<<<<<<<<" .
	"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" .
	    "<<<<<<<<<<<<<<<<<<<<<<<<<<<<@<<<<<<<<<<<<<<<<<<<<";
    foreach $y ( keys %stat_hash_accfiles ) {
	$line = &my_formline( $format, "<a href=\"$HTML_URL/" . 
			     $conf{'LogsDir'} . "/$y.html\">$y</a>", 
			     $stat_hash_accfiles{$y});
	$acctempl{'Accesses'} .= $line ;
    }
    $acctempl{'Accesses'} .= "\n</pre>"; 

#--------------------------------------------
    $templ{'Visitors'} = "<pre><hr size=1><b>     Last 20 visitors...</b>\n\n";
    $templ{'Visitors'} .= "<hr><b>     Host " .
	"                        Time       Date        Browser</b>\n\n";
    $format = "     @<<<<<<<<<<<<<<<<<<<<<<<<<<< @<<<<<<<<< " .
	"@<<<<<<<<<< @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<";
    foreach $i (1..20) {
	$y = 21-$i;
	if ($stat_hash_visitors[$y] =~ 'none') {
	    next;
	} else {
	    ($host, $time, $date, $browser) = split(/\s+/,$stat_hash_visitors[$y],4);
	    $line = &my_formline( $format, $host, $time, $date, $browser);
	    $templ{'Visitors'} .= $line;
	}
    }
    $templ{'Visitors'} .= "\n</pre>";

    $repFile = &FormatAccordingToTemplate( $repFile, *templ );
    print (LOG "$repFile");
    $accFile = &FormatAccordingToTemplate( $accFile, *acctempl );
    print (ACCFILEHTML "$accFile");
    
    flock(LOG,$unlock);
    flock(ACCFILEHTML,$unlock);
    close(ACCFILEHTML) || 
	&Error( 'ErrorUpdateFile', $accfilehtml );
#    $err = `chmod 777 $accfilehtml`;
    &Error( 'ChmodFailed' ) if( $err ne '' );
    close( LOG );

#    $err = `chmod 777 $htmlfile`;
    &Error( 'ChmodFailed' ) if( $err ne '' );
}
#F my_formline
## simulates formline rutine from perl5
## *warning* just @ is supported and just left alignament with '<'
sub my_formline
{
    local($fmt,@vars) = @_;
    local($templine,$lng);
    $templine = "";
    $i = 0;
    while( $fmt =~ s/([^@]*)@(<+)//) {
	if( defined($vars[$i]) ) {
	    $templine .= $1;
	    $lng = length( $vars[$i] );
	    $lng = length( $2 ) - $lng + 1;
	    $templine .= $vars[$i];
	    $templine .= " "x$lng;
	}
	$i++;
    }
    $templine .= "\n";
    return $templine;
}

###############################################################################
#	
###############################################################################
sub checkmaxday {
    if ($month == 2) {	
	if ( $year%4 == 0 ) {
	    $maxday = 29;
	} else {
	    $maxday = 28;
	}
    } else {		
	@maxdays=(31,28,31,30,31,30,31,31,30,31,30,31);
	$maxday = $maxdays[$month-1];
    }
}		

#########################################
#
#########################################
sub anulday {
    @stat_hash_dayarray = ();
    for $y (0..$maxday-1) {
	$stat_hash_dayarray[$y] = "-";
    }
}

##########################################
#
##########################################
sub anulmonth {
    for $y (0..11) {
	$stat_hash_montharray[$y] = "-";
    }		
}

##########################################
#S Configuration File Processing
#
sub ReadConfigSection
{
    local( $filename, $section ) = @_;   
    local( $flag ) = 0;
    local( %ht );
    if( open( CONFIG_FILE, "<$filename" ) )
    {
      READ_CONF:
	while( <CONFIG_FILE> )
        {
            #test for an empty line
            if( /^\n$/ ) { next READ_CONF; }
	    
	    
	    #test for  comments
            if ( /^[#;]/ ) { next READ_CONF; }


            #test for a section 
            if( /^\[(.*)\]$/ )
            {
		if( $flag ) 
                {
		    last READ_CONF;
                }
                if( $1 eq $section )
                {
                    $flag = 1;
                }
                next READ_CONF;
            }

            if( $flag )
            {
                #test for every line in&the config file
                if( /\s*(\S+)\s*=\s*(\S+)\s*/ )
                {
                    %ht = ( %ht, $1, $2 );
                    next READ_CONF;
                }
            }
            else { next READ_CONF; }
		return 0;
        }
	close( CONFIG_FILE );
	
        %ht;
    }
    else
    {
	&Error( 'ErrorOpenSetup', $filename );
    }
    
}
#F  FormatAccordingToTemplate($template, *%placeHolders) . . . . . . .
##
##  PARAMETERS
##      $template, *%placeHolders
##
##  RETURNED VALUE
##      
##
##  DESCRIPTION
##      Formats the template using the values in the placeHolders
#
sub FormatAccordingToTemplate
{
    local ($template, *placeHolders) = @_;
    local ($p_name, $p_val);

    # Here we replace the parameter placeholders with the parameter values
    while (($p_name, $p_val) = each(%placeHolders)) 
    {
        # Replace occurances of '${P_NAME}' and '$P_NAME' with
        # the parameter's value.
        $template =~ s/\$\{${p_name}\}/${p_val}/g;
        $template =~ s/\$${p_name}/${p_val}/g;
    }

    return $template;
}


#F  Error( <ErrorCode>, <params> ) . . . . . . .display an error message
##
##  PARAMETERS
##     errorCode
##     params - up to three parameters    
##
##  RETURNED VALUE
##    none
##
##  DESCRIPTION
##      
#
sub Error
{
    local( $errorCode, $param1, $param2, $param3 ) = @_;
    $message = $ErrMsg{"$errorCode"};

    $message =~ s/\$param1/$param1/;
    $message =~ s/\$param2/$param2/;
    $message =~ s/\$param3/$param3/;
    warn $message; # there is no sense in printing the errors, because the
                   # browser expects an image

    exit( 1 );
}

 
#E  Emacs . . . . . . . . . . . . . . . . . . . . . . . local emacs variables
##
##  Local Variables:
##  mode:               perl
##  outline-regexp:     "^#[A-Za-z]\\|^##[A-Za-z]"
##  fill-column:        77
##  paragraph-start:    "^##$\\\|^#$"
##  paragraph-separate: "^##$\\\|^#$"
##  eval:               (outline-minor-mode)
##  eval:               (hide-body)
##  End:
#
