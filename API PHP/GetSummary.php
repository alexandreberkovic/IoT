<?php

$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, "https://wbsapi.withings.net/v2/sleep ");

curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

curl_setopt($ch, CURLOPT_HTTPHEADER, [
	'Authorization: Bearer 96fdbabd15474d2ca8dc56be0e2e41a7b1e77f46'
]);

curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([ 
	'action' => 'getsummary',
	'startdateymd' => '2021-10-11',
	'enddateymd' => '2021-11-11'
]));

$rsp = curl_exec($ch);
curl_close($ch);

var_dump($rsp);

?>