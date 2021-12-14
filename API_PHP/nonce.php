<?php

$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, "https://wbsapi.withings.net/v2/signature");

curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([ 
	'action' => 'getnonce',
	'client_id' => '156a17f1c19805f39cd29194733717a4a0a8b254d550ae162f01a386618ad53c',
	'timestamp' => 'timestamp',
	'signature' => 'ab44d1c13cb1680f1843546746eaf4227258e6d6467dfed923874bbe937ad5cb'
]));

$rsp = curl_exec($ch);
curl_close($ch);

var_dump($rsp);

?>