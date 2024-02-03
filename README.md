# moodle-grade-filler
a script for filling students grades in Moodle. the current moodle system is not ideal so some parameters needs to be filled by hand,
like tasks number.
For every course there is an excel with a column named 'students', specifying the students names seperated by a comma.
also, for each task X, there is a desingnated column named 'exX' and 'exX_comments'. This is a format that i found comfortable using, but others may be used.
The automation will fill each student's grade & comment on the task if there is one.
