<?php

$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, "https://wbsapi.withings.net/v2/sleep");

curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

curl_setopt($ch, CURLOPT_HTTPHEADER, [
	'Authorization: Bearer 8fcb2cb543879a0c222538587180737fa5cb3806'
]);

curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([ 
	'action' => 'get',
	'startdate' => '2021-11-10',
	'enddate' => '2021-11-11',
	'data_fields' => 'hr'
]));

$rsp = curl_exec($ch);
curl_close($ch);

var_dump($rsp);

?>