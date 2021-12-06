<?php

$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, "https://wbsapi.withings.net/v2/oauth2");

curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([ 
	'action' => 'requesttoken',
	'grant_type' => 'authorization_code',
	'client_id' => '156a17f1c19805f39cd29194733717a4a0a8b254d550ae162f01a386618ad53c',
	'client_secret' => '89553a120b09f7518b6f6c18f63bd2fdc254dbc8cfbc9c746b603660b8000d89',
	'grant_type' => 'authorization_code',
	'code' => 'd6982cdf-2134-474c-936f-e7f139d5e3b2',
	'redirect_uri' => 'https://hooks.zapier.com/hooks/catch/11269009/bdt08t3/'
]));

$rsp = curl_exec($ch);
curl_close($ch);

var_dump($rsp);

?>